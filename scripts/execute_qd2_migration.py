"""
Execute QĐ2 Migration (Stage 2b) for MedGraph-VI.
Moves dosage from drug node names into relationship property 'r.dosage'.
Merges duplicate active ingredient nodes (Meloxicam, Hydrocortisone) while preserving all 217 relationships.
"""

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient

DOSAGE_REGEX = re.compile(
    r'\s+('
    r'\d+(?:[\.,]\d+)?(?:/\d+)?'
    r'\s*'
    r'(?:mg|g|mcg|µg|ml|L|IU|UI|%)(?:/[a-zA-Zà-ỹ]+)?'
    r')\s*$',
    re.IGNORECASE
)

def parse_drug_name(name: str):
    match = DOSAGE_REGEX.search(name)
    if match:
        dosage = match.group(1).strip()
        active_ingredient = name[:match.start()].strip()
        return active_ingredient, dosage
    return name.strip(), ""


def relocate_node_edges(client: Neo4jClient, old_name: str, active_name: str, dosage: str):
    """
    Sets r.dosage on all attached relationships of old_name.
    If active_name != old_name:
      - If active_name node exists, relocates all incoming/outgoing relationships to active_name and deletes old_name.
      - If active_name node does not exist, renames old_name node to active_name.
    """
    # 1. Set r.dosage on relationships connected to old_name
    if dosage:
        client.execute_query("""
        MATCH (d {name: $old_name})-[r]-()
        WHERE r.dosage IS NULL OR r.dosage = ""
        SET r.dosage = $dosage
        """, {"old_name": old_name, "dosage": dosage})

    if old_name == active_name:
        return

    # Check if active_name node already exists
    active_exists = bool(client.execute_query(
        "MATCH (d {name: $active_name}) RETURN d", {"active_name": active_name}
    ))

    if not active_exists:
        # Simple node rename
        client.execute_query("""
        MATCH (d {name: $old_name})
        SET d.name = $active_name
        """, {"old_name": old_name, "active_name": active_name})
    else:
        # Move outgoing relationships
        out_rels = client.execute_query("""
        MATCH (old {name: $old_name})-[r]->(target)
        RETURN type(r) AS rel_type, target.name AS target_name,
               r.source_sample_id AS sample_id, r.dosage AS dosage, r.confidence AS confidence,
               r.negated AS negated, r.temporal AS temporal, r.head_surface AS head_surface, r.tail_surface AS tail_surface
        """, {"old_name": old_name})

        for r in out_rels:
            rel_type = r["rel_type"]
            target_name = r["target_name"]
            sample_id = r["sample_id"] or ""
            r_dosage = r["dosage"] or dosage or ""

            # Create new edge on active_name
            client.execute_query(f"""
            MATCH (active {{name: $active_name}}), (t {{name: $target_name}})
            CREATE (active)-[r_new:{rel_type}]->(t)
            SET r_new.source_sample_id = $sample_id,
                r_new.dosage = $r_dosage,
                r_new.confidence = $confidence,
                r_new.negated = $negated,
                r_new.temporal = $temporal,
                r_new.head_surface = $head_surface,
                r_new.tail_surface = $tail_surface
            """, {
                "active_name": active_name,
                "target_name": target_name,
                "sample_id": sample_id,
                "r_dosage": r_dosage,
                "confidence": r.get("confidence", 0.9),
                "negated": r.get("negated", False),
                "temporal": r.get("temporal", "unknown"),
                "head_surface": r.get("head_surface"),
                "tail_surface": r.get("tail_surface")
            })

        # Move incoming relationships
        in_rels = client.execute_query("""
        MATCH (source)-[r]->(old {name: $old_name})
        RETURN source.name AS source_name, type(r) AS rel_type,
               r.source_sample_id AS sample_id, r.dosage AS dosage, r.confidence AS confidence,
               r.negated AS negated, r.temporal AS temporal, r.head_surface AS head_surface, r.tail_surface AS tail_surface
        """, {"old_name": old_name})

        for r in in_rels:
            source_name = r["source_name"]
            rel_type = r["rel_type"]
            sample_id = r["sample_id"] or ""
            r_dosage = r["dosage"] or dosage or ""

            client.execute_query(f"""
            MATCH (s {{name: $source_name}}), (active {{name: $active_name}})
            CREATE (s)-[r_new:{rel_type}]->(active)
            SET r_new.source_sample_id = $sample_id,
                r_new.dosage = $r_dosage,
                r_new.confidence = $confidence,
                r_new.negated = $negated,
                r_new.temporal = $temporal,
                r_new.head_surface = $head_surface,
                r_new.tail_surface = $tail_surface
            """, {
                "source_name": source_name,
                "active_name": active_name,
                "sample_id": sample_id,
                "r_dosage": r_dosage,
                "confidence": r.get("confidence", 0.9),
                "negated": r.get("negated", False),
                "temporal": r.get("temporal", "unknown"),
                "head_surface": r.get("head_surface"),
                "tail_surface": r.get("tail_surface")
            })

        # Detach delete old node
        client.execute_query("MATCH (old {name: $old_name}) DETACH DELETE old", {"old_name": old_name})


def check_total_relations(client: Neo4jClient) -> int:
    res = client.execute_query("MATCH ()-[r]->() RETURN count(r) AS cnt")
    return res[0]["cnt"]


def run_migration():
    client = Neo4jClient()
    if not client.is_online():
        print("Neo4j offline!")
        return

    # Check baseline count
    baseline_cnt = check_total_relations(client)
    print(f"Baseline relationship count: {baseline_cnt}")
    assert baseline_cnt == 217, f"Expected 217 relationships, got {baseline_cnt}"

    # BATCH 1: Meloxicam
    print("\n--- Running Batch 1: Meloxicam ---")
    relocate_node_edges(client, "Meloxicam 15mg", "Meloxicam", "15mg")
    relocate_node_edges(client, "Meloxicam 7.5mg", "Meloxicam", "7.5mg")
    b1_cnt = check_total_relations(client)
    print(f"Batch 1 relationship count: {b1_cnt}")
    assert b1_cnt == 217, f"Batch 1 relationship count mismatch! Expected 217, got {b1_cnt}"

    # BATCH 2: Hydrocortisone
    print("\n--- Running Batch 2: Hydrocortisone ---")
    relocate_node_edges(client, "Hydrocortisone 10mg", "Hydrocortisone", "10mg")
    relocate_node_edges(client, "Hydrocortisone", "Hydrocortisone", "")
    b2_cnt = check_total_relations(client)
    print(f"Batch 2 relationship count: {b2_cnt}")
    assert b2_cnt == 217, f"Batch 2 relationship count mismatch! Expected 217, got {b2_cnt}"

    # BATCH 3: All remaining drug nodes
    print("\n--- Running Batch 3: All remaining drug nodes ---")
    nodes = client.execute_query("MATCH (d) WHERE d:DRUG OR d:DRUG_GROUP RETURN d.name AS name ORDER BY d.name")
    for row in nodes:
        name = row["name"]
        if name in ("Meloxicam", "Hydrocortisone"):
            continue
        ing, dos = parse_drug_name(name)
        if ing != name or dos:
            relocate_node_edges(client, name, ing, dos)

    b3_cnt = check_total_relations(client)
    print(f"Batch 3 relationship count: {b3_cnt}")
    assert b3_cnt == 217, f"Batch 3 relationship count mismatch! Expected 217, got {b3_cnt}"

    print("\n✅ All 3 batches completed successfully!")


if __name__ == "__main__":
    run_migration()
