import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.qa.qa_engine import QAEngine
from src.llm_client import LLMClient
from src.graph.neo4j_client import Neo4jClient

print("Testing QAEngine initialization...")
client = LLMClient(provider="mock")
qa = QAEngine(llm_client=client)

res = qa.compare_answers("Bệnh nhân Đái tháo đường týp 2 được kê thuốc gì?")
print("QA Output Success!")
print("Fallback Status:", res["kg_qa"].get("fallback_status"))
print("Node Info:", res["kg_qa"].get("node_existence_info"))
