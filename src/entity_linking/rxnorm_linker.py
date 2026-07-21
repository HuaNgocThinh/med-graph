"""
RxNorm Entity Linker for Vietnamese Drug Entities.
Calls NIH RxNav REST API with local dictionary and rapidfuzz fallbacks.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from src.config import RXNORM_DICT_PATH, RXNAV_API_BASE
from src.entity_linking.fuzzy_matcher import FuzzyMatcher

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RxNormLinker")

class RxNormLinker:
    """Links drug entities to standard RxCUI codes via RxNav API and local Vietnamese drug dictionary."""

    def __init__(self, dict_path: Path = RXNORM_DICT_PATH):
        self.dict_path = dict_path
        self.records = self._load_records()
        self.exact_map = self._build_exact_map()
        self.fuzzy_matcher = FuzzyMatcher(score_cutoff=60.0)

    def link_drug(self, entity_text: str) -> Dict[str, Any]:
        """
        Links drug text to RxNorm code.
        Attempts RxNav REST API -> Local Exact Match -> Local Fuzzy Match -> Unlinked.
        """
        clean_text = entity_text.strip()

        # 1. Local exact match lookup first for Vietnamese drug names
        clean_lower = clean_text.lower()
        if clean_lower in self.exact_map:
            rec = self.exact_map[clean_lower]
            return {
                "standard_name": rec["name_vi"],
                "code": f"RXCUI:{rec['rxcui']}",
                "confidence": 1.0,
                "method": "exact"
            }

        # 2. Call NIH RxNav REST API
        rxnav_res = self._call_rxnav_api(clean_text)
        if rxnav_res:
            return rxnav_res

        # 3. Local fuzzy match fallback
        fuzzy_res = self.fuzzy_matcher.find_best_match(clean_lower, self.records, key="name_vi")
        if fuzzy_res:
            rec, conf = fuzzy_res
            return {
                "standard_name": rec["name_vi"],
                "code": f"RXCUI:{rec['rxcui']}",
                "confidence": conf,
                "method": "fuzzy"
            }

        # 4. Unlinked fallback
        return {
            "standard_name": clean_text.title(),
            "code": "RXCUI-UNKNOWN",
            "confidence": 0.0,
            "method": "unlinked"
        }

    def _call_rxnav_api(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """Invokes NIH RxNav REST API for concept normalization."""
        try:
            import requests
            url = f"{RXNAV_API_BASE}/rxcui.json"
            params = {"name": drug_name}
            resp = requests.get(url, params=params, timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                id_group = data.get("idGroup", {})
                rxnorm_ids = id_group.get("rxnormId", [])
                if rxnorm_ids:
                    rxcui = rxnorm_ids[0]
                    return {
                        "standard_name": drug_name.title(),
                        "code": f"RXCUI:{rxcui}",
                        "confidence": 0.95,
                        "method": "rxnav_api"
                    }
        except Exception as e:
            logger.debug(f"RxNav API call skipped or failed for '{drug_name}': {e}")
        return None

    def _load_records(self):
        if not self.dict_path.exists():
            logger.warning(f"RxNorm dictionary missing at {self.dict_path}")
            return []
        with open(self.dict_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _build_exact_map(self) -> Dict[str, Dict[str, Any]]:
        lookup = {}
        for item in self.records:
            if "name_vi" in item:
                lookup[item["name_vi"].lower()] = item
            if "name_en" in item:
                lookup[item["name_en"].lower()] = item
            for syn in item.get("synonyms", []):
                lookup[syn.lower()] = item
        return lookup

if __name__ == "__main__":
    linker = RxNormLinker()
    print("Local Link:", linker.link_drug("Paracetamol 500mg"))
    print("RxNav/Fuzzy Link:", linker.link_drug("Aspirin"))
