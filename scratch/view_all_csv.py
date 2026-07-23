import sys
sys.stdout.reconfigure(encoding="utf-8")

with open(r"C:\Users\thinhlaluot\MedGraph\data\exports\all_relationships.csv", "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        print(f"{idx+1}: {line.strip()}")
