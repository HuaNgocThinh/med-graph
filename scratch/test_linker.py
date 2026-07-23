import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.entity_linking.icd10_linker import ICD10Linker

linker = ICD10Linker()
print("Link Viêm loét dạ dày tá tràng:", linker.link_disease("Viêm loét dạ dày tá tràng"))
print("Link Viêm loét dạ dày:", linker.link_disease("Viêm loét dạ dày"))
print("Link Cao huyết áp:", linker.link_disease("Cao huyết áp"))
