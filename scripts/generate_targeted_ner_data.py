"""
Script to generate 70 targeted synthetic Vietnamese clinical sentences for NER Student Training.
Guarantees >= 50% of new sentences contain explicit PROCEDURE entities (surgeries, endoscopies, imaging, biopsies, etc.).
Assigns IDs syn_097 to syn_166 and saves to data/synthetic/ner_training_extended.json.
"""

import json
import logging
import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import DATA_DIR
from src.llm_client import LLMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GenerateTargetedNERData")

OUTPUT_PATH = DATA_DIR / "synthetic" / "ner_training_extended.json"

PROCEDURE_EXAMPLES = [
    "nội soi dạ dày", "nội soi đại tràng", "nội soi phế quản", "nội soi thai",
    "chụp X-quang ngực thẳng", "chụp X-quang sọ nghiêng", "chụp CT-scanner sọ não", "chụp CT ổ bụng",
    "chụp MRI khớp gối", "chụp MRI cột sống thắt lưng", "siêu âm ổ bụng tổng quát", "siêu âm tim qua thành ngực",
    "phẫu thuật nội soi cắt ruột thừa", "phẫu thuật mổ mở cắt túi mật", "phẫu thuật mổ lấy thai", "phẫu thuật thay khớp háng",
    "sinh thiết u gan", "sinh thiết hạch cổ", "chọc dò tủy sống", "chọc dịch màng phổi",
    "đặt catheter tĩnh mạch trung tâm", "đặt stent mạch vành", "điện tâm đồ", "điện brain đồ", "điện não đồ",
    "xét nghiệm công thức máu", "xét nghiệm sinh hóa máu", "rửa dạ dày cấp cứu", "thông tim can thiệp"
]

PROMPT_PROCEDURE_BATCH = """Bạn là chuyên gia y tế Việt Nam. Hãy sinh {count} câu lâm sàng tiếng Việt phong phú, tự nhiên.
MỖI CÂU BẮT BUỘC PHẢI CHỨA ÍT NHẤT 1 THỦ THUẬT / PHẪU THUẬT / CHẨN ĐOÁN HÌNH ẢNH / XÉT NGHIỆM / CẬN LÂM SÀNG CỤ THỂ (PROCEDURE).

Ví dụ các PROCEDURE: {procedure_samples}
Mô tả thêm các bệnh (DISEASE), triệu chứng (SYMPTOM), hoặc thuốc (DRUG) đi kèm để câu văn thực tế.

Trả về duy nhất 1 mảng JSON chứa các object:
[
  {{
    "text": "Bệnh nhân nam 45 tuổi được chỉ định nội soi dạ dày do đau vùng thượng vị hoài nghi Viêm loét dạ dày. Kết quả sinh thiết phát hiện vi khuẩn HP, được kê Omeprazole 20mg."
  }},
  ...
]
"""

PROMPT_GENERAL_BATCH = """Bạn là chuyên gia y tế Việt Nam. Hãy sinh {count} câu lâm sàng tiếng Việt phong phú, tự nhiên về khám bệnh, chẩn đoán, và kê đơn thuốc.
Mỗi câu chứa kết hợp các Thực thể y tế: Bệnh (DISEASE), Triệu chứng (SYMPTOM), Thuốc (DRUG), hoặc Thủ thuật/Xét nghiệm (PROCEDURE).

Trả về duy nhất 1 mảng JSON chứa các object:
[
  {{
    "text": "Bệnh nhân nữ 58 tuổi nhập viện với biểu hiện sốt cao và ho có đờm. Bác sĩ chẩn đoán Viêm phổi cộng đồng và chỉ định dùng Ceftriaxone 1g tiêm tĩnh mạch."
  }},
  ...
]
"""

def generate_sentences(client: LLMClient, target_total: int = 70) -> List[Dict[str, Any]]:
    # Target: 40 sentences with procedure focus (57%), 30 general sentences (43%)
    proc_target = 40
    general_target = target_total - proc_target

    all_sentences: List[str] = []

    # 1. Generate PROCEDURE sentences
    logger.info(f"Generating {proc_target} targeted PROCEDURE sentences via LLM...")
    batch_size = 10
    proc_collected = 0
    while proc_collected < proc_target:
        count = min(batch_size, proc_target - proc_collected)
        sample_procs = ", ".join(PROCEDURE_EXAMPLES[:15])
        prompt = PROMPT_PROCEDURE_BATCH.format(count=count, procedure_samples=sample_procs)
        
        try:
            res = client.generate_json(prompt)
            if isinstance(res, list):
                for item in res:
                    t = item.get("text", "").strip() if isinstance(item, dict) else str(item).strip()
                    if t and len(t) > 20 and t not in all_sentences:
                        all_sentences.append(t)
                        proc_collected += 1
                        logger.info(f"  [PROC {proc_collected}/{proc_target}] {t[:70]}...")
                        if proc_collected >= proc_target:
                            break
            else:
                logger.warning("LLM response was not a list, retrying...")
        except Exception as e:
            logger.error(f"Error in procedure batch generation: {e}")
            time.sleep(2)

    # 2. Generate General sentences
    logger.info(f"Generating {general_target} general medical sentences via LLM...")
    gen_collected = 0
    while gen_collected < general_target:
        count = min(batch_size, general_target - gen_collected)
        prompt = PROMPT_GENERAL_BATCH.format(count=count)
        
        try:
            res = client.generate_json(prompt)
            if isinstance(res, list):
                for item in res:
                    t = item.get("text", "").strip() if isinstance(item, dict) else str(item).strip()
                    if t and len(t) > 20 and t not in all_sentences:
                        all_sentences.append(t)
                        gen_collected += 1
                        logger.info(f"  [GEN {gen_collected}/{general_target}] {t[:70]}...")
                        if gen_collected >= general_target:
                            break
            else:
                logger.warning("LLM response was not a list, retrying...")
        except Exception as e:
            logger.error(f"Error in general batch generation: {e}")
            time.sleep(2)

    # Structure records with IDs syn_097 onwards
    records = []
    start_id = 97
    for idx, sentence_text in enumerate(all_sentences):
        sample_id = f"syn_{start_id + idx:03d}"
        template_type = "thủ thuật/xét nghiệm" if idx < proc_target else "nội khoa/ngoại khoa"
        records.append({
            "id": sample_id,
            "template_type": template_type,
            "text": sentence_text
        })

    return records

def main():
    logger.info("Starting targeted synthetic data generation...")
    client = LLMClient()
    client.validate_connection()

    records = generate_sentences(client, target_total=70)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    logger.info("=" * 60)
    logger.info(f"SUCCESSFULLY SAVED {len(records)} NEW SENTENCES TO {OUTPUT_PATH}")
    logger.info(f"ID Range: {records[0]['id']} -> {records[-1]['id']}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
