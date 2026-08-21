"""
Script to generate 80 clinical Vietnamese sentences focused on complex, multi-word SYMPTOM entities,
and format them into strict CoNLL-U format with IDs syn_v3_001 to syn_v3_080.
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import DATA_DIR
from src.llm_client import LLMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GenerateSymptomV3CoNLL")

OUTPUT_CONLL_PATH = DATA_DIR / "student_training" / "symptom_v3_80.conll"

COMPLEX_SYMPTOM_SEEDS = [
    "đau nhức mỏi toàn thân", "cảm giác nóng rát vùng thượng vị", "đau quặn bụng từng cơn",
    "ho khan kéo dài về đêm", "tiểu buốt tiểu rắt", "tức ngực trái lan ra sau lưng",
    "khó thở khi nằm phẳng", "tê bì hai chi dưới", "hoa mắt chóng mặt xây sẩm mặt mày",
    "nổi mẩn đỏ ngứa ngáy khắp người", "ợ chua trào ngược dịch dạ dày", "sốt cao rét run từng cơn",
    "ăn uống kém sụt cân nhanh chóng", "sưng đau nhức các khớp ngón tay", "đau đầu dữ dội như búa bổ",
    "buồn nôn nôn ra dịch mật vàng", "khó nuốt nghẹn cổ họng khi ăn", "tiểu đêm nhiều lần khoảng 4-5 lần",
    "đau tức hạ sườn phải lan ra sau lưng", "hồi hộp đánh trống ngực dồn dập", "khàn tiếng kéo dài trên hai tuần",
    "chướng bụng đầy hơi khó tiêu", "ngứa cộm xốn hai mắt", "co thắt cơ tay chân từng đợt",
    "tê cứng khớp gối buổi sáng", "rối loạn giấc ngủ trằn trọc hàng đêm", "chảy máu cam hoài nghi vỡ mạch",
    "đau nhức nhối hốc mắt", "xuất hiện vết tím tái dưới da", "phù mềm hai cẳng chân"
]

BATCH_PROMPT_TEMPLATE = """Bạn là Chuyên gia Kỹ thuật Dữ liệu Y tế (Medical Data Annotator).
Hãy tạo ra {count} câu tiếng Việt mô tả bệnh án, quá trình khám lâm sàng, hoặc lời kể của bệnh nhân.

YÊU CẦU BẮT BUỘC:
1. Trọng tâm tuyệt đối vào Triệu chứng (SYMPTOM): 100% các câu ĐỀU PHẢI chứa ít nhất 2 đến 3 cụm từ chỉ triệu chứng bệnh.
2. Độ phức tạp của thực thể: Cố tình tạo các cụm triệu chứng DÀI (mô tả tính chất/mức độ/vị trí).
   - KHÔNG dùng thực thể ngắn 1 từ như "đau", "sốt", "ho".
   - BẮT BUỘC DÙNG các cụm triệu chứng dài 3-7 từ (Ví dụ: "đau nhức mỏi toàn thân", "cảm giác nóng rát vùng thượng vị", "đau quặn bụng từng cơn", "ho khan kéo dài về đêm", "tiểu buốt tiểu rắt", "tức ngực trái lan ra sau lưng", "khó thở khi nằm phẳng", "tê bì hai chi dưới", "hoa mắt chóng mặt xây sẩm mặt mày", "sốt cao rét run từng cơn", "ợ chua trào ngược dịch dạ dày", "sưng đau nhức các khớp ngón tay", "buồn nôn nôn ra dịch mật vàng", "khó nuốt nghẹn cổ họng khi ăn"...).
3. Ngoài SYMPTOM, câu có thể chứa các thực thể khác nếu tự nhiên: DISEASE (Bệnh), DRUG (Thuốc), PROCEDURE (Thủ thuật/Xét nghiệm).

