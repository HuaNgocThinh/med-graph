"""
Test script for Section 6.3 questions against Live Neo4j Database and QAEngine.
"""

import sys
import json
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.qa.text_to_cypher import TextToCypherQA

qa = TextToCypherQA()

questions = [
    "Thalassemia có điều trị gì?",
    "Metformin điều trị bệnh gì?",
    "Triệu chứng của Bệnh không tồn tại là gì?"
]

out_lines = []
out_lines.append("=" * 80)
out_lines.append("6.3 KIỂM TRA THÊM TRÊN LIVE DB & QA ENGINE")
out_lines.append("=" * 80)

for idx, q in enumerate(questions, 1):
    out_lines.append(f"\n--- CÂU HỎI {idx}: '{q}' ---")
    res = qa.answer_question(q)
    out_lines.append(f"Fallback Status : {res.get('fallback_status')}")
    out_lines.append(f"Cypher Query    : {res.get('cypher_query')}")
    out_lines.append(f"Graph Results   : {json.dumps(res.get('graph_results'), ensure_ascii=False)}")
    out_lines.append(f"Source SampleIDs: {res.get('source_sample_ids')}")
    out_lines.append(f"Answer          :\n{res.get('answer')}")
    out_lines.append("-" * 80)

content = "\n".join(out_lines)
with open(BASE_DIR / "scratch" / "6_3_output.txt", "w", encoding="utf-8") as f:
    f.write(content)

print("Done writing to scratch/6_3_output.txt")
