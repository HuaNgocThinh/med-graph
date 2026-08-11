"""
Dictionary-based Named Entity Recognition (NER) for Vietnamese Medical Text.
Matches terms against ICD-10 disease dictionary and RxNorm drug dictionary.
"""

import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Any
from src.config import ICD10_DICT_PATH, RXNORM_DICT_PATH
from src.entity_linking.dict_loader import load_records

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DictionaryNER")

class DictionaryNER:
    """Matches Vietnamese medical entities using loaded ICD-10 and RxNorm dictionaries."""

    def __init__(self, icd10_path: Path = ICD10_DICT_PATH, rxnorm_path: Path = RXNORM_DICT_PATH):
        self.disease_terms = self._load_dictionary(icd10_path, entity_type="DISEASE")
        self.drug_terms = self._load_dictionary(rxnorm_path, entity_type="DRUG")
        # Sort terms by length descending to match longer multi-word entities first
        self.all_terms = sorted(self.disease_terms + self.drug_terms, key=lambda x: len(x["term"]), reverse=True)

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts medical entities from text using dictionary regex matching.
        Returns list of dicts: {"entity", "type", "start", "end", "source": "dictionary"}
        """
        entities = []
        text_lower = text.lower()
        matched_spans = []

        for item in self.all_terms:
            term = item["term"]
            entity_type = item["type"]
            pattern = r'\b' + re.escape(term) + r'\b'

            for match in re.finditer(pattern, text_lower):
                start, end = match.span()
                
                # Check for overlap with already matched longer terms
                if any(s <= start and end <= e for s, e in matched_spans):
                    continue

                entity_text = text[start:end]
                entities.append({
                    "entity": entity_text,
                    "type": entity_type,
                    "start": start,
                    "end": end,
                    "source": "dictionary"
                })
                matched_spans.append((start, end))

        return sorted(entities, key=lambda x: x["start"])

    def _load_dictionary(self, path: Path, entity_type: str) -> List[Dict[str, str]]:
        terms = []
        if not path.exists():
            logger.warning(f"Dictionary file missing at {path}")
            return terms

        # Both dictionaries now carry a metadata block alongside their records
        # (rxnorm_vi.json: _provenance/drugs; icd10_vi.json: _rules/diseases). The hand-written
        # isinstance() branch that used to live here only knew about "drugs", so it silently
        # returned an EMPTY gazetteer for icd10_vi.json the moment that file grew a metadata
        # key. One shared loader instead of a per-consumer branch.
        data = load_records(path)

        for entry in data:
            names = []
            if "name_vi" in entry:
                names.append(entry["name_vi"])
            if "synonyms" in entry:
                names.extend(entry["synonyms"])

            for name in names:
                if name:
                    terms.append({"term": name.strip().lower(), "type": entity_type})

        return terms

if __name__ == "__main__":
    ner = DictionaryNER()
    sample_text = "Bệnh nhân bị Đái tháo đường týp 2 và Cao huyết áp, được kê Paracetamol 500mg."
    res = ner.extract_entities(sample_text)
    print("Dictionary NER Results:", json.dumps(res, ensure_ascii=False, indent=2))
