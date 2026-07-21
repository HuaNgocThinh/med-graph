"""
ICD-10 Entity Linker for Vietnamese Disease Entities.
Maps Vietnamese disease strings to standardized ICD-10 medical codes and terms.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from src.config import ICD10_DICT_PATH
from src.entity_linking.fuzzy_matcher import FuzzyMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ICD10Linker")

class ICD10Linker:
    """Links disease entity names to standardized ICD-10 codes."""

    def __init__(self, dict_path: Path = ICD10_DICT_PATH):
        self.dict_path = dict_path
        self.records = self._load_records()
        self.exact_map = self._build_exact_map()
        self.fuzzy_matcher = FuzzyMatcher(score_cutoff=75.0)

    def link_disease(self, entity_text: str) -> Dict[str, Any]:
        """
        Links a disease entity text to standard ICD-10 representation.
        Returns: {"standard_name", "code", "confidence", "method": "exact"|"fuzzy"|"unlinked"}
        """
        clean_text = entity_text.strip().lower()

        # 1. Exact match lookup
        if clean_text in self.exact_map:
            rec = self.exact_map[clean_text]
            return {
                "standard_name": rec["name_vi"],
                "code": rec["code"],
                "confidence": 1.0,
                "method": "exact"
            }

        # 2. Fuzzy match fallback
        fuzzy_res = self.fuzzy_matcher.find_best_match(clean_text, self.records, key="name_vi")
        if fuzzy_res:
            rec, conf = fuzzy_res
            return {
                "standard_name": rec["name_vi"],
                "code": rec["code"],
                "confidence": conf,
                "method": "fuzzy"
            }

        # 3. Unlinked fallback
        return {
            "standard_name": entity_text.title(),
            "code": "ICD-UNKNOWN",
            "confidence": 0.0,
            "method": "unlinked"
        }

    def _load_records(self):
        if not self.dict_path.exists():
            logger.warning(f"ICD-10 dictionary missing at {self.dict_path}")
            return []
        with open(self.dict_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_exact_map(self) -> Dict[str, Dict[str, Any]]:
        lookup = {}
        for item in self.records:
            if "name_vi" in item:
                lookup[item["name_vi"].lower()] = item
            for syn in item.get("synonyms", []):
                lookup[syn.lower()] = item
        return lookup

if __name__ == "__main__":
    linker = ICD10Linker()
    print("Exact Link:", linker.link_disease("Đái tháo đường týp 2"))
    print("Fuzzy Link:", linker.link_disease("bệnh tiểu đường tuýp 2"))
