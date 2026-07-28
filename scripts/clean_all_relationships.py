"""
One-Time Relationship CSV Cleaning & Entity Normalization Script for MedGraph-VI.
Cleans 'data/exports/all_relationships_raw.csv' (or exports fresh from Neo4j) by:
1. Applying entity normalization & alias resolution (get_canonical_name).
2. Merging TREATS and PRESCRIBED_FOR to PRESCRIBED_FOR for Drug-Disease pairs.
3. Validating head/tail co-occurrence in raw sample text (cross-sample leakage removal).
4. Generating clean relationship CSV (all_relationships.csv) with full traceability.
"""

import csv
import json
import logging
import sys
import re
from pathlib import Path
from typing import List, Set, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
from src.entity_linking.dict_loader import load_records  # noqa: E402
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Ensure UTF-8 output encoding for Windows terminal printing
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.entity_linking.entity_normalizer import get_canonical_name, is_drug_group, ALIAS_MAP
from src.relation_extraction.re_validator import split_sentences
from src.graph.neo4j_client import Neo4jClient
from run_pipeline import export_all_relationships_csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CSVCleaner")

CSV_PATH = BASE_DIR / "data" / "exports" / "all_relationships.csv"
RAW_CSV_PATH = BASE_DIR / "data" / "exports" / "all_relationships_raw.csv"
SYNTHETIC_PATH = BASE_DIR / "data" / "synthetic" / "synthetic_data.json"

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

def load_standard_synonyms() -> Dict[str, Set[str]]:
    synonyms_map = {}
    
    # 1. Load from ALIAS_MAP in entity_normalizer
    for alias, canon in ALIAS_MAP.items():
        canon_lower = canon.lower().strip()
        if canon_lower not in synonyms_map:
            synonyms_map[canon_lower] = {canon_lower}
        synonyms_map[canon_lower].add(alias.lower().strip())
        
    # 2. Load from ICD10 dictionary
    icd_path = BASE_DIR / "data" / "dictionaries" / "icd10_vi.json"
    if icd_path.exists():
        try:
            icd_data = load_records(icd_path)
            if True:
                for item in icd_data:
                    name = item.get("name_vi", "").strip()
                    if name:
                        canon_name = get_canonical_name(name)
                        canon_lower = canon_name.lower().strip()
                        if canon_lower not in synonyms_map:
                            synonyms_map[canon_lower] = {canon_lower}
                        synonyms_map[canon_lower].add(name.lower().strip())
                        for syn in item.get("synonyms", []):
                            synonyms_map[canon_lower].add(syn.lower().strip())
        except Exception as e:
            logger.warning(f"Error reading ICD-10 dictionary: {e}")

    # 3. Load from RxNorm dictionary
    rx_path = BASE_DIR / "data" / "dictionaries" / "rxnorm_vi.json"
    if rx_path.exists():
        try:
            with open(rx_path, "r", encoding="utf-8") as f:
                rx_data = json.load(f)
                for item in rx_data:
                    name = item.get("name_vi", "").strip()
                    if name:
                        canon_name = get_canonical_name(name)
                        canon_lower = canon_name.lower().strip()
                        if canon_lower not in synonyms_map:
                            synonyms_map[canon_lower] = {canon_lower}
                        synonyms_map[canon_lower].add(name.lower().strip())
                        for syn in item.get("synonyms", []):
                            synonyms_map[canon_lower].add(syn.lower().strip())
        except Exception as e:
            logger.warning(f"Error reading RxNorm dictionary: {e}")
                        
    return synonyms_map

SYNONYMS_MAP = load_standard_synonyms()

# Load dictionaries for entity type classification
DISEASE_NAMES = set()
DRUG_NAMES = set()

# Populate DISEASE_NAMES
icd_path = BASE_DIR / "data" / "dictionaries" / "icd10_vi.json"
if icd_path.exists():
    try:
        icd_data = load_records(icd_path)
        if True:
            for item in icd_data:
                name = item.get("name_vi", "").strip()
                if name:
                    DISEASE_NAMES.add(get_canonical_name(name).lower())
                    for syn in item.get("synonyms", []):
                        DISEASE_NAMES.add(get_canonical_name(syn).lower())
    except Exception:
        pass

