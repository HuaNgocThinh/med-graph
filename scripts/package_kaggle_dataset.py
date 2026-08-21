"""
Script to package updated CoNLL files into a ZIP file for Kaggle Dataset Version 2 upload.
"""

import zipfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "student_training"
ZIP_OUTPUT = DATA_DIR / "student_ner_dataset_v2.zip"

FILES_TO_PACK = [
    "ner_train.conll",
    "ner_dev.conll",
    "ner_test.conll",
    "ner_pseudo_labels.json"
]

def main():
    print("=" * 60)
    print("BƯỚC 4: ĐÓNG GÓI DATASET KAGGLE (STUDENT-TRAINING V2)")
    print("=" * 60)

    missing = [f for f in FILES_TO_PACK if not (DATA_DIR / f).exists()]
    if missing:
        print(f"Lỗi: Không tìm thấy các file sau trong {DATA_DIR}: {missing}")
        return

    with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zipf:
        for fname in FILES_TO_PACK:
            fpath = DATA_DIR / fname
            zipf.write(fpath, arcname=fname)
            size_kb = fpath.stat().st_size / 1024
            print(f"  - Đã thêm: {fname:<22} ({size_kb:.1f} KB)")

    zip_size_kb = ZIP_OUTPUT.stat().st_size / 1024
    print(f"\n✓ Đã tạo thành công file nén Kaggle: {ZIP_OUTPUT}")
    print(f"  Dung lượng gói ZIP: {zip_size_kb:.1f} KB")
    print("=" * 60)

if __name__ == "__main__":
    main()
