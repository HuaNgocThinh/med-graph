import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import json
from src.entity_linking.rxnorm_linker import RxNormLinker
from src.entity_linking.entity_normalizer import normalize_entity_name, get_canonical_name

linker = RxNormLinker()

print("dict records:", len(linker.records))
print("exact_map keys containing 'melox':",
      [k for k in linker.exact_map if "melox" in k])
print("exact_map keys containing 'hydrocort':",
      [k for k in linker.exact_map if "hydrocort" in k])

tests = ["Meloxicam 15mg", "Meloxicam 7.5mg", "Meloxicam",
         "Hydrocortisone", "Hydrocortisone 10mg",
         "Paracetamol 500mg", "Paracetamol",
         "Metformin 500mg", "Metformin"]

for t in tests:
    res = linker.link_drug(t)
    print(f"\nlink_drug({t!r})")
    print("  normalize_entity_name ->", repr(normalize_entity_name(t, entity_type="DRUG")))
    print("  get_canonical_name    ->", repr(get_canonical_name(t)))
    print("  RESULT:", json.dumps(res, ensure_ascii=False))