# Populate DRUG_NAMES
rx_path = BASE_DIR / "data" / "dictionaries" / "rxnorm_vi.json"
if rx_path.exists():
    try:
        with open(rx_path, "r", encoding="utf-8") as f:
            rx_data = json.load(f)
            for item in rx_data:
                name = item.get("name_vi", "").strip()
                if name:
                    DRUG_NAMES.add(get_canonical_name(name).lower())
                    for syn in item.get("synonyms", []):
                        DRUG_NAMES.add(get_canonical_name(syn).lower())
    except Exception:
        pass

def is_disease_entity(name: str) -> bool:
    name_lower = name.lower().strip()
    if name_lower in DISEASE_NAMES:
        return True
    disease_keywords = ["viêm", "bệnh", "đái tháo đường", "suy tim", "loãng xương", "cường giáp", "động kinh", "sỏi", "u xơ", "nhồi máu", "trào ngược", "gút", "suy giáp", "phì đại", "rung nhĩ"]
    if any(kw in name_lower for kw in disease_keywords):
        return True
    return False

def is_drug_entity(name: str) -> bool:
    name_lower = name.lower().strip()
    if is_drug_group(name) or name_lower in DRUG_NAMES or name_lower in DRUG_ROOT_WORDS:
        return True
    for root in DRUG_ROOT_WORDS.values():
        if root in name_lower:
            return True
    return False

def find_entity_sentence_indices(sentences: List[str], canonical_name: str) -> List[int]:
    """Finds all sentence indices containing the canonical name, any of its aliases, or its drug root word."""
    canon_lower = canonical_name.lower().strip()
    root_word = DRUG_ROOT_WORDS.get(canon_lower, canon_lower)
    
    aliases = set()
    if canon_lower in SYNONYMS_MAP:
        aliases.update(SYNONYMS_MAP[canon_lower])
    aliases.add(canon_lower)
    aliases.add(root_word)
    
    indices = []
    for idx, s in enumerate(sentences):
        s_lower = s.lower()
        found = False
        
        # 1. Substring match
        for alias in aliases:
            if alias in s_lower:
                indices.append(idx)
                found = True
                break
                
        if found:
            continue
            
        # 2. Word overlap match for multi-word entities
        s_words = set(re.findall(r'\b\w+\b', s_lower))
        for alias in aliases:
            alias_words = re.findall(r'\b\w+\b', alias)
            if len(alias_words) >= 2:
                alias_words_set = set(alias_words)
                intersection = alias_words_set.intersection(s_words)
                overlap_ratio = len(intersection) / len(alias_words_set)
                if overlap_ratio >= 0.80:
                    indices.append(idx)
                    break
                    
    return indices

