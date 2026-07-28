"""
B1c + B1d: Backfill first_surface for DISEASE nodes from surface_form_recovery.csv
and verify non-null / null node counts.
"""

import csv
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient

CSV_PATH = BASE_DIR / "data" / "exports" / "surface_form_recovery.csv"

def main():
    client = Neo4jClient()
    if not client.is_online():
        print("Neo4j offline!")
        return 1

    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = list(csv.DictReader(f))

    print("=" * 80)
    print("B1c: BACKFILL FIRST_SURFACE ONTO DISEASE NODES")
    print("=" * 80)

    updated_count = 0
    null_count = 0

    for row in reader:
        node_name = row["node_name"]
        code = row["code"]
        surface = row["recovered_surface"]
        tier = row["recovery_tier"]

        if tier == "VERBATIM" and surface:
            query = "MATCH (n:DISEASE {name: $name}) SET n.first_surface = $surface RETURN n.name AS name"
            res = client.execute_query(query, {"name": node_name, "surface": surface})
            if res:
                print(f"  [SET] {node_name!r:<35} ({code:<6}) -> first_surface = {surface!r}")
                updated_count += 1
            else:
                print(f"  [MISSING NODE] {node_name!r}")
        else:
            query = "MATCH (n:DISEASE {name: $name}) REMOVE n.first_surface RETURN n.name AS name"
            res = client.execute_query(query, {"name": node_name})
            print(f"  [NULL] {node_name!r:<35} ({code:<6}) -> first_surface = null (Lý do: tên node không khôi phục được từ corpus)")
            null_count += 1

    print("\n" + "=" * 80)
    print(f"Backfilled: {updated_count} nodes SET, {null_count} nodes NULL.")

    print("\n" + "=" * 80)
    print("B1d: VERIFYING NEO4J DISEASE FIRST_SURFACE COUNTS")
    print("=" * 80)

    count_query = """
    MATCH (n:DISEASE)
    RETURN count(n.first_surface) AS with_surface,
           sum(CASE WHEN n.first_surface IS NULL THEN 1 ELSE 0 END) AS null_surface,
           count(n) AS total
    """
    res = client.execute_query(count_query)
    if res:
        with_surf = res[0]["with_surface"]
        null_surf = res[0]["null_surface"]
        total = res[0]["total"]
        print(f"Total DISEASE nodes : {total}")
        print(f"With first_surface  : {with_surf}  (Kỳ vọng: 40)")
        print(f"Null first_surface  : {null_surf}  (Kỳ vọng: 1)")

        if with_surf == 40 and null_surf == 1:
            print(">>> B1d VERIFICATION SUCCESS: 40 có / 1 null (M54.5)!")
        else:
            print(f">>> WARNING: expected 40/1, got {with_surf}/{null_surf}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
