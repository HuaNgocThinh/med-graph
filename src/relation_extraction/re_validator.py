"""
Relation Extraction Validation Module for MedGraph-VI.
Validates sentence-level proximity and evidence between head and tail entities in source clinical text.
Prevents cross-context relation hallucinations and flags distant entity pairs for manual expert review.
"""

import re
import logging
from typing import List, Dict, Any, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("REValidator")

def split_sentences(text: str) -> List[str]:
    """Splits Vietnamese clinical text into clean sentence units using standard sentence boundaries."""
    if not text:
        return []
    
    # Split on periods, exclamation marks, question marks, semicolons, and newlines
    raw_sentences = re.split(r'(?<=[.!?;\n])\s+', text)
    cleaned = [s.strip() for s in raw_sentences if s.strip()]
    return cleaned if cleaned else [text]

def validate_triple_sentence_distance(text: str, head: str, tail: str) -> Dict[str, Any]:
    """
    Validates sentence-level distance between head and tail entities in raw clinical text.
    
    Returns status:
    - 'CONFIRMED': Both entities appear in the exact same sentence (highest evidence).
    - 'NEIGHBOR': Entities appear in adjacent sentences (sentence index distance = 1).
    - 'MANUAL_REVIEW_REQUIRED': Entities are separated by >1 sentence or one entity is missing.
    """
    if not text or not head or not tail:
        return {
            "status": "MANUAL_REVIEW_REQUIRED",
            "sentence_distance": -1,
            "review_required": True,
            "reason": "Missing text or entity strings"
        }

    sentences = split_sentences(text)
    head_lower = head.lower().strip()
    tail_lower = tail.lower().strip()

    head_sentence_indices = []
    tail_sentence_indices = []

    for idx, s in enumerate(sentences):
        s_lower = s.lower()
        if head_lower in s_lower:
            head_sentence_indices.append(idx)
        if tail_lower in s_lower:
            tail_sentence_indices.append(idx)

    if not head_sentence_indices or not tail_sentence_indices:
        # Fallback check on full text substring
        text_lower = text.lower()
        if head_lower in text_lower and tail_lower in text_lower:
            # Found in text but sentence boundaries split them irregularly
            min_dist = 1
        else:
            return {
                "status": "MANUAL_REVIEW_REQUIRED",
                "sentence_distance": -1,
                "review_required": True,
                "reason": "One or both entities not found in sentence list"
            }
    else:
        min_dist = min(abs(h_idx - t_idx) for h_idx in head_sentence_indices for t_idx in tail_sentence_indices)

    if min_dist == 0:
        return {
            "status": "CONFIRMED",
            "sentence_distance": 0,
            "review_required": False,
            "reason": "Head and tail co-occur in the same sentence"
        }
    elif min_dist == 1:
        return {
            "status": "NEIGHBOR",
            "sentence_distance": 1,
            "review_required": False,
            "reason": "Head and tail occur in adjacent sentences"
        }
    else:
        return {
            "status": "MANUAL_REVIEW_REQUIRED",
            "sentence_distance": min_dist,
            "review_required": True,
            "reason": f"Head and tail separated by {min_dist} sentences (>1 threshold)"
        }
