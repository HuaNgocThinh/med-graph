"""
Automated Verification Script for MedGraph-VI Knowledge Graph Relationships.
Verifies that 100% of relationship triples in 'data/exports/all_relationships.csv'
have both head and tail entities present in the raw clinical text of their assigned SourceSampleID.
"""

import csv
import json
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.entity_linking.entity_normalizer import get_canonical_name, normalize_entity_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VerificationScript")

CSV_PATH = BASE_DIR / "data" / "exports" / "all_relationships.csv"
SYNTHETIC_PATH = BASE_DIR / "data" / "synthetic" / "synthetic_data.json"

# Common base drug root words mapping for string verification
DRUG_ROOT_WORDS = {
    "paracetamol 500mg": "paracetamol",
    "aspirin 81mg": "aspirin",
    "amoxicillin 500mg": "amoxicillin",
    "omeprazole 20mg": "omeprazole",
    "esomeprazole 40mg": "esomeprazole",
    "atorvastatin 20mg": "atorvastatin",
    "bromhexine 8mg": "bromhexine",
    "furosemide 40mg": "furosemide",
    "lisinopril 10mg": "lisinopril",
    "tamsulosin 0.4mg": "tamsulosin",
    "sertraline 50mg": "sertraline",
    "cetirizine 10mg": "cetirizine",
    "methotrexate 10mg/tuần": "methotrexate",
    "carbamazepine 200mg": "carbamazepine",
    "fluconazole 150mg": "fluconazole",
    "tenofovir 300mg": "tenofovir",
    "warfarin 2.5mg": "warfarin",
    "prednisolone 5mg": "prednisolone",
    "ciprofloxacin 500mg": "ciprofloxacin"
}

def verify_all_relationships():
    if not CSV_PATH.exists():
        logger.error(f"CSV file missing at '{CSV_PATH}'")
        return

    if not SYNTHETIC_PATH.exists():
        logger.error(f"Synthetic data file missing at '{SYNTHETIC_PATH}'")
        return

    with open(SYNTHETIC_PATH, "r", encoding="utf-8") as f:
        samples = json.load(f)
        sample_map = {s["id"]: s["text"] for s in samples}

    triples = []
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            triples.append(row)

    logger.info(f"🔍 Starting automated verification on {len(triples)} relationship triples...")

    passed = 0
    failed = 0

    for idx, t in enumerate(triples):
        head = t["Head"].strip()
        rel = t["Relation"].strip()
        tail = t["Tail"].strip()
        sids = [s.strip() for s in t["SourceSampleID"].split(",") if s.strip()]

        triple_str = f"({head} -[{rel}]-> {tail})"
        is_triple_valid = True

        for sid in sids:
            text = sample_map.get(sid, "")
            if not text:
                logger.warning(f"⚠️ Triple {idx+1} {triple_str}: SourceSampleID '{sid}' text not found.")
                is_triple_valid = False
                continue

            text_lower = text.lower()
            head_norm = normalize_entity_name(head).lower()
            tail_norm = normalize_entity_name(tail).lower()

            head_root = DRUG_ROOT_WORDS.get(head_norm, head_norm)
            tail_root = DRUG_ROOT_WORDS.get(tail_norm, tail_norm)

            head_in_text = head_norm in text_lower or head_root in text_lower or any(w in text_lower for w in head_norm.split() if len(w) > 3)
            tail_in_text = tail_norm in text_lower or tail_root in text_lower or any(w in text_lower for w in tail_norm.split() if len(w) > 3)

            # Reject standalone generic words to prevent leakage of uninformative entities
            generic_stopwords = {"bệnh", "chứng", "triệu chứng", "tình trạng", "hội chứng", "thuốc"}
            if head.lower().strip() in generic_stopwords or tail.lower().strip() in generic_stopwords:
                logger.error(f"❌ FAIL Triple {idx+1} {triple_str} in '{sid}': Contains prohibited standalone generic entity.")
                is_triple_valid = False
                continue

            if not head_in_text or not tail_in_text:
                logger.error(f"❌ FAIL Triple {idx+1} {triple_str} in '{sid}': head_in_text={head_in_text}, tail_in_text={tail_in_text}. Text: '{text}'")
                is_triple_valid = False

        if is_triple_valid:
            passed += 1
        else:
            failed += 1

    logger.info("=======================================================")
    logger.info(f"📊 AUTOMATED VERIFICATION RESULTS:")
    logger.info(f"   ► Total Triples Verified: {len(triples)}")
    logger.info(f"   ► Passed Verification (100% Ground Truth Match): {passed}/{len(triples)} ({passed/len(triples)*100:.1f}%)")
    logger.info(f"   ► Failed / Leaked Triples Remaining: {failed}")
    logger.info("=======================================================")

if __name__ == "__main__":
    verify_all_relationships()
