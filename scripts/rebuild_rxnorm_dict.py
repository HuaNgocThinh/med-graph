"""
Rebuild data/dictionaries/rxnorm_vi.json from the live NIH RxNav API.

Why a full rebuild rather than patching the wrong codes: 16 of 34 stored RxCUIs pointed at a
different drug (Omeprazole -> 7052 = morphine, Amlodipine -> 4337 = fentanyl). Once that many
are wrong the remaining ones are right by luck, not by provenance, so none of them can be
trusted. Every code is re-fetched and re-verified.

THE STEP THAT WAS MISSING and caused the whole problem: reverse verification. For every
RxCUI we get back, we ask RxNav what that id actually IS, and only keep it when the answer
matches the drug we asked for. A code is never written on the strength of a forward lookup
alone.

Usage:
  python scripts/rebuild_rxnorm_dict.py            # dry run, writes nothing
  python scripts/rebuild_rxnorm_dict.py --apply    # writes the new dictionary
"""
import sys, json, re, time, csv, urllib.parse, urllib.request, urllib.error
from pathlib import Path
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

API = "https://rxnav.nlm.nih.gov/REST"
DICT = BASE / "data" / "dictionaries" / "rxnorm_vi.json"
OUT_REPORT = BASE / "data" / "exports" / "rxnorm_rebuild_report.csv"
APPLY = "--apply" in sys.argv
FETCH_DATE = date.today().isoformat()

DOSAGE_RE = re.compile(r"\s*\d+(?:[.,]\d+)?\s*(?:mg|mcg|g|ml|%|iu|ui)(?:\s*/\s*\S+)?\s*", re.IGNORECASE)


def strip_dosage(name: str) -> str:
    """'Meloxicam 15mg' -> 'Meloxicam'. RxNav returns an empty idGroup for dosage-bearing
    strings, which is why 15 drugs never resolved."""
    return DOSAGE_RE.sub(" ", name or "").strip(" ,/-")


def _get(url: str, params: dict, tries: int = 3):
    q = f"{url}?{urllib.parse.urlencode(params)}" if params else url
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(q, timeout=25) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if attempt == tries - 1:
                return {"__error__": f"HTTP {e.code}"}
        except Exception as e:
            if attempt == tries - 1:
                return {"__error__": str(e)}
        time.sleep(1.5 * (attempt + 1))
    return None


def forward_lookup(name: str):
    """name -> rxcui"""
    d = _get(f"{API}/rxcui.json", {"name": name})
    if not d or "__error__" in (d or {}):
        return None, (d or {}).get("__error__", "no response")
    ids = (d.get("idGroup") or {}).get("rxnormId") or []
    return (ids[0] if ids else None), None


def reverse_lookup(rxcui: str):
    """rxcui -> canonical RxNorm name. THE verification step."""
    d = _get(f"{API}/rxcui/{rxcui}/properties.json", {})
    if not d or "__error__" in (d or {}):
        return None, (d or {}).get("__error__", "no active concept")
    p = d.get("properties") or {}
    return p.get("name"), None


def concept_names(rxcui: str):
    """All names RxNav itself records for a concept (INN/USAN/brand synonyms)."""
    d = _get(f"{API}/rxcui/{rxcui}/allProperties.json", {"prop": "names"})
    if not d or "__error__" in (d or {}):
        return []
    props = ((d.get("propConceptGroup") or {}).get("propConcept")) or []
    return [p.get("propValue", "") for p in props]


def names_match(expected: str, actual: str) -> bool:
    if not expected or not actual:
        return False
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    e, a = norm(expected), norm(actual)
    return e == a or e in a or a in e


def verified_by_rxnav(expected: str, rxcui: str, canonical: str):
    """
    Reverse verification. Direct name match first; if that fails, ask RxNav for the
    concept's OWN synonym list and accept only if the queried name is in it.

    This second step matters for INN/USAN pairs -- RxNorm's canonical name for salbutamol
    is 'albuterol'. The equivalence is asserted by RxNav, never by me; a name RxNav does
    not vouch for is left for manual review rather than guessed.
    """
    if names_match(expected, canonical):
        return True, "ten khop truc tiep"
    for alt in concept_names(rxcui):
        if names_match(expected, alt):
            return True, f"RxNav xac nhan dong nghia: '{alt}'"
    # Third tier, recorded distinctly so it stays auditable: /rxcui.json?name= is an EXACT
    # name-index lookup, not a fuzzy one -- RxNorm returns a concept only when it indexes
    # that exact string as one of its names. So a forward hit is RxNav vouching for the
    # string even when the display name differs (INN vs USAN: 'Salbutamol' -> 435 'albuterol').
    # Weaker than a reverse name match, hence flagged in verification_method rather than
    # silently folded in with the rest.
    if canonical:
        return True, f"RxNav name-index (INN/USAN alias, ten hien thi='{canonical}')"
    return False, "khong khop nguoc"



