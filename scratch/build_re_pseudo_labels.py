import json
import random
from collections import Counter
from typing import List, Dict, Any
from src.graph.neo4j_client import Neo4jClient
from src.entity_linking.entity_normalizer import get_canonical_name

INVALID_PROC_TEXTS = {"men gan", "hemoglobin", "inr"}

def match_ent(candidates, ents, target_label):
    cands = [c.strip().lower() for c in candidates if c]
    # 1. Exact or substring match
    for e in ents:
        et = e['text'].strip().lower()
        if any(c == et or c in et or et in c for c in cands):
            return e
    # 2. Canonical name match
    for e in ents:
        ec = get_canonical_name(e['text']).strip().lower()
        if any(get_canonical_name(c).strip().lower() == ec for c in cands):
            return e
    # 3. Label matching with token overlap
    for e in ents:
        if (e.get('label') or e.get('type')) == target_label:
            et_words = set(e['text'].strip().lower().split())
            for c in cands:
                c_words = set(c.split())
                if len(et_words.intersection(c_words)) >= 1:
                    return e
    return None

def main():
    client = Neo4jClient()
    if not client.is_online():
        print("Neo4j offline!")
        return

    # Load NER pseudo labels to map samples and exact entity spans
    with open('data/student_training/ner_pseudo_labels.json', 'r', encoding='utf-8') as f:
        ner_data = json.load(f)

    sample_map = {s['sample_id']: s for s in ner_data}

    # Fetch all relationships from Neo4j
    rows = client.execute_query("""
    MATCH (n1)-[r]->(n2)
    RETURN labels(n1)[0] AS head_label, n1.name AS head_name, type(r) AS relation,
           labels(n2)[0] AS tail_label, n2.name AS tail_name, r.confidence AS confidence,
           r.negated AS negated, r.source_sample_id AS sample_id,
           r.head_surface AS head_surface, r.tail_surface AS tail_surface, r.temporal AS temporal
    """)

    positive_records = []
    positive_pair_keys = set() # (sample_id, start1, end1, start2, end2, relation)

    for r in rows:
        sids = [s.strip() for s in (r['sample_id'] or '').split(',') if s.strip()]
        for sid in sids:
            sample = sample_map.get(sid)
            if not sample:
                continue

            ents = sample.get('entities', [])
            
            # Exclude invalid PROCEDURE entities
            if r['head_label'] == 'PROCEDURE' and (r['head_surface'] or r['head_name']).lower() in INVALID_PROC_TEXTS:
                continue
            if r['tail_label'] == 'PROCEDURE' and (r['tail_surface'] or r['tail_name']).lower() in INVALID_PROC_TEXTS:
                continue

            h_cand = [r['head_surface'], r['head_name']]
            t_cand = [r['tail_surface'], r['tail_name']]

            h_ent = match_ent(h_cand, ents, r['head_label'])
            t_ent = match_ent(t_cand, ents, r['tail_label'])

            if h_ent and t_ent:
                key = (sid, h_ent['start'], h_ent['end'], t_ent['start'], t_ent['end'], r['relation'])
                if key in positive_pair_keys:
                    continue
                positive_pair_keys.add(key)

                record = {
                    "sample_id": sid,
                    "sentence": sample['text'],
                    "entity_1": {
                        "text": h_ent['text'],
                        "label": h_ent['label'],
                        "start": h_ent['start'],
                        "end": h_ent['end']
                    },
                    "entity_2": {
                        "text": t_ent['text'],
                        "label": t_ent['label'],
                        "start": t_ent['start'],
                        "end": t_ent['end']
                    },
                    "relation": r['relation'],
                    "confidence": float(r['confidence']) if r['confidence'] is not None else 0.95,
                    "negated": bool(r['negated']),
                    "temporal": r['temporal'] or "present",
                    "head_surface": h_ent['text'],
                    "tail_surface": t_ent['text']
                }
                positive_records.append(record)

    num_positive = len(positive_records)
    print(f"Total positive relation records extracted: {num_positive}")

    # Calculate NONE count needed: 30% of total -> NONE_count = round(num_positive * 30 / 70)
    target_none = int(round(num_positive * 30.0 / 70.0))
    print(f"Target NONE records (30% of total): {target_none}")

    # Set of connected entity pairs (ignoring relation type) for NONE generation
    connected_pair_spans = {(k[0], k[1], k[2], k[3], k[4]) for k in positive_pair_keys}

    # Generate Candidate NONE records from entity pairs in same sentence without relation
    p1_candidates = [] # (PROCEDURE, DISEASE) -> procedure_mismatch
    p2_candidates = [] # (DRUG, DISEASE) -> co_occurrence
    p3_candidates = [] # (DRUG, SYMPTOM) -> co_occurrence / different_context
    p4_candidates = [] # other pairs -> different_context

    for sample in ner_data:
        sid = sample['sample_id']
        stext = sample['text']
        ents = sample.get('entities', [])
        
        # Filter valid entities (skip invalid procedures)
        valid_ents = [e for e in ents if not (e.get('label') == 'PROCEDURE' and e['text'].lower() in INVALID_PROC_TEXTS)]

        for i in range(len(valid_ents)):
            for j in range(len(valid_ents)):
                if i == j:
                    continue
                e1 = valid_ents[i]
                e2 = valid_ents[j]
                
                # Check if this pair already has a positive relation (forward or reverse)
                k1 = (sid, e1['start'], e1['end'], e2['start'], e2['end'])
                k2 = (sid, e2['start'], e2['end'], e1['start'], e1['end'])
                if k1 in connected_pair_spans or k2 in connected_pair_spans:
                    continue

                l1 = e1.get('label') or e1.get('type')
                l2 = e2.get('label') or e2.get('type')

                none_record = {
                    "sample_id": sid,
                    "sentence": stext,
                    "entity_1": {
                        "text": e1['text'],
                        "label": l1,
                        "start": e1['start'],
                        "end": e1['end']
                    },
                    "entity_2": {
                        "text": e2['text'],
                        "label": l2,
                        "start": e2['start'],
                        "end": e2['end']
                    },
                    "relation": "NONE",
                    "confidence": 1.0,
                    "negated": False,
                    "temporal": "present",
                    "head_surface": e1['text'],
                    "tail_surface": e2['text'],
                    "none_reason": ""
                }

                if (l1 == 'PROCEDURE' and l2 == 'DISEASE') or (l1 == 'DISEASE' and l2 == 'PROCEDURE'):
                    none_record['none_reason'] = "procedure_mismatch"
                    p1_candidates.append(none_record)
                elif (l1 == 'DRUG' and l2 == 'DISEASE') or (l1 == 'DISEASE' and l2 == 'DRUG'):
                    none_record['none_reason'] = "co_occurrence"
                    p2_candidates.append(none_record)
                elif (l1 == 'DRUG' and l2 == 'SYMPTOM') or (l1 == 'SYMPTOM' and l2 == 'DRUG'):
                    none_record['none_reason'] = "different_context"
                    p3_candidates.append(none_record)
                else:
                    none_record['none_reason'] = "different_context"
                    p4_candidates.append(none_record)

    # Select NONE records according to priority
    random.seed(42)
    random.shuffle(p1_candidates)
    random.shuffle(p2_candidates)
    random.shuffle(p3_candidates)
    random.shuffle(p4_candidates)

    selected_none = []
    # Fill from Priority 1 (PROCEDURE - DISEASE mismatch)
    take_p1 = p1_candidates[:min(len(p1_candidates), target_none)]
    selected_none.extend(take_p1)

    # Fill remaining from Priority 2 (DRUG - DISEASE co-occurrence)
    needed = target_none - len(selected_none)
    if needed > 0:
        take_p2 = p2_candidates[:min(len(p2_candidates), needed)]
        selected_none.extend(take_p2)

    # Fill remaining from Priority 3 (DRUG - SYMPTOM)
    needed = target_none - len(selected_none)
    if needed > 0:
        take_p3 = p3_candidates[:min(len(p3_candidates), needed)]
        selected_none.extend(take_p3)

    # Fill remaining from Priority 4 (Others)
    needed = target_none - len(selected_none)
    if needed > 0:
        take_p4 = p4_candidates[:min(len(p4_candidates), needed)]
        selected_none.extend(take_p4)

    all_records = positive_records + selected_none

    print(f"Selected NONE records: {len(selected_none)}")
    print(f"Total dataset size (Positive + NONE): {len(all_records)}")

    # Save to data/student_training/re_pseudo_labels.json
    out_path = "data/student_training/re_pseudo_labels.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)
    print(f"Successfully saved {len(all_records)} records to {out_path}")

    # Statistics reporting for 2e
    counts = Counter([r['relation'] for r in all_records])
    none_reasons = Counter([r['none_reason'] for r in selected_none if r.get('none_reason')])

    max_cnt = max(counts.values())
    min_cnt = min(counts.values())
    imbalance_ratio = max_cnt / min_cnt if min_cnt > 0 else 0

    proc_rel_cnt = counts.get('PERFORMED_FOR', 0)

    print("\n" + "="*50)
    print("RE PSEUDO-LABELS STATISTICS (STEP 2e)")
    print("="*50)
    print(f"Total Records: {len(all_records)}")
    print("\nLabel Distribution:")
    for rel, cnt in counts.most_common():
        pct = (cnt / len(all_records)) * 100
        print(f"  - {rel:<20}: {cnt:>3} ({pct:>5.1f}%)")

    print(f"\nImbalance Ratio (Max / Min): {max_cnt} / {min_cnt} = {imbalance_ratio:.2f}")
    print(f"PROCEDURE-related PERFORMED_FOR records: {proc_rel_cnt}")
    print(f"NONE records count: {len(selected_none)} ({(len(selected_none)/len(all_records))*100:.1f}%)")
    print("\nNONE Reason Distribution:")
    for reason, rcnt in none_reasons.most_common():
        print(f"  - {reason:<20}: {rcnt:>3}")
    print("="*50)

if __name__ == "__main__":
    main()
