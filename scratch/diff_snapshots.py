"""Delta report between before_synonym.csv and after_synonym.csv, plus the mandated
regression assertion that Metformin - Đái tháo đường týp 2 survived."""
import csv, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent / "data" / "exports"

def load(p):
    with open(BASE / p, encoding="utf-8-sig") as f:
        return [tuple(r[k] for k in ("Head", "Relation", "Tail", "SourceSampleID"))
                for r in csv.DictReader(f)]

before, after = load("before_synonym.csv"), load("after_synonym.csv")
sb, sa = set(before), set(after)

print("=" * 80)
print("DELTA before_synonym.csv  ->  after_synonym.csv")
print("=" * 80)
print(f"  before : {len(before)} quan hệ ({len(sb)} unique)")
print(f"  after  : {len(after)} quan hệ ({len(sa)} unique)")
print(f"  delta  : {len(after) - len(before):+d}")

removed, added = sorted(sb - sa), sorted(sa - sb)
print(f"\n  DÒNG BỊ XOÁ / MẤT : {len(removed)}")
for r in removed:
    print(f"    - {r}")
if not removed:
    print("    (không có dòng nào bị xoá)")
print(f"\n  DÒNG ĐƯỢC THÊM   : {len(added)}")
for r in added:
    print(f"    + {r}")
if not added:
    print("    (không có dòng nào được thêm)")

# Mandated regression check
print("\n" + "=" * 80)
print("KIỂM TRA HỒI QUY BẮT BUỘC")
print("=" * 80)
core = [r for r in after if r[0] == "Metformin" and r[2] == "Đái tháo đường týp 2"]
if core:
    for r in core:
        print(f"  ✅ CÒN NGUYÊN: Metformin -[{r[1]}]-> Đái tháo đường týp 2")
        print(f"     SourceSampleID = {r[3]}")
    before_core = [r for r in before if r[0] == "Metformin" and r[2] == "Đái tháo đường týp 2"]
    print(f"  SourceSampleID trước = {before_core[0][3] if before_core else 'N/A'}")
    print(f"  Truy vết bảo toàn    = {before_core == core}")
else:
    print("  ❌ MẤT quan hệ Metformin - Đái tháo đường týp 2!")
    sys.exit(1)

# No SourceSampleID may be lost anywhere in the graph
def ids(rows):
    s = set()
    for r in rows:
        for p in r[3].split(","):
            if p.strip():
                s.add(p.strip())
    return s

lost = ids(before) - ids(after)
print(f"\n  Tổng SourceSampleID trước: {len(ids(before))}, sau: {len(ids(after))}")
print(f"  SourceSampleID bị mất    : {len(lost)} {sorted(lost) if lost else '(không mất cái nào)'}")
