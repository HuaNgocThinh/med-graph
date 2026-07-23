import json
import sys
from pathlib import Path

# Ensure UTF-8 output encoding for Windows terminal
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ner.ner_ensemble import NEREnsemble
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.rxnorm_linker import RxNormLinker

ner = NEREnsemble()
icd = ICD10Linker()
rx = RxNormLinker()

with open(BASE_DIR / "data" / "synthetic" / "synthetic_data.json", "r", encoding="utf-8") as f:
    samples = json.load(f)

for s in samples:
    sid = s["id"]
    text = s["text"]
    entities = ner.extract_entities(text)
    for e in entities:
        ent = e["entity"]
        etype = e["type"]
        if etype == "DISEASE":
            link = icd.link_disease(ent)
        elif etype == "DRUG":
            link = rx.link_drug(ent)
        else:
            continue
        
        if link.get("method") == "fuzzy":
            print(f"[{sid}] ({etype}) '{ent}' -> FUZZY -> '{link['standard_name']}' (conf: {link['confidence']})")
