"""
B5: Audit script for ICD-10 dictionary synonyms against the 4 criteria in _rules.
Reads current synonyms in data/dictionaries/icd10_vi.json and checks against
icd10_synonyms_audit.csv classifications.
"""

import csv
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

DICT_PATH = BASE_DIR / "data" / "dictionaries" / "icd10_vi.json"
AUDIT_PATH = BASE_DIR / "data" / "exports" / "icd10_synonyms_audit.csv"

def main():
    with open(AUDIT_PATH, "r", encoding="utf-8-sig") as f:
        audit_rows = list(csv.DictReader(f))

    audit_map = {(r["icd_code"], r["synonym"]): r for r in audit_rows}

    with open(DICT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    diseases = data.get("diseases", [])

    print("=" * 80)
    print("B5: AUDIT REMAINING RULE VIOLATIONS IN ICD-10 DICTIONARY")
    print("=" * 80)

    total_synonyms = 0
    violation_counts = Counter()
    violations = []

    for d in diseases:
        code = d["code"]
        name_vi = d["name_vi"]
        for syn in d.get("synonyms", []):
            total_synonyms += 1
            info = audit_map.get((code, syn))
            if not info:
                # Try matching remapped codes (e.g. M19.9 -> M17, N76.0 -> B37.3)
                old_code = "M19.9" if code == "M17" else ("N76.0" if code == "B37.3" else code)
                info = audit_map.get((old_code, syn))

            if info:
                violates = info["violates_rule"] == "YES"
                classification = info["classification"]
                if violates:
                    violation_counts[classification] += 1
                    violations.append((code, name_vi, syn, classification, info["reason"]))

    print(f"Total current synonyms in icd10_vi.json: {total_synonyms}")
    print("\nViolation counts by criterion:")
    print("  1. CATEGORY_NARROWING :", violation_counts.get("CATEGORY_NARROWING", 0))
    print("  2. SYMPTOM_AS_DISEASE :", violation_counts.get("SYMPTOM_AS_DISEASE", 0))
    print("  3. OVER_COMMITMENT/ACUTE :", violation_counts.get("OVER_COMMITMENT", 0))
    print("  4. REDUNDANT/ALIAS_MAP :", violation_counts.get("OTHER", 0) + violation_counts.get("REDUNDANT", 0))
    print(f"\nTotal remaining rule violations: {sum(violation_counts.values())}")

    if violations:
        print("\nDetail of remaining violations:")
        for code, name, syn, cat, reason in violations:
            print(f"  - [{code}] {name} <- {syn!r} ({cat}): {reason}")

    return 0

if __name__ == "__main__":
    main()
