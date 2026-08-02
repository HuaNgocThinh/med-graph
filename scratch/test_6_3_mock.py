"""
Test script for 6.3 queries using mock provider / direct logic verification.
"""
import sys
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
sys.stdout.reconfigure(encoding="utf-8")

from src.qa.text_to_cypher import TextToCypherQA
from src.llm_client import LLMClient

mock_llm = LLMClient(provider="mock")
qa = TextToCypherQA(llm_client=mock_llm)

questions = [
    "Thalassemia có điều trị gì?",
    "Metformin điều trị bệnh gì?",
    "Triệu chứng của Bệnh không tồn tại là gì?"
]

print("=" * 80)
print("6.3 MOCK / DIRECT QUERY VERIFICATION")
print("=" * 80)

for idx, q in enumerate(questions, 1):
    print(f"\n--- CÂU HỎI {idx}: '{q}' ---")
    res = qa.answer_question(q)
    print(f"Fallback Status : {res.get('fallback_status')}")
    print(f"Cypher Query    : {res.get('cypher_query')}")
    print(f"Graph Results   : {json.dumps(res.get('graph_results'), ensure_ascii=False)}")
    print(f"Source SampleIDs: {res.get('source_sample_ids')}")
    print(f"Answer          :\n{res.get('answer')}")
    print("-" * 80)
