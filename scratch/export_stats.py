import sys
import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient

def export_and_stats():
    sys.stdout.reconfigure(encoding='utf-8')
    client = Neo4jClient()

    # 1. Export all relationships to CSV
    export_dir = BASE_DIR / "data" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    csv_path = export_dir / "all_relationships.csv"

    cypher_rels = "MATCH (a)-[r]->(b) RETURN a.name AS Head, type(r) AS Relation, b.name AS Tail ORDER BY a.name"
    rels = client.execute_query(cypher_rels)

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Head", "Relation", "Tail"])
        writer.writeheader()
        writer.writerows(rels)

    print(f"✅ Exported {len(rels)} relationships to '{csv_path}'")

    # 2. Node statistics
    cypher_nodes = "MATCH (n) RETURN labels(n) AS loai, count(*) AS so_luong"
    node_stats = client.execute_query(cypher_nodes)

    # Total nodes count
    total_nodes_res = client.execute_query("MATCH (n) RETURN count(*) AS total")
    total_nodes = total_nodes_res[0]["total"] if total_nodes_res else 0

    # 3. Relationship statistics
    cypher_rel_types = "MATCH ()-[r]->() RETURN type(r) AS quan_he, count(*) AS so_luong"
    rel_stats = client.execute_query(cypher_rel_types)

    total_rels_res = client.execute_query("MATCH ()-[r]->() RETURN count(*) AS total")
    total_rels = total_rels_res[0]["total"] if total_rels_res else 0

    print(f"\n📊 TOTAL GRAPH SUMMARY:")
    print(f"   ► Total Nodes: {total_nodes}")
    print(f"   ► Total Relationships: {total_rels}")

    print("\n--- NODE DISTRIBUTION BY LABEL ---")
    print(json.dumps(node_stats, ensure_ascii=False, indent=2))

    print("\n--- RELATIONSHIP DISTRIBUTION BY TYPE ---")
    print(json.dumps(rel_stats, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    export_and_stats()
