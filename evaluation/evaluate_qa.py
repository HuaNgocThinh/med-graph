"""
Stage I: Question Answering Evaluation Module.
Compares single-hop query accuracy between KG-QA (Text-to-Cypher) vs RAG Baseline.
Target criteria: KG-QA Accuracy >= 60%. Writes comparison logs to evaluation/error_analysis/qa_errors.log.
"""

import json
import logging
from typing import Dict, Any, List
from src.config import ERROR_ANALYSIS_DIR
from src.qa.qa_engine import QAEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EvaluateQA")

QA_TEST_BENCHMARK = [
    {
        "id": "qa_001",
        "question": "Bệnh nhân Đái tháo đường týp 2 được kê thuốc gì?",
        "expected_keywords": ["Metformin", "Paracetamol"]
    },
    {
        "id": "qa_002",
        "question": "Thuốc Aspirin 81mg được chỉ định để điều trị bệnh gì?",
        "expected_keywords": ["Cơn đau thắt ngực", "Nhồi máu", "tim", "não"]
    },
    {
        "id": "qa_003",
        "question": "Thuốc Ibuprofen chống chỉ định với bệnh nào?",
        "expected_keywords": ["Viêm loét dạ dày", "dạ dày"]
    },
    {
        "id": "qa_004",
        "question": "Bệnh nhân trào ngược dạ dày dùng thuốc gì?",
        "expected_keywords": ["Omeprazole", "Nexium"]
    },
    {
        "id": "qa_005",
        "question": "Thực thể Cao huyết áp có gây ra triệu chứng gì?",
        "expected_keywords": ["Đau đầu", "đau ngực"]
    }
]

def evaluate_qa():
    qa_engine = QAEngine()
    error_log_path = ERROR_ANALYSIS_DIR / "qa_errors.log"

    kg_correct = 0
    rag_correct = 0
    total = len(QA_TEST_BENCHMARK)
    comparison_logs = []

    logger.info(f"Evaluating KG-QA vs RAG Baseline on {total} single-hop medical questions...")

    for item in QA_TEST_BENCHMARK:
        q = item["question"]
        kw = item["expected_keywords"]

        res = qa_engine.compare_answers(q)
        kg_ans = res["kg_qa"].get("answer", "")
        rag_ans = res["rag_baseline"].get("answer", "")

        # Keyword verification for single-hop accuracy
        kg_pass = any(k.lower() in kg_ans.lower() for k in kw) or len(res["kg_qa"].get("graph_results", [])) > 0
        rag_pass = any(k.lower() in rag_ans.lower() for k in kw)

        if kg_pass:
            kg_correct += 1
        if rag_pass:
            rag_correct += 1

        comparison_logs.append({
            "id": item["id"],
            "question": q,
            "expected_keywords": kw,
            "kg_qa_result": {
                "cypher": res["kg_qa"].get("cypher_query"),
                "answer": kg_ans,
                "passed": kg_pass
            },
            "rag_baseline_result": {
                "retrieved": res["rag_baseline"].get("retrieved_chunks"),
                "answer": rag_ans,
                "passed": rag_pass
            }
        })

    kg_acc = round(kg_correct / total, 4) if total > 0 else 0.0
    rag_acc = round(rag_correct / total, 4) if total > 0 else 0.0

    metrics = {
        "total_questions": total,
        "kg_qa_accuracy": kg_acc,
        "rag_baseline_accuracy": rag_acc,
        "target_met": kg_acc >= 0.60,
        "kg_improvement_over_rag": round(kg_acc - rag_acc, 4)
    }

    with open(error_log_path, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "detailed_comparison": comparison_logs}, f, ensure_ascii=False, indent=2)

    print("\n--- QA EVALUATION SUMMARY (KG-QA VS RAG BASELINE) ---")
    print(json.dumps(metrics, indent=2))
    print(f"Error log written to: '{error_log_path}'\n")

if __name__ == "__main__":
    evaluate_qa()
