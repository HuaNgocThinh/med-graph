"""
Vietnamese ConText Processor for Negation and Temporal Scope Detection.
Adapts the ConText clinical NLP algorithm for Vietnamese medical syntax.
Annotates extracted entities with 'negated' (bool) and 'temporal_context' ('past'|'present'|'unknown').
"""

import re
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ConTextProcessor")

# 20+ Vietnamese medical negation patterns (Pre-trigger & Post-trigger patterns)
NEGATION_PRE_TRIGGERS = [
    r"không\s+có",
    r"chưa\s+ghi\s+nhận",
    r"loại\s+trừ",
    r"không\s+thấy\s+dấu\s+hiệu",
    r"âm\s+tính\s+với",
    r"không\s+phát\s+hiện",
    r"chưa\s+từng",
    r"không\s+tổn\s+thương",
    r"không\s+phát\s+hiện\s+bất\s+thường",
    r"loại\s+trừ\s+khả\s+năng",
    r"chưa\s+phát\s+hiện",
    r"không\s+ghi\s+nhận",
    r"không\s+mắc",
    r"không\s+bị",
    r"chưa\s+bị",
    r"không\s+thấy",
    r"chối\s+bỏ",
    r"không\s+dị\s+ứng",
    r"không\s+sốt",
    r"không\s+ho"
]

NEGATION_POST_TRIGGERS = [
    r"âm\s+tính",
    r"bình\s+thường",
    r"đã\s+khỏi",
    r"đã\s+dừng"
]

# Temporal indicators
PAST_TRIGGERS = [
    r"tiền\s+sử",
    r"\d+\s*ngày\s+trước",
    r"\d+\s*tháng\s+trước",
    r"\d+\s*năm\s+trước",
    r"trước\s+đây",
    r"đã\s+từng",
    r"vừa\s+qua",
    r"đã\s+điều\s+trị"
]

PRESENT_TRIGGERS = [
    r"hiện\s+tại",
    r"đang",
    r"bây\s+giờ",
    r"nhập\s+viện",
    r"khám\s+lâm\s+sàng",
    r"cấp\s+tính",
    r"ngày\s+thứ\s+\d+"
]

class ConTextProcessor:
    """Vietnamese ConText algorithm for clinical entity assertion and temporal classification."""

    def __init__(self):
        self.pre_neg_regex = re.compile(r"|".join(NEGATION_PRE_TRIGGERS), re.IGNORECASE)
        self.post_neg_regex = re.compile(r"|".join(NEGATION_POST_TRIGGERS), re.IGNORECASE)
        self.past_regex = re.compile(r"|".join(PAST_TRIGGERS), re.IGNORECASE)
        self.present_regex = re.compile(r"|".join(PRESENT_TRIGGERS), re.IGNORECASE)

        # Context window size in characters (or word count distance)
        self.window_chars = 45

    def process_entities(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enriches entities with negation status and temporal context based on sentence context window.
        """
        processed = []
        for ent in entities:
            ent_copy = ent.copy()
            start = ent_copy["start"]
            end = ent_copy["end"]

            # Extract local sentence window around entity
            pre_window = text[max(0, start - self.window_chars):start]
            post_window = text[end:min(len(text), end + self.window_chars)]
            full_window = text[max(0, start - self.window_chars):min(len(text), end + self.window_chars)]

            # 1. Negation assertion check (Must not cross sentence boundaries)
            is_negated = False
            pre_matches = list(self.pre_neg_regex.finditer(pre_window))
            if pre_matches:
                last_match = pre_matches[-1]
                between_text = pre_window[last_match.end():]
                if not any(delim in between_text for delim in (".", ";", "?", "!", "\n")):
                    is_negated = True

            if not is_negated:
                post_matches = list(self.post_neg_regex.finditer(post_window))
                if post_matches:
                    first_match = post_matches[0]
                    between_text = post_window[:first_match.start()]
                    if not any(delim in between_text for delim in (".", ";", "?", "!", "\n")):
                        is_negated = True

            # 2. Temporal context determination (Must not cross sentence boundaries)
            temporal = "unknown"
            past_found = False
            past_pre = list(self.past_regex.finditer(pre_window))
            past_post = list(self.past_regex.finditer(post_window))
            if past_pre:
                last_match = past_pre[-1]
                if not any(delim in pre_window[last_match.end():] for delim in (".", ";", "?", "!", "\n")):
                    past_found = True
            if not past_found and past_post:
                first_match = past_post[0]
                if not any(delim in post_window[:first_match.start()] for delim in (".", ";", "?", "!", "\n")):
                    past_found = True

            if past_found:
                temporal = "past"
            else:
                pres_found = False
                pres_pre = list(self.present_regex.finditer(pre_window))
                pres_post = list(self.present_regex.finditer(post_window))
                if pres_pre:
                    last_match = pres_pre[-1]
                    if not any(delim in pre_window[last_match.end():] for delim in (".", ";", "?", "!", "\n")):
                        pres_found = True
                if not pres_found and pres_post:
                    first_match = pres_post[0]
                    if not any(delim in post_window[:first_match.start()] for delim in (".", ";", "?", "!", "\n")):
                        pres_found = True
                if pres_found:
                    temporal = "present"

            ent_copy["negated"] = is_negated
            ent_copy["temporal_context"] = temporal
            processed.append(ent_copy)

        return processed

if __name__ == "__main__":
    processor = ConTextProcessor()
    sample_text = "Bệnh nhân có tiền sử Cao huyết áp 3 năm trước. Hiện tại không thấy dấu hiệu Viêm phổi, khám lâm sàng bình thường."
    sample_entities = [
        {"entity": "Cao huyết áp", "type": "DISEASE", "start": 22, "end": 34, "source": "test"},
        {"entity": "Viêm phổi", "type": "DISEASE", "start": 76, "end": 85, "source": "test"}
    ]
    res = processor.process_entities(sample_text, sample_entities)
    import json
    print("ConText Processor Results:", json.dumps(res, ensure_ascii=False, indent=2))
