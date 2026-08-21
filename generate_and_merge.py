import os
import sys
import json
import time
import logging
from pathlib import Path
from pyvi import ViTokenizer

# 1. Khởi tạo đường dẫn dự án
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.llm_client import LLMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("GenerateAndMerge")

OLD_DATA_FILE = BASE_DIR / "data" / "kaggle_train_augmented.py"
NEW_DATA_FILE = BASE_DIR / "data" / "kaggle_train_900.py"


BATCH_SIZE = 50
TARGET_NEW_COUNT = 500


def load_existing_data() -> list:
    """
    Đọc và trích xuất danh sách câu dữ liệu hiện tại từ kaggle_train_augmented.py
    """
    if not OLD_DATA_FILE.exists():
        logger.warning(f"Không tìm thấy file cũ {OLD_DATA_FILE}. Khởi tạo mảng rỗng.")
        return []
    
    try:
        from data.kaggle_train_augmented import TRAIN_DATA
        logger.info(f"✅ Đã đọc thành công {len(TRAIN_DATA)} câu từ kaggle_train_augmented.py")
        return TRAIN_DATA
    except Exception as e:
        logger.error(f"Lỗi khi import TRAIN_DATA từ {OLD_DATA_FILE}: {e}")
        return []


def build_system_prompt() -> str:
    return """Bạn là Chuyên gia Data Engineer Y tế tiếng Việt.
Nhiệm vụ của bạn là sinh ra các câu bệnh án tiếng Việt chuẩn với cấu trúc ngữ pháp phức tạp và nhãn NER/RE tương ứng.

YÊU CẦU NGÔN NGỮ VÀ CÚ PHÁP:
- BẮT BUỘC dùng các cấu trúc câu phức, câu đảo, mệnh đề nguyên nhân - kết quả, mục đích, điều kiện.
- Dùng đan xen các từ nối: "nhằm chẩn đoán", "do nghi ngờ", "tuyệt đối chống chỉ định", "có chỉ định khẩn cấp", "nhập viện trong tình trạng", "kê đơn phối hợp".
- Rải đều các chuyên khoa: Tim mạch, Hô hấp, Tiêu hóa, Cơ xương khớp, Thần kinh, Nội tiết, Sản phụ khoa, Da liễu, Nhãn khoa.

QUY TẮC NHÃN:
- Nhãn NER (chỉ chọn từ 4 loại): DISEASE, SYMPTOM, DRUG, PROCEDURE.
- Nhãn RE (chỉ chọn từ 7 loại): CAUSES, CONTRAINDICATED_FOR, HAS_SYMPTOM, PERFORMED_FOR, PRESCRIBED_FOR, TREATS, NONE.

ĐỊNH DẠNG ĐẦU RA BẮT BUỘC:
Trả về đúng một JSON Array gồm các object có cấu trúc:
[
  {
    "raw_text": "Chống chỉ định dùng Ibuprofen 400mg khi bệnh nhân có tiền sử viêm loét dạ dày.",
    "entity_1": {"word": "Ibuprofen 400mg", "type": "DRUG"},
    "entity_2": {"word": "viêm loét dạ dày", "type": "DISEASE"},
    "relation": "CONTRAINDICATED_FOR"
  }
]
CHỈ TRẢ VỀ CHUỖI JSON ARRAY THUẦN, KHÔNG BỌC TRONG THẺ MARKDOWN KHI KHÔNG CẦN THIẾT.
"""


def generate_batch_from_llm(llm: LLMClient, count: int, batch_idx: int) -> list:
    """
    Gọi LLM API sinh một batch gồm `count` câu y tế chuẩn.
    """
    prompt = f"Hãy sinh chính xác {count} mẫu dữ liệu y tế tiếng Việt mới tuân thủ nghiêm ngặt yêu cầu trên."
    sys_prompt = build_system_prompt()
    
    logger.info(f"⏳ [Batch {batch_idx}] Đang gọi LLM API sinh {count} câu...")
    raw_response = llm.generate(prompt=prompt, system_prompt=sys_prompt)
    
    # Parse JSON từ response của LLM
    clean_resp = raw_response.strip()
    if clean_resp.startswith("```json"):
        clean_resp = clean_resp[7:]
    if clean_resp.startswith("```"):
        clean_resp = clean_resp[3:]
    if clean_resp.endswith("```"):
        clean_resp = clean_resp[:-3]
    clean_resp = clean_resp.strip()
    
    try:
        items = json.loads(clean_resp)
        if isinstance(items, list):
            logger.info(f"✅ [Batch {batch_idx}] Parse thành công {len(items)} mẫu từ LLM.")
            return items
        else:
            logger.warning(f"⚠️ [Batch {batch_idx}] Kết quả từ LLM không phải JSON List.")
            return []
    except Exception as e:
        logger.error(f"❌ [Batch {batch_idx}] Lỗi parse JSON từ LLM response: {e}")
        return []


