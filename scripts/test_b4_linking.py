"""
B4 Verification Script:
Tests link_disease() for all queries associated with the 6 removed synonyms
to verify they no longer link to incorrect codes and do not cross-link.
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.entity_linking.icd10_linker import ICD10Linker

def main():
    linker = ICD10Linker()

    print("=" * 80)
    print("B4: TESTING LINKING FOR THE 6 REMOVED SYNONYMS")
    print("=" * 80)

    test_queries = [
        # Pair 1: Viêm phổi vs Viêm phế quản
        ("viêm phổi", "Expected: J18.9 (Viêm phổi)"),
        ("viêm phế quản", "Expected: J20.9 (Viêm phế quản cấp)"),
        ("viêm phế quản phổi", "Expected: unlinked or J18.0 (NOT J18.9)"),

        # Case 2: Loét dạ dày tá tràng
        ("loét dạ dày tá tràng", "Expected: unlinked (NOT K25)"),
        ("loét tá tràng", "Expected: unlinked / K26 (NOT K25)"),
        ("loét dạ dày", "Expected: K25 (Viêm loét dạ dày)"),

        # Case 3: Cơn co giật (symptom R56.8, not epilepsy G40.9)
        ("cơn co giật", "Expected: rejected_generic / unlinked (NOT G40.9)"),

        # Case 4: Rối loạn lo âu (F41.9 unspecified, not F41.1 GAD)
        ("rối loạn lo âu", "Expected: unlinked (NOT F41.1)"),
        ("rối loạn lo âu lan tỏa", "Expected: F41.1 (Rối loạn lo âu lan tỏa)"),

        # Case 5: Thiếu máu nặng (severity, not D50.9 iron deficiency)
        ("thiếu máu nặng", "Expected: unlinked (NOT D50.9)"),
        ("thiếu máu thiếu sắt", "Expected: D50.9 (Thiếu máu thiếu sắt)"),
    ]

    for q, exp in test_queries:
        res = linker.link_disease(q)
        print(f"Query: {q!r:<25} ({exp})")
        print(f"       -> standard_name={res.get('standard_name')!r}, code={res.get('code')!r}, method={res.get('method')!r}, conf={res.get('confidence')}")
        print("-" * 80)

if __name__ == "__main__":
    main()
