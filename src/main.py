import json
import os
import sys
import time
from pathlib import Path

# Đảm bảo import được các module trong thư mục src bất kể vị trí chạy script
CURRENT_DIR = Path(__file__).resolve().parent
BASE_DIR = CURRENT_DIR.parent

if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from predict import extract_medical_info
from graph_builder import MedGraphBuilder

# Cấu hình đường dẫn dữ liệu
DATA_FILE_PATHS = [
    BASE_DIR / "data" / "annotated" / "test_set.json",
    BASE_DIR / "test_set.json",
]


def load_data(file_path: Path) -> list:
    """
    Đọc dữ liệu từ file JSON linh hoạt (hỗ trợ cả danh sách chuỗi hoặc danh sách dict).
    Trả về danh sách các câu văn bản (list of strings).
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu tại: {file_path}")

    print(f"📖 Đang đọc dữ liệu từ file: {file_path.name}...")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                texts.append(item.strip())
            elif isinstance(item, dict) and "text" in item:
                texts.append(str(item["text"]).strip())

    print(f"✅ Đã đọc thành công {len(texts)} câu từ file dữ liệu.\n")
    return texts


def process_batch(texts: list):
    """
    Xử lý hàng loạt (Batch Processing) trích xuất tri thức và nạp lên Neo4j.
    Được thiết kế để tự bảo vệ, chịu lỗi và không làm hỏng (crash) hệ thống khi xảy ra sự cố.
    """
    # Khởi tạo kết nối Neo4j
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    PASSWORD = os.getenv("NEO4J_PASSWORD", "medgraph_secret_password")

    builder = MedGraphBuilder(URI, USER, PASSWORD)
    success_count = 0
    skipped_count = 0
    start_time = time.time()

    print("🚀 BẮT ĐẦU CHẠY LUỒNG PIPELINE XỬ LÝ HÀNG LOẠT (BATCH PROCESSING)...\n")

    try:
        for idx, text in enumerate(texts, 1):
            # Bỏ qua các câu quá ngắn (dưới 10 ký tự)
            if not text or len(text) < 10:
                skipped_count += 1
                continue

            print(f"[{idx}/{len(texts)}] Đang xử lý: '{text[:60]}...'")

            # Bọc khối try-except riêng cho từng câu để chống crash toàn bộ batch
            try:
                result = extract_medical_info(text)

                # Kiểm tra nếu phát hiện quan hệ hợp lệ
                if (
                    result
                    and result.get("relation")
                    and result["relation"] != "NONE"
                    and result.get("entity_1")
                    and result.get("entity_2")
                ):
                    e1_name = result["entity_1"]["text"]
                    e1_type = result["entity_1"]["type"]
                    e2_name = result["entity_2"]["text"]
                    e2_type = result["entity_2"]["type"]
                    relation = result["relation"]

                    # Đẩy bộ ba tri thức lên Đồ thị Neo4j
                    builder.add_triplet(
                        e1_name, e1_type, relation, e2_name, e2_type
                    )
                    success_count += 1
                    print(
                        f"   🎉 Đã đẩy Triplet: ({e1_name}:{e1_type}) -[{relation}]-> ({e2_name}:{e2_type})"
                    )
                else:
                    print("   ℹ️ Bỏ qua (Không phát hiện quan hệ hợp lệ hoặc không đủ 2 thực thể).")

            except Exception as e:
                print(f"   ⚠️ Xảy ra lỗi khi xử lý câu {idx}: {e}. Đang tiếp tục câu tiếp theo...")

    finally:
        builder.close()
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 70)
        print("📊 BÁO CÁO TỔNG KẾT XỬ LÝ HÀNG LOẠT (BATCH PROCESSING REPORT)")
        print("=" * 70)
        print(f"⏱️ Tổng thời gian thực thi    : {elapsed_time:.2f} giây")
        print(f"📝 Tổng số câu đã quét        : {len(texts)}")
        print(f"⏭️ Số câu bị bỏ qua (Quá ngắn): {skipped_count}")
        print(f"✅ Số Triplet đẩy thành công  : {success_count}")
        print("=" * 70 + "\n")


if __name__ == "__main__":
    # Tìm file dữ liệu test_set.json trong dự án
    target_file = None
    for path in DATA_FILE_PATHS:
        if path.exists():
            target_file = path
            break

    if not target_file:
        print(
            f"❌ Không tìm thấy file test_set.json tại các vị trí mặc định."
        )
        sys.exit(1)

    # Đọc dữ liệu
    all_texts = load_data(target_file)

    # Lấy 50 câu đầu tiên để test xử lý hàng loạt cho nhanh
    batch_sample = all_texts[:50]
    process_batch(batch_sample)
