"""
Runs the 4 required questions through the EXACT Streamlit path:
  LLMClient(provider, api_key) -> QAEngine(llm_client) -> compare_answers(question)
which is what app/streamlit_app.py:163-168 and :247 do.
No internal shortcuts.

Usage: python scratch/run_4_questions.py [tag]
"""
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import LLM_PROVIDER, LLM_API_KEY
from src.llm_client import LLMClient
from src.qa.qa_engine import QAEngine

TAG = sys.argv[1] if len(sys.argv) > 1 else "run"

QUESTIONS = [
    "Tiểu đường có triệu chứng gì?",
    "Đái tháo đường có triệu chứng gì?",
    "Thuốc nào điều trị tiểu đường?",
    "Thuốc nào điều trị đái tháo đường týp 2?",
]

# Exactly as streamlit get_qa_engine() does
llm_client = LLMClient(provider=LLM_PROVIDER, api_key=LLM_API_KEY)
qa_engine = QAEngine(llm_client=llm_client)

out = []
for i, q in enumerate(QUESTIONS, 1):
    res = qa_engine.compare_answers(q)      # <- the exact Streamlit call
    kg = res.get("kg_qa", {})
    print("\n" + "=" * 78)
    print(f"[Q{i}] {q}")
    print("=" * 78)
    print("CYPHER SINH RA:")
    print("  " + kg.get("cypher_query", "(none)"))
    print(f"fallback_status : {kg.get('fallback_status')}")
    print(f"fallback_used   : {kg.get('fallback_used')}")
    print(f"data_source     : {kg.get('data_source')}")
    print(f"source_sample_ids: {kg.get('source_sample_ids')}")
    print("GRAPH RESULTS:")
    gr = kg.get("graph_results", [])
    if not gr:
        print("  [] (rỗng)")
    for r in gr:
        print("  " + json.dumps(r, ensure_ascii=False))
    print("ANSWER:")
    print("  " + str(kg.get("answer", "")).replace("\n", "\n  "))
    out.append({"question": q, "kg_qa": kg})

# Machine-readable dump for the PASS/FAIL comparison
dump = BASE_DIR / "data" / "exports" / f"qa_run_{TAG}.json"
with open(dump, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"\n\nSaved: {dump}")

# --- PASS CRITERION: Q1 and Q2 must return the SAME result set ---
def resultset(kg):
    """Normalized comparable set of (entity-ish) tuples from graph_results."""
    s = set()
    for r in kg.get("graph_results", []):
        s.add(tuple(sorted((k, str(v)) for k, v in r.items() if k != "source_sample_id")))
    return s

s1, s2 = resultset(out[0]["kg_qa"]), resultset(out[1]["kg_qa"])
print("\n" + "=" * 78)
print("TIÊU CHÍ PASS: Q1 vs Q2 phải CÙNG một tập kết quả")
print("=" * 78)
print(f"Q1 result count: {len(s1)}")
print(f"Q2 result count: {len(s2)}")
if s1 == s2 and len(s1) > 0:
    print(">>> PASS: hai câu trả về cùng tập kết quả, và tập không rỗng.")
elif s1 == s2:
    print(">>> FAIL: hai câu giống nhau nhưng CẢ HAI ĐỀU RỖNG (không tính là pass).")
else:
    print(">>> FAIL: hai câu trả về tập KHÁC nhau.")
    print("  chỉ có ở Q1:", [dict(t) for t in (s1 - s2)])
    print("  chỉ có ở Q2:", [dict(t) for t in (s2 - s1)])
