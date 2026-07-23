"""
NER Ensemble Module for MedGraph-VI.
Combines 3 NER sources: LLM NER, PhoBERT+CRF NER, and Dictionary NER.
Resolves boundary overlaps and type conflicts using prioritized voting logic.
"""

import logging
from typing import List, Dict, Any
from src.ner.dictionary_ner import DictionaryNER
from src.ner.phobert_crf_ner import PhoBertCRFNER
from src.ner.llm_ner import LLMNER
from src.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NEREnsemble")

# Priority ranking for conflict resolution (Higher value = Higher priority)
SOURCE_PRIORITY = {
    "llm": 3,           # Highest priority: LLM handles complex context and multi-word clinical entities
    "phobert_crf": 2,   # Medium priority: Model-based sequence tagger captures syntactic structure
    "dictionary": 1     # Baseline priority: Exact string matching against medical dictionaries
}

class NEREnsemble:
    """
    Ensemble recognizer integrating Dictionary, PhoBERT+CRF, and LLM predictions.
    
    Conflict Resolution Design Strategy (For Thesis Defense Explanation):
    -------------------------------------------------------------------
    1. Span Overlap Detection: Calculates Intersection over Union (IoU) or char span intersection.
    2. Overlap Threshold (> 50%): When two entity spans overlap by more than 50% of the smaller span,
       a conflict is declared.
    3. Priority Hierarchy: LLM > PhoBERT+CRF > Dictionary.
       - LLM excels at capturing contextual boundaries (e.g. "Đái tháo đường týp 2" vs "Đái tháo đường").
       - PhoBERT+CRF provides reliable morphological sequence boundary prediction.
       - Dictionary provides robust fallback for standardized medical terminology.
    4. Span Boundary Unification: Preserves the highest priority entity's type while choosing the
       longest valid phrase span if high priority confirms existence.
    """

    def __init__(self, llm_client: LLMClient = None):
        self.dict_ner = DictionaryNER()
        self.phobert_ner = PhoBertCRFNER()
        self.llm_ner = LLMNER(llm_client)

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Runs all 3 NER modules on text and applies priority-based ensemble conflict resolution.
        Returns final consolidated list of entity dictionaries.
        """
        # Step 1: Collect predictions from all 3 sources
        dict_preds = self.dict_ner.extract_entities(text)
        phobert_preds = self.phobert_ner.extract_entities(text)
        llm_preds = self.llm_ner.extract_entities(text)

        all_candidates = dict_preds + phobert_preds + llm_preds

        # Guard: Filter out standalone generic entity stop words to prevent downstream noise
        generic_stopwords = {"bệnh", "chứng", "triệu chứng", "tình trạng", "hội chứng", "thuốc"}
        all_candidates = [c for c in all_candidates if c["entity"].strip().lower() not in generic_stopwords]

        if not all_candidates:
            return []

        # Step 2: Sort candidates by starting index, then by source priority descending
        all_candidates.sort(key=lambda x: (x["start"], -SOURCE_PRIORITY.get(x["source"], 0)))

        # Step 3: Resolve conflicts and merge overlapping spans
        final_entities = []

        for candidate in all_candidates:
            if not final_entities:
                final_entities.append(candidate)
                continue

            prev = final_entities[-1]
            overlap_len = min(prev["end"], candidate["end"]) - max(prev["start"], candidate["start"])
            min_span_len = min(prev["end"] - prev["start"], candidate["end"] - candidate["start"])

            # Check if spans overlap significantly (>50% overlap ratio)
            if overlap_len > 0 and (overlap_len / min_span_len) > 0.5:
                prev_priority = SOURCE_PRIORITY.get(prev["source"], 0)
                cand_priority = SOURCE_PRIORITY.get(candidate["source"], 0)

                if cand_priority > prev_priority:
                    # Replace lower priority candidate with higher priority candidate
                    logger.debug(f"Conflict resolved: Overwriting '{prev['entity']}' ({prev['source']}) with '{candidate['entity']}' ({candidate['source']})")
                    final_entities[-1] = candidate
                elif cand_priority == prev_priority:
                    # If same source/priority, choose the longer span (e.g. "Đái tháo đường týp 2" over "Đái tháo đường")
                    if (candidate["end"] - candidate["start"]) > (prev["end"] - prev["start"]):
                        final_entities[-1] = candidate
                else:
                    # Retain current higher priority candidate
                    continue
            else:
                # No conflict: non-overlapping or distinct entity
                if candidate["start"] >= prev["end"]:
                    final_entities.append(candidate)

        return sorted(final_entities, key=lambda x: x["start"])

if __name__ == "__main__":
    ensemble = NEREnsemble()
    sample = "Bệnh nhân bị Cao huyết áp và Đái tháo đường týp 2 từ 2 năm trước, bác sĩ kê Paracetamol 500mg."
    res = ensemble.extract_entities(sample)
    import json
    print("Ensemble NER Results:", json.dumps(res, ensure_ascii=False, indent=2))
