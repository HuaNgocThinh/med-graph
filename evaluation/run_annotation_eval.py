"""
Evaluation script for Human-Annotated Gold Datasets (MedGraph-VI Phase 7).
Reads completed CSV files (re_annotation_set.csv, el_annotation_set.csv)
and computes Precision, Recall, F1 for RE, and Exact Match % for EL.
Includes mock test mode (--test) to verify math logic on synthetic fake rows.
"""

import csv
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.stdout.reconfigure(encoding="utf-8")

RE_CSV_PATH = BASE_DIR / "data" / "annotation" / "re_annotation_set.csv"
EL_CSV_PATH = BASE_DIR / "data" / "annotation" / "el_annotation_set.csv"

def compute_re_metrics(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    """Computes Precision, Recall, F1 overall and per-relation type for RE."""
    valid_rows = [r for r in rows if r.get("relation_gold", "").strip() != ""]
    if not valid_rows:
        return {"total_valid": 0, "message": "Chưa có dòng nào được điền nhãn relation_gold."}

    labels = set()
    for r in valid_rows:
        labels.add(r["relation_predicted"].strip())
        labels.add(r["relation_gold"].strip())

    # Confusion matrix counters per label
    tp = {l: 0 for l in labels}
    fp = {l: 0 for l in labels}
    fn = {l: 0 for l in labels}

    for r in valid_rows:
        pred = r["relation_predicted"].strip()
        gold = r["relation_gold"].strip()

        if pred == gold:
            tp[pred] += 1
        else:
            fp[pred] += 1
            fn[gold] += 1

    per_label_metrics = {}
    total_tp = sum(tp.values())
    total_fp = sum(fp.values())
    total_fn = sum(fn.values())

    for l in labels:
        p = tp[l] / max(1, tp[l] + fp[l])
        rec = tp[l] / max(1, tp[l] + fn[l])
        f1 = (2 * p * rec) / max(1e-6, p + rec)
        per_label_metrics[l] = {"precision": p, "recall": rec, "f1": f1, "count": tp[l] + fn[l]}

    micro_p = total_tp / max(1, total_tp + total_fp)
    micro_r = total_tp / max(1, total_tp + total_fn)
    micro_f1 = (2 * micro_p * micro_r) / max(1e-6, micro_p + micro_r)

    macro_f1 = sum(m["f1"] for m in per_label_metrics.values()) / max(1, len(labels))

    return {
        "total_valid": len(valid_rows),
        "micro_precision": micro_p,
        "micro_recall": micro_r,
        "micro_f1": micro_f1,
        "macro_f1": macro_f1,
        "per_label": per_label_metrics
    }


def compute_el_metrics(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    """Computes Exact Match Accuracy % for Entity Linking."""
    valid_rows = [r for r in rows if r.get("code_gold", "").strip() != ""]
    if not valid_rows:
        return {"total_valid": 0, "message": "Chưa có dòng nào được điền nhãn code_gold."}

    correct = 0
    per_source = {}

    for r in valid_rows:
        pred = r["code_predicted"].strip().upper()
        gold = r["code_gold"].strip().upper()
        src = r.get("code_source", "UNKNOWN").strip()

        if src not in per_source:
            per_source[src] = {"correct": 0, "total": 0}
        per_source[src]["total"] += 1

        if pred == gold:
            correct += 1
            per_source[src]["correct"] += 1

    acc = (correct / len(valid_rows)) * 100.0

    return {
        "total_valid": len(valid_rows),
        "exact_match_count": correct,
        "accuracy_pct": acc,
        "per_source": {
            src: (d["correct"] / max(1, d["total"])) * 100.0
            for src, d in per_source.items()
        }
    }


def run_mock_test():
    """Runs verification test on 5 fake rows with pre-defined gold labels."""
    print("=" * 80)
    print("🧪 CHẠY KIỂM THỬ SCRIPT EVALUATION TRÊN DỮ LIỆU GIẢ (5 FAKE ROWS)")
    print("=" * 80)

    fake_re_rows = [
        {"relation_predicted": "PRESCRIBED_FOR", "relation_gold": "PRESCRIBED_FOR"},
        {"relation_predicted": "PRESCRIBED_FOR", "relation_gold": "PRESCRIBED_FOR"},
        {"relation_predicted": "TREATS", "relation_gold": "TREATS"},
        {"relation_predicted": "HAS_SYMPTOM", "relation_gold": "NONE"},  # False Positive
        {"relation_predicted": "CONTRAINDICATED_FOR", "relation_gold": "CONTRAINDICATED_FOR"},
    ]

    re_res = compute_re_metrics(fake_re_rows)
    print("\n--- RE EVALUATION RESULT (FAKE DATA) ---")
    print(f"Total Evaluated : {re_res['total_valid']}")
    print(f"Micro Precision : {re_res['micro_precision'] * 100:.1f}%")
    print(f"Micro Recall    : {re_res['micro_recall'] * 100:.1f}%")
    print(f"Micro F1 Score  : {re_res['micro_f1'] * 100:.1f}%")
    print(f"Macro F1 Score  : {re_res['macro_f1'] * 100:.1f}%")
    print("\nChi tiết từng loại quan hệ (Per-label):")
    for lbl, m in re_res['per_label'].items():
        print(f"  • {lbl:<20}: P={m['precision']*100:.1f}%, R={m['recall']*100:.1f}%, F1={m['f1']*100:.1f}%")

    fake_el_rows = [
        {"code_predicted": "E11", "code_gold": "E11", "code_source": "ICD10"},
        {"code_predicted": "I10", "code_gold": "I10", "code_source": "ICD10"},
        {"code_predicted": "K25", "code_gold": "K25", "code_source": "ICD10"},
        {"code_predicted": "RXCUI:6809", "code_gold": "RXCUI:6809", "code_source": "RxNorm"},
        {"code_predicted": "UNLINKED", "code_gold": "D56.9", "code_source": "ICD10"},  # Mismatch
    ]

    el_res = compute_el_metrics(fake_el_rows)
    print("\n--- EL EVALUATION RESULT (FAKE DATA) ---")
    print(f"Total Evaluated : {el_res['total_valid']}")
    print(f"Exact Match Count: {el_res['exact_match_count']}/{el_res['total_valid']}")
    print(f"Exact Match Acc  : {el_res['accuracy_pct']:.1f}%")
    for src, acc_val in el_res['per_source'].items():
        print(f"  • {src:<10}: {acc_val:.1f}%")

    print("\n✅ KIỂM THỬ SCRIPT EVALUATION THÀNH CÔNG!")
    print("=" * 80)


def evaluate_live_files():
    print("=" * 80)
    print("📊 ĐÁNH GIÁ TRÊN FILE GÁN NHÃN THỰC TẾ (REAL ANNOTATION FILES)")
    print("=" * 80)

    if RE_CSV_PATH.exists():
        with open(RE_CSV_PATH, "r", encoding="utf-8-sig") as f:
            re_rows = list(csv.DictReader(f))
        re_res = compute_re_metrics(re_rows)
        msg = re_res.get("message")
        total_v = re_res.get("total_valid", 0)
        status_str = msg if msg else f"Đã gán {total_v} dòng"
        print(f"\n[RE Annotation Status]: {status_str}")
        if "micro_f1" in re_res:
            print(f"  Micro F1: {re_res['micro_f1']*100:.1f}% | Macro F1: {re_res['macro_f1']*100:.1f}%")
    else:
        print(f"❌ File '{RE_CSV_PATH}' không tồn tại.")

    if EL_CSV_PATH.exists():
        with open(EL_CSV_PATH, "r", encoding="utf-8-sig") as f:
            el_rows = list(csv.DictReader(f))
        el_res = compute_el_metrics(el_rows)
        msg = el_res.get("message")
        total_v = el_res.get("total_valid", 0)
        status_str = msg if msg else f"Đã gán {total_v} dòng"
        print(f"\n[EL Annotation Status]: {status_str}")
        if "accuracy_pct" in el_res:
            print(f"  Exact Match Accuracy: {el_res['accuracy_pct']:.1f}%")
    else:
        print(f"❌ File '{EL_CSV_PATH}' không tồn tại.")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluation script for human-annotated datasets.")
    parser.add_argument("--test", action="store_true", help="Run mock evaluation test on fake rows.")
    args = parser.parse_args()

    if args.test:
        run_mock_test()
    else:
        evaluate_live_files()
