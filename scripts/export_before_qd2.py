import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient

def export_before_qd2():
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
           r.source_sample_id AS SourceSampleID,
           coalesce(r.dosage, "") AS Dosage
    ORDER BY Head, Relation, Tail
    """
    rows = client.execute_query(query)
    out_path = BASE_DIR / "data" / "exports" / "before_qd2.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Head", "HeadCode", "Relation", "Tail", "TailCode", "SourceSampleID", "Dosage"
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} relationships to {out_path}")
    return 0

if __name__ == "__main__":
    export_before_qd2()
