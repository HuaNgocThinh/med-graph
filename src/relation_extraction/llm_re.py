"""
LLM-Assisted Relation Extraction (RE) module for Vietnamese Medical Text.
Extracts clinical relation triples between identified entities using structured few-shot prompting.
"""

import json
import logging
from typing import List, Dict, Any
from src.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMRelationExtraction")

VALID_RELATIONS = {
    "TREATS",               # Thuốc điều trị bệnh
    "PRESCRIBED_FOR",       # Thuốc được kê cho bệnh
    "CAUSES",               # Bệnh/Thuốc gây ra triệu chứng/biến chứng
    "HAS_SYMPTOM",          # Bệnh có triệu chứng
    "CONTRAINDICATED_FOR"   # Thuốc chống chỉ định với bệnh
}

SYSTEM_PROMPT = """Bạn là chuyên gia trích xuất quan hệ y tế (Medical Relation Extraction).
Nhiệm vụ của bạn là phân tích câu văn y tế và danh sách các thực thể đã xác định để rút ra các bộ ba quan hệ (triples).

QUY TẮC PHÂN BỔ LOẠI QUAN HỆ BẮT BUỘC (QUAN TRỌNG):
1. PRESCRIBED_FOR: DÙNG DUY NHẤT cho cặp (DRUG, DISEASE) — Thuốc được chỉ định/kê đơn để điều trị BỆNH. Tuyệt đối KHÔNG dùng TREATS cho cặp (DRUG, DISEASE).
2. TREATS: DÙNG DUY NHẤT cho cặp (DRUG, SYMPTOM) — Thuốc dùng để giảm/long/cắt TRIỆU CHỨNG cụ thể (VD: ho nhiều đờm, sốt, đau ngực, khó thở).
3. HAS_SYMPTOM: DÙNG DUY NHẤT cho cặp (DISEASE, SYMPTOM) — Bệnh biểu hiện bằng triệu chứng.
4. CONTRAINDICATED_FOR: DÙNG DUY NHẤT cho cặp (DRUG, DISEASE) — Thuốc bị chống chỉ định đối với bệnh.
5. CAUSES: Dùng cho (DISEASE/DRUG, SYMPTOM/DISEASE) — Bệnh hoặc thuốc gây ra triệu chứng/tác dụng phụ/biến chứng.

QUY TẮC LIÊN KẾT NGÔN NGỮ:
1. Với MỖI cặp thực thể, chỉ trích quan hệ nếu có cụm từ nối TRỰC TIẾP và GẦN NHẤT giữa 2 thực thể đó trong câu.
2. XỬ LÝ RIÊNG TỪNG CẶP, KHÔNG áp dụng chung 1 loại quan hệ cho tất cả các thực thể trong cùng câu.
3. Từ khóa "chống chỉ định với X" chỉ áp dụng cho ĐÚNG thực thể X đứng cạnh cụm từ đó, KHÔNG áp dụng cho các thuốc khác xuất hiện trong cùng đoạn văn.

VÍ DỤ BẮT BUỘC HỌC THEO:

--- FEW-SHOT SET 1: CONTRAINDICATED_FOR vs PRESCRIBED_FOR ---
Văn bản: "Bệnh nhân Viêm loét dạ dày kèm trào ngược dạ dày. Không phát hiện Tiêu chảy cấp. Chống chỉ định với Ibuprofen. Đã kê Omeprazole 20mg."
Thực thể: 'Viêm loét dạ dày' (DISEASE), 'trào ngược dạ dày' (DISEASE), 'Ibuprofen' (DRUG), 'Omeprazole 20mg' (DRUG)
Output:
[
  {"head": "Ibuprofen", "relation": "CONTRAINDICATED_FOR", "tail": "Viêm loét dạ dày", "confidence": 0.98, "evidence_span": "Viêm loét dạ dày ... Chống chỉ định với Ibuprofen"},
  {"head": "Omeprazole 20mg", "relation": "PRESCRIBED_FOR", "tail": "Viêm loét dạ dày", "confidence": 0.95, "evidence_span": "Viêm loét dạ dày ... Đã kê Omeprazole 20mg"},
  {"head": "Omeprazole 20mg", "relation": "PRESCRIBED_FOR", "tail": "trào ngược dạ dày", "confidence": 0.92, "evidence_span": "trào ngược dạ dày ... Đã kê Omeprazole 20mg"}
]
TUYỆT ĐỐI KHÔNG TRÍCH:
- (Omeprazole 20mg, CONTRAINDICATED_FOR, Viêm loét dạ dày) ← SAI HOÀN TOÀN
- (Omeprazole 20mg, TREATS, Viêm loét dạ dày) ← SAI (Phải dùng PRESCRIBED_FOR cho Drug-Disease)

--- FEW-SHOT SET 2: PRESCRIBED_FOR (Drug-Disease) vs TREATS (Drug-Symptom) ---
Ví dụ 2a:
Văn bản: "Bệnh nhân Hen phế quản. Đã kê Salbutamol xịt để cắt cơn khó thở."
Thực thể: 'Hen phế quản' (DISEASE), 'Salbutamol' (DRUG), 'khó thở' (SYMPTOM)
Output:
[
  {"head": "Salbutamol", "relation": "PRESCRIBED_FOR", "tail": "Hen phế quản", "confidence": 0.95, "evidence_span": "Bệnh nhân Hen phế quản ... kê Salbutamol"},
  {"head": "Salbutamol", "relation": "TREATS", "tail": "khó thở", "confidence": 0.95, "evidence_span": "kê Salbutamol xịt để cắt cơn khó thở"}
]

Ví dụ 2b:
Văn bản: "Bệnh nhân Viêm phế quản cấp, ho nhiều đờm. Kê Amoxicillin 500mg và Bromhexine 8mg để long đờm."
Thực thể: 'Viêm phế quản cấp' (DISEASE), 'ho nhiều đờm' (SYMPTOM), 'Amoxicillin 500mg' (DRUG), 'Bromhexine 8mg' (DRUG)
Output:
[
  {"head": "Amoxicillin 500mg", "relation": "PRESCRIBED_FOR", "tail": "Viêm phế quản cấp", "confidence": 0.95, "evidence_span": "Viêm phế quản cấp ... Kê Amoxicillin 500mg"},
  {"head": "Bromhexine 8mg", "relation": "TREATS", "tail": "ho nhiều đờm", "confidence": 0.92, "evidence_span": "Bromhexine 8mg để long đờm"}
]

--- FEW-SHOT SET 3: HAS_SYMPTOM ---
Văn bản: "Bệnh nhân Viêm phế quản cấp, ho nhiều đờm, sốt nhẹ."
Thực thể: 'Viêm phế quản cấp' (DISEASE), 'ho nhiều đờm' (SYMPTOM), 'sốt nhẹ' (SYMPTOM)
Output:
[
  {"head": "Viêm phế quản cấp", "relation": "HAS_SYMPTOM", "tail": "ho nhiều đờm", "confidence": 0.95, "evidence_span": "Viêm phế quản cấp, ho nhiều đờm"},
  {"head": "Viêm phế quản cấp", "relation": "HAS_SYMPTOM", "tail": "sốt nhẹ", "confidence": 0.95, "evidence_span": "Viêm phế quản cấp ... sốt nhẹ"}
]

Yêu cầu đầu ra: Trả về một JSON Array duy nhất không chứa lời giải thích:
[
  {"head": "...", "relation": "...", "tail": "...", "confidence": 0.95, "evidence_span": "..."}
]
"""

