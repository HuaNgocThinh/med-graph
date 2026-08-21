"""
Script to run Stage B NER Extraction on the Extended Dataset (166 sentences),
perform Stratified Train/Dev/Test Split (70/15/15), export BIO CoNLL files,
and print label distribution statistics.
"""

import json
import logging
import math
import random
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Any, Set

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import DATA_DIR
from src.llm_client import LLMClient
from src.ner.dictionary_ner import DictionaryNER
from src.ner.phobert_crf_ner import PhoBertCRFNER
from src.ner.llm_ner import LLMNER

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ExportExtendedNERCoNLL")

SOURCE_PRIORITY = {
    "llm": 3,
    "phobert": 2,
    "phobert_crf": 2,
    "dictionary": 1
}

GENERIC_STOPWORDS = {"bệnh", "chứng", "triệu chứng", "tình trạng", "hội chứng", "thuốc"}
INVALID_PROC_TEXTS = {"men gan", "hemoglobin", "inr"}

def sanitize_candidate(text: str, ent: Dict[str, Any]) -> Dict[str, Any]:
    raw_text = ent.get("entity") or ent.get("text") or ""
    start = ent.get("start", 0)
    end = ent.get("end", len(raw_text))
    source = ent.get("source", "unknown")
    if source == "phobert_crf":
        source = "phobert"
    label = ent.get("type") or ent.get("label") or "UNKNOWN"

    clean_text = raw_text.rstrip(",.;:")
    end = start + len(clean_text)

    actual_substr = text[start:end]
    if actual_substr != clean_text:
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
    valid_cands = []
    for c in candidates:
        if c["text"].strip().lower() in GENERIC_STOPWORDS:
            continue
        if len(c["text"].strip()) <= 1:
            continue
        # Filter out invalid procedure entities
        if c["label"] == "PROCEDURE" and c["text"].strip().lower() in INVALID_PROC_TEXTS:
            continue
        valid_cands.append(c)

    if not valid_cands:
        return []

    valid_cands.sort(key=lambda x: (x["start"], -SOURCE_PRIORITY.get(x["source"], 0)))
    clusters: List[List[Dict[str, Any]]] = []

    for cand in valid_cands:
        added = False
        for cluster in clusters:
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

    final_entities.sort(key=lambda x: x["start"])
    return final_entities

def tokenize_with_spans(text: str) -> List[Tuple[str, int, int]]:
    tokens = []
    for match in re.finditer(r'\w+|[^\w\s]', text, re.UNICODE):
        token_str = match.group(0)
        start, end = match.span()
        tokens.append((token_str, start, end))
    return tokens