Trả về duy nhất 1 mảng JSON chứa các object có cấu trúc:
[
  {{
    "text": "Bệnh nhân nam 54 tuổi nhập viện vì cảm giác nóng rát vùng thượng vị kèm đau quặn bụng từng cơn kéo dài 3 ngày.",
    "entities": [
      {{"text": "cảm giác nóng rát vùng thượng vị", "label": "SYMPTOM"}},
      {{"text": "đau quặn bụng từng cơn", "label": "SYMPTOM"}}
    ]
  }},
  ...
]
"""

def tokenize_words(text: str) -> List[Tuple[str, int, int]]:
    tokens = []
    for match in re.finditer(r'\w+|[^\w\s]', text, re.UNICODE):
        token_str = match.group(0)
        start, end = match.span()
        tokens.append((token_str, start, end))
    return tokens

def build_bio_conll_sample(sample_id: str, text: str, entities: List[Dict[str, Any]]) -> str:
    tokens = tokenize_words(text)
    bio_tags = ["O"] * len(tokens)

    # Find exact character spans in text for entities
    located_entities = []
    for ent in entities:
        etxt = ent["text"].strip()
        label = ent["label"].upper()
        
        # Validate label
        if label not in ("DISEASE", "DRUG", "PROCEDURE", "SYMPTOM"):
            continue
            
        start_idx = text.find(etxt)
        if start_idx != -1:
            located_entities.append({
                "text": etxt,
                "label": label,
                "start": start_idx,
                "end": start_idx + len(etxt)
            })

    # Sort by start index
    located_entities.sort(key=lambda x: (x["start"], -len(x["text"])))

    # Assign BIO tags token-by-token
    for ent in located_entities:
        label = ent["label"]
        estart = ent["start"]
        eend = ent["end"]

        overlapping = []
        for idx, (tstr, tstart, tend) in enumerate(tokens):
            if max(tstart, estart) < min(tend, eend):
                overlapping.append(idx)

        if overlapping:
            # Check if already tagged to avoid overlap collision
            if bio_tags[overlapping[0]] == "O":
                bio_tags[overlapping[0]] = f"B-{label}"
                for idx in overlapping[1:]:
                    bio_tags[idx] = f"I-{label}"

    lines = [f"# id = {sample_id}", f"# text = {text}"]
    for (tok, _, _), tag in zip(tokens, bio_tags):
        lines.append(f"{tok}\t{tag}")
    lines.append("")
    return "\n".join(lines)

def generate_80_samples() -> List[Dict[str, Any]]:
    client = LLMClient()
    client.validate_connection()

    all_samples = []
    seen_texts = set()
    target_total = 80
    batch_size = 10

    logger.info("Generating 80 complex SYMPTOM medical sentences...")

    while len(all_samples) < target_total:
        count = min(batch_size, target_total - len(all_samples))
        prompt = BATCH_PROMPT_TEMPLATE.format(count=count)

        try:
            res = client.generate_json(prompt)
            if isinstance(res, list):
                for item in res:
                    if not isinstance(item, dict):
                        continue
                    text = item.get("text", "").strip()
                    ents = item.get("entities", [])
                    
                    if not text or text in seen_texts or len(text) < 25:
                        continue
                        
                    # Filter: Must contain at least 2 SYMPTOM entities with length >= 2 words
                    symptom_ents = [
                        e for e in ents 
                        if e.get("label", "").upper() == "SYMPTOM" and len(e.get("text", "").split()) >= 2
                    ]
                    
                    if len(symptom_ents) >= 2:
                        seen_texts.add(text)
                        all_samples.append({
                            "text": text,
                            "entities": ents
                        })
                        logger.info(f"  [{len(all_samples)}/{target_total}] Added: {text[:65]}... ({len(symptom_ents)} long symptoms)")
                        if len(all_samples) >= target_total:
                            break
            else:
                logger.warning("LLM response was not a list, retrying...")
        except Exception as e:
            logger.error(f"Generation batch error: {e}")

    return all_samples

def main():
    samples = generate_80_samples()
    
    conll_blocks = []
    for idx, sample in enumerate(samples, 1):
        sample_id = f"syn_v3_{idx:03d}"
        conll_block = build_bio_conll_sample(sample_id, sample["text"], sample["entities"])
        conll_blocks.append(conll_block)

    full_conll_content = "\n".join(conll_blocks)

    OUTPUT_CONLL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_CONLL_PATH, "w", encoding="utf-8") as f:
        f.write(full_conll_content)

    logger.info("=" * 70)
    logger.info(f"SUCCESSFULLY GENERATED AND SAVED 80 CoNLL-U SENTENCES TO:")
    logger.info(f"  {OUTPUT_CONLL_PATH}")
    logger.info("=" * 70)

if __name__ == "__main__":
    main()
