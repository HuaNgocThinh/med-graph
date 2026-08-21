"""
Test script to generate complex medical sentences with 2-3 long symptom phrases
and format them into strict CoNLL-U.
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.llm_client import LLMClient

def tokenize_words(text: str) -> List[Tuple[str, int, int]]:
    tokens = []
    for match in re.finditer(r'\w+|[^\w\s]', text, re.UNICODE):
        token_str = match.group(0)
        start, end = match.span()
        tokens.append((token_str, start, end))
    return tokens

def build_bio_conll(sample_id: str, text: str, entities: List[Dict[str, Any]]) -> str:
    tokens = tokenize_words(text)
    bio_tags = ["O"] * len(tokens)
    
    # Sort entities by start char index
    valid_entities = sorted(entities, key=lambda x: x["start"])
    
    for ent in valid_entities:
        label = ent["label"].upper()
        estart = ent["start"]
        eend = ent["end"]
        
        overlapping = []
        for idx, (tstr, tstart, tend) in enumerate(tokens):
            if max(tstart, estart) < min(tend, eend):
                overlapping.append(idx)
                
        if overlapping:
            bio_tags[overlapping[0]] = f"B-{label}"
            for idx in overlapping[1:]:
                bio_tags[idx] = f"I-{label}"
                
    lines = [f"# id = {sample_id}", f"# text = {text}"]
    for (tok, _, _), tag in zip(tokens, bio_tags):
        lines.append(f"{tok}\t{tag}")
    lines.append("")
    return "\n".join(lines)

def main():
    client = LLMClient()
    client.validate_connection()
    
    prompt = """Bạn là Chuyên gia Kỹ thuật Dữ liệu Y tế Việt Nam. Hãy tạo 3 câu lâm sàng tiếng Việt.
MỖI CÂU BẮT BUỘC CHỨA 2-3 CỤM TRIỆU CHỨNG DÀI (SYMPTOM), chi tiết tính chất/mức độ/vị trí (VD: "đau quặn bụng từng cơn", "tức ngực trái lan ra sau lưng", "ho khan kéo dài về đêm", "cảm giác nóng rát vùng thượng vị", "tê bì hai chi dưới", "tiểu buốt tiểu rắt").
CÓ THỂ chứa thêm DISEASE, DRUG, PROCEDURE.

Trả về duy nhất 1 mảng JSON chứa các object có cấu trúc:
[
  {
    "text": "Bệnh nhân nam 54 tuổi nhập viện vì cảm giác nóng rát vùng thượng vị kèm đau quặn bụng từng cơn kéo dài 3 ngày.",
    "entities": [
      {"text": "cảm giác nóng rát vùng thượng vị", "label": "SYMPTOM", "start": 35, "end": 67},
      {"text": "đau quặn bụng từng cơn", "label": "SYMPTOM", "start": 72, "end": 94}
    ]
  }
]
Chú ý tính chính xác của chỉ số `start` và `end` (chỉ số ký tự trong string `text`).
"""
    res = client.generate_json(prompt)
    print("Response raw:", json.dumps(res, ensure_ascii=False, indent=2))
    
    if isinstance(res, list):
        for i, item in enumerate(res, 1):
            text = item["text"]
            ents = item["entities"]
            # Recalculate/verify start and end substring offsets
            clean_ents = []
            for e in ents:
                etxt = e["text"]
                lbl = e["label"]
                idx = text.find(etxt)
                if idx != -1:
                    clean_ents.append({"text": etxt, "label": lbl, "start": idx, "end": idx + len(etxt)})
                else:
                    print(f"Warning: '{etxt}' not found in '{text}'")
            conll = build_bio_conll(f"syn_v3_{i:03d}", text, clean_ents)
            print(conll)

if __name__ == "__main__":
    main()
