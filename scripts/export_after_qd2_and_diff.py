import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient

def export_after_qd2():
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
    out_path = BASE_DIR / "data" / "exports" / "after_qd2.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Head", "HeadCode", "Relation", "Tail", "TailCode", "SourceSampleID", "Dosage"
        ])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} relationships to {out_path}")

    # Compare before_qd2.csv and after_qd2.csv
    before_path = BASE_DIR / "data" / "exports" / "before_qd2.csv"
    with open(before_path, "r", encoding="utf-8-sig") as f:
        before_rows = list(csv.DictReader(f))

    print("\n--- DELTA ANALYSIS BETWEEN before_qd2.csv AND after_qd2.csv ---")
    print(f"Total relationships before: {len(before_rows)}")
    print(f"Total relationships after:  {len(rows)}")

    changed_rows = 0
    merged_rows = 0
    renamed_rows = 0

    # Map changes
    for b in before_rows:
        head_b = b["Head"]
        # Find matching row in after_rows by (Relation, Tail, SourceSampleID)
        matches = [a for a in rows if a["Relation"] == b["Relation"] and a["Tail"] == b["Tail"] and a["SourceSampleID"] == b["SourceSampleID"]]
        if matches:
            a = matches[0]
            if head_b != a["Head"] or b["Dosage"] != a["Dosage"]:
                changed_rows += 1

    print(f"Total changed relationships (Head renamed and/or Dosage populated): {changed_rows}")
    return 0

if __name__ == "__main__":
    export_after_qd2()