def generate_bio_tags(text: str, entities: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    tokens_with_spans = tokenize_with_spans(text)
    
    valid_entities = [
        e for e in entities 
        if not (e.get('label') == 'PROCEDURE' and e['text'].strip().lower() in INVALID_PROC_TEXTS)
    ]
    valid_entities.sort(key=lambda x: x['start'])

    bio_labels = ['O'] * len(tokens_with_spans)

    for ent in valid_entities:
        lbl = ent.get('label') or ent.get('type')
        estart = ent['start']
        eend = ent['end']
        
        overlapping_indices = []
        for idx, (tstr, tstart, tend) in enumerate(tokens_with_spans):
            if max(tstart, estart) < min(tend, eend):
                overlapping_indices.append(idx)

        if overlapping_indices:
            first_idx = overlapping_indices[0]
            bio_labels[first_idx] = f"B-{lbl}"
            for o_idx in overlapping_indices[1:]:
                bio_labels[o_idx] = f"I-{lbl}"

    return [(tokens_with_spans[i][0], bio_labels[i]) for i in range(len(tokens_with_spans))]

def stratified_split(records: List[Dict[str, Any]], train_ratio=0.70, dev_ratio=0.15, seed=42) -> Dict[str, str]:
    """
    Performs entity-aware stratified splitting so rare classes (PROCEDURE) are balanced across splits.
    """
    random.seed(seed)
    
    # Categorize records by highest priority label present (PROCEDURE first, then DRUG, DISEASE, SYMPTOM)
    proc_records = []
    other_records = []

    for r in records:
        has_proc = any(e['label'] == 'PROCEDURE' for e in r.get('entities', []))
        if has_proc:
            proc_records.append(r)
        else:
            other_records.append(r)

    random.shuffle(proc_records)
    random.shuffle(other_records)

    split_assignment = {}

    def assign_group(group: List[Dict[str, Any]]):
        n = len(group)
        n_train = max(1, math.floor(n * train_ratio))
        n_dev = max(1, math.floor(n * dev_ratio))
        n_test = n - n_train - n_dev
        
        for i, item in enumerate(group):
            sid = item['sample_id']
            if i < n_train:
                split_assignment[sid] = 'train'
            elif i < n_train + n_dev:
                split_assignment[sid] = 'dev'
            else:
                split_assignment[sid] = 'test'

    assign_group(proc_records)
    assign_group(other_records)

    return split_assignment

def run_export():
    orig_path = DATA_DIR / "synthetic" / "synthetic_data.json"
    ext_path = DATA_DIR / "synthetic" / "ner_training_extended.json"
    output_dir = DATA_DIR / "student_training"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_pseudo_path = output_dir / "ner_pseudo_labels.json"
    cache_path = output_dir / ".ner_cache.json"

    # Load data sources
    with open(orig_path, "r", encoding="utf-8") as f:
        orig_data = json.load(f)

    ext_data = []
    if ext_path.exists():
        with open(ext_path, "r", encoding="utf-8") as f:
            ext_data = json.load(f)
        logger.info(f"Loaded {len(ext_data)} extended samples from {ext_path}")

    all_data = orig_data + ext_data
    logger.info(f"Combined total dataset size: {len(all_data)} sentences")

    # Load cache
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
    total_samples = len(all_data)

    for idx, sample in enumerate(all_data, 1):
        sample_id = sample.get("id") or f"syn_{idx:03d}"
        text = sample["text"]

        logger.info(f"Processing [{idx}/{total_samples}] {sample_id}...")

        dict_preds = [sanitize_candidate(text, c) for c in dict_ner.extract_entities(text)]
        phobert_preds = [sanitize_candidate(text, c) for c in phobert_ner.extract_entities(text)]

        if sample_id in cache:
            raw_llm_preds = cache[sample_id]
        else:
            raw_llm_preds = llm_ner.extract_entities(text)
            cache[sample_id] = raw_llm_preds
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

    # Save full pseudo labels JSON
    with open(output_pseudo_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved extended pseudo labels to {output_pseudo_path}")

    # Perform Stratified Split
    split_assignment = stratified_split(records, train_ratio=0.70, dev_ratio=0.15, seed=42)

    ner_splits = {'train': [], 'dev': [], 'test': []}
    for sample in records:
        sid = sample['sample_id']
        split_name = split_assignment.get(sid, 'train')
        sentence = sample['text']
        entities = sample['entities']
        conll_tuples = generate_bio_tags(sentence, entities)
        ner_splits[split_name].append({
            'sample_id': sid,
            'sentence': sentence,
            'entities': entities,
            'conll': conll_tuples
        })

    # Export CoNLL files
    for split_name, samples in ner_splits.items():
        out_file = output_dir / f"ner_{split_name}.conll"
        with open(out_file, 'w', encoding='utf-8') as f:
            for s in samples:
                f.write(f"# id = {s['sample_id']}\n")
                f.write(f"# text = {s['sentence']}\n")
                for tok, tag in s['conll']:
                    f.write(f"{tok}\t{tag}\n")
                f.write("\n")
        logger.info(f"✓ Exported {out_file} ({len(samples)} sentences)")

    # Print Summary Statistics
    print("\n" + "="*70)
    print("BƯỚC 3: THỐNG KÊ DATASET MỞ RỘNG CO NLL-2003 (EXTENDED NER DATASET)")
    print("="*70)

    total_all_tokens = 0
    total_all_o = 0
    total_all_nono = 0

    split_entity_counts = {}

    for split_name in ['train', 'dev', 'test']:
        samples = ner_splits[split_name]
        total_sents = len(samples)
        
        all_tokens = [tok for s in samples for tok, tag in s['conll']]
        all_tags = [tag for s in samples for tok, tag in s['conll']]
        
        o_count = sum(1 for tag in all_tags if tag == 'O')
        nono_count = len(all_tags) - o_count
        
        total_all_tokens += len(all_tokens)
        total_all_o += o_count
        total_all_nono += nono_count

        span_counts = Counter()
        for s in samples:
            for e in s['entities']:
                lbl = e.get('label') or e.get('type')
                span_counts[lbl] += 1

        split_entity_counts[split_name] = span_counts

        print(f"\n--- Split: {split_name.upper()} ---")
        print(f"  - Số câu (Sentences): {total_sents}")
        print(f"  - Total Tokens      : {len(all_tokens)}")
        print(f"  - O Tokens          : {o_count} ({(o_count/len(all_tokens))*100:.1f}%)")
        print(f"  - Non-O Tokens      : {nono_count} ({(nono_count/len(all_tokens))*100:.1f}%)")
        print("  - Phân phối Entity Spans:")
        for lbl, scnt in span_counts.most_common():
            print(f"      * {lbl:<15}: {scnt:>3} mẫu")

    print("\n" + "="*70)
    print("SO SÁNH RIÊNG NHÃN 'PROCEDURE' (TRƯỚC VS SAU MỞ RỘNG):")
    print("="*70)
    print(f"  - Train PROCEDURE: Trước = 10  ===> SAU MỞ RỘNG = {split_entity_counts['train'].get('PROCEDURE', 0)}")
    print(f"  - Dev   PROCEDURE: Trước =  2  ===> SAU MỞ RỘNG = {split_entity_counts['dev'].get('PROCEDURE', 0)}")
    print(f"  - Test  PROCEDURE: Trước =  3  ===> SAU MỞ RỘNG = {split_entity_counts['test'].get('PROCEDURE', 0)}")
    total_proc = sum(split_entity_counts[s].get('PROCEDURE', 0) for s in ['train', 'dev', 'test'])
    print(f"  - TỔNG PROCEDURE : Trước = 15  ===> SAU MỞ RỘNG = {total_proc}")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_export()
