import sys
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path

task_dir = Path(r"C:\Users\thinhlaluot\.gemini\antigravity-ide\brain\e1061b8e-c098-4772-87f2-775e9dafc775\.system_generated\tasks")

log_files = ["task-222.log", "task-420.log"]

for log_file in log_files:
    log_path = task_dir / log_file
    if not log_path.exists():
        print(f"Log {log_file} does not exist.")
        continue
    
    print(f"\n==========================================")
    print(f"SEARCHING IN LOG: {log_file}")
    print(f"==========================================")
    
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
