import os
import sys
from pathlib import Path

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    AutoModelForSequenceClassification,
)

# Base paths and parameters
BASE_DIR = Path(__file__).resolve().parent.parent
NER_MODEL_PATH = BASE_DIR / "models" / "ner_best.pt"
RE_MODEL_PATH = BASE_DIR / "models" / "re_best.pt"

BASE_MODEL = "vinai/phobert-base-v2"
NUM_NER_LABELS = 9
NUM_RE_LABELS = 7


def main():
    # 1. Khởi tạo Tokenizer
    print("⏳ Đang tải Tokenizer (vinai/phobert-base-v2)...")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    special_tokens = ["[E1]", "[/E1]", "[E2]", "[/E2]"]
    tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})

    # 2. Load Mô hình NER
    print(f"⏳ Đang nạp mô hình NER ({NER_MODEL_PATH.name})...")
    ner_model = AutoModelForTokenClassification.from_pretrained(
        BASE_MODEL, num_labels=NUM_NER_LABELS
    )
    ner_state_dict = torch.load(NER_MODEL_PATH, map_location="cpu")
    ner_model.load_state_dict(ner_state_dict)
    ner_model.eval()

    # 3. Load Mô hình RE
    print(f"⏳ Đang nạp mô hình RE ({RE_MODEL_PATH.name})...")
    re_model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL, num_labels=NUM_RE_LABELS
    )
    # QUAN TRỌNG: Gọi resize_token_embeddings trước khi load weights
    re_model.resize_token_embeddings(len(tokenizer))
    re_state_dict = torch.load(RE_MODEL_PATH, map_location="cpu")
    re_model.load_state_dict(re_state_dict)
    re_model.eval()

    print(
        "🚀 CHÚC MƯNG! HỆ THỐNG MEDGRAPH-VI ĐÃ SẴN SÀNG HOẠT ĐỘNG TRÊN MÁY LOCAL!"
    )


if __name__ == "__main__":
    main()
