import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent

with open(BASE_DIR / "data" / "synthetic" / "synthetic_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Searching for 'angina' and 'aspirin' in samples...")
for s in data:
    text = s["text"]
    text_lower = text.lower()
    if ("cơn đau thắt ngực" in text_lower or "đau thắt ngực" in text_lower) and "aspirin" in text_lower:
        print(f"\n==========================================")
        print(f"Sample ID: {s['id']}")
        print(f"Text: {text}")
