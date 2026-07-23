import sys
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path

backup_path = Path(r"C:\Users\thinhlaluot\MedGraph\data\exports\all_relationships_raw_backup.csv")

if not backup_path.exists():
    print("Backup file does not exist.")
    sys.exit(0)

with open(backup_path, "r", encoding="utf-8") as f:
    for idx, line in enumerate(f):
        if "Aspirin" in line or "aspirin" in line:
            print(f"Row {idx+1}: {line.strip()}")
