"""
Coverage Gap Analysis Script for MedGraph-VI Knowledge Graph.
Audits the Neo4j database to identify diseases missing minimum symptoms/treatments
and drugs without clinical associations, exporting findings to 'data/exports/coverage_gaps.csv'.
"""

import csv
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Ensure UTF-8 output encoding for Windows terminal printing
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.graph.neo4j_client import Neo4jClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CoverageAnalysis")

EXPORT_PATH = BASE_DIR / "data" / "exports" / "coverage_gaps.csv"

def get_coverage_gaps() -> List[Dict[str, Any]]:
    client = Neo4jClient()
    if not client.is_online():
        logger.error("Neo4j database is offline. Cannot perform coverage analysis.")
        return []

    # 1. Audit Disease Nodes
    disease_query = """
    MATCH (d:DISEASE)
    OPTIONAL MATCH (d)-[r:HAS_SYMPTOM]->(s:SYMPTOM)
    WITH d, count(s) AS symptom_count
    OPTIONAL MATCH (d)<-[r2:PRESCRIBED_FOR|TREATS]-(drug)
    RETURN d.name AS name, symptom_count, count(drug) AS treatment_count, (symptom_count + count(drug)) as total_degree
    ORDER BY total_degree ASC, name ASC
    """
    diseases = client.execute_query(disease_query)

    # 2. Audit Drug Nodes
    drug_query = """
    MATCH (d) WHERE d:DRUG OR d:DRUG_GROUP
    OPTIONAL MATCH (d)-[r:PRESCRIBED_FOR|TREATS|CONTRAINDICATED_FOR]->(t)
    RETURN d.name AS name, count(r) AS rel_count, labels(d)[0] AS label
    ORDER BY rel_count ASC, name ASC
    """
    drugs = client.execute_query(drug_query)

    gaps = []

    # Process diseases
    total_diseases = len(diseases)
    diseases_with_symptoms = 0
    diseases_with_treatments = 0

    for d in diseases:
        name = d["name"]
        s_count = d["symptom_count"]
        t_count = d["treatment_count"]

        # Criteria: >= 2 symptoms, >= 1 treatment
        if s_count >= 2:
            diseases_with_symptoms += 1
        else:
            gaps.append({
                "entity_name": name,
                "entity_type": "DISEASE",
                "missing_relation_type": "HAS_SYMPTOM",
                "degree": d.get("total_degree", 0)
            })

        if t_count >= 1:
            diseases_with_treatments += 1
        else:
            gaps.append({
                "entity_name": name,
                "entity_type": "DISEASE",
                "missing_relation_type": "PRESCRIBED_FOR/TREATS",
                "degree": d.get("total_degree", 0)
            })

    # Process drugs
    total_drugs = len(drugs)
    drugs_connected = 0

    for dr in drugs:
        name = dr["name"]
        rel_count = dr["rel_count"]
        label = dr["label"]

        if rel_count >= 1:
            drugs_connected += 1
        else:
            gaps.append({
                "entity_name": name,
                "entity_type": label,
                "missing_relation_type": "PRESCRIBED_FOR/TREATS/CONTRAINDICATED_FOR",
                "degree": rel_count
            })

    # Export gaps to CSV
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EXPORT_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["entity_name", "entity_type", "missing_relation_type"])
        writer.writeheader()
        for gap in gaps:
            writer.writerow({
                "entity_name": gap["entity_name"],
                "entity_type": gap["entity_type"],
                "missing_relation_type": gap["missing_relation_type"]
            })

    # Print Summary Statistics
    print("\n=======================================================")
    print("📊 KNOWLEDGE GRAPH COVERAGE STATISTICS:")
    print(f"   ► Disease Symptoms Coverage: {diseases_with_symptoms}/{total_diseases} ({diseases_with_symptoms/max(1, total_diseases)*100:.1f}%)")
    print(f"   ► Disease Treatments Coverage: {diseases_with_treatments}/{total_diseases} ({diseases_with_treatments/max(1, total_diseases)*100:.1f}%)")
    print(f"   ► Drug Clinical Associations: {drugs_connected}/{total_drugs} ({drugs_connected/max(1, total_drugs)*100:.1f}%)")
    print(f"   ► Total Coverage Gaps Found: {len(gaps)}")
    print("=======================================================\n")

    return gaps

if __name__ == "__main__":
    get_coverage_gaps()
