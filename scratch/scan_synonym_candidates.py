"""
Requirement 4: scan all 96 samples for folk<->medical synonym pairs of the SAME KIND
as Tiểu đường <-> Đái tháo đường (different strings, same concept, NOT solvable by
prefix-stripping in normalize_disease_name()).

Method:
  1. Build concept groups from icd10_vi.json (name_vi + its synonyms = one concept).
  2. Find which surface forms of each concept actually occur in the 96 sample texts
     and/or exist as Neo4j node names.
  3. Report a concept as a CANDIDATE only if two of its surface forms are NOT already
     unified by the existing mechanisms (normalize_disease_name / ALIAS_MAP /
     current SYNONYM_MAP). Anything already unified is reported as ALREADY-COVERED.
"""
import sys, json, re
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.entity_linking.entity_normalizer import (
    normalize_disease_name, get_term_synonyms, ALIAS_MAP, SYNONYM_MAP
)
from src.graph.neo4j_client import Neo4jClient

samples = json.load(open(BASE_DIR / "data/synthetic/synthetic_data.json", encoding="utf-8"))
texts = {s["id"]: s["text"] for s in samples}
print(f"Loaded {len(samples)} samples.")

icd = json.load(open(BASE_DIR / "data/dictionaries/icd10_vi.json", encoding="utf-8"))

c = Neo4jClient()
db_nodes = [r["name"] for r in c.execute_query("MATCH (n) RETURN n.name AS name") if r.get("name")]
db_lower = {n.lower() for n in db_nodes}


def already_unified(a: str, b: str) -> bool:
    """True if existing machinery already maps a and b to the same thing."""
    if normalize_disease_name(a).lower() == normalize_disease_name(b).lower():
        return True
    sa = {x.lower() for x in get_term_synonyms(a)}
    sb = {x.lower() for x in get_term_synonyms(b)}
    # unified if each can reach the other's normalized form
    na, nb = normalize_disease_name(a).lower(), normalize_disease_name(b).lower()
    if nb in sa or na in sb or b.lower() in sa or a.lower() in sb:
        return True
    return False


def occurrences(surface: str):
    """Sample ids whose text contains this surface form (word-ish, case-insensitive)."""
    pat = re.compile(re.escape(surface), re.IGNORECASE)
    return [sid for sid, t in texts.items() if pat.search(t)]


candidates = []
covered = []

for entry in icd:
    forms = [entry["name_vi"]] + list(entry.get("synonyms", []))
    # which forms actually appear in the corpus or in the DB?
    present = {}
    for f in forms:
        occ = occurrences(f)
        in_db = f.lower() in db_lower
        if occ or in_db:
            present[f] = {"samples": occ, "in_db": in_db}
    if len(present) < 2:
        continue
    keys = list(present.keys())
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            # skip pure prefix/substring variants -> those are normalize_disease_name's job
            rec = {
                "icd": entry["code"],
                "a": a, "b": b,
                "a_samples": present[a]["samples"], "a_in_db": present[a]["in_db"],
                "b_samples": present[b]["samples"], "b_in_db": present[b]["in_db"],
            }
            if already_unified(a, b):
                covered.append(rec)
            else:
                candidates.append(rec)

print("\n" + "=" * 90)
print("A. ĐÃ ĐƯỢC XỬ LÝ SẴN (normalize_disease_name / ALIAS_MAP / SYNONYM_MAP hiện tại)")
print("=" * 90)
for r in covered:
    print(f"  [{r['icd']}] {r['a']!r} == {r['b']!r}")
print(f"  (tổng: {len(covered)} cặp)")

print("\n" + "=" * 90)
print("B. ỨNG VIÊN CHƯA XỬ LÝ — cần bạn duyệt trước khi thêm vào SYNONYM_MAP")
print("=" * 90)
if not candidates:
    print("  (không có)")
for r in candidates:
    a_loc = f"samples={r['a_samples']}" + (" +DB_NODE" if r['a_in_db'] else "")
    b_loc = f"samples={r['b_samples']}" + (" +DB_NODE" if r['b_in_db'] else "")
    print(f"\n  [{r['icd']}]")
    print(f"    A = {r['a']!r}   ({a_loc})")
    print(f"    B = {r['b']!r}   ({b_loc})")
print(f"\n  (tổng: {len(candidates)} cặp)")
