import json
import re
from collections import Counter
from typing import List, Dict, Tuple, Any

INVALID_PROC_TEXTS = {"men gan", "hemoglobin", "inr"}

def tokenize_with_spans(text: str) -> List[Tuple[str, int, int]]:
    """
    Tokenizes text into words and punctuation while tracking (token_str, start_char, end_char).
    """
    tokens = []
    # Match words or non-whitespace punctuation/symbols
    for match in re.finditer(r'\w+|[^\w\s]', text, re.UNICODE):
        token_str = match.group(0)
        start, end = match.span()
        tokens.append((token_str, start, end))
    return tokens

def generate_bio_tags(text: str, entities: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    """
    Generates (token, bio_tag) pairs for a given text and its entity annotations.
    """
    tokens_with_spans = tokenize_with_spans(text)
    
    # Filter out invalid procedure entities
    valid_entities = []
    for e in entities:
        lbl = e.get('label') or e.get('type')
        etxt = e['text'].strip().lower()
        if lbl == 'PROCEDURE' and etxt in INVALID_PROC_TEXTS:
            continue
        valid_entities.append(e)

    # Sort entities by start index
    valid_entities.sort(key=lambda x: x['start'])

    bio_labels = ['O'] * len(tokens_with_spans)

    for ent in valid_entities:
        lbl = ent.get('label') or ent.get('type')
        estart = ent['start']
        eend = ent['end']
        
        # Find tokens that overlap with this entity span
        overlapping_indices = []
        for idx, (tstr, tstart, tend) in enumerate(tokens_with_spans):
            # Token overlaps if max(tstart, estart) < min(tend, eend)
            if max(tstart, estart) < min(tend, eend):
                overlapping_indices.append(idx)

        if overlapping_indices:
            first_idx = overlapping_indices[0]
            bio_labels[first_idx] = f"B-{lbl}"
            for o_idx in overlapping_indices[1:]:
                bio_labels[o_idx] = f"I-{lbl}"

    res = [(tokens_with_spans[i][0], bio_labels[i]) for i in range(len(tokens_with_spans))]
    return res

def main():
    # Load NER pseudo labels
    with open('data/student_training/ner_pseudo_labels.json', 'r', encoding='utf-8') as f:
        ner_data = json.load(f)

    # Load split assignment from Step 2f
    with open('scratch/sample_split_assignment.json', 'r', encoding='utf-8') as f:
        split_assignment = json.load(f)

    # Clean NER pseudo labels: remove invalid PROCEDURE entities and save cleaned version
    cleaned_ner_data = []
    for sample in ner_data:
        cleaned_ents = []
        for e in sample.get('entities', []):
            lbl = e.get('label') or e.get('type')
            etxt = e['text'].strip().lower()
            if lbl == 'PROCEDURE' and etxt in INVALID_PROC_TEXTS:
                continue
            cleaned_ents.append(e)
        sample['entities'] = cleaned_ents
        cleaned_ner_data.append(sample)

    with open('data/student_training/ner_pseudo_labels.json', 'w', encoding='utf-8') as f:
        json.dump(cleaned_ner_data, f, ensure_ascii=False, indent=2)

    print("✓ Filtered invalid PROCEDURE entities from ner_pseudo_labels.json.")

    ner_splits = {'train': [], 'dev': [], 'test': []}

    for sample in cleaned_ner_data:
        sid = sample['sample_id']
        split_name = split_assignment.get(sid, 'train')
        
        sentence = sample['text']
        entities = sample.get('entities', [])
        
        conll_tuples = generate_bio_tags(sentence, entities)
        ner_splits[split_name].append({
            'sample_id': sid,
            'sentence': sentence,
            'entities': entities,
            'conll': conll_tuples
        })

    # Save CoNLL files
    for split_name, samples in ner_splits.items():
        out_file = f"data/student_training/ner_{split_name}.conll"
        with open(out_file, 'w', encoding='utf-8') as f:
            for s in samples:
                f.write(f"# id = {s['sample_id']}\n")
                f.write(f"# text = {s['sentence']}\n")
                for tok, tag in s['conll']:
                    f.write(f"{tok}\t{tag}\n")
                f.write("\n")
        print(f"✓ Saved {out_file} ({len(samples)} sentences)")

    # CoNLL Statistics
    print("\n" + "="*60)
    print("STEP 3d: CoNLL-2003 NER STATISTICS")
    print("="*60)

    total_all_tokens = 0
    total_all_o = 0
    total_all_nono = 0

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

        # Count entity spans by label
        span_counts = Counter()
        for s in samples:
            for e in s['entities']:
                lbl = e.get('label') or e.get('type')
                span_counts[lbl] += 1

        print(f"\n--- Split: {split_name.upper()} ---")
        print(f"  - Sentences         : {total_sents}")
        print(f"  - Total Tokens      : {len(all_tokens)}")
        print(f"  - O Tokens          : {o_count} ({(o_count/len(all_tokens))*100:.1f}%)")
        print(f"  - Non-O Tokens      : {nono_count} ({(nono_count/len(all_tokens))*100:.1f}%)")
        print("  - Entity Spans Count:")
        for lbl, scnt in span_counts.most_common():
            print(f"      * {lbl:<15}: {scnt:>3}")

    print("\n--- OVERALL NER DATASET SUMMARY ---")
    print(f"  - Total Sentences   : {len(cleaned_ner_data)}")
    print(f"  - Total Tokens      : {total_all_tokens}")
    print(f"  - O Tokens Ratio    : {total_all_o} / {total_all_tokens} ({(total_all_o/total_all_tokens)*100:.1f}%)")
    print(f"  - Non-O Tokens Ratio: {total_all_nono} / {total_all_tokens} ({(total_all_nono/total_all_tokens)*100:.1f}%)")
    print("="*60)

if __name__ == "__main__":
    main()
