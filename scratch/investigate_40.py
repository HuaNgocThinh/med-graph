"""
Script for Step 4.0: Investigation of Negation / Temporal assertion pipeline.
DO NOT MODIFY ANY CODEBASE FILES IN THIS STEP.
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
from src.graph.neo4j_client import Neo4jClient

def run_investigation():
    print("=" * 80)
    print("4.0a & 4.0c & 4.0d: INVESTIGATION OF NEGATION / TEMPORAL ASSERTION FLAG")
    print("=" * 80)

    context_proc = ConTextProcessor()
    ner = NEREnsemble(llm_client=LLMClient(provider="mock"))
    llm_re = LLMRelationExtractor(llm_client=LLMClient(provider="mock"))
    rule_re = RuleBasedRelationExtractor()

    # Load syn_004 and syn_015
    annotated_path = BASE_DIR / "data" / "synthetic" / "synthetic_data.json"
    with open(annotated_path, "r", encoding="utf-8") as f:
        all_samples = json.load(f)

    corpus_samples = [s for s in all_samples if s["id"] in ("syn_004", "syn_015")]

    print("\n--- 4.0a/4.0c: CORPUS SAMPLES WITH NEGATION (syn_004, syn_015) ---")
    for sample in corpus_samples:
        sid = sample["id"]
        text = sample["text"]
        print(f"\n[SAMPLE {sid}]")
        print(f"Text: '{text}'")

        # 1. NER
        ents = ner.extract_entities(text)
        print("1. NER Entities:")
        for e in ents:
            print(f"   - {e}")

        # 2. ConText Processor
        proc_ents = context_proc.process_entities(text, ents)
        print("2. ConText Processed Entities (with negated & temporal_context):")
        for e in proc_ents:
            print(f"   - entity='{e['entity']}', type='{e['type']}', negated={e.get('negated')}, temporal={e.get('temporal_context')}")

        # 3. LLM RE
        llm_triples = llm_re.extract_relations(text, proc_ents)
        rule_triples = rule_re.extract_relations(text, proc_ents)
        print("3. LLM RE Triples:")
        for t in llm_triples:
            print(f"   - {t}")
        print("   Rule RE Triples:")
        for t in rule_triples:
            print(f"   - {t}")

        # 4. Pipeline Enriched Triple Building (run_pipeline.py logic)
        extracted_triples = llm_triples + [r for r in rule_triples if r not in llm_triples]
        print("4. Enriched Triples passed to GraphBuilder:")
        for triple in extracted_triples:
            head_str = triple["head"]
            tail_str = triple["tail"]
            head_ent_obj = next((e for e in proc_ents if e["entity"] == head_str or get_canonical_name(e["entity"]) == head_str), {})
            tail_ent_obj = next((e for e in proc_ents if e["entity"] == tail_str or get_canonical_name(e["entity"]) == tail_str), {})
            is_negated = bool(head_ent_obj.get("negated", False) or tail_ent_obj.get("negated", False))
            enriched = {
                "head": head_str,
                "relation": triple["relation"],
                "tail": tail_str,
                "negated": is_negated,
                "temporal": head_ent_obj.get("temporal_context", "unknown"),
                "head_negated": head_ent_obj.get("negated"),
                "tail_negated": tail_ent_obj.get("negated")
            }
            print(f"   - {enriched}")

    # 4.0d: 3 Test Sentences
    test_sentences = [
        "Bệnh nhân không sốt, không đau ngực.",
        "Không có tiền sử đái tháo đường.",
        "Chưa ghi nhận dị ứng thuốc."
    ]

    print("\n" + "=" * 80)
    print("4.0d: RUNNING 3 TEST SENTENCES THROUGH FULL PIPELINE")
    print("=" * 80)

    # Use mock provider for deterministic, instant execution
    real_llm = LLMClient(provider="mock")

    for idx, test_text in enumerate(test_sentences, 1):
        print(f"\n--- TEST SENTENCE {idx}: '{test_text}' ---")
        
        # STAGE B: NER Ensemble
        ner_engine = NEREnsemble(llm_client=real_llm)
        ents = ner_engine.extract_entities(test_text)
        print("STAGE B (NER Ensemble):")
        for e in ents:
            print(f"  - [{e['type']}] {e['entity']!r} (start={e['start']}, end={e['end']})")

        # STAGE C: ConText Processor
        proc_ents = context_proc.process_entities(test_text, ents)
        print("STAGE C (ConText Processor):")
        for e in proc_ents:
            print(f"  - [{e['type']}] {e['entity']!r} -> negated={e.get('negated')}, temporal={e.get('temporal_context')}")

        # STAGE D: Relation Extraction
        llm_extractor = LLMRelationExtractor(llm_client=real_llm)
        llm_triples = llm_extractor.extract_relations(test_text, proc_ents)
        rule_triples = rule_re.extract_relations(test_text, proc_ents)
        print("STAGE D (LLM RE & Rule RE):")
        print(f"  LLM Triples  : {llm_triples}")
        print(f"  Rule Triples : {rule_triples}")

        # STAGE E/F: Enriched Triples
        extracted_triples = llm_triples + [r for r in rule_triples if r not in llm_triples]
        print("STAGE E/F (Enriched Triples for GraphBuilder):")
        for triple in extracted_triples:
            head_str = triple["head"]
            tail_str = triple["tail"]
            head_ent_obj = next((e for e in proc_ents if e["entity"] == head_str or get_canonical_name(e["entity"]) == head_str), {})
            tail_ent_obj = next((e for e in proc_ents if e["entity"] == tail_str or get_canonical_name(e["entity"]) == tail_str), {})
            is_negated = bool(head_ent_obj.get("negated", False) or tail_ent_obj.get("negated", False))
            enriched = {
                "head": head_str,
                "relation": triple["relation"],
                "tail": tail_str,
                "negated": is_negated,
                "temporal": head_ent_obj.get("temporal_context", "unknown"),
                "head_negated": head_ent_obj.get("negated"),
                "tail_negated": tail_ent_obj.get("negated")
            }
            print(f"  - {enriched}")

if __name__ == "__main__":
    run_investigation()
