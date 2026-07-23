import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient
from run_pipeline import export_all_relationships_csv

client = Neo4jClient()
export_all_relationships_csv(client, BASE_DIR / "data" / "exports" / "all_relationships_raw.csv")

with open(BASE_DIR / "data" / "exports" / "all_relationships_raw.csv", "r", encoding="utf-8") as f:
    lines = f.readlines()
    print(f"Exported raw CSV lines count: {len(lines)}")
    for idx, line in enumerate(lines[:10]):
        print(f"Row {idx+1}: {line.strip()}")
