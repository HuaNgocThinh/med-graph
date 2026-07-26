import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import json
from src.graph.neo4j_client import Neo4jClient

c = Neo4jClient()
print("online:", c.is_online())

nodes = c.execute_query(
    "MATCH (n) RETURN id(n) AS nid, labels(n) AS labels, properties(n) AS props ORDER BY nid"
)
rels = c.execute_query(
    "MATCH (a)-[r]->(b) RETURN id(r) AS rid, type(r) AS rtype, "
    "labels(a) AS a_labels, a.name AS a_name, a.code AS a_code, "
    "labels(b) AS b_labels, b.name AS b_name, b.code AS b_code, "
    "properties(r) AS rprops ORDER BY rid"
)
print("NODE COUNT:", len(nodes))
print("REL COUNT:", len(rels))

out = {"nodes": nodes, "rels": rels}
p = r"c:\Users\thinhlaluot\MedGraph\scratch\_graph_dump.json"
with open(p, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("written", p)

for n in nodes:
    print(n["nid"], n["labels"], json.dumps(n["props"], ensure_ascii=False))
c.close()
