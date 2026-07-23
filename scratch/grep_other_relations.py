import sys
sys.stdout.reconfigure(encoding="utf-8")

with open(r"C:\Users\thinhlaluot\MedGraph\data\exports\all_relationships.csv", "r", encoding="utf-8") as f:
    lines = f.readlines()

search_terms = ["Paracetamol", "Migraine", "tiết niệu", "phổi tắc nghẽn", "Nhồi máu não", "Augmentin", "Tenofovir"]

for term in search_terms:
    print(f"\nSearch for: {term}")
    found = False
    for idx, line in enumerate(lines):
        if term.lower() in line.lower():
            print(f"  Row {idx+1}: {line.strip()}")
            found = True
    if not found:
        print("  NOT FOUND")
