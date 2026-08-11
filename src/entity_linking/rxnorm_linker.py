"""
RxNorm Entity Linker for Vietnamese Drug Entities.
Calls NIH RxNav REST API with local dictionary and rapidfuzz fallbacks.
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional
from src.config import RXNORM_DICT_PATH, RXNAV_API_BASE
from src.entity_linking.fuzzy_matcher import FuzzyMatcher
from src.entity_linking.entity_normalizer import normalize_entity_name, get_canonical_name, is_drug_group

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RxNormLinker")

# Shared with scripts/rebuild_rxnorm_dict.py: RxNorm indexes ingredients, not dosage strings.
DOSAGE_RE = re.compile(r"\s*\d+(?:[.,]\d+)?\s*(?:mg|mcg|g|ml|%|iu|ui)(?:\s*/\s*\S+)?\s*", re.IGNORECASE)

GENERIC_STOP_WORDS = {
    "thuốc", "kháng sinh", "dùng thuốc", "đau", "sốt", "ho", "bệnh",
    "tình trạng", "xét nghiệm", "viên", "liều", "mất nước", "tiểu đêm"
}

class RxNormLinker:
    """Links drug entities to standard RxCUI codes via RxNav API and local Vietnamese drug dictionary."""

    def __init__(self, dict_path: Path = RXNORM_DICT_PATH):
        self.dict_path = dict_path
        self.records = self._load_records()
        self.exact_map = self._build_exact_map()
        self.fuzzy_matcher = FuzzyMatcher(score_cutoff=88.0)

    def link_drug(self, entity_text: str) -> Dict[str, Any]:
        """
        Links drug text to RxNorm code.
        Attempts Local Exact Match -> RxNav REST API -> Local Fuzzy Match -> Unlinked.
        """
        clean_text = normalize_entity_name(entity_text, entity_type="DRUG")
        clean_lower = clean_text.lower()
        canonical_fallback = get_canonical_name(clean_text)

        # Check if entity is a Drug Group/Class (e.g. Corticoid, Kháng sinh)
        is_group = is_drug_group(clean_text)
        group_type = "DRUG_GROUP" if is_group else "DRUG"

        # Guard check: Ignore generic non-drug stop words from fuzzy matching
        if clean_lower in GENERIC_STOP_WORDS or len(clean_lower) < 3:
            return {
                "standard_name": canonical_fallback,
                "code": None,   # item 3: null, not a sentinel string
                "confidence": 0.0,
                "method": "unlinked",
                "type": group_type
            }

        # 1. Local exact match lookup first for Vietnamese drug names
        if clean_lower in self.exact_map:
            rec = self.exact_map[clean_lower]
            return {
                "standard_name": get_canonical_name(rec["name_vi"]),
                "code": f"RXCUI:{rec['rxcui']}",
                "confidence": 1.0,
                "method": "exact",
                "type": group_type
            }

        # 2. Call NIH RxNav REST API
        rxnav_res = self._call_rxnav_api(clean_text)
        if rxnav_res:
            rxnav_res["type"] = group_type
            return rxnav_res

        # 3. Local fuzzy match fallback (Score cutoff raised to 88.0)
        fuzzy_res = self.fuzzy_matcher.find_best_match(clean_lower, self.records, key="name_vi")
        if fuzzy_res:
            rec, conf = fuzzy_res
            return {
                "standard_name": get_canonical_name(rec["name_vi"]),
                "code": f"RXCUI:{rec['rxcui']}",
                "confidence": conf,
                "method": "fuzzy",
                "type": group_type
            }

        # 4. Unlinked fallback - PRESERVES ORIGINAL CANONICAL NAME, DOES NOT OVERWRITE WITH WRONG MATCH
        return {
            "standard_name": canonical_fallback,
            "code": None,   # item 3: null, not a sentinel string
            "confidence": 0.0,
            "method": "unlinked",
            "type": group_type
        }

    def _call_rxnav_api(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """
        Invokes NIH RxNav REST API for concept normalization.

        The dosage suffix is stripped first. RxNorm indexes ingredients, not Vietnamese
        product strings, so it answered with an empty idGroup for every dosage-bearing name --
        'Meloxicam 15mg' -> {} while 'Meloxicam' -> 41493. That alone accounted for 15 of the
        unlinked drug nodes.
        """
        query = DOSAGE_RE.sub(" ", drug_name or "").strip(" ,/-") or drug_name
        try:
            import requests
            url = f"{RXNAV_API_BASE}/rxcui.json"
            params = {"name": query}
            resp = requests.get(url, params=params, timeout=3.0)
            if resp.status_code == 200:
                data = resp.json()
                id_group = data.get("idGroup", {})
                rxnorm_ids = id_group.get("rxnormId", [])
                if rxnorm_ids:
                    rxcui = rxnorm_ids[0]
                    return {
                        "standard_name": get_canonical_name(drug_name),
                        "code": f"RXCUI:{rxcui}",
                        "confidence": 0.95,
                        "method": "rxnav_api"
                    }
        except Exception as e:
            logger.debug(f"RxNav API call skipped or failed for '{drug_name}': {e}")
        return None

    def _load_records(self):
        """
        Accepts both the legacy flat list and the rebuilt provenance-bearing shape
        {"_provenance": {...}, "drugs": [...], "needs_manual_review": [...]}.
        """
        if not self.dict_path.exists():
            logger.warning(f"RxNorm dictionary missing at {self.dict_path}")
            return []
        with open(self.dict_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            prov = data.get("_provenance", {})
            logger.info(
                f"RxNorm cache: {len(data.get('drugs', []))} record da xac minh nguoc, "
                f"nguon={prov.get('source', '?')}, fetch_date={prov.get('fetch_date', '?')}"
            )
            return data.get("drugs", [])
        logger.warning(
            "⚠️ RxNorm dictionary is in the legacy un-provenanced format. Its RxCUIs have no "
            "recorded source and must not be trusted. Run scripts/rebuild_rxnorm_dict.py."
        )
        return data

    def _build_exact_map(self) -> Dict[str, Dict[str, Any]]:
        """
        Only REVERSE-VERIFIED, API-sourced records may serve as cache hits.

        This is what makes cache-first safe. The old file was a hand/LLM-authored list with no
        provenance -- 27 of its 49 RxCUIs named a different drug (Omeprazole -> morphine,
        Amlodipine -> fentanyl) -- and because local-exact ran before the API, those poisoned
        entries permanently beat the correct RxNav answer. Records lacking
        reverse_verified/source are now skipped entirely, so they fall through to the live API
        instead of overriding it. A poisoned cache can no longer win.
        """
        lookup = {}
        skipped = 0
        for item in self.records:
            if not (item.get("reverse_verified") and item.get("source") == "rxnav_api"):
                skipped += 1
                continue
            if "name_vi" in item:
                lookup[item["name_vi"].lower()] = item
            if "name_en" in item:
                lookup[item["name_en"].lower()] = item
            for syn in item.get("synonyms", []):
                lookup[syn.lower()] = item
        if skipped:
            logger.warning(
                f"⚠️ {skipped} RxNorm record bi BO QUA khoi cache vi thieu provenance "
                f"(reverse_verified/source). Chung se duoc tra cuu lai qua RxNav API."
            )
        return lookup

if __name__ == "__main__":
    linker = RxNormLinker()
    print("Local Link:", linker.link_drug("Paracetamol 500mg"))
    print("RxNav/Fuzzy Link:", linker.link_drug("Aspirin"))
    print("Drug Group Test:", linker.link_drug("Corticoid"))
