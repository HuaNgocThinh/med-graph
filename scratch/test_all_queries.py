import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.qa.qa_engine import QAEngine
from src.llm_client import LLMClient

client = LLMClient()
qa = QAEngine(llm_client=client)

questions = [
    "Viêm mũi dị ứng có triệu chứng gì?",
    "Cường giáp có triệu chứng lâm sàng nào?",
    "Thuốc Amoxicillin 500mg được kê cho bệnh nào?"
]

for q in questions:
    print(f"\n==========================================")
    print(f"QUESTION: {q}")
    res = qa.compare_answers(q)
    kg = res["kg_qa"]
    print("Cypher query:", kg["cypher_query"])
    print("Fallback status:", kg["fallback_status"])
    print("Graph results:", kg["graph_results"])
    print("Answer:", kg["answer"])
