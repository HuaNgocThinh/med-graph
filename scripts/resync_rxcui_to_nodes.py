"""
Item 2a-2d: push reverse-verified RxCUIs onto the DRUG nodes already in Neo4j.

Why this step exists on its own: rebuilding data/dictionaries/rxnorm_vi.json fixed the LOOKUP,
but the nodes in Neo4j still carried the codes they were created with -- 27 of which named a
different drug (Omeprazole held 7052 = morphine). The linker and the graph disagreed, and a
query only ever reads the graph.

Matching is done by running each node name through the PRODUCTION linker
(RxNormLinker.link_drug), not by string-equality against name_vi. Node names carry dosage
('Meloxicam 15mg') that the dictionary keys do not, so exact-name matching left 11 nodes
unmatched; the linker strips dosage exactly the way it does at build time. Whatever this
script writes is therefore what the pipeline itself would produce.

Every code written is reverse-verified here, regardless of which tier produced it:
  cache hit  -> the record must already carry source=rxnav_api + reverse_verified=true
  API hit    -> /rxcui/{id}/properties.json is called and the name must match
  fuzzy hit  -> REFUSED. A fuzzy score is not evidence about a numeric identifier.
A drug RxNorm has no concept for is left with NO code (null), never an approximate one.

Only the `code` property is touched. No node or relationship is created or deleted.

Usage:
  python scripts/resync_rxcui_to_nodes.py            # dry run + before CSV
  python scripts/resync_rxcui_to_nodes.py --apply
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "scripts"))

from src.config import RXNORM_DICT_PATH                          # noqa: E402
from src.graph.neo4j_client import Neo4jClient                   # noqa: E402
from src.entity_linking.entity_normalizer import normalize_code  # noqa: E402
from src.entity_linking.rxnorm_linker import RxNormLinker        # noqa: E402
from rebuild_rxnorm_dict import strip_dosage, verified_by_rxnav, reverse_lookup  # noqa: E402

EXPORTS = BASE / "data" / "exports"
BEFORE = EXPORTS / "before_rxcui_sync.csv"
AFTER = EXPORTS / "after_rxcui_sync.csv"
LOG = EXPORTS / "rxcui_sync_log.csv"
APPLY = "--apply" in sys.argv

# Item 2d: RxNorm genuinely has no concept for these. Recorded as a limitation of RxNorm's
# coverage of Vietnamese-market products, NOT patched with a near-enough code.
NO_RXNORM_CONCEPT = {
    "Oresol": "Dung dich bu nuoc dien giai (ORS) - RxNorm khong co concept tuong duong",
    "Salmeterol/Fluticasone 50/250 mcg": "Thuoc phoi hop 2 hoat chat dang hit - khong co concept don",
    "Diane-35": "Biet duoc (cyproterone + ethinylestradiol), khong luu hanh tai My",
    "Depakine Chrono 500mg": "Biet duoc valproate phong thich cham - RxNorm chi co hoat chat",
    "Trimebutin 200mg": "Trimebutine khong duoc FDA phe duyet, khong co trong RxNorm",
}


def snapshot(client, path):
    rows = client.execute_query(
        "MATCH (n:DRUG) RETURN n.name AS name, n.code AS code ORDER BY n.name")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "code"])
        for r in rows:
            w.writerow([r["name"], r["code"] if r["code"] is not None else ""])
    return {r["name"]: r["code"] for r in rows}


def graph_totals(client):
    n = client.execute_query("MATCH (n) RETURN count(n) AS c")[0]["c"]
    r = client.execute_query("MATCH ()-[r]->() RETURN count(r) AS c")[0]["c"]
    sids = client.execute_query(
        "MATCH ()-[r]->() WHERE r.source_sample_id IS NOT NULL "
        "UNWIND split(r.source_sample_id, ',') AS s RETURN count(DISTINCT trim(s)) AS c")[0]["c"]
    return n, r, sids


def resolve(name, linker, verified_by_name):
    """Return (new_code | None, method, note) for one node name. Never guesses."""
    if name in NO_RXNORM_CONCEPT:
        return None, "no_concept", "item 2d: " + NO_RXNORM_CONCEPT[name]

    res = linker.link_drug(name)
    code = normalize_code(res.get("code"))
    method = res.get("method", "")

    if not code:
        return None, method or "unlinked", "linker khong tra ve ma nao"

    if method == "fuzzy":
        return None, "fuzzy_refused", (
            f"linker fuzzy ra {code} - TU CHOI: diem fuzzy khong phai bang chung ve mot ma so")

    if method == "exact":
        rec = verified_by_name.get(res.get("standard_name", "").lower()) \
            or verified_by_name.get(strip_dosage(name).lower())
        if rec:
            return code, "cache_reverse_verified", (
                f"cache da xac minh nguoc: {rec['name_en']} ({rec.get('verification_method','')})")
        return None, "cache_unverified", "ban ghi cache thieu provenance - khong ghi"

    # API tier: verify it here, the linker itself does not.
    rxcui = code.split(":", 1)[-1]
    ingredient = strip_dosage(name)
    rxnav_name, err = reverse_lookup(rxcui)
    if err:
        return None, "api_unverified", f"khong tra nguoc duoc {code}: {err} - khong ghi"
    ok, how = verified_by_rxnav(ingredient, rxcui, rxnav_name)
    if ok:
        return code, "api_reverse_verified", f"RxNav xac minh nguoc: {rxnav_name!r} ({how})"
    return None, "api_unverified", (
        f"RxNav tra {code} nhung xac minh nguoc THAT BAI (ten nguoc = {rxnav_name!r}) - khong ghi")


def main():
    payload = json.loads(RXNORM_DICT_PATH.read_text(encoding="utf-8"))
    drugs = payload["drugs"] if isinstance(payload, dict) else payload
    verified_by_name = {}
    for d in drugs:
        if d.get("source") == "rxnav_api" and d.get("reverse_verified") is True and d.get("rxcui"):
            verified_by_name[d["name_vi"].lower()] = d
            verified_by_name[strip_dosage(d["name_vi"]).lower()] = d
    print(f"Ban ghi da xac minh nguoc trong tu dien: "
          f"{sum(1 for d in drugs if d.get('reverse_verified'))}/{len(drugs)}")

    client = Neo4jClient()
    if not client.is_online():
        print("Neo4j OFFLINE - dung lai, khong ghi gi.")
        return 1

    before_nodes, before_rels, before_sids = graph_totals(client)
    before = snapshot(client, BEFORE)
    print(f"Truoc: {len(before)} node DRUG | do thi {before_nodes} node / {before_rels} quan he "
          f"/ {before_sids} SourceSampleID\nSnapshot: {BEFORE.name}\n")

    linker = RxNormLinker()
    log_rows, changes = [], []
    for name in sorted(before):
        old_raw = before[name]
        old = normalize_code(old_raw)
        new, method, note = resolve(name, linker, verified_by_name)

        if new == old:
            action = "KEEP" if old else "KEEP_NULL"
        elif new and not old:
            action = "FILL"
        elif new and old:
            action = "CORRECT"
        else:
            action = "CLEAR_SENTINEL" if old_raw else "KEEP_NULL"
            new = None

        log_rows.append({"name": name, "old_code": old_raw or "", "new_code": new or "",
                         "action": action, "method": method, "reason": note})
        if action in ("CORRECT", "FILL", "CLEAR_SENTINEL"):
            changes.append((name, old_raw, new, action, note))

    print("=" * 114)
    for name, old_raw, new, action, note in changes:
        print(f"  {action:<15}{name:<36}{str(old_raw or 'null'):>16} -> {str(new or 'null'):<13}")
        print(f"                 ly do: {note}")
    print("=" * 114)
    print(dict(Counter(r["action"] for r in log_rows)))
    print(dict(Counter(r["method"] for r in log_rows)), "\n")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["name", "old_code", "new_code", "action",
                                          "method", "reason"])
        w.writeheader()
        w.writerows(log_rows)
    print(f"Log tung dong: {LOG}")

    # Duplicate guard. Two kinds of collision, with opposite meanings:
    #
    #  (a) DIFFERENT drugs sharing one RxCUI -- a real data error, the Metformin/Methotrexate
    #      RXCUI:6809 case. Abort; writing it would recreate the exact defect we just removed.
    #
    #  (b) The SAME ingredient split across dosage-bearing node names ('Meloxicam 15mg' and
    #      'Meloxicam 7.5mg'). Once the codes are correct these MUST collide, because they are
    #      one drug. The collision is not caused by this sync -- it is the ontology defect
    #      (decision 2 in docs/ontology_freeze.md) becoming visible. Writing the correct code
    #      is right; what stays blocked is the drug_code uniqueness constraint, and now for one
    #      documented reason instead of a silent sentinel.
    final = {}
    for r in log_rows:
        if r["new_code"]:
            final.setdefault(r["new_code"], []).append(r["name"])
    dups = {k: v for k, v in final.items() if len(v) > 1}
    same_ingredient, different_drugs = {}, {}
    for code, names in dups.items():
        bucket = same_ingredient if len({strip_dosage(n).lower() for n in names}) == 1 \
            else different_drugs
        bucket[code] = names
    if different_drugs:
        print(f"\n❌ ABORT: hai THUOC KHAC NHAU se dung chung mot RxCUI: {different_drugs}")
        return 1
    if same_ingredient:
        print(f"\n⚠️  {len(same_ingredient)} ma bi trung do CUNG MOT HOAT CHAT bi tach node theo lieu:")
        for code, names in same_ingredient.items():
            print(f"     {code}: {names}")
        print("     Day KHONG phai loi cua buoc dong bo - la hau qua cua ontology ten thuoc")
        print("     (quyet dinh 2 trong docs/ontology_freeze.md). Ma dung van duoc ghi;")
        print("     rang buoc drug_code IS UNIQUE se con bi chan boi dung {} truong hop nay."
              .format(sum(len(v) - 1 for v in same_ingredient.values())))
    else:
        print("Kiem tra trung ma sau dong bo: 0 trung.")

    if not APPLY:
        print("\n[DRY RUN] Chua ghi gi. Chay lai voi --apply.")
        return 0

    for name, _old, new, _action, _note in changes:
        if new is None:
            client.execute_query("MATCH (n:DRUG {name: $n}) REMOVE n.code", {"n": name})
        else:
            client.execute_query("MATCH (n:DRUG {name: $n}) SET n.code = $c", {"n": name, "c": new})
    print(f"\nDA GHI {len(changes)} node.")

    after = snapshot(client, AFTER)
    after_nodes, after_rels, after_sids = graph_totals(client)
    print(f"Sau:  {len(after)} node DRUG | do thi {after_nodes} node / {after_rels} quan he "
          f"/ {after_sids} SourceSampleID")

    ok = (before_nodes, before_rels, before_sids) == (after_nodes, after_rels, after_sids)
    print(f"\n[2b] Node/quan he/SourceSampleID giu nguyen: {'PASS' if ok else 'FAIL'}  "
          f"({before_nodes}/{before_rels}/{before_sids} -> {after_nodes}/{after_rels}/{after_sids})")
    assert set(before) == set(after), "Ten node DRUG thay doi - khong duoc phep"

    live = [c for c in after.values() if normalize_code(c)]
    print(f"[2c] Node DRUG mang ma that VA da xac minh nguoc: {len(live)}/{len(after)} "
          f"= {100*len(live)/len(after):.1f}%")
    print(f"     Con {len(after)-len(live)} node de trong, moi node co ly do ghi trong {LOG.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
