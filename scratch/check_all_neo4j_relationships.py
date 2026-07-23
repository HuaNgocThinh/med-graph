import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient

client = Neo4jClient()
res = client.execute_query("MATCH (h)-[r]->(t) RETURN h.name, type(r), t.name, properties(r) as props, labels(h) as h_labels, labels(t) as t_labels")
for r in res:
    print(r)
