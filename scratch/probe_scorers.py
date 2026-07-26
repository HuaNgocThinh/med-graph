"""
Evidence for choosing the FuzzyMatcher threshold (item 1a).
Replicates the current matching logic but reports WHICH candidate matched and the
query/candidate length ratio, under three rapidfuzz scorers, for known-good and
known-bad queries. Read-only: does not touch source or Neo4j.
"""
import sys, json, re
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from rapidfuzz import process, fuzz

records = json.load(open(BASE / "data/dictionaries/icd10_vi.json", encoding="utf-8"))
cands, cmap = [], {}
for it in records:
    n = it.get("name_vi", "")
    if n:
        cands.append(n); cmap[n.lower()] = it
    for s in it.get("synonyms", []):
        if s:
            cands.append(s); cmap[s.lower()] = it

exact = {}
for it in records:
    exact[it["name_vi"].lower()] = it
    for s in it.get("synonyms", []):
        exact[s.lower()] = it

# MUST still link (real folk/clinical terms the system depends on)
GOOD = ["tiểu đường", "bệnh tiểu đường", "mỡ máu cao", "tan máu bẩm sinh",
        "viêm phổi cộng đồng", "cao huyết áp", "thoái hóa khớp gối",
        "đái tháo đường tuýp 2", "viêm ruột thừa", "trào ngược dạ dày"]
# MUST NOT link (generic fragments that caused the Meloxicam bug)
BAD = ["viêm", "đau", "sốt", "ho", "bệnh", "giảm viêm", "kháng viêm", "giảm đau",
       "viêm nhiễm", "nhiễm"]

SCORERS = [("WRatio", fuzz.WRatio), ("token_set_ratio", fuzz.token_set_ratio), ("ratio", fuzz.ratio)]


def probe(q):
    cq = re.sub(r'\b\d+(?:mg|mcg|ml|g|%)\b', '', q.lower()).strip() or q.lower()
    row = {"query": q, "exact_hit": cq in exact}
    for name, sc in SCORERS:
        r = process.extractOne(cq, cands, scorer=sc, score_cutoff=0)
        if r:
            ms, score, _ = r
            ratio = len(cq) / len(ms.lower()) if ms else 0
            row[name] = (round(score, 1), ms, round(ratio, 2), cmap[ms.lower()]["code"])
        else:
            row[name] = None
    return row


for title, group in (("GOOD (phải link được)", GOOD), ("BAD (phải BỊ CHẶN)", BAD)):
    print("\n" + "=" * 100)
    print(title)
    print("=" * 100)
    for q in group:
        r = probe(q)
        print(f"\n  query={q!r}  exact_map_hit={r['exact_hit']}")
        for name, _ in SCORERS:
            v = r[name]
            if v:
                print(f"     {name:16} score={v[0]:5}  match={v[1]!r:34} len_ratio={v[2]:5}  {v[3]}")

print("\n" + "=" * 100)
print("PHAN TACH: len_ratio cua GOOD vs BAD duoi WRatio (chi tinh ca KHONG co exact hit)")
print("=" * 100)
g = [(q, probe(q)) for q in GOOD]
b = [(q, probe(q)) for q in BAD]
gf = [(q, r["WRatio"][2]) for q, r in g if not r["exact_hit"] and r["WRatio"]]
bf = [(q, r["WRatio"][2]) for q, r in b if not r["exact_hit"] and r["WRatio"]]
print(f"  GOOD (fuzzy path): {gf}")
print(f"  BAD  (fuzzy path): {bf}")
if gf and bf:
    print(f"\n  min(len_ratio) GOOD = {min(v for _, v in gf)}")
    print(f"  max(len_ratio) BAD  = {max(v for _, v in bf)}")
