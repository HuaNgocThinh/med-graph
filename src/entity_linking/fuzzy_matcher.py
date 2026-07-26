"""
Fuzzy Matcher module utilizing rapidfuzz with difflib fallback for string similarity normalization.
"""

import re
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

    # Minimum len(query)/len(matched_candidate). Measured, not guessed: across every term in
    # the system (302 of them, scratch/probe_scorers.py), the ONLY legitimate term that reaches
    # the fuzzy path rather than the exact map is 'tiểu đường' at ratio 0.62, while every bogus
    # fragment sits at 0.56 or below ('kháng viêm' 0.56, 'giảm viêm' 0.50, 'viêm' 0.31,
    # 'đau' 0.18, 'ho' 0.12). 0.6 is the separating value.
    #
    # This targets the actual mechanism rather than the symptom: fuzz.WRatio switches to
    # partial_ratio when the two strings differ a lot in length, which scores ANY substring at
    # ~90 regardless of meaning -- that is why 'viêm' matched 'Viêm phổi' at 0.90 and produced
    # three false PRESCRIBED_FOR edges. Requiring a length ratio disables exactly that path.
    MIN_LENGTH_RATIO = 0.6

    def __init__(self, score_cutoff: float = 88.0, min_length_ratio: float = MIN_LENGTH_RATIO):
        self.score_cutoff = score_cutoff
        self.min_length_ratio = min_length_ratio

    def _passes_length_guard(self, query: str, matched: str) -> bool:
        """Rejects a match where the query is far shorter than the candidate it matched."""
        if not matched:
            return False
        ratio = len(query) / len(matched)
        if ratio < self.min_length_ratio:
            logger.info(
                f"🚫 Fuzzy match rejected by length guard: query={query!r} vs candidate={matched!r} "
                f"(ratio {ratio:.2f} < {self.min_length_ratio})"
            )
            return False
        return True

    def find_best_match(self, query: str, choices: List[Dict[str, Any]], key: str = "name_vi") -> Optional[Tuple[Dict[str, Any], float]]:
        """
        Finds best candidate match from dictionary choices for query string.
        Strips pure dosage numbers/units from query during matching to prevent false dosage matches (e.g. Celecoxib 200mg vs Sắt 200mg).
        Returns Tuple of (matched_item, normalized_confidence_score [0.0-1.0]).
        """
        if not query or not choices:
            return None

        # Clean query by removing isolated dosage numbers/units for string comparison
        cleaned_query = re.sub(r'\b\d+(?:mg|mcg|ml|g|%)\b', '', query.lower()).strip()
        if not cleaned_query:
            cleaned_query = query.lower()

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

        if HAS_RAPIDFUZZ:
            match_result = process.extractOne(
                cleaned_query,
                candidate_strings,
                scorer=fuzz.WRatio,
                score_cutoff=self.score_cutoff
            )

            if match_result:
                matched_str, score, _ = match_result
                if not self._passes_length_guard(cleaned_query, matched_str.lower()):
                    return None
                item = candidate_map[matched_str.lower()]
                normalized_score = round(score / 100.0, 3)
                return item, normalized_score
        else:
            best_ratio = 0.0
            best_str = None
            for cand in candidate_strings:
                cand_clean = re.sub(r'\b\d+(?:mg|mcg|ml|g|%)\b', '', cand.lower()).strip()
                ratio = difflib.SequenceMatcher(None, cleaned_query, cand_clean).ratio() * 100.0
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_str = cand

            if best_str and best_ratio >= self.score_cutoff:
                if not self._passes_length_guard(cleaned_query, best_str.lower()):
                    return None
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