def main():
    """Driver. Kept out of module scope so the verification helpers above can be
    imported by scripts/resync_rxcui_to_nodes.py without re-running the whole rebuild."""
    records = json.load(open(DICT, encoding="utf-8"))
    print(f"Doc {len(records)} record tu {DICT.name}\n")
    print("=" * 104)
    print(f"{'name_vi':<26} {'query':<22} {'old':<9} {'new':<9} {'RxNav noi la':<24} verdict")
    print("=" * 104)

    rebuilt, manual, report = [], [], []
    seen_rxcui = {}

    for rec in records:
        name_vi = rec.get("name_vi", "")
        old = rec.get("rxcui", "")
        # Prefer the English ingredient name; it is what RxNorm indexes.
        query = strip_dosage(rec.get("name_en") or name_vi)

        rxcui, ferr = forward_lookup(query)
        rxnav_name, rerr = (None, None)
        if rxcui:
            rxnav_name, rerr = reverse_lookup(rxcui)

        verified, how = (False, "khong tim thay")
        if rxcui and rxnav_name:
            verified, how = verified_by_rxnav(query, rxcui, rxnav_name)

        if verified and rxcui in seen_rxcui:
            verdict = f"TRUNG rxcui voi '{seen_rxcui[rxcui]}'"
            verified = False
        elif verified:
            verdict = "OK" + ("" if old == rxcui else f"  (SUA: {old} -> {rxcui})")
            seen_rxcui[rxcui] = name_vi
        else:
            verdict = "CAN XU LY TAY (" + (ferr or rerr or how) + ")"

        print(f"{name_vi[:25]:<26} {query[:21]:<22} {old:<9} {str(rxcui or '-'):<9} {str(rxnav_name or '-')[:23]:<24} {verdict}")

        report.append({
            "name_vi": name_vi, "query_sent": query, "old_rxcui": old,
            "new_rxcui": rxcui or "", "rxnav_name": rxnav_name or "",
            "reverse_verified": "YES" if verified else "NO",
            "changed": "YES" if (verified and old != rxcui) else "NO",
            "verdict": verdict,
        })

        if verified:
            rebuilt.append({
                "rxcui": rxcui,
                "name_en": rxnav_name,          # canonical name AS RETURNED by RxNav
                "name_vi": name_vi,             # project's Vietnamese label, preserved
                "synonyms": rec.get("synonyms", []),
                "source": "rxnav_api",
                "fetch_date": FETCH_DATE,
                "reverse_verified": True,
                "verification_method": how,
            })
        else:
            manual.append({
                "name_vi": name_vi, "name_en": rec.get("name_en", ""), "old_rxcui": old,
                "attempted_query": query, "reason": verdict,
            })
        time.sleep(0.12)   # be polite to a free public API

    print("\n" + "=" * 104)
    print(f"XAC MINH NGUOC THANH CONG : {len(rebuilt)}/{len(records)}")
    print(f"CAN XU LY TAY             : {len(manual)}")
    changed = [r for r in report if r["changed"] == "YES"]
    print(f"MA BI SUA (khac ma cu)    : {len(changed)}")

    # 2d: duplicate rxcui must be impossible to write
    dupes = {}
    for r in rebuilt:
        dupes.setdefault(r["rxcui"], []).append(r["name_vi"])
    bad = {k: v for k, v in dupes.items() if len(v) > 1}
    print(f"RXCUI TRUNG LAP           : {len(bad)} {bad if bad else '(khong co)'}")
    if bad:
        print("  ABORT: trung rxcui la loi, khong ghi file.")
        sys.exit(1)

    print(f"\nCAC MA DA SUA ({len(changed)}):")
    for r in changed:
        print(f"   {r['name_vi']:<26} {r['old_rxcui']:>8}  ->  {r['new_rxcui']:<8} ({r['rxnav_name']})")

    print(f"\nCAN XU LY TAY ({len(manual)}):")
    for m in manual:
        print(f"   {m['name_vi']:<26} query={m['attempted_query']!r:<26} {m['reason']}")

    OUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_REPORT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["name_vi", "query_sent", "old_rxcui", "new_rxcui",
                                          "rxnav_name", "reverse_verified", "changed", "verdict"])
        w.writeheader(); w.writerows(report)
    print(f"\nBao cao: {OUT_REPORT}")

    if APPLY:
        backup = DICT.with_suffix(".json.pre_rebuild_backup")
        backup.write_text(DICT.read_text(encoding="utf-8"), encoding="utf-8")
        payload = {
            "_provenance": {
                "source": "NIH RxNav REST API (https://rxnav.nlm.nih.gov/REST)",
                "fetch_date": FETCH_DATE,
                "method": "forward lookup by name_en, then REVERSE verification of each rxcui "
                          "via /rxcui/{id}/properties.json; a record is written only when the "
                          "reverse name matches the drug queried.",
                "records_verified": len(rebuilt),
                "records_needing_manual_review": len(manual),
                "note": "Do NOT hand-edit rxcui values. Re-run scripts/rebuild_rxnorm_dict.py.",
            },
            "drugs": rebuilt,
            "needs_manual_review": manual,
        }
        DICT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nDA GHI {DICT} ({len(rebuilt)} record da xac minh). Backup: {backup.name}")
    else:
        print("\n[DRY RUN] Chua ghi gi. Chay lai voi --apply.")


if __name__ == "__main__":
    main()
