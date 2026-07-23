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
from src.entity_linking.entity_normalizer import normalize_entity_name, get_canonical_name

logging.basicConfig(level=logging.INFO)
GENERIC_STOP_WORDS = {
    "bệnh", "bệnh nhân", "đau", "sốt", "ho", "bị", "trẻ", "bệnh nhi",
    "thuốc", "khám", "chẩn đoán", "tiền sử", "hiện tại", "triệu chứng", "lâm sàng",
    "chứng", "tình trạng", "hội chứng"
}

class ICD10Linker:
    """Links disease entity names to standardized ICD-10 codes."""

    def __init__(self, dict_path: Path = ICD10_DICT_PATH):
        self.dict_path = dict_path
        self.records = self._load_records()
        self.exact_map = self._build_exact_map()
        self.fuzzy_matcher = FuzzyMatcher(score_cutoff=88.0)

    def link_disease(self, entity_text: str) -> Dict[str, Any]:
        """
        Links a disease entity text to standard ICD-10 representation.
        Returns: {"standard_name", "code", "confidence", "method": "exact"|"fuzzy"|"unlinked"}
        """
        clean_text = normalize_entity_name(entity_text, entity_type="DISEASE")
        clean_lower = clean_text.lower()
        canonical_fallback = get_canonical_name(clean_text)

        # Guard check: Ignore generic non-disease stop words from fuzzy matching
        if clean_lower in GENERIC_STOP_WORDS or len(clean_lower) < 3:
            return {
                "standard_name": canonical_fallback,
                "code": "ICD-UNKNOWN",
                "confidence": 0.0,
                "method": "unlinked",
                "type": "DISEASE"
            }

        # 1. Exact match lookup
        if clean_lower in self.exact_map:
            rec = self.exact_map[clean_lower]
            return {
                "standard_name": get_canonical_name(rec["name_vi"]),
                "code": rec["code"],
                "confidence": 1.0,
                "method": "exact",
                "type": "DISEASE"
            }

        # 2. Fuzzy match fallback (Score cutoff 88.0)
        fuzzy_res = self.fuzzy_matcher.find_best_match(clean_lower, self.records, key="name_vi")
        if fuzzy_res:
            rec, conf = fuzzy_res
            return {
                "standard_name": get_canonical_name(rec["name_vi"]),
                "code": rec["code"],
                "confidence": conf,
                "method": "fuzzy",
                "type": "DISEASE"
            }

        # 3. Unlinked fallback - PRESERVES ORIGINAL CANONICAL NAME, DOES NOT OVERWRITE WITH WRONG MATCH
        return {
            "standard_name": canonical_fallback,
            "code": "ICD-UNKNOWN",
            "confidence": 0.0,
            "method": "unlinked",
            "type": "DISEASE"
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
