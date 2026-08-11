"""
Item 1.05c: can the original surface form be recovered from what is already stored?

The graph records source_sample_id on every relationship, so we know WHICH document a node
came from -- but not WHICH STRING in that document produced it. This script tests whether the
string can be recovered after the fact, by searching each node's name back into the text of
the samples it is attached to.

A node whose name cannot be found in any of its own source documents is, by definition, named
after something other than the corpus. M54.5 'Đau lưng dưới' is the known case and must appear
in that group; anything else that appears there is a case nobody had noticed.

Read-only. Output: data/exports/surface_form_recovery.csv
Usage: python scripts/recover_surface_forms.py
"""
import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.graph.neo4j_client import Neo4jClient                        # noqa: E402
from src.entity_linking.entity_normalizer import get_term_synonyms    # noqa: E402

OUT = BASE / "data" / "exports" / "surface_form_recovery.csv"
CORPUS = {r["id"]: r["text"]
          for r in json.loads((BASE / "data/synthetic/synthetic_data.json").read_text(encoding="utf-8"))}


def fold(s):
    """Lowercase + strip diacritics, for the loosest recovery tier."""
    return "".join(c for c in unicodedata.normalize("NFD", s.lower())
                   if unicodedata.category(c) != "Mn")


def find_in(text, needle):
    """Return the matched substring with its original casing, or None."""
    m = re.search(r"(?<![\wÀ-ỹ])" + re.escape(needle) + r"(?![\wÀ-ỹ])", text, re.IGNORECASE)
    return m.group(0) if m else None


def recover(name, texts):
    """Try increasingly loose tiers. Returns (tier, surface) or (None, None)."""
    for t in texts:
        hit = find_in(t, name)
        if hit:
            return ("VERBATIM", hit)
    # tier 2: a synonym variant of the node name
    for var in sorted(get_term_synonyms(name), key=len, reverse=True):
        if var.lower() == name.lower():
            continue
        for t in texts:
            hit = find_in(t, var)
            if hit:
                return ("SYNONYM", hit)
    # tier 3: diacritic-insensitive
    folded_name = fold(name)
    for t in texts:
        if folded_name in fold(t):
            i = fold(t).index(folded_name)
            return ("KHONG DAU", t[i:i + len(name)])
    # tier 4: every content word of the name appears somewhere in the text
    words = [w for w in re.split(r"\s+", name) if len(w) > 2]
    for t in texts:
        ft = fold(t)
        if words and all(fold(w) in ft for w in words):
            return ("RAI RAC (tung tu roi rac, khong lien tuc)", "")
    return (None, None)


def main():
    c = Neo4jClient()
    if not c.is_online():
        print("Neo4j offline."); return 1

    nodes = c.execute_query(
        "MATCH (n:DISEASE) OPTIONAL MATCH (n)-[r]-() "
        "RETURN n.name AS name, n.code AS code, collect(r.source_sample_id) AS sids "
        "ORDER BY n.name")

    rows = []
    for n in nodes:
        sids = sorted({s.strip() for blob in n["sids"] if blob
                       for s in str(blob).split(",") if s.strip()})
        texts = [CORPUS[s] for s in sids if s in CORPUS]
        tier, surface = recover(n["name"], texts)
        rows.append({
            "node_name": n["name"], "code": n["code"] or "",
            "source_sample_ids": ";".join(sids),
            "n_samples": len(texts),
            "recovery_tier": tier or "KHONG KHOI PHUC DUOC",
            "recovered_surface": surface or "",
            "same_as_node_name": "YES" if (surface or "").lower() == n["name"].lower() else "NO",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    print("=" * 112)
    print("1.05c  KHOI PHUC DANG BE MAT TU DU LIEU HIEN CO")
    print("=" * 112)
    print(f"{'node':<32}{'code':<9}{'mau':<5}{'tang khoi phuc':<22}dang be mat tim duoc")
    for r in rows:
        flag = "" if r["recovery_tier"] == "VERBATIM" else "  <<<"
        print(f"{r['node_name'][:31]:<32}{r['code']:<9}{r['n_samples']:<5}"
              f"{r['recovery_tier'][:21]:<22}{r['recovered_surface'][:34]}{flag}")

    print("\n" + "=" * 112)
    cnt = Counter(r["recovery_tier"] for r in rows)
    for k, v in cnt.most_common():
        print(f"  {v:>3}  {k}")
    ok = cnt.get("VERBATIM", 0)
    print(f"\n  KHOI PHUC DUOC nguyen van : {ok}/{len(rows)}")
    print(f"  KHONG khoi phuc duoc      : {cnt.get('KHONG KHOI PHUC DUOC', 0)}")
    bad = [r for r in rows if r["recovery_tier"] != "VERBATIM"]
    if bad:
        print("\n  Cac node KHONG khop nguyen van trong chinh mau nguon cua no:")
        for r in bad:
            print(f"    [{r['code']:<7}] {r['node_name']!r}  tang={r['recovery_tier']}"
                  f"  mau={r['source_sample_ids']}")
    print(f"\nCSV: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
