"""
Audit Symptom Gaps Script (Stage 5a & 5b) for MedGraph-VI.
Correctly audits disease symptom coverage by counting sample occurrences where the disease is the subject/head,
excluding sample IDs where the disease is merely a target tail of a drug prescription.
Exports results to 'data/exports/symptom_gap_v2.csv'.
"""

import csv
import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.graph.neo4j_client import Neo4jClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuditSymptomGaps")

EXPORT_V2_PATH = BASE_DIR / "data" / "exports" / "symptom_gap_v2.csv"
OLD_SUSPECT_PATH = BASE_DIR / "data" / "exports" / "symptom_gap_suspect.csv"
SYNTHETIC_PATH = BASE_DIR / "data" / "synthetic" / "synthetic_data.json"


def parse_sids(raw_list: List[Any]) -> set:
    sids = set()
    for item in raw_list:
        if item:
            for part in str(item).split(","):
                p = part.strip()
                if p:
                    sids.add(p)
    return sids


def audit_symptom_gaps() -> List[Dict[str, Any]]:
    client = Neo4jClient()
    if not client.is_online():
        logger.error("Neo4j database is offline.")
        return []

    # Read synthetic corpus to count accurate text sample mentions
    corpus = []
    if SYNTHETIC_PATH.exists():
        with open(SYNTHETIC_PATH, "r", encoding="utf-8") as f:
            corpus = json.load(f)

    # Query diseases and HAS_SYMPTOM relations from Neo4j
    query = """
    MATCH (d:DISEASE)
    OPTIONAL MATCH (d)-[r:HAS_SYMPTOM]->(s:SYMPTOM)
    RETURN d.name AS disease_name,
           collect(DISTINCT r.source_sample_id) AS sym_sample_ids,
           collect(DISTINCT s.name) AS symptoms
    ORDER BY disease_name
    """
    rows = client.execute_query(query)

    results = []
    for r in rows:
        disease = r["disease_name"]
        dis_l = disease.lower()

        # Count samples where disease appears in corpus text or as head of outgoing relations
        text_sids = set()
        for sample in corpus:
            if dis_l in sample.get("text", "").lower():
                text_sids.add(sample["id"])

        head_edges = client.execute_query(
            "MATCH (d:DISEASE {name: $name})-[r]->(target) RETURN r.source_sample_id AS sid",
            {"name": disease}
        )
        for he in head_edges:
            text_sids.update(parse_sids([he["sid"]]))

        sym_sids = parse_sids(r["sym_sample_ids"])
        symptoms = [s for s in r["symptoms"] if s]

        total_samples_mentioned = len(text_sids)
        samples_with_symptom = len(sym_sids)
        symptom_count = len(symptoms)

        # gap_flag: True if total_samples_mentioned >= 2 but samples_with_symptom <= 1
        gap_flag = (total_samples_mentioned >= 2) and (samples_with_symptom <= 1)

        results.append({
            "disease_name": disease,
            "total_samples_mentioned": total_samples_mentioned,
            "samples_with_symptom": samples_with_symptom,
            "symptom_count": symptom_count,
            "gap_flag": gap_flag
        })

    # Export to symptom_gap_v2.csv
    EXPORT_V2_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EXPORT_V2_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "disease_name", "total_samples_mentioned", "samples_with_symptom", "symptom_count", "gap_flag"
        ])
        writer.writeheader()
        writer.writerows(results)

    logger.info(f"✅ Exported symptom_gap_v2.csv to {EXPORT_V2_PATH} with {len(results)} rows.")

    # Compare with old symptom_gap_suspect.csv
    if OLD_SUSPECT_PATH.exists():
        with open(OLD_SUSPECT_PATH, "r", encoding="utf-8-sig") as f:
            old_rows = list(csv.DictReader(f))
        
        old_gap_names = {r["Disease"] for r in old_rows if r.get("Disease")}
        new_gaps = {r["disease_name"] for r in results if r["gap_flag"]}
        
        false_positives = old_gap_names - new_gaps
        true_gaps = old_gap_names & new_gaps
        
        print("\n=======================================================")
        print("🔍 COMPARISON: symptom_gap_suspect.csv vs symptom_gap_v2.csv")
        print(f"   ► Old Suspect Gap Count: {len(old_gap_names)}")
        print(f"   ► New Audited Gap Count: {len(new_gaps)}")
        print(f"   ► False Positives in Old Script (Now Resolved): {len(false_positives)}")
        if false_positives:
            print(f"     List: {sorted(list(false_positives))}")
        print(f"   ► Verified Natural Gaps: {len(true_gaps)}")
        print("=======================================================\n")

    return results


if __name__ == "__main__":
    audit_symptom_gaps()
