"""
LLM-based Named Entity Recognition (NER) for Vietnamese Medical Text.
Uses few-shot prompting via LLMClient abstraction layer to extract medical entities with character span boundaries.
"""

import json
import logging
import re
from typing import List, Dict, Any
from src.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMNER")

SYSTEM_PROMPT = """Bạn là chuyên gia trích xuất thực thể y tế tiếng Việt (Medical Named Entity Recognition).
Nhiệm vụ: Tìm tất cả các thực thể y tế thuộc các loại:
- DISEASE: Tên bệnh, hội chứng, tình trạng bệnh lý (VD: Cao huyết áp, Đái tháo đường týp 2, Viêm họng cấp)
- DRUG: Tên thuốc, hoạt chất, biệt dược (VD: Paracetamol 500mg, Metformin, Aspirin)
- SYMPTOM: Triệu chứng lâm sàng (VD: khó thở, ho kéo dài, đau ngực)
- PROCEDURE: Thủ thuật, phẫu thuật, xét nghiệm y tế (VD: Chụp X-quang, Xét nghiệm máu)

Yêu cầu đầu ra: Trả về một JSON Array không chứa ký tự thừa:
[
  {"entity": "Cao huyết áp", "type": "DISEASE"},
  {"entity": "Paracetamol 500mg", "type": "DRUG"}
]
"""

class LLMNER:
    """Few-shot LLM-assisted Named Entity Recognizer."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts medical entities using LLM and computes character offset spans.
        Returns unified dicts: {"entity", "type", "start", "end", "source": "llm"}
        """
        prompt = f"""Văn bản y tế: "{text}"
Hãy trích xuất danh sách thực thể y tế theo đúng định dạng JSON Array."""

        raw_entities = self.llm.generate_json(prompt, system_prompt=SYSTEM_PROMPT)
        if not isinstance(raw_entities, list):
            logger.warning("LLM NER did not return a valid list.")
            return []

        formatted_entities = []
        text_lower = text.lower()
        used_spans = []

        for item in raw_entities:
            if not isinstance(item, dict) or "entity" not in item or "type" not in item:
                continue

            ent_text = item["entity"].strip()
            ent_type = item["type"].upper()

            # Locate character offset span in original text
            pattern = r'\b' + re.escape(ent_text.lower()) + r'\b'
            matches = list(re.finditer(pattern, text_lower))
            
            if not matches:
                # Fallback substring match without word boundaries
                idx = text_lower.find(ent_text.lower())
                if idx != -1:
                    matches = [re.search(re.escape(ent_text.lower()), text_lower[idx:])]

            for m in matches:
                start = m.start()
                end = m.end()
                if not any(s == start and e == end for s, e in used_spans):
                    formatted_entities.append({
                        "entity": text[start:end],
                        "type": ent_type,
                        "start": start,
                        "end": end,
                        "source": "llm"
                    })
                    used_spans.append((start, end))
                    break

        return sorted(formatted_entities, key=lambda x: x["start"])

if __name__ == "__main__":
    ner = LLMNER()
    sample_text = "Bệnh nhân có tiền sử Cao huyết áp, được bác sĩ chỉ định uống Paracetamol 500mg."
    res = ner.extract_entities(sample_text)
    print("LLM NER Results:", json.dumps(res, ensure_ascii=False, indent=2))
