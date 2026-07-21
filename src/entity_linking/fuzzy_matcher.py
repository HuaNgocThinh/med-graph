"""
Fuzzy Matcher module utilizing rapidfuzz with difflib fallback for string similarity normalization.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FuzzyMatcher")

try:
    from rapidfuzz import process, fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    import difflib
    HAS_RAPIDFUZZ = False

class FuzzyMatcher:
    """Fuzzy string matching helper using rapidfuzz token similarity or difflib fallback."""

    def __init__(self, score_cutoff: float = 60.0):
        self.score_cutoff = score_cutoff

    def find_best_match(self, query: str, choices: List[Dict[str, Any]], key: str = "name_vi") -> Optional[Tuple[Dict[str, Any], float]]:
        """
        Finds best candidate match from dictionary choices for query string.
        Returns Tuple of (matched_item, normalized_confidence_score [0.0-1.0]).
        """
        if not query or not choices:
            return None

        # Build candidate string lookup map including synonyms
        candidate_map = {}
        candidate_strings = []

        for item in choices:
            primary_name = item.get(key, "")
            if primary_name:
                candidate_strings.append(primary_name)
                candidate_map[primary_name.lower()] = item

            for syn in item.get("synonyms", []):
                if syn:
                    candidate_strings.append(syn)
                    candidate_map[syn.lower()] = item

        if not candidate_strings:
            return None

        query_lower = query.lower()

        if HAS_RAPIDFUZZ:
            match_result = process.extractOne(
                query_lower,
                candidate_strings,
                scorer=fuzz.WRatio,
                score_cutoff=self.score_cutoff
            )

            if match_result:
                matched_str, score, _ = match_result
                item = candidate_map[matched_str.lower()]
                normalized_score = round(score / 100.0, 3)
                return item, normalized_score
        else:
            best_ratio = 0.0
            best_str = None
            for cand in candidate_strings:
                ratio = difflib.SequenceMatcher(None, query_lower, cand.lower()).ratio() * 100.0
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_str = cand

            if best_str and best_ratio >= self.score_cutoff:
                item = candidate_map[best_str.lower()]
                return item, round(best_ratio / 100.0, 3)

        return None

if __name__ == "__main__":
    matcher = FuzzyMatcher()
    sample_choices = [
        {"code": "E11", "name_vi": "Đái tháo đường týp 2", "synonyms": ["tiểu đường tuýp 2"]},
        {"code": "I10", "name_vi": "Bệnh cao huyết áp", "synonyms": ["tăng huyết áp"]}
    ]
    res = matcher.find_best_match("tiểu đường loại 2", sample_choices)
    print("Fuzzy match result:", res)
