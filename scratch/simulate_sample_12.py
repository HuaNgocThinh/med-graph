import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import json
from src.llm_client import LLMClient
from src.ner.ner_ensemble import NEREnsemble
from src.negation_temporal.context_processor import ConTextProcessor
from src.relation_extraction.llm_re import LLMRelationExtractor
from src.relation_extraction.rule_based_re import RuleBasedRelationExtractor
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.rxnorm_linker import RxNormLinker
from src.entity_linking.entity_normalizer import get_canonical_name, normalize_disease_name

text = "Bệnh nhân nữ 42 tuổi nhập viện vì đau thượng vị. Nội soi dạ dày chẩn đoán Viêm loét dạ dày tá tràng. Bệnh nhân không có tiền sử dị ứng thuốc, hiện được chỉ định dùng Omeprazole 20mg và Amoxicillin 500mg."

llm_client = LLMClient()
ner_ensemble = NEREnsemble(llm_client=llm_client)
context_proc = ConTextProcessor()
llm_re = LLMRelationExtractor(llm_client=llm_client)
rule_re = RuleBasedRelationExtractor()
icd_linker = ICD10Linker()
rx_linker = RxNormLinker()

print("--- Running Simulation for Sample 12 ---")
entities = ner_ensemble.extract_entities(text)
print("NER Entities:", [e["entity"] for e in entities])

processed = context_proc.process_entities(text, entities)
print("ConText Entities:", [e["entity"] for e in processed])

llm_triples = llm_re.extract_relations(text, processed)
print("LLM Triples:", llm_triples)

rule_triples = rule_re.extract_relations(text, processed)
print("Rule Triples:", rule_triples)

extracted_triples = llm_triples + [r for r in rule_triples if r not in llm_triples]

sample_triples = []
for triple in extracted_triples:
    head_str = triple["head"]
    tail_str = triple["tail"]

    head_type = next((e["type"] for e in processed if e["entity"] == head_str or get_canonical_name(e["entity"]) == head_str), "Entity")
    tail_type = next((e["type"] for e in processed if e["entity"] == tail_str or get_canonical_name(e["entity"]) == tail_str), "Entity")

    if head_type == "DISEASE":
        head_link = icd_linker.link_disease(head_str)
    elif head_type in ("DRUG", "DRUG_GROUP"):
        head_link = rx_linker.link_drug(head_str)
    else:
        head_link = {"standard_name": get_canonical_name(head_str), "code": "UNKNOWN"}

    if tail_type == "DISEASE":
        tail_link = icd_linker.link_disease(tail_str)
    elif tail_type in ("DRUG", "DRUG_GROUP"):
        tail_link = rx_linker.link_drug(tail_str)
    else:
        tail_link = {"standard_name": get_canonical_name(tail_str), "code": "UNKNOWN"}

    sample_triples.append({
        "head": head_str,
        "relation": triple["relation"],
        "tail": tail_str,
        "head_link": head_link,
        "tail_link": tail_link
    })

print("Final Resolved Triples:")
for t in sample_triples:
    print(f"  ({t['head_link']['standard_name']} -[{t['relation']}]-> {t['tail_link']['standard_name']})")
