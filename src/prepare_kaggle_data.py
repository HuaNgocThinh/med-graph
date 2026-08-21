import json
import os
import random
import sys
from pathlib import Path
from pyvi import ViTokenizer

# 1. Khởi tạo đường dẫn và môi trường
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data"
OUTPUT_FILE = OUTPUT_DIR / "kaggle_train_augmented.py"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 2. Bước 1: Từ điển từ vựng Y khoa thô
RAW_DRUGS = [
    "Paracetamol",
    "Aspirin",
    "Ibuprofen",
    "Omeprazole",
    "Amoxicillin",
    "Metformin",
    "Atorvastatin",
    "Azithromycin",
    "Salbutamol",
    "Clopidogrel",
]

RAW_DISEASES = [
    "viêm phổi",
    "đái tháo đường",
    "cao huyết áp",
    "viêm loét dạ dày",
    "bệnh gút",
    "sốt xuất huyết",
    "trào ngược dạ dày",
    "nhồi máu cơ tim",
    "hen phế quản",
    "sỏi thận",
]

RAW_SYMPTOMS = [
    "ho khan",
    "đau đầu",
    "sốt cao",
    "chóng mặt",
    "buồn nôn",
    "khó thở",
    "tê bì chi",
    "tức ngực",
    "tiêu chảy",
    "đau bụng",
]

RAW_PROCEDURES = [
    "chụp X-quang",
    "nội soi",
    "xét nghiệm máu",
    "siêu âm",
    "khám lâm sàng",
    "điện tâm đồ",
    "chụp CT",
    "đo huyết áp",
    "thử máu",
    "mổ nội soi",
]


# 3. Bước 2: Tách từ chuẩn bằng PyVi cho Từ điển
def segment_vocab_list(vocab_list):
    return [ViTokenizer.tokenize(item) for item in vocab_list]


DRUGS = segment_vocab_list(RAW_DRUGS)
DISEASES = segment_vocab_list(RAW_DISEASES)
SYMPTOMS = segment_vocab_list(RAW_SYMPTOMS)
PROCEDURES = segment_vocab_list(RAW_PROCEDURES)

# 4. Bước 3: Định nghĩa Templates chuẩn hóa tiếng Việt kèm nhãn quan hệ RE
TEMPLATES = [
    # Nhãn TREATS
    {
        "template": "Bác sĩ chỉ định {DRUG} để điều trị {DISEASE}.",
        "relation": "TREATS",
        "e1_key": "DRUG",
        "e2_key": "DISEASE",
    },
    {
        "template": "Bệnh nhân dùng {DRUG} giúp kiểm soát hiệu quả bệnh {DISEASE}.",
        "relation": "TREATS",
        "e1_key": "DRUG",
        "e2_key": "DISEASE",
    },
    {
        "template": "{DRUG} được sử dụng phổ biến trong điều trị {DISEASE}.",
        "relation": "TREATS",
        "e1_key": "DRUG",
        "e2_key": "DISEASE",
    },
    # Nhãn CAUSES
    {
        "template": "Bệnh nhân có biểu hiện {SYMPTOM} do {DISEASE} gây ra.",
        "relation": "CAUSES",
        "e1_key": "SYMPTOM",
        "e2_key": "DISEASE",
    },
    {
        "template": "{DISEASE} thường dẫn đến triệu chứng {SYMPTOM} kéo dài.",
        "relation": "CAUSES",
        "e1_key": "DISEASE",
        "e2_key": "SYMPTOM",
    },
    {
        "template": "Triệu chứng {SYMPTOM} xuất hiện do bệnh nhân mắc {DISEASE}.",
        "relation": "CAUSES",
        "e1_key": "SYMPTOM",
        "e2_key": "DISEASE",
    },
    # Nhãn CONTRAINDICATED_FOR
    {
        "template": "Chống chỉ định dùng {DRUG} cho người bị {DISEASE}.",
        "relation": "CONTRAINDICATED_FOR",
        "e1_key": "DRUG",
        "e2_key": "DISEASE",
    },
    {
        "template": "Tuyệt đối không được dùng {DRUG} đối với bệnh nhân mắc {DISEASE}.",
        "relation": "CONTRAINDICATED_FOR",
        "e1_key": "DRUG",
        "e2_key": "DISEASE",
    },
    {
        "template": "{DRUG} chống chỉ định đối với bệnh nhân có tiền sử {DISEASE}.",
        "relation": "CONTRAINDICATED_FOR",
        "e1_key": "DRUG",
        "e2_key": "DISEASE",
    },
    # Nhãn HAS_SYMPTOM
    {
        "template": "Bệnh nhân mắc {DISEASE} kèm theo triệu chứng {SYMPTOM}.",
        "relation": "HAS_SYMPTOM",
        "e1_key": "DISEASE",
        "e2_key": "SYMPTOM",
    },
    {
        "template": "Ghi nhận dấu hiệu {SYMPTOM} ở người bệnh bị {DISEASE}.",
        "relation": "HAS_SYMPTOM",
        "e1_key": "SYMPTOM",
        "e2_key": "DISEASE",
    },
    # Nhãn PRESCRIBED_FOR
    {
        "template": "Bác sĩ kê đơn {DRUG} cho bệnh nhân chẩn đoán {DISEASE}.",
        "relation": "PRESCRIBED_FOR",
        "e1_key": "DRUG",
        "e2_key": "DISEASE",
    },
    {
        "template": "Kê đơn {DRUG} để điều trị cho trường hợp bị {DISEASE}.",
        "relation": "PRESCRIBED_FOR",
        "e1_key": "DRUG",
        "e2_key": "DISEASE",
    },
    # Nhãn PERFORMED_FOR
    {
        "template": "Bác sĩ chỉ định {PROCEDURE} để chẩn đoán bệnh {DISEASE}.",
        "relation": "PERFORMED_FOR",
        "e1_key": "PROCEDURE",
        "e2_key": "DISEASE",
    },
    {
        "template": "Thực hiện {PROCEDURE} cho bệnh nhân nghi ngờ mắc {DISEASE}.",
        "relation": "PERFORMED_FOR",
        "e1_key": "PROCEDURE",
        "e2_key": "DISEASE",
    },
]


