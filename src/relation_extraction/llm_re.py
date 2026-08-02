"""
LLM-Assisted Relation Extraction (RE) module for Vietnamese Medical Text.
Extracts clinical relation triples between identified entities using structured few-shot prompting.
Includes strict defensive checks and sentence-level proximity validation to prevent cross-sample entity contamination.
"""

import json
import logging
import re
from typing import List, Dict, Any
from src.llm_client import LLMClient
from src.entity_linking.entity_normalizer import normalize_entity_name, get_canonical_name
from src.relation_extraction.re_validator import validate_triple_sentence_distance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMRelationExtraction")

VALID_RELATIONS = {
    "TREATS",               # Thuốc điều trị triệu chứng cụ thể
    "PRESCRIBED_FOR",       # Thuốc được kê cho bệnh
    "CAUSES",               # Bệnh/Thuốc gây ra triệu chứng/biến chứng
    "HAS_SYMPTOM",          # Bệnh có triệu chứng
    "CONTRAINDICATED_FOR"   # Thuốc chống chỉ định với bệnh
}

SYSTEM_PROMPT = """Bạn là chuyên gia trích xuất quan hệ y tế (Medical Relation Extraction).
Nhiệm vụ của bạn là phân tích câu văn y tế và danh sách các thực thể đã xác định để rút ra các bộ ba quan hệ (triples).

QUY TẮC RÀNG BUỘC NGHIÊM NGẶT (RẤT QUAN TRỌNG):
1. TUYỆT ĐỐI CHỈ TRÍCH XUẤT quan hệ giữa các thực thể CÓ TRONG DANH SÁCH THỰC THỂ CỦA VĂN BẢN HIỆN TẠI.
2. NGHIÊM CẤM tự ý đưa các tên thuốc, tên bệnh từ ví dụ mẫu (như Metformin, Aspirin, Ibuprofen, Omeprazole, Losartan) hoặc từ tri thức bên ngoài vào nếu chúng KHÔNG CÓ trong câu văn được cung cấp.

QUY TẮC BẰNG CHỨNG TRỰC TIẾP (BẮT BUỘC):
1. Chỉ trích xuất quan hệ khi có bằng chứng trực tiếp TRONG CÙNG MỘT CÂU hoặc 2 CÂU LIÊN KỀ.
2. TUYỆT ĐỐI KHÔNG suy diễn hoặc liên kết các thực thể nằm ở các câu xa nhau trong tài liệu.
3. XỬ LÝ RIÊNG TỪNG CẶP, không áp dụng chung 1 loại quan hệ cho tất cả các thực thể trong cùng văn bản.

QUY TẮC PHÂN BỔ LOẠI QUAN HỆ BẮT BUỘC:
1. PRESCRIBED_FOR: DÙNG DUY NHẤT cho cặp (DRUG, DISEASE) — Thuốc được chỉ định/kê đơn để điều trị BỆNH.
2. TREATS: DÙNG DUY NHẤT cho cặp (DRUG, SYMPTOM) — Thuốc dùng để giảm/long/cắt TRIỆU CHỨNG cụ thể (VD: ho nhiều đờm, sốt, đau ngực).
3. HAS_SYMPTOM: DÙNG DUY NHẤT cho cặp (DISEASE, SYMPTOM) — Bệnh biểu hiện bằng triệu chứng.
4. CONTRAINDICATED_FOR: DÙNG DUY NHẤT cho cặp (DRUG, DISEASE) — Thuốc bị chống chỉ định đối với bệnh.
5. CAUSES: Dùng cho (DISEASE/DRUG, SYMPTOM/DISEASE) — Bệnh hoặc thuốc gây ra triệu chứng/tác dụng phụ/biến chứng.

QUY TẮC XỬ LÝ THỰC THỂ BỊ PHỦ ĐỊNH (NGHIÊM CẤM TẠO QUAN HỆ ĐỒNG XUẤT HIỆN GIẢ):
1. Khi một thực thể bệnh/triệu chứng bị PHỦ ĐỊNH trong văn bản (VD: "không thấy dấu hiệu Viêm phổi", "chưa ghi nhận Bệnh Gút", "không bị sốt"), KHÔNG ĐƯỢC tự ý liên kết các thuốc kê đơn trong bài với thực thể bị phủ định đó.
2. TUYỆT ĐỐI KHÔNG tạo quan hệ (DRUG, PRESCRIBED_FOR, DISEASE_BỊ_PHỦ_ĐỊNH) nếu bệnh đó không phải là chỉ định của thuốc.
3. Thực thể bị phủ định CHỈ tạo quan hệ khi văn bản trực tiếp khẳng định mối quan hệ với thực thể đó.

VÍ DỤ MẪU (CHỈ ĐỂ THAM KHẢO CÚ PHÁP, KHÔNG LẤY TÊN THỰC THỂ Ở ĐÂY CHO CÂU THỰC TẾ):
Ví dụ 1:
Văn bản: "Bệnh nhân Viêm phế quản cấp, ho nhiều đờm. Kê Amoxicillin 500mg và Bromhexine 8mg để long đờm."
Thực thể: 'Viêm phế quản cấp' (DISEASE), 'ho nhiều đờm' (SYMPTOM), 'Amoxicillin 500mg' (DRUG), 'Bromhexine 8mg' (DRUG)
Output:
[
  {"head": "Amoxicillin 500mg", "relation": "PRESCRIBED_FOR", "tail": "Viêm phế quản cấp", "confidence": 0.95, "evidence_span": "Viêm phế quản cấp ... Kê Amoxicillin 500mg"},
  {"head": "Bromhexine 8mg", "relation": "TREATS", "tail": "ho nhiều đờm", "confidence": 0.92, "evidence_span": "Bromhexine 8mg để long đờm"}
]

Ví dụ 2 (Chống đồng xuất hiện giả với thực thể phủ định):
Văn bản: "Bệnh nhân Đái tháo đường týp 2. Khám không thấy dấu hiệu Viêm phổi. Kê Metformin 500mg."
Thực thể: 'Đái tháo đường týp 2' (DISEASE), 'Viêm phổi' (DISEASE), 'Metformin 500mg' (DRUG)
Output:
[
  {"head": "Metformin 500mg", "relation": "PRESCRIBED_FOR", "tail": "Đái tháo đường týp 2", "confidence": 0.95, "evidence_span": "Đái tháo đường týp 2 ... Kê Metformin 500mg"}
]
(TUYỆT ĐỐI KHÔNG tạo bộ ba (Metformin 500mg, PRESCRIBED_FOR, Viêm phổi) vì Viêm phổi bị phủ định "không thấy dấu hiệu").

Ví dụ 3 (Chống đồng xuất hiện giả với bệnh tiền sử phủ định):
Văn bản: "Bệnh nhân Cơn đau thắt ngực. Tiền sử chưa ghi nhận Bệnh Gút. Kê Aspirin 81mg."
Thực thể: 'Cơn đau thắt ngực' (DISEASE), 'Bệnh Gút' (DISEASE), 'Aspirin 81mg' (DRUG)
Output:
[
  {"head": "Aspirin 81mg", "relation": "PRESCRIBED_FOR", "tail": "Cơn đau thắt ngực", "confidence": 0.95, "evidence_span": "Cơn đau thắt ngực ... Kê Aspirin 81mg"}
]
(TUYỆT ĐỐI KHÔNG tạo bộ ba (Aspirin 81mg, PRESCRIBED_FOR, Bệnh Gút) vì Bệnh Gút bị phủ định "chưa ghi nhận").

Yêu cầu đầu ra: Trả về một JSON Array duy nhất không chứa lời giải thích:
[
  {"head": "...", "relation": "...", "tail": "...", "confidence": 0.95, "evidence_span": "..."}
]
"""

