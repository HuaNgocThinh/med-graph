import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

from src.graph.neo4j_client import Neo4jClient
import json

c = Neo4jClient()
print("online:", c.is_online())

print("\n-- total nodes --")
print(c.execute_query("MATCH (n) RETURN count(n) AS total"))

print("\n-- label combos + counts --")
for r in c.execute_query("MATCH (n) RETURN labels(n) AS labels, count(*) AS cnt ORDER BY cnt DESC"):
    print(r)

print("\n-- distinct property keys per label combo --")
for r in c.execute_query(
    "MATCH (n) UNWIND keys(n) AS k RETURN labels(n) AS labels, k, count(*) AS cnt ORDER BY labels, cnt DESC"
):
    print(r)

print("\n-- sample nodes (5 per label combo) --")
for r in c.execute_query(
    "MATCH (n) WITH labels(n) AS L, collect(properties(n))[0..3] AS samples RETURN L, samples"
):
    print(r["L"])
    for s in r["samples"]:
        print("   ", json.dumps(s, ensure_ascii=False))

c.close()