def get_random_entity(entity_type):
    if entity_type == "DRUG":
        return random.choice(DRUGS), "DRUG"
    elif entity_type == "DISEASE":
        return random.choice(DISEASES), "DISEASE"
    elif entity_type == "SYMPTOM":
        return random.choice(SYMPTOMS), "SYMPTOM"
    elif entity_type == "PROCEDURE":
        return random.choice(PROCEDURES), "PROCEDURE"
    raise ValueError(f"Entity type không hợp lệ: {entity_type}")


def generate_augmented_dataset(num_samples: int = 200):
    print(f"🔄 Đang sinh {num_samples} câu dữ liệu huấn luyện tự động (Data Augmentation)...")
    dataset = []

    # Cố định random seed để tính lặp lại
    random.seed(42)

    for i in range(1, num_samples + 1):
        tmpl_config = random.choice(TEMPLATES)
        raw_tmpl = tmpl_config["template"]
        relation = tmpl_config["relation"]
        e1_key = tmpl_config["e1_key"]
        e2_key = tmpl_config["e2_key"]

        # Lấy 2 thực thể đã tách từ
        e1_word, e1_type = get_random_entity(e1_key)
        e2_word, e2_type = get_random_entity(e2_key)

        # Đảm bảo 2 thực thể không bị trùng nhau nếu cùng loại
        while e1_word == e2_word:
            e2_word, e2_type = get_random_entity(e2_key)

        # Đặt đúng key vào placeholder trong format
        format_kwargs = {e1_key: e1_word, e2_key: e2_word}
        raw_filled_text = raw_tmpl.format(**format_kwargs)

        # Tách từ toàn bộ câu bằng PyVi
        segmented_text = ViTokenizer.tokenize(raw_filled_text)

        sample = {
            "sample_id": f"aug_{i:03d}",
            "text": segmented_text,
            "entities": [
                {"word": e1_word, "type": e1_type},
                {"word": e2_word, "type": e2_type},
            ],
            "relation": relation,
        }
        dataset.append(sample)

    # Bước 6: Xuất file Python (.py) chứa biến TRAIN_DATA
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# File dữ liệu tự động sinh ra từ script Augmentation\n\n")
        f.write(f"TRAIN_DATA = {json.dumps(dataset, ensure_ascii=False, indent=4)}\n")

    print(f"✅ Đã sinh thành công {len(dataset)} câu dữ liệu huấn luyện tăng cường!")
    print(f"📁 Tệp lưu tại: {OUTPUT_FILE}\n")


if __name__ == "__main__":
    generate_augmented_dataset(200)