class LLMRelationExtractor:
    """Extracts clinical relation triples using LLM few-shot prompting with strict defensive checks."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()

    def extract_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts relation triples between entities in the input text.
        Applies strict pre-validation and post-validation defensive checks.
        """
        if not entities or len(entities) < 2:
            return []

        text_lower = text.lower()

        # DEFENSIVE CHECK 1 (Pre-validation): Ensure all entities passed to prompt exist in raw text
        valid_sample_entities = []
        for e in entities:
            ent_str = e.get("entity", "").strip()
            if ent_str and ent_str.lower() in text_lower:
                valid_sample_entities.append(e)
            else:
                logger.warning(f"⚠️ [DEFENSIVE PRE-CHECK] Dropped entity '{ent_str}' because it is NOT present in sample raw text.")

        if len(valid_sample_entities) < 2:
            logger.info("Fewer than 2 valid entities found in raw text after defensive check. Skipping RE.")
            return []

        ent_str_list = [f"'{normalize_entity_name(e['entity'])}' ({e['type']})" for e in valid_sample_entities]
        logger.info(f"🔍 [DEFENSIVE PRE-CHECK OK] Prompt Entity Candidate List ({len(valid_sample_entities)}): {[e['entity'] for e in valid_sample_entities]}")

        prompt = f"""Văn bản y tế: "{text}"
Danh sách thực thể ĐÃ XÁC ĐỊNH trong câu: {", ".join(ent_str_list)}

Hãy trích xuất tất cả quan hệ hợp lệ giữa các thực thể trên dưới dạng JSON Array (TUYỆT ĐỐI CHỈ DÙNG THỰC THỂ TRONG DANH SÁCH TRÊN):"""

        raw_triples = self.llm.generate_json(prompt, system_prompt=SYSTEM_PROMPT)
        if not isinstance(raw_triples, list):
            logger.warning("LLM RE returned invalid output format.")
            return []

        valid_triples = []
        sample_entity_map = {e["entity"].lower(): e["entity"] for e in valid_sample_entities}
        sample_entity_norm_map = {normalize_entity_name(e["entity"]).lower(): e["entity"] for e in valid_sample_entities}

        for item in raw_triples:
            if not isinstance(item, dict):
                continue
            head = item.get("head", "").strip()
            rel = item.get("relation", "").strip().upper()
            tail = item.get("tail", "").strip()
            conf = float(item.get("confidence", 0.9))
            evidence = item.get("evidence_span", "").strip()

            if rel in VALID_RELATIONS and head and tail:
                head_lower = head.lower()
                tail_lower = tail.lower()
                head_norm_lower = normalize_entity_name(head).lower()
                tail_norm_lower = normalize_entity_name(tail).lower()

                # DEFENSIVE CHECK 2 (Post-validation): Strict exact matching against sample's entity list
                matched_head = sample_entity_map.get(head_lower) or sample_entity_norm_map.get(head_norm_lower)
                matched_tail = sample_entity_map.get(tail_lower) or sample_entity_norm_map.get(tail_norm_lower)

                if not matched_head or not matched_tail:
                    logger.error(f"❌ [DEFENSIVE POST-CHECK REJECTED] Rejected hallucinated/unmatched entity triple: ({head} -[{rel}]-> {tail}) for text: '{text[:60]}...'")
                    continue

                if matched_head.lower() == matched_tail.lower():
                    continue

                # Sentence-level distance validation
                val_res = validate_triple_sentence_distance(text, matched_head, matched_tail)
                
                is_low_conf = False
                if conf < 0.70 or not evidence or val_res["review_required"]:
                    is_low_conf = True

                valid_triples.append({
                    "head": get_canonical_name(matched_head),
                    "relation": rel,
                    "tail": get_canonical_name(matched_tail),
                    "confidence": min(1.0, max(0.1, conf)),
                    "evidence_span": evidence,
                    "low_confidence": is_low_conf,
                    "validation_status": val_res["status"],
                    "sentence_distance": val_res["sentence_distance"],
                    "source": "llm_re"
                })

        return valid_triples

if __name__ == "__main__":
    re_extractor = LLMRelationExtractor()
    sample_text = "Bệnh nhân Viêm phế quản cấp, ho nhiều đờm. Kê Amoxicillin 500mg và Bromhexine 8mg."
    sample_entities = [
        {"entity": "Viêm phế quản cấp", "type": "DISEASE"},
        {"entity": "ho nhiều đờm", "type": "SYMPTOM"},
        {"entity": "Amoxicillin 500mg", "type": "DRUG"},
        {"entity": "Bromhexine 8mg", "type": "DRUG"}
    ]
    res = re_extractor.extract_relations(sample_text, sample_entities)
    print("LLM RE Results:", json.dumps(res, ensure_ascii=False, indent=2))
