"""
Stage I: Entity Linking Evaluation Module.
Evaluates normalization accuracy for ICD-10 Disease and RxNorm Drug linking.
Target criteria: Accuracy >= 70%. Logs errors to evaluation/error_analysis/el_errors.log.
"""

import json
import logging
from typing import Dict, Any
from src.config import ERROR_ANALYSIS_DIR
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.rxnorm_linker import RxNormLinker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EvaluateEL")

TEST_EL_BENCHMARK = [
    {"entity": "Cao huyết áp", "type": "DISEASE", "expected_code": "I10"},
    {"entity": "tiểu đường tuýp 2", "type": "DISEASE", "expected_code": "E11"},
    {"entity": "Viêm phổi cấp", "type": "DISEASE", "expected_code": "J18.9"},
    {"entity": "hen suyễn", "type": "DISEASE", "expected_code": "J45"},
    {"entity": "đau dạ dày", "type": "DISEASE", "expected_code": "K29.7"},
    {"entity": "GERD", "type": "DISEASE", "expected_code": "K21.9"},
    {"entity": "Paracetamol 500mg", "type": "DRUG", "expected_code": "RXCUI:161"},
    {"entity": "panadol", "type": "DRUG", "expected_code": "RXCUI:161"},
    {"entity": "Aspirin 81mg", "type": "DRUG", "expected_code": "RXCUI:1191"},
    {"entity": "Ibuprofen", "type": "DRUG", "expected_code": "RXCUI:5640"},
    {"entity": "Glucophage", "type": "DRUG", "expected_code": "RXCUI:6809"},
    {"entity": "Metformin", "type": "DRUG", "expected_code": "RXCUI:6809"},
    {"entity": "Amlor", "type": "DRUG", "expected_code": "RXCUI:4337"},
    {"entity": "Lipitor", "type": "DRUG", "expected_code": "RXCUI:83367"},
    {"entity": "Nexium", "type": "DRUG", "expected_code": "RXCUI:283742"}
]

def evaluate_entity_linking():
    icd_linker = ICD10Linker()
    rx_linker = RxNormLinker()
    error_log_path = ERROR_ANALYSIS_DIR / "el_errors.log"

    correct = 0
    total = len(TEST_EL_BENCHMARK)
    errors = []

    logger.info(f"Evaluating Entity Linking on {total} benchmark items...")

    for item in TEST_EL_BENCHMARK:
        ent = item["entity"]
        ent_type = item["type"]
        expected = item["expected_code"]

        if ent_type == "DISEASE":
            res = icd_linker.link_disease(ent)
        else:
            res = rx_linker.link_drug(ent)

        pred_code = res.get("code")
        if pred_code == expected:
            correct += 1
        else:
            errors.append({
                "entity": ent,
                "type": ent_type,
                "expected_code": expected,
                "predicted_code": pred_code,
                "method_used": res.get("method"),
                "confidence": res.get("confidence")
            })

    accuracy = round(correct / total, 4) if total > 0 else 0.0
    metrics = {
        "total_samples": total,
        "correct_matches": correct,
        "accuracy_rate": accuracy,
        "target_met": accuracy >= 0.70
    }

    with open(error_log_path, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "errors": errors}, f, ensure_ascii=False, indent=2)

    print("\n--- ENTITY LINKING EVALUATION SUMMARY ---")
    print(json.dumps(metrics, indent=2))
    print(f"Error log written to: '{error_log_path}'\n")

if __name__ == "__main__":
    evaluate_entity_linking()
