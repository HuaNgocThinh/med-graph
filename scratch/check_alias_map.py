import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.entity_linking.entity_normalizer import ALIAS_MAP

print("bệnh in ALIAS_MAP:", "bệnh" in ALIAS_MAP)
print("bệnh cao huyết áp in ALIAS_MAP:", "bệnh cao huyết áp" in ALIAS_MAP)
for k, v in ALIAS_MAP.items():
    if k == "bệnh" or k == "bị" or len(k) < 3:
        print(f"{k} -> {v}")
