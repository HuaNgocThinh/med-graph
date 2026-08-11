"""
Export snapshot of all relationships with node codes and source sample IDs.
Usage: python scripts/export_atomic_snapshot.py <filename>
"""

import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient

def export_snapshot(out_filename: str):
    client = Neo4jClient()
    if not client.is_online():
        print("Neo4j offline!")
        return 1

    query = """
    MATCH (h)-[r]->(t)
    RETURN h.name AS Head,
           coalesce(h.code, "") AS HeadCode,
           type(r) AS Relation,
           t.name AS Tail,
           coalesce(t.code, "") AS TailCode,
           r.source_sample_id AS SourceSampleID
    ORDER BY Head, Relation, Tail
    """
    rows = client.execute_query(query)

    out_path = BASE_DIR / "data" / "exports" / out_filename
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Head", "HeadCode", "Relation", "Tail", "TailCode", "SourceSampleID"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} relationships to {out_path}")
    return 0

if __name__ == "__main__":
    fname = sys.argv[1] if len(sys.argv) > 1 else "atomic_snapshot.csv"
    sys.exit(export_snapshot(fname))