class LLMRelationExtractor:
    """Extracts clinical relation triples using LLM few-shot prompting."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()

    def extract_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts relation triples between entities in the input text.
        Returns list of dicts: {"head", "relation", "tail", "confidence", "evidence_span", "low_confidence", "source": "llm_re"}
        """
        if not entities or len(entities) < 2:
            return []

        ent_str_list = [f"'{e['entity']}' ({e['type']})" for e in entities]
        prompt = f"""Văn bản y tế: "{text}"
Danh sách thực thể trong câu: {", ".join(ent_str_list)}

Hãy trích xuất tất cả quan hệ hợp lệ giữa các thực thể trên dưới dạng JSON Array (tuân thủ nghiêm ngặt quy tắc không trích xuất quan hệ đồng xuất hiện giả):"""

        raw_triples = self.llm.generate_json(prompt, system_prompt=SYSTEM_PROMPT)
        if not isinstance(raw_triples, list):
            logger.warning("LLM RE returned invalid output format.")
            return []

        valid_triples = []
        entity_names = {e["entity"].lower(): e["entity"] for e in entities}
        text_lower = text.lower()

        for item in raw_triples:
            if not isinstance(item, dict):
                continue
            head = item.get("head", "").strip()
            rel = item.get("relation", "").strip().upper()
            tail = item.get("tail", "").strip()
            conf = float(item.get("confidence", 0.9))
            evidence = item.get("evidence_span", "").strip()

            if rel in VALID_RELATIONS and head and tail:
                # Align exact entity text spelling from extracted entities
                matched_head = entity_names.get(head.lower(), head)
                matched_tail = entity_names.get(tail.lower(), tail)

                # Validation step for confidence & evidence span
                is_low_conf = False
                if conf < 0.70:
                    is_low_conf = True
                elif not evidence:
                    is_low_conf = True
                else:
                    # Check if evidence span or key entity names exist in text
                    ev_clean = evidence.lower().replace("...", " ")
                    ev_words = [w for w in ev_clean.split() if len(w) > 2]
                    # If less than 50% of evidence words appear in original text, flag low confidence
                    matches = sum(1 for w in ev_words if w in text_lower)
                    if ev_words and (matches / len(ev_words)) < 0.5:
                        is_low_conf = True

                valid_triples.append({
                    "head": matched_head,
                    "relation": rel,
                    "tail": matched_tail,
                    "confidence": min(1.0, max(0.1, conf)),
                    "evidence_span": evidence,
                    "low_confidence": is_low_conf,
                    "source": "llm_re"
                })

        return valid_triples

if __name__ == "__main__":
    re_extractor = LLMRelationExtractor()
    sample_text = "Bệnh nhân Viêm loét dạ dày bị chống chỉ định dùng Ibuprofen. Bác sĩ kê Omeprazole 20mg."
    sample_entities = [
        {"entity": "Viêm loét dạ dày", "type": "DISEASE"},
        {"entity": "Ibuprofen", "type": "DRUG"},
        {"entity": "Omeprazole 20mg", "type": "DRUG"}
    ]
    res = re_extractor.extract_relations(sample_text, sample_entities)
    print("LLM RE Results:", json.dumps(res, ensure_ascii=False, indent=2))
