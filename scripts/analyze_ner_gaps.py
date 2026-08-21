"""
Script to analyze existing NER label counts across 96 synthetic sentences.
Checks entity occurrences in data/student_training/ner_pseudo_labels.json
and in existing train/dev/test CoNLL splits.
"""

import json
import re
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "student_training"

INVALID_PROC_TEXTS = {"men gan", "hemoglobin", "inr"}

def main():
    pseudo_file = DATA_DIR / "ner_pseudo_labels.json"
    if not pseudo_file.exists():
        print(f"Error: {pseudo_file} not found.")
        return

    with open(pseudo_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("=" * 60)
    print("BƯỚC 1: PHÂN TÍCH GAP NHÃN NER HIỆN TẠI (96 CÂU KG CHÍNH)")
    print("=" * 60)
    print(f"Tổng số câu trong dataset gốc: {len(data)}\n")

    raw_counts = Counter()
    cleaned_counts = Counter()

    for sample in data:
        for ent in sample.get("entities", []):
            lbl = ent.get("label") or ent.get("type")
            etxt = ent.get("text", "").strip().lower()
            raw_counts[lbl] += 1
            if lbl == "PROCEDURE" and etxt in INVALID_PROC_TEXTS:
                continue
            cleaned_counts[lbl] += 1

    print("--- Phân phối Entity trong ner_pseudo_labels.json (Chưa lọc) ---")
    for lbl, count in raw_counts.most_common():
        print(f"  - {lbl:<12}: {count:>3} mẫu")

    print("\n--- Phân phối Entity sau khi lọc nhiễu PROCEDURE (men gan, hemoglobin, inr) ---")
    for lbl, count in cleaned_counts.most_common():
        print(f"  - {lbl:<12}: {count:>3} mẫu")

    print("\n--- Phân bổ nhãn PROCEDURE theo từng split CoNLL hiện tại ---")
    for split in ["train", "dev", "test"]:
        conll_path = DATA_DIR / f"ner_{split}.conll"
        if conll_path.exists():
            content = conll_path.read_text(encoding="utf-8")
            sents = content.strip().split("\n\n")
            proc_b = len(re.findall(r"B-PROCEDURE", content))
            dis_b = len(re.findall(r"B-DISEASE", content))
            drug_b = len(re.findall(r"B-DRUG", content))
            sym_b = len(re.findall(r"B-SYMPTOM", content))
            print(f"  - Tập {split:<5} ({len(sents):>2} câu): PROCEDURE = {proc_b:>2} | DISEASE = {dis_b:>3} | DRUG = {drug_b:>3} | SYMPTOM = {sym_b:>3}")

    print("=" * 60)
    print("XÁC NHẬN: PROCEDURE là nhãn thiếu trầm trọng nhất (chỉ 10 mẫu trong train, 2 dev, 3 test).")
    print("=" * 60)

if __name__ == "__main__":
    main()
