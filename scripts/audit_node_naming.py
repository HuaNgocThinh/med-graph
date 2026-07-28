"""
Item 1.0: for every DISEASE node in the graph, determine WHERE ITS NAME CAME FROM.

Why this has to run before QĐ3. ICD10Linker returns

    standard_name = get_canonical_name(rec["name_vi"])

so a node is named after the DICTIONARY, and the only thing that can pull that back to the
corpus form is an ALIAS_MAP entry. Where such an entry happens to exist the node looks
corpus-anchored; where it does not, the dictionary string flows straight through and becomes
the node name. That is not a policy, it is a coincidence -- and it is exactly how the node
'Viêm dạ dày' silently became 'Viêm loét dạ dày' in commit e64df49 while keeping K29.7.

QĐ3 is about to ADD two records (M17, B37.3) that have no ALIAS_MAP entry at all, so their
node names would be decided by whichever string gets typed into name_vi.

Read-only. Output: data/exports/node_naming_provenance.csv
Usage: python scripts/audit_node_naming.py
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.config import ICD10_DICT_PATH                                  # noqa: E402
from src.entity_linking.dict_loader import load_records                 # noqa: E402
from src.entity_linking.entity_normalizer import (                      # noqa: E402
    ALIAS_MAP, get_canonical_name, normalize_disease_name,
)
from src.graph.neo4j_client import Neo4jClient                          # noqa: E402

OUT = BASE / "data" / "exports" / "node_naming_provenance.csv"
CORPUS = json.loads((BASE / "data/synthetic/synthetic_data.json").read_text(encoding="utf-8"))

# Node names pinned by a test. Anything outside this set can be renamed by a dictionary edit
# without a single test failing.
PINNED_BY_TESTS = {
    "Viêm loét dạ dày", "Thoái hóa khớp", "Viêm âm đạo do nấm",   # test_regression_pins.py
    "Đái tháo đường týp 2",                                        # test_regression_pins.py
    "Cao huyết áp",                                                # test_entity_linking.py
    "Viêm phổi",                                                   # test_entity_gate.py
}


def corpus_hits(name):
    """Sample ids whose text literally contains this string (case-insensitive)."""
    pat = re.compile(re.escape(name), re.IGNORECASE)
    return [r["id"] for r in CORPUS if pat.search(r["text"])]


def main():
    records = load_records(ICD10_DICT_PATH)
    by_code = {r["code"]: r for r in records}

    client = Neo4jClient()
    if not client.is_online():
        print("Neo4j offline."); return 1

    nodes = client.execute_query(
        "MATCH (n:DISEASE) RETURN n.name AS name, n.code AS code ORDER BY n.name")

    rows = []
    for n in nodes:
        name, code = n["name"], n["code"]
        rec = by_code.get(code) if code else None

        if rec is None:
            # Unlinked: the name came from the normalized corpus surface form, not a dictionary.
            source = "CORPUS (node chua link, khong co record)"
            risk = "AN TOAN"
            dict_str = ""
        else:
            dict_str = rec.get("name_vi", "")
            canon = get_canonical_name(dict_str)
            alias_key = dict_str.strip().lower()
            stripped = re.sub(r"^(bệnh|hội\s+chứng|chứng|tình\s+trạng)\s+", "", alias_key).strip()
            aliased = alias_key in ALIAS_MAP or stripped in ALIAS_MAP

            if canon == name and aliased and canon != dict_str:
                source = f"ALIAS_MAP gap ve (name_vi={dict_str!r} -> {canon!r})"
                risk = "NEO BOI ALIAS"
            elif canon == name and aliased:
                source = f"ALIAS_MAP giu nguyen (name_vi={dict_str!r})"
                risk = "NEO BOI ALIAS"
            elif canon == name:
                source = f"name_vi CHAY THANG ({dict_str!r})"
                risk = "SE TU DOI TEN"
            elif normalize_disease_name(dict_str) == name:
                source = f"name_vi qua normalize ({dict_str!r})"
                risk = "SE TU DOI TEN"
            elif name.lower() in [s.lower() for s in rec.get("synonyms", [])]:
                source = f"khop SYNONYM cua record (name_vi={dict_str!r})"
                risk = "AN TOAN (ten != name_vi)"
            else:
                source = f"KHAC (name_vi={dict_str!r}, canon={canon!r})"
                risk = "CAN XEM TAY"

        hits = corpus_hits(name)
        rows.append({
            "node_name": name,
            "code": code or "",
            "dict_name_vi": dict_str,
            "name_source": source,
            "rename_risk": risk,
            "in_corpus": "YES" if hits else "NO",
            "corpus_samples": ";".join(hits[:4]),
            "pinned_by_test": "YES" if name in PINNED_BY_TESTS else "NO",
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    # --- 1.0a ---
    print("=" * 118)
    print("1.0a  NGUON GOC TEN TUNG NODE DISEASE")
    print("=" * 118)
    print(f"{'node':<30}{'code':<9}{'corpus':<8}{'test':<6}nguon ten")
    for r in sorted(rows, key=lambda x: (x["rename_risk"], x["node_name"])):
        print(f"{r['node_name'][:29]:<30}{r['code']:<9}{r['in_corpus']:<8}"
              f"{r['pinned_by_test']:<6}{r['name_source'][:58]}")

    # --- 1.0b ---
    print("\n" + "=" * 118)
    print("1.0b  DEM")
    print("=" * 118)
    c = Counter(r["rename_risk"] for r in rows)
    for k, v in c.most_common():
        print(f"  {v:>3}  {k}")
    straight = [r for r in rows if r["rename_risk"] == "SE TU DOI TEN"]
    print(f"\n  Neo boi ALIAS_MAP           : {c.get('NEO BOI ALIAS', 0)}")
    print(f"  Mang thang chuoi tu dien    : {len(straight)}")
    drift = [r for r in straight if r["in_corpus"] == "NO"]
    print(f"\n  Trong so mang thang chuoi tu dien, ten node KHONG khop corpus: {len(drift)}")
    print("  -> day la cac ca TROI TEN TIEM TANG (ten node khong co trong van ban goc):")
    for r in drift:
        print(f"       [{r['code']:<7}] {r['node_name']!r}  (name_vi={r['dict_name_vi']!r})")
    if not drift:
        print("       (khong co)")

    # --- 1.0c ---
    print("\n" + "=" * 118)
    print("1.0c  BAO NHIEU NODE SE TU DOI TEN MA KHONG TEST NAO BAT DUOC?")
    print("=" * 118)
    at_risk = [r for r in rows if r["rename_risk"] in ("SE TU DOI TEN", "NEO BOI ALIAS")]
    unguarded = [r for r in at_risk if r["pinned_by_test"] == "NO"]
    print(f"  Node co ten phu thuoc tu dien (name_vi hoac ALIAS)  : {len(at_risk)}/{len(rows)}")
    print(f"  Trong do KHONG co test nao neo ten                 : {len(unguarded)}")
    print(f"  Co test neo                                        : {len(at_risk)-len(unguarded)}")
    print("\n  Danh sach node se doi ten AM THAM neu sua name_vi:")
    for r in unguarded:
        print(f"    [{r['code']:<7}] {r['node_name']}")
    print(f"\nCSV: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
