"""
Script to export NER Pseudo-Labels for Student model training (BƯỚC 1).
Extracts entities from synthetic_data.json using Dictionary, PhoBERT-CRF, and LLM (Gemini),
applies source tracking and ensemble merging logic, saves result to
data/student_training/ner_pseudo_labels.json, and prints required statistics.
"""

import json
import logging
import re
import time
import sys
from pathlib import Path
from typing import List, Dict, Any, Set

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import BASE_DIR, DATA_DIR
from src.llm_client import LLMClient
from src.ner.dictionary_ner import DictionaryNER
from src.ner.phobert_crf_ner import PhoBertCRFNER
from src.ner.llm_ner import LLMNER

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ExportNERPseudoLabels")

SOURCE_PRIORITY = {
    "llm": 3,
    "phobert": 2,
    "phobert_crf": 2,
    "dictionary": 1
}

GENERIC_STOPWORDS = {"bệnh", "chứng", "triệu chứng", "tình trạng", "hội chứng", "thuốc"}

def sanitize_candidate(text: str, ent: Dict[str, Any]) -> Dict[str, Any]:
    raw_text = ent.get("entity") or ent.get("text") or ""
    start = ent.get("start", 0)
    end = ent.get("end", len(raw_text))
    source = ent.get("source", "unknown")
    if source == "phobert_crf":
        source = "phobert"
    label = ent.get("type") or ent.get("label") or "UNKNOWN"

    # Trim trailing punctuation from surface text
    clean_text = raw_text.rstrip(",.;:")
    end = start + len(clean_text)

    # Double check substring alignment
    actual_substr = text[start:end]
    if actual_substr != clean_text:
        # Fallback search near start
        idx = text.find(clean_text, max(0, start - 5))
        if idx != -1:
            start = idx
            end = start + len(clean_text)

    return {
        "text": clean_text,
        "label": label.upper(),
        "start": start,
        "end": end,
        "source": source
    }

def cluster_entities(candidates: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
    # Filter stopwords
    valid_cands = []
    for c in candidates:
        if c["text"].strip().lower() in GENERIC_STOPWORDS:
            continue
        if len(c["text"].strip()) <= 1:
            continue
        valid_cands.append(c)

    if not valid_cands:
        return []

    # Sort candidates by start index, then source priority
    valid_cands.sort(key=lambda x: (x["start"], -SOURCE_PRIORITY.get(x["source"], 0)))

    clusters: List[List[Dict[str, Any]]] = []

    for cand in valid_cands:
        added = False
        for cluster in clusters:
            # Check overlap with candidates in cluster
            for member in cluster:
                overlap = min(cand["end"], member["end"]) - max(cand["start"], member["start"])
                min_len = min(cand["end"] - cand["start"], member["end"] - member["start"])
                if overlap > 0 and (min_len == 0 or (overlap / min_len) > 0.4):
                    cluster.append(cand)
                    added = True
                    break
            if added:
                break
        if not added:
            clusters.append([cand])

    final_entities = []
    for cluster in clusters:
        sources: Set[str] = {c["source"] for c in cluster}

        # Normalize sources
        norm_sources = set()
        for s in sources:
            if s in ("phobert_crf", "phobert"):
                norm_sources.add("phobert")
            else:
                norm_sources.add(s)

        if len(norm_sources) >= 2:
            final_source = "ensemble"
            confidence = 0.95
        else:
            final_source = list(norm_sources)[0]
            if final_source == "llm":
                confidence = 0.90
            elif final_source == "phobert":
                confidence = 0.85
            else:
                confidence = 0.80

        # Select best representative candidate from cluster
        # Priority: highest source priority, then longest span
        cluster.sort(key=lambda x: (-SOURCE_PRIORITY.get(x["source"], 0), -(x["end"] - x["start"])))
        best = cluster[0]

        final_entities.append({
            "text": best["text"],
            "label": best["label"],
            "start": best["start"],
            "end": best["end"],
            "confidence": confidence,
            "source": final_source
        })

    # Sort final entities by start offset
    final_entities.sort(key=lambda x: x["start"])
    return final_entities

def run_export():
    synthetic_path = DATA_DIR / "synthetic" / "synthetic_data.json"
    output_dir = DATA_DIR / "student_training"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "ner_pseudo_labels.json"
    cache_path = output_dir / ".ner_cache.json"

    with open(synthetic_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"Loaded {len(data)} synthetic samples from {synthetic_path}")

    # Load cache if exists
    cache = {}
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
            logger.info(f"Loaded {len(cache)} cached LLM NER responses from {cache_path}")
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")

    dict_ner = DictionaryNER()
    phobert_ner = PhoBertCRFNER()
    llm_client = LLMClient()
    llm_ner = LLMNER(llm_client)

    records = []
    total_samples = len(data)

    for idx, sample in enumerate(data, 1):
        sample_id = sample.get("id") or f"syn_{idx:03d}"
        text = sample["text"]

        logger.info(f"Processing [{idx}/{total_samples}] {sample_id}...")

        # 1. Dict NER
        dict_preds = [sanitize_candidate(text, c) for c in dict_ner.extract_entities(text)]

        # 2. PhoBERT NER
        phobert_preds = [sanitize_candidate(text, c) for c in phobert_ner.extract_entities(text)]

        # 3. LLM NER (with cache)
        if sample_id in cache:
            raw_llm_preds = cache[sample_id]
        else:
            raw_llm_preds = llm_ner.extract_entities(text)
            cache[sample_id] = raw_llm_preds
            # Save cache incrementally
            with open(cache_path, "w", encoding="utf-8") as cf:
                json.dump(cache, cf, ensure_ascii=False, indent=2)

        llm_preds = [sanitize_candidate(text, c) for c in raw_llm_preds]

        all_candidates = dict_preds + phobert_preds + llm_preds
        consolidated = cluster_entities(all_candidates, text)

        records.append({
            "sample_id": sample_id,
            "text": text,
            "entities": consolidated
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    logger.info(f"Exported {len(records)} records to {output_path}")

    # Compute Statistics
    all_entities = [ent for r in records for ent in r["entities"]]
    total_entities = len(all_entities)

    label_counts = {}
    source_counts = {}

    for ent in all_entities:
        lbl = ent["label"]
        src = ent["source"]
        label_counts[lbl] = label_counts.get(lbl, 0) + 1
        source_counts[src] = source_counts.get(src, 0) + 1

    ensemble_count = source_counts.get("ensemble", 0)
    ensemble_ratio = (ensemble_count / total_entities * 100.0) if total_entities > 0 else 0.0

    print("\n" + "="*50)
    print("THỐNG KÊ NER PSEUDO-LABELS (BƯỚC 1)")
    print("="*50)
    print(f"Tổng số sample: {len(records)}")
    print(f"Tổng số entity: {total_entities}")
    print("\nPhân phối theo nhãn (label):")
    for lbl, cnt in sorted(label_counts.items(), key=lambda x: -x[1]):
        pct = (cnt / total_entities * 100.0) if total_entities > 0 else 0.0
        print(f"  - {lbl}: {cnt} ({pct:.1f}%)")

    print("\nPhân phối theo nguồn (source):")
    for src, cnt in sorted(source_counts.items(), key=lambda x: -x[1]):
        pct = (cnt / total_entities * 100.0) if total_entities > 0 else 0.0
        print(f"  - {src}: {cnt} ({pct:.1f}%)")

    print(f"\nTỉ lệ ensemble (≥2 nguồn đồng ý): {ensemble_count}/{total_entities} ({ensemble_ratio:.1f}%)")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_export()
