"""
Item 1d: assert the pinned regression edges against the LIVE graph.

The expectations come from tests/test_regression_pins.py, which in turn derives them from the
source documents. Keeping one table means the graph check and the document check can never
disagree about what is being asserted.

Usage: python scripts/check_regression_edges.py
Exit code 0 = all pins hold.
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.graph.neo4j_client import Neo4jClient                       # noqa: E402
from tests.test_regression_pins import (                             # noqa: E402
    PINNED_EDGES, FORBIDDEN_EDGES, DISEASE_CODES,
)

c = Neo4jClient()
if not c.is_online():
    print("Neo4j offline."); sys.exit(1)

fails = 0

print("=" * 92)
print("PHAI CO (neo theo van ban goc)")
print("=" * 92)
for sid, drug, rel, disease in PINNED_EDGES:
    rows = c.execute_query(
        f"MATCH (d {{name:$d}})-[r:{rel}]->(b {{name:$b}}) RETURN r.source_sample_id AS s",
        {"d": drug, "b": disease})
    ok = bool(rows) and any(sid in (r["s"] or "") for r in rows)
    fails += not ok
    print(f"  [{'PASS' if ok else 'FAIL'}] {drug} -[{rel}]-> {disease}   (nguon {sid})")
    if rows:
        print(f"           source_sample_id = {rows[0]['s']}")

print("\n" + "=" * 92)
print("PHAI KHONG CO")
print("=" * 92)
for drug, rel, disease in FORBIDDEN_EDGES:
    rows = c.execute_query(
        f"MATCH (d {{name:$d}})-[r:{rel}]->(b {{name:$b}}) RETURN r.source_sample_id AS s",
        {"d": drug, "b": disease})
    ok = not rows
    fails += not ok
    print(f"  [{'PASS' if ok else 'FAIL'}] {drug} -[{rel}]-> {disease}"
          + ("" if ok else f"   <-- TON TAI: {rows}"))

print("\n" + "=" * 92)
print("MA ICD CUA CAC NODE DUOC NEO (quyet dinh 3/4 DA DUYET VA DA AP DUNG)")
print("=" * 92)
for name, (current, expected, why) in DISEASE_CODES.items():
    rows = c.execute_query("MATCH (n:DISEASE {name:$n}) RETURN n.code AS code", {"n": name})
    live = rows[0]["code"] if rows else None
    match = live == current
    fails += not match
    print(f"  [{'OK  ' if match else 'LECH'}] {name:<22} do thi={live!r:<9} "
          f"neo={current!r:<9} dung ra phai la {expected!r}")
    print(f"          {why}")

print("\n" + "=" * 92)
print(f"KET QUA: {'TAT CA PASS' if fails == 0 else f'{fails} MUC THAT BAI'}")
sys.exit(1 if fails else 0)
