import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import re, json
from collections import defaultdict
from src.graph.neo4j_client import Neo4jClient

TASK_RE = re.compile(r"\d+(?:[.,]\d+)?\s*(mg|mcg|ml|g|%|/tuần)", re.IGNORECASE)

c = Neo4jClient()
rows = c.execute_query("""
MATCH (n) WHERE n:DRUG OR n:DRUG_GROUP
OPTIONAL MATCH (n)-[r]-()
RETURN n.name AS name, n.code AS code, labels(n) AS labels, count(r) AS degree
ORDER BY name
""")

wd_unk = wd_ok = nd_unk = nd_ok = 0
for r in rows:
    has = bool(TASK_RE.search(r["name"] or ""))
    unk = (r["code"] == "RXCUI-UNKNOWN")
    if has and unk: wd_unk += 1
    elif has: wd_ok += 1
    elif unk: nd_unk += 1
    else: nd_ok += 1

print("dosage=Y & RXCUI-UNKNOWN :", wd_unk)
print("dosage=Y & has RXCUI     :", wd_ok)
print("dosage=N & RXCUI-UNKNOWN :", nd_unk)
print("dosage=N & has RXCUI     :", nd_ok)

# code collisions
bycode = defaultdict(list)
for r in rows:
    bycode[r["code"]].append(r["name"])
print("\n=== codes used by >1 node ===")
for k, v in bycode.items():
    if len(v) > 1:
        print(f"  {k}: {v}")

# how many distinct non-unknown codes
codes = {r["code"] for r in rows if r["code"] != "RXCUI-UNKNOWN"}
print(f"\ndistinct real RXCUI codes: {len(codes)}  over {len([r for r in rows if r['code']!='RXCUI-UNKNOWN'])} coded nodes")

# relationship spread for the meloxicam pair
print("\n=== Meloxicam node relationships ===")
for r in c.execute_query("""
MATCH (n:DRUG)-[r]-(m)
WHERE n.name STARTS WITH 'Meloxicam'
RETURN n.name AS drug, type(r) AS rel, m.name AS other, labels(m) AS olabels
ORDER BY drug, rel, other
"""):
    print("  ", r)

print("\n=== Hydrocortisone node relationships ===")
for r in c.execute_query("""
MATCH (n:DRUG)-[r]-(m)
WHERE n.name STARTS WITH 'Hydrocortisone'
RETURN n.name AS drug, type(r) AS rel, m.name AS other
ORDER BY drug, rel, other
"""):
    print("  ", r)

c.close()
