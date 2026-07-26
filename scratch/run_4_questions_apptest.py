# -*- coding: utf-8 -*-
"""
Drives app/streamlit_app.py through Streamlit's official AppTest runtime:
executes the real app file, types into the real 'custom_query_input' box,
clicks the real '🚀 Gửi Câu Hỏi' button. No internal shortcut calls.
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
from dotenv import load_dotenv
load_dotenv(BASE / ".env")
os.environ["LLM_PROVIDER"] = "gemini"

from streamlit.testing.v1 import AppTest

QUESTIONS = [
    "Bệnh nhân tiểu đường được kê thuốc gì?",          # folk 'tiểu đường' -> đái tháo đường
    "Người bị mỡ máu cao nên uống thuốc gì?",           # folk 'mỡ máu' -> rối loạn lipid máu
    "Bệnh nhân đau bao tử thì chống chỉ định thuốc gì?", # folk 'đau bao tử' -> viêm loét dạ dày
    "Bệnh loạn nhịp tim được điều trị bằng thuốc nào?",  # folk 'loạn nhịp tim' -> rung nhĩ
]

APP = str(BASE / "app" / "streamlit_app.py")

for i, q in enumerate(QUESTIONS, 1):
    print("=" * 78)
    print(f"[CÂU {i}] {q}")
    print("=" * 78)
    at = AppTest.from_file(APP, default_timeout=180)
    at.run()
    # type into the real text box (same key the app binds)
    at.text_input(key="custom_query_input").set_value(q).run()
    # click the real submit button by its label
    btn = [b for b in at.button if "Gửi Câu Hỏi" in b.label][0]
    btn.click().run()

    res = at.session_state["last_qa_result"]
    kg = res.get("kg_qa", {})
    print("Câu hỏi (app ghi nhận):", res.get("question"))
    print("Cypher sinh ra        :", kg.get("cypher_query"))
    print("fallback_status       :", kg.get("fallback_status"))
    print("fallback_used         :", kg.get("fallback_used"))
    print("data_source           :", kg.get("data_source"))
    print("source_sample_ids     :", kg.get("source_sample_ids"))
    print("graph_results         :", json.dumps(kg.get("graph_results", []), ensure_ascii=False))
    print("node_existence_info   :", json.dumps(kg.get("node_existence_info", []), ensure_ascii=False))
    print("--- CÂU TRẢ LỜI KG-QA (hiển thị trên UI) ---")
    print(kg.get("answer", "").strip())
    print()
