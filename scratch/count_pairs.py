import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import json

with open(r"c:\Users\thinhlaluot\MedGraph\data\dictionaries\icd10_vi.json", encoding="utf-8") as f:
    data = json.load(f)

print("entries:", len(data))
n = 0
for e in data:
    n += len(e.get("synonyms", []))
print("pairs:", n)

# check for duplicate codes
codes = [e["code"] for e in data]
print("unique codes:", len(set(codes)))
from collections import Counter
dupes = [c for c, k in Counter(codes).items() if k > 1]
print("dupe codes:", dupes)

# synonyms identical to name_vi (case-insensitive)
for e in data:
    for s in e["synonyms"]:
        if s.strip().lower() == e["name_vi"].strip().lower():
            print("SELF-ECHO:", e["code"], e["name_vi"], "|", s)

# synonyms appearing under more than one code
sm = {}
for e in data:
    for s in e["synonyms"]:
        sm.setdefault(s.strip().lower(), []).append(e["code"])
for s, cs in sm.items():
    if len(cs) > 1:
        print("CROSS-CODE SYNONYM:", s, cs)
