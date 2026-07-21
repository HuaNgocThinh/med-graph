"""
Stage I: NER Evaluation Module.
Evaluates Precision, Recall, and F1-score for NER Ensemble against hand-annotated test set.
Outputs structured metrics and logs categorized errors to evaluation/error_analysis/ner_errors.log.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from sklearn.metrics import precision_recall_fscore_support
from src.config import ANNOTATED_DATA_DIR, ERROR_ANALYSIS_DIR
from src.ner.ner_ensemble import NEREnsemble

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EvaluateNER")

def evaluate_ner():
    test_path = ANNOTATED_DATA_DIR / "test_set.json"
    if not test_path.exists():
        logger.error(f"Test dataset not found at '{test_path}'")
        return

    with open(test_path, "r", encoding="utf-8") as f:
        test_samples = json.load(f)

    ensemble = NEREnsemble()
    error_log_path = ERROR_ANALYSIS_DIR / "ner_errors.log"

    y_true = []
    y_pred = []
    error_records = []

    logger.info(f"Evaluating NER on {len(test_samples)} annotated test samples...")

    for sample in test_samples:
        text = sample["text"]
        true_ents = sample.get("entities", [])
        pred_ents = ensemble.extract_entities(text)

        true_tuples = {(e["entity"].lower(), e["type"]) for e in true_ents}
        pred_tuples = {(e["entity"].lower(), e["type"]) for e in pred_ents}

        # Count true positives, false positives, false negatives
        for t in pred_tuples:
            if t in true_tuples:
                y_true.append(1)
                y_pred.append(1)
            else:
                y_true.append(0)
                y_pred.append(1)
                error_records.append({
                    "sample_id": sample["id"],
                    "error_type": "FALSE_POSITIVE_BOUNDARY_OR_TYPE",
                    "text": text,
                    "predicted": t,
                    "ground_truth": list(true_tuples)
                })

        for t in true_tuples:
            if t not in pred_tuples:
                y_true.append(1)
                y_pred.append(0)
                error_records.append({
                    "sample_id": sample["id"],
                    "error_type": "MISSED_ENTITY_FALSE_NEGATIVE",
                    "text": text,
                    "missed_entity": t,
                    "predicted_entities": list(pred_tuples)
                })

    if y_true and y_pred:
        precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary")
    else:
        precision, recall, f1 = 0.0, 0.0, 0.0

    metrics = {
        "precision": round(float(precision), 4),
        "recall": round(float(recall), 4),
        "f1_score": round(float(f1), 4),
        "total_errors": len(error_records)
    }

    # Write detailed error log
    with open(error_log_path, "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "errors": error_records}, f, ensure_ascii=False, indent=2)

    logger.info(f"NER Evaluation Complete: Precision={metrics['precision']}, Recall={metrics['recall']}, F1={metrics['f1_score']}")
    print("\n--- NER EVALUATION SUMMARY ---")
    print(json.dumps(metrics, indent=2))
    print(f"Error log saved to: '{error_log_path}'\n")

if __name__ == "__main__":
    evaluate_ner()
