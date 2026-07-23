import sys
sys.stdout.reconfigure(encoding="utf-8")

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "data" / "synthetic" / "synthetic_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for s in data:
    if s["id"] == "syn_012":
        print("Text:", s["text"])
