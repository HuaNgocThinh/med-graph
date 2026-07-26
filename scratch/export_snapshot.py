"""Export a full relationship snapshot from Neo4j to a named CSV. Usage: python scratch/export_snapshot.py <name>"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient
from run_pipeline import export_all_relationships_csv

name = sys.argv[1] if len(sys.argv) > 1 else "snapshot"
out = BASE_DIR / "data" / "exports" / f"{name}.csv"

client = Neo4jClient()
if not client.is_online():
    print("ABORT: Neo4j offline, refusing to write a fake snapshot.")
    sys.exit(1)

export_all_relationships_csv(client, out)

with open(out, "r", encoding="utf-8-sig") as f:
    lines = [ln.rstrip("\n") for ln in f]
print(f"\nFile: {out}")
print(f"Total rows (excl. header): {len(lines) - 1}")

# Node counts for context
nodes = client.execute_query("MATCH (n) RETURN n.name AS name, labels(n) AS labels ORDER BY n.name")
print(f"Total nodes: {len(nodes)}")
