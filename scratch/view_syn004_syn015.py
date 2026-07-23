import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "data" / "synthetic" / "synthetic_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for s in data:
    if s["id"] in ("syn_004", "syn_015"):
        print(f"Sample ID: {s['id']}")
        print(f"Text: {s['text']}")
