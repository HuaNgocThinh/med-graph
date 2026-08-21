"""
Script to merge symptom_v3_80.conll (80 sentences) into existing CoNLL dataset splits
(ner_train.conll, ner_dev.conll, ner_test.conll), verify exact block counts and blank lines,
and package the updated dataset into student_ner_dataset_v3.zip.
"""

import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "student_training"

SYMPTOM_FILE = DATA_DIR / "symptom_v3_80.conll"
TRAIN_FILE = DATA_DIR / "ner_train.conll"
DEV_FILE = DATA_DIR / "ner_dev.conll"
TEST_FILE = DATA_DIR / "ner_test.conll"
ZIP_OUTPUT = DATA_DIR / "student_ner_dataset_v3.zip"

def parse_blocks(file_path: Path):
    text = file_path.read_text(encoding="utf-8")
    blocks = [b.strip() for b in text.strip().split("\n\n") if b.strip()]
    return blocks

def append_blocks_to_file(file_path: Path, new_blocks: list) -> tuple:
    old_blocks = parse_blocks(file_path)
    old_count = len(old_blocks)

    # Format new content: join blocks with double newline and ensure trailing double newline
    new_content_str = "\n\n".join(new_blocks) + "\n\n"
    
    # Read existing content, ensure clean ending with \n\n
    existing_text = file_path.read_text(encoding="utf-8").strip()
    updated_text = existing_text + "\n\n" + new_content_str

    file_path.write_text(updated_text, encoding="utf-8")

    updated_blocks = parse_blocks(file_path)
    new_count = len(updated_blocks)
    
    return old_count, len(new_blocks), new_count

def main():
    print("=" * 70)
    print("DATA ENGINEER SCRIPT: MERGING SYMPTOM_V3_80.CONLL INTO DATASET SPLITS")
    print("=" * 70)

    # Step 1: Read symptom_v3_80.conll and confirm count = 80
    if not SYMPTOM_FILE.exists():
        raise FileNotFoundError(f"Missing file: {SYMPTOM_FILE}")

    symptom_blocks = parse_blocks(SYMPTOM_FILE)
    total_symptom_sents = len(symptom_blocks)
    print(f"Bước 1: Đã đọc file {SYMPTOM_FILE.name}")
    print(f"       ► Tổng số câu đọc được: {total_symptom_sents} câu (Yêu cầu: 80 câu)")

    if total_symptom_sents != 80:
        raise ValueError(f"Số lượng câu trong {SYMPTOM_FILE.name} là {total_symptom_sents}, khác 80!")

    # Step 2: Split 80 sentences into Train (55), Dev (10), Test (15)
    train_new = symptom_blocks[0:55]   # syn_v3_001 -> syn_v3_055
    dev_new = symptom_blocks[55:65]    # syn_v3_056 -> syn_v3_065
    test_new = symptom_blocks[65:80]   # syn_v3_066 -> syn_v3_080

    print("\nBước 2: Phân chia 80 câu thành 3 phần:")
    print(f"       ► Train: {len(train_new)} câu (syn_v3_001 -> syn_v3_055)")
    print(f"       ► Dev  : {len(dev_new)} câu (syn_v3_056 -> syn_v3_065)")
    print(f"       ► Test : {len(test_new)} câu (syn_v3_066 -> syn_v3_080)")

    # Step 3: Append to existing files
    print("\nBước 3: Nối dữ liệu vào các file CoNLL hiện có...")
    
    tr_old, tr_add, tr_new = append_blocks_to_file(TRAIN_FILE, train_new)
    print(f"       ✓ {TRAIN_FILE.name:<16}: {tr_old:>3} câu cũ + {tr_add:>2} câu mới ➔ TỔNG: {tr_new:>3} câu")

    dev_old, dev_add, dev_new_cnt = append_blocks_to_file(DEV_FILE, dev_new)
    print(f"       ✓ {DEV_FILE.name:<16}: {dev_old:>3} câu cũ + {dev_add:>2} câu mới ➔ TỔNG: {dev_new_cnt:>3} câu")

    te_old, te_add, te_new = append_blocks_to_file(TEST_FILE, test_new)
    print(f"       ✓ {TEST_FILE.name:<16}: {te_old:>3} câu cũ + {te_add:>2} câu mới ➔ TỔNG: {te_new:>3} câu")

    total_dataset = tr_new + dev_new_cnt + te_new
    print(f"\n       ► TỔNG CỘNG TOÀN BỘ DATASET NER SAU KHI GỘP: {total_dataset} câu")

    # Step 4: Zip updated files into student_ner_dataset_v3.zip
    print("\nBước 4: Nén cả 3 file CoNLL thành student_ner_dataset_v3.zip...")
    files_to_zip = [TRAIN_FILE, DEV_FILE, TEST_FILE]
    
    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zipf:
        for fpath in files_to_zip:
            zipf.write(fpath, arcname=fpath.name)
            size_kb = fpath.stat().st_size / 1024
            print(f"       + Đã nén: {fpath.name:<16} ({size_kb:.1f} KB)")

    zip_size_kb = ZIP_OUTPUT.stat().st_size / 1024
    print(f"\n✓ Đã tạo thành công gói Kaggle ZIP: {ZIP_OUTPUT}")
    print(f"  Dung lượng ZIP: {zip_size_kb:.1f} KB")

    print("\n" + "=" * 70)
    print("HOÀN THÀNH TẤT CẢ CÁC BƯỚC THÀNH CÔNG!")
    print("=" * 70)

if __name__ == "__main__":
    main()
