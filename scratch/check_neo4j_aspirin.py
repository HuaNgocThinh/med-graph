import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient

client = Neo4jClient()
res = client.execute_query("MATCH (n) WHERE toLower(n.name) CONTAINS 'aspirin' RETURN labels(n) as labels, n.name as name, n")
print("Aspirin nodes in Neo4j:")
for r in res:
    print(r)

print("\nAspirin relationships in Neo4j:")
res_rel = client.execute_query("MATCH (h)-[r]->(t) WHERE toLower(h.name) CONTAINS 'aspirin' OR toLower(t.name) CONTAINS 'aspirin' RETURN h.name, type(r), t.name, r")
for r in res_rel:
    print(r)