def format_and_segment_item(item: dict, sample_id: str) -> dict:
    """
    Chuẩn hóa và đồng bộ câu văn sinh ra từ LLM bằng PyVi Word Segmentation,
    khớp 100% với cấu trúc mã nguồn của kaggle_train_augmented.py.
    """
    raw_text = item.get("raw_text", "").strip()
    e1 = item.get("entity_1", {})
    e2 = item.get("entity_2", {})
    relation = item.get("relation", "NONE")

    # Phân tách từ bằng PyVi cho câu và cho từng thực thể
    seg_text = ViTokenizer.tokenize(raw_text)
    seg_e1_word = ViTokenizer.tokenize(e1.get("word", "").strip())
    seg_e2_word = ViTokenizer.tokenize(e2.get("word", "").strip())

    return {
        "sample_id": sample_id,
        "text": seg_text,
        "entities": [
            {"word": seg_e1_word, "type": e1.get("type", "O")},
            {"word": seg_e2_word, "type": e2.get("type", "O")},
        ],
        "relation": relation,
    }


def main():
    logger.info("🚀 ĐANG KHỞI CHẠY SCRIPT TỰ ĐỘNG SINH VÀ GỘP DỮ LIỆU (GENERATE_AND_MERGE)...")

    # 1. Đọc dữ liệu cũ
    existing_data = load_existing_data()
    start_id_num = len(existing_data) + 1
    
    llm = LLMClient()
    new_generated_items = []
    
    num_batches = (TARGET_NEW_COUNT + BATCH_SIZE - 1) // BATCH_SIZE
    
    # 2. Sinh dữ liệu theo Batch
    for b in range(1, num_batches + 1):
        items_to_gen = min(BATCH_SIZE, TARGET_NEW_COUNT - len(new_generated_items))
        if items_to_gen <= 0:
            break
            
        raw_items = generate_batch_from_llm(llm, items_to_gen, b)
        
        for item in raw_items:
            current_id = f"aug_{len(existing_data) + len(new_generated_items) + 1:03d}"
            formatted_item = format_and_segment_item(item, current_id)
            new_generated_items.append(formatted_item)
            
        logger.info(f"📈 Tiến độ tổng: Đã sinh {len(new_generated_items)}/{TARGET_NEW_COUNT} câu mới.")
        time.sleep(1) # Tránh Rate Limit API

    # 3. Gộp 400 câu cũ và 500 câu mới
    merged_dataset = existing_data + new_generated_items
    logger.info(f"🎉 Tổng cộng dữ liệu sau gộp: {len(merged_dataset)} câu.")

    # 4. Xuất file kaggle_train_900.py
    logger.info(f"💾 Đang ghi toàn bộ dữ liệu ra file: {NEW_DATA_FILE}...")
    with open(NEW_DATA_FILE, "w", encoding="utf-8") as f:
        f.write("# File dữ liệu tự động sinh và gộp (kaggle_train_900.py)\n")
        f.write(f"# Tổng số mẫu: {len(merged_dataset)} câu (Tự động sinh từ LLM & PyVi Word Segmentation)\n\n")
        f.write(f"TRAIN_DATA = {json.dumps(merged_dataset, ensure_ascii=False, indent=4)}\n")

    logger.info(f"✅ THÀNH CÔNG! Đã tạo file {NEW_DATA_FILE.name} chứa {len(merged_dataset)} câu dữ liệu huấn luyện!")


if __name__ == "__main__":
    main()
