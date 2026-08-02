import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.graph.neo4j_client import Neo4jClient

c = Neo4jClient()
res = c.execute_query("MATCH (n {name:'Thoái hóa khớp gối'})-[r]-(t) RETURN n.name AS Disease, type(r) AS Rel, t.name AS Node, labels(t) AS Labels")
print(f"Total edges connected to Thoái hóa khớp gối: {len(res)}")
for r in res:
    print(r)
