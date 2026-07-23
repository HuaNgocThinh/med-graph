import sys
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path

backup_path = Path(r"C:\Users\thinhlaluot\MedGraph\data\exports\all_relationships_raw_backup.csv")
if backup_path.exists():
    with open(backup_path, "r", encoding="utf-8") as f:
        print("Lines with syn_002 in RAW backup:")
        for line in f:
            if "syn_002" in line:
                print(line.strip())
else:
    print("No backup file found.")
