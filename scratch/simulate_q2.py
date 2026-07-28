"""
Simulation script for Q2: Scan 96 synthetic samples and check how many triples
carry negated=True when comparing entities via get_canonical_name() instead of exact ==.
DO NOT MODIFY ANY PROJECT SOURCE FILES.
"""

import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.ner.ner_ensemble import NEREnsemble
from src.negation_temporal.context_processor import ConTextProcessor
from src.relation_extraction.llm_re import LLMRelationExtractor
from src.relation_extraction.rule_based_re import RuleBasedRelationExtractor
from src.llm_client import LLMClient
from src.entity_linking.entity_normalizer import get_canonical_name

def simulate_q2():
    data_path = BASE_DIR / "data" / "synthetic" / "synthetic_data.json"
    if not data_path.exists():
        print("synthetic_data.json not found!")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    llm_client = LLMClient(provider="mock")
    ner = NEREnsemble(llm_client=llm_client)
    context_proc = ConTextProcessor()
    llm_re = LLMRelationExtractor(llm_client=llm_client)
    rule_re = RuleBasedRelationExtractor()

    total_samples = len(samples)
    negated_triples_count = 0
    negated_examples = []

    print(f"Simulating Q2 on {total_samples} synthetic samples...")

    for sample in samples:
        sid = sample["id"]
        text = sample["text"]

        # 1. NER
        ents = ner.extract_entities(text)
        if not ents:
            continue

        # 2. ConText
        proc_ents = context_proc.process_entities(text, ents)

        # 3. RE
        llm_triples = llm_re.extract_relations(text, proc_ents)
        rule_triples = rule_re.extract_relations(text, proc_ents)
        extracted_triples = llm_triples + [r for r in rule_triples if r not in llm_triples]

        # 4. Canonical matching simulation (replacing exact == with get_canonical_name matching)
        for triple in extracted_triples:
            head_str = triple["head"]
            tail_str = triple["tail"]

            head_canon = get_canonical_name(head_str)
            tail_canon = get_canonical_name(tail_str)

            # Match using canonical name comparison
            head_ent_obj = next((e for e in proc_ents if get_canonical_name(e["entity"]) == head_canon), {})
            tail_ent_obj = next((e for e in proc_ents if get_canonical_name(e["entity"]) == tail_canon), {})

            # Exact matching (old code) vs Canonical matching (new proposal)
            old_head_obj = next((e for e in proc_ents if e["entity"] == head_str or get_canonical_name(e["entity"]) == head_str), {})
            old_tail_obj = next((e for e in proc_ents if e["entity"] == tail_str or get_canonical_name(e["entity"]) == tail_str), {})

            old_is_negated = bool(old_head_obj.get("negated", False) or old_tail_obj.get("negated", False))
            new_is_negated = bool(head_ent_obj.get("negated", False) or tail_ent_obj.get("negated", False))

            if new_is_negated:
                negated_triples_count += 1
                negated_examples.append({
                    "sample_id": sid,
                    "text": text,
                    "head": head_str,
                    "relation": triple["relation"],
                    "tail": tail_str,
                    "head_negated": head_ent_obj.get("negated", False),
                    "tail_negated": tail_ent_obj.get("negated", False),
                    "old_is_negated": old_is_negated,
                    "new_is_negated": new_is_negated
                })

    print("=" * 80)
    print(f"Q2 SIMULATION RESULTS across {total_samples} samples:")
    print(f"Total negated triples caught with canonical matching: {negated_triples_count}")
    print("=" * 80)

    print("\nConcrete Examples of Negated Triples Found:")
    for idx, ex in enumerate(negated_examples[:5], 1):
        print(f"\nExample {idx} [Sample: {ex['sample_id']}]")
        print(f"Text: '{ex['text']}'")
        print(f"Triple: ({ex['head']} -[{ex['relation']}]-> {ex['tail']})")
        print(f"Head Negated: {ex['head_negated']}, Tail Negated: {ex['tail_negated']}")
        print(f"Old Matching Result: negated={ex['old_is_negated']} -> New Canonical Matching Result: negated={ex['new_is_negated']}")

if __name__ == "__main__":
    simulate_q2()
