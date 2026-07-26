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
from src.entity_linking.entity_normalizer import (
    normalize_entity_name, get_canonical_name, is_generic_term,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ICD10Linker")

# The stop-word list that used to live here has moved to entity_normalizer.is_generic_term(),
# which is now the single authority. A per-module copy is precisely how this bug family kept
# recurring: the local list was missing 'viêm', so 'viêm' fuzzy-matched to Viêm phổi (J18.9).
# Import the gate, never re-declare it.

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

        # THE gate. Single authority, shared with GraphBuilder.
        # standard_name is deliberately None and rejected=True is set: the old code returned
        # the canonical_fallback here, which meant a caller doing
        #   head_info.get("standard_name") or item.get("head")
        # got a perfectly usable name back and built a node anyway. That is how the bogus
        # :DISEASE 'đau' node was created despite 'đau' already being in the stop list.
        if is_generic_term(entity_text, "DISEASE") or is_generic_term(clean_text, "DISEASE"):
            logger.info(f"🚫 Rejected generic term as DISEASE entity: {entity_text!r}")
            return {
                "standard_name": None,
                "code": None,   # item 3: null, not a sentinel string
                "confidence": 0.0,
                "method": "rejected_generic",
                "rejected": True,
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
            "code": None,   # item 3: null, not a sentinel string
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
