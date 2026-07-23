import sys
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path

log_path = Path(r"C:\Users\thinhlaluot\.gemini\antigravity-ide\brain\e1061b8e-c098-4772-87f2-775e9dafc775\.system_generated\tasks\task-554.log")

if not log_path.exists():
    print("Log does not exist.")
    sys.exit(0)

in_sample = False
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "syn_002" in line:
            in_sample = True
            print(line.strip())
        elif "syn_003" in line or "Processing Sample 3" in line:
            in_sample = False
        elif in_sample:
            print(line.strip())
