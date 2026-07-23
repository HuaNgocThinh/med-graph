import json
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.ERROR)

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ner.ner_ensemble import NEREnsemble
from src.negation_temporal.context_processor import ConTextProcessor
from src.relation_extraction.rule_based_re import RuleBasedRelationExtractor
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.rxnorm_linker import RxNormLinker

ner_ensemble = NEREnsemble()
context_proc = ConTextProcessor()
rule_re = RuleBasedRelationExtractor()
icd_linker = ICD10Linker()
rx_linker = RxNormLinker()

synthetic_file = BASE_DIR / "data" / "synthetic" / "synthetic_data.json"
with open(synthetic_file, "r", encoding="utf-8") as f:
    samples = json.load(f)

print(f"Loaded {len(samples)} synthetic samples.\n")

fuzzy_matches = []
unmatched_entities = []

for sample in samples:
    sid = sample["id"]
    text = sample["text"]
    text_lower = text.lower()
    
    entities = ner_ensemble.extract_entities(text)
    processed_entities = context_proc.process_entities(text, entities)
    
    for e in processed_entities:
        ent_str = e["entity"]
        ent_type = e["type"]
        
        # Check 1: Entity exists in raw text
        if ent_str.lower() not in text_lower:
            unmatched_entities.append((sid, ent_str, text))
            
        # Check 2: Entity Linking
        if ent_type == "DISEASE":
            link = icd_linker.link_disease(ent_str)
        elif ent_type == "DRUG":
            link = rx_linker.link_drug(ent_str)
        else:
            link = {"standard_name": ent_str, "method": "unlinked"}
            
        if link.get("method") == "fuzzy":
            fuzzy_matches.append((sid, ent_str, ent_type, link["standard_name"], link["confidence"]))

print("=== 1. ENTITIES NOT FOUND IN RAW TEXT ===")
if not unmatched_entities:
    print("None! All NER entities were found in raw text.")
else:
    for sid, ent, txt in unmatched_entities:
        print(f"[{sid}] '{ent}' not in text: '{txt}'")

print("\n=== 2. FUZZY LINKED ENTITIES (POSSIBLE FALSE MAPS) ===")
for sid, orig, etype, std, conf in fuzzy_matches:
    print(f"[{sid}] ({etype}) '{orig}' -> Linked to: '{std}' (confidence: {conf})")
