"""
Rule-Based Baseline Relation Extraction module for Vietnamese Medical Text.
Uses regex pattern matching and token proximity between entity pairs to establish baseline relation extraction.
"""

import re
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RuleBasedRE")

# Pattern triggers for baseline relation extraction
PATTERN_RULES = [
    (r"(?:chống\s+chỉ\s+định|không\s+được\s+dùng|tránh\s+dùng)", "CONTRAINDICATED_FOR"),
    (r"(?:điều\s+trị|giảm|chữa|đặc\s+trị)", "TREATS"),
    (r"(?:chỉ\s+định|được\s+kê|cho\s+uống|kê\s+đơn)", "PRESCRIBED_FOR"),
    (r"(?:gây\s+ra|dẫn\s+đến|kèm\s+theo|gây)", "CAUSES"),
    (r"(?:biểu\s+hiện|triệu\s+chứng|có\s+dấu\s+hiệu)", "HAS_SYMPTOM")
]

class RuleBasedRelationExtractor:
    """Baseline relation extractor utilizing syntactic pattern matching and token proximity."""

    def __init__(self, max_distance_words: int = 12):
        self.max_distance_words = max_distance_words
        self.compiled_rules = [(re.compile(pat, re.IGNORECASE), rel) for pat, rel in PATTERN_RULES]

    def extract_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts candidate relations between adjacent entity pairs within word distance threshold.
        Returns list of dicts: {"head", "relation", "tail", "confidence", "source": "rule_based"}
        """
        if not entities or len(entities) < 2:
            return []

        triples = []
        text_lower = text.lower()

        # Iterate over all entity pairs
        for i in range(len(entities)):
            for j in range(len(entities)):
                if i == j:
                    continue

                e1 = entities[i]
                e2 = entities[j]

                # Distance calculation between entity spans
                if e1["end"] <= e2["start"]:
                    between_text = text_lower[e1["end"]:e2["start"]]
                elif e2["end"] <= e1["start"]:
                    between_text = text_lower[e2["end"]:e1["start"]]
                else:
                    continue

                word_count = len(between_text.split())
                if word_count > self.max_distance_words:
                    continue

                # Do not match relations across sentence boundaries
                if any(punct in between_text for punct in [".", ";", "?", "!", "\n"]):
                    continue

                # Match patterns in intervening text
                for pattern, relation in self.compiled_rules:
                    if pattern.search(between_text):
                        # Infer head/tail directionality based on entity types and relation type
                        head, tail, canonical_rel = self._assign_roles(e1, e2, relation)
                        if not head or not tail:
                            continue
                        
                        # Add unique triple
                        triple = {
                            "head": head["entity"],
                            "relation": canonical_rel,
                            "tail": tail["entity"],
                            "confidence": 0.70,
                            "evidence_span": between_text.strip(),
                            "low_confidence": False,
                            "source": "rule_based"
                        }
                        if triple not in triples:
                            triples.append(triple)
                        break

        return triples

    def _assign_roles(self, e1: Dict[str, Any], e2: Dict[str, Any], relation: str):
        """Assigns head, tail, and canonical relation based on medical ontology constraints."""
        t1, t2 = e1.get("type"), e2.get("type")

        if relation in ("TREATS", "PRESCRIBED_FOR", "CONTRAINDICATED_FOR"):
            if relation == "CONTRAINDICATED_FOR":
                if t1 == "DRUG" and t2 == "DISEASE":
                    return e1, e2, "CONTRAINDICATED_FOR"
                elif t2 == "DRUG" and t1 == "DISEASE":
                    return e2, e1, "CONTRAINDICATED_FOR"
                return None, None, relation

            # DRUG -> DISEASE is PRESCRIBED_FOR; DRUG -> SYMPTOM is TREATS
            if t1 == "DRUG" and t2 == "DISEASE":
                return e1, e2, "PRESCRIBED_FOR"
            elif t2 == "DRUG" and t1 == "DISEASE":
                return e2, e1, "PRESCRIBED_FOR"
            elif t1 == "DRUG" and t2 == "SYMPTOM":
                return e1, e2, "TREATS"
            elif t2 == "DRUG" and t1 == "SYMPTOM":
                return e2, e1, "TREATS"
            return None, None, relation

        elif relation == "HAS_SYMPTOM":
            if t1 == "DISEASE" and t2 == "SYMPTOM":
                return e1, e2, "HAS_SYMPTOM"
            elif t2 == "DISEASE" and t1 == "SYMPTOM":
                return e2, e1, "HAS_SYMPTOM"
            return None, None, relation

        elif relation == "CAUSES":
            if t1 in ("DISEASE", "DRUG") and t2 in ("SYMPTOM", "DISEASE"):
                return e1, e2, "CAUSES"
            elif t2 in ("DISEASE", "DRUG") and t1 in ("SYMPTOM", "DISEASE"):
                return e2, e1, "CAUSES"
            return None, None, relation

        return None, None, relation

if __name__ == "__main__":
    extractor = RuleBasedRelationExtractor()
    text = "Aspirin 81mg được kê cho bệnh nhân Nhồi máu não."
    ents = [
        {"entity": "Aspirin 81mg", "type": "DRUG", "start": 0, "end": 12},
        {"entity": "Nhồi máu não", "type": "DISEASE", "start": 35, "end": 47}
    ]
    res = extractor.extract_relations(text, ents)
    import json
    print("Rule-based RE Results:", json.dumps(res, ensure_ascii=False, indent=2))
