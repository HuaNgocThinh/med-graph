import sys
sys.stdout.reconfigure(encoding="utf-8")

log_path = r"C:\Users\thinhlaluot\.gemini\antigravity-ide\brain\e1061b8e-c098-4772-87f2-775e9dafc775\.system_generated\tasks\task-222.log"
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for idx, line in enumerate(f):
        if "REJECTED" in line or "Rejected" in line or "post-check" in line.lower():
            print(f"Line {idx+1}: {line.strip()}")
