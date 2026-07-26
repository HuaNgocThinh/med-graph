import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import json
from src.graph.neo4j_client import Neo4jClient

c = Neo4jClient()
rels = c.execute_query(
    "MATCH (a)-[r]->(b) RETURN id(r) AS rid, type(r) AS rtype, "
    "id(a) AS aid, labels(a) AS a_labels, a.name AS a_name, a.code AS a_code, "
    "id(b) AS bid, labels(b) AS b_labels, b.name AS b_name, b.code AS b_code, "
    "properties(r) AS rprops ORDER BY rid"
)
print("rels:", len(rels))
p = r"c:\Users\thinhlaluot\MedGraph\scratch\_rels2.json"
with open(p, "w", encoding="utf-8") as f:
    json.dump(rels, f, ensure_ascii=False, indent=1)
print("written", p)
c.close()