def clean_relationships():
    # If Neo4j is online, always export the freshest raw relationships first before cleaning
    neo4j_client = Neo4jClient()
    if neo4j_client.is_online():
        logger.info("🔄 Exporting fresh raw relationships from Neo4j database...")
        export_all_relationships_csv(neo4j_client, RAW_CSV_PATH)
        
    # Fallback to copy CSV to RAW_CSV if raw is missing but CSV exists
    if not RAW_CSV_PATH.exists() and CSV_PATH.exists():
        import shutil
        shutil.copy(CSV_PATH, RAW_CSV_PATH)

    if not RAW_CSV_PATH.exists():
        logger.error(f"CSV file missing at '{RAW_CSV_PATH}'")
        return

    # Load synthetic dataset indexed by sample ID
    sample_text_map = {}
    if SYNTHETIC_PATH.exists():
        with open(SYNTHETIC_PATH, "r", encoding="utf-8") as f:
            samples = json.load(f)
            sample_text_map = {s["id"]: s["text"] for s in samples}

    raw_rows = []
    with open(RAW_CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_rows.append(row)

    logger.info(f"Loaded {len(raw_rows)} raw relationships from '{RAW_CSV_PATH}'.")

    cleaned_rows = []
    rejected_rows = []
    seen_keys = set()

    for idx, row in enumerate(raw_rows):
        head = row.get("Head", "").strip()
        rel = row.get("Relation", "").strip()
        tail = row.get("Tail", "").strip()
        sample_ids_str = row.get("SourceSampleID", "").strip()

        # Handle comma-separated sample IDs if merged
        sample_ids = [s.strip() for s in sample_ids_str.split(",") if s.strip()]
        if not sample_ids:
            sample_ids = ["unknown"]

        # Apply Entity Normalization & Alias Mapping
        norm_head = get_canonical_name(head)
        norm_tail = get_canonical_name(tail)

        # Merge TREATS and PRESCRIBED_FOR for Drug-Disease pairs to PRESCRIBED_FOR
        if is_drug_entity(norm_head) and is_disease_entity(norm_tail):
            if rel in ("TREATS", "PRESCRIBED_FOR"):
                rel = "PRESCRIBED_FOR"
        elif is_drug_entity(norm_tail) and is_disease_entity(norm_head):
            if rel in ("TREATS", "PRESCRIBED_FOR"):
                rel = "PRESCRIBED_FOR"

        # Reject standalone generic words to prevent leakage of uninformative entities
        generic_stopwords = {"bệnh", "chứng", "triệu chứng", "tình trạng", "hội chứng", "thuốc"}
        if norm_head.lower().strip() in generic_stopwords or norm_tail.lower().strip() in generic_stopwords:
            reason = "Contains prohibited standalone generic entity"
            logger.info(f"Removed [{head}]-[{rel}]-[{tail}] because: {reason}")
            rejected_rows.append({
                "Head": head,
                "Relation": rel,
                "Tail": tail,
                "SourceSampleID": sample_ids_str,
                "Reason": reason
            })
            continue

        # Reject known wrong inferences (Ferrous sulfate mismatch)
        if norm_head.lower() == "ferrous sulfate" and "thiếu máu" not in norm_tail.lower():
            reason = "Known wrong relation (Ferrous sulfate should only be for anemia)"
            logger.info(f"Removed [{head}]-[{rel}]-[{tail}] because: {reason}")
            rejected_rows.append({
                "Head": head,
                "Relation": rel,
                "Tail": tail,
                "SourceSampleID": sample_ids_str,
                "Reason": reason
            })
            continue

        # Validate against raw sample text for each source_sample_id
        valid_samples_for_triple = []
        reject_reasons = []
        for sid in sample_ids:
            raw_text = sample_text_map.get(sid, "")
            if not raw_text:
                valid_samples_for_triple.append(sid)
                continue

            sentences = split_sentences(raw_text)
            head_indices = find_entity_sentence_indices(sentences, norm_head)
            tail_indices = find_entity_sentence_indices(sentences, norm_tail)

            if not head_indices or not tail_indices:
                reason = f"Entity not found in text: head_found={bool(head_indices)} (norm='{norm_head}'), tail_found={bool(tail_indices)} (norm='{norm_tail}')"
                reject_reasons.append(f"{sid}: {reason}")
                continue

            # We DO NOT delete the relationship based on sentence distance constraint.
            # As long as both entities are found in the text, it is accepted to prevent false negative deletions of valid clinical context.
            valid_samples_for_triple.append(sid)

        if valid_samples_for_triple:
            clean_sid_str = ",".join(valid_samples_for_triple)
            dedup_key = (norm_head.lower(), rel.upper(), norm_tail.lower(), clean_sid_str)
            if dedup_key not in seen_keys:
                seen_keys.add(dedup_key)
                cleaned_rows.append({
                    "Head": norm_head,
                    "Relation": rel,
                    "Tail": norm_tail,
                    "SourceSampleID": clean_sid_str
                })
        else:
            reason_str = "; ".join(reject_reasons)
            logger.info(f"Removed [{head}]-[{rel}]-[{tail}] because: {reason_str}")
            rejected_rows.append({
                "Head": head,
                "Relation": rel,
                "Tail": tail,
                "SourceSampleID": sample_ids_str,
                "Reason": reason_str
            })

    # Backup original raw CSV
    backup_path = CSV_PATH.parent / "all_relationships_raw_backup.csv"
    with open(backup_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Head", "Relation", "Tail", "SourceSampleID"])
        writer.writeheader()
        writer.writerows(raw_rows)

    # Overwrite clean CSV
    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Head", "Relation", "Tail", "SourceSampleID"])
        writer.writeheader()
        writer.writerows(cleaned_rows)

    logger.info(f"✅ CLEANING COMPLETE: Kept {len(cleaned_rows)} valid relationships, Rejected {len(rejected_rows)} leaked triples.")
    logger.info(f"💾 Saved clean CSV to '{CSV_PATH}' and raw backup to '{backup_path}'.")

if __name__ == "__main__":
    clean_relationships()
