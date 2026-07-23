import sys
sys.stdout.reconfigure(encoding="utf-8")

log_path = r"C:\Users\thinhlaluot\.gemini\antigravity-ide\brain\e1061b8e-c098-4772-87f2-775e9dafc775\.system_generated\tasks\task-222.log"
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()
    for i in range(210, 235):
        if i < len(lines):
            print(f"Line {i+1}: {lines[i].strip()}")
