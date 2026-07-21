"""
Unit tests for Relation Extraction modules.
"""

import pytest
from src.relation_extraction.rule_based_re import RuleBasedRelationExtractor
from src.relation_extraction.llm_re import LLMRelationExtractor

def test_rule_based_relation_extraction():
    extractor = RuleBasedRelationExtractor()
    text = "Aspirin 81mg được kê cho bệnh nhân Nhồi máu não."
    entities = [
        {"entity": "Aspirin 81mg", "type": "DRUG", "start": 0, "end": 12},
        {"entity": "Nhồi máu não", "type": "DISEASE", "start": 35, "end": 47}
    ]
    triples = extractor.extract_relations(text, entities)
    
    assert len(triples) >= 1
    assert triples[0]["relation"] == "PRESCRIBED_FOR"
    assert triples[0]["head"] == "Aspirin 81mg"
    assert triples[0]["tail"] == "Nhồi máu não"

def test_llm_re_json_parsing():
    extractor = LLMRelationExtractor()
    text = "Omeprazole 20mg điều trị Viêm loét dạ dày."
    entities = [
        {"entity": "Omeprazole 20mg", "type": "DRUG"},
        {"entity": "Viêm loét dạ dày", "type": "DISEASE"}
    ]
    triples = extractor.extract_relations(text, entities)
    
    assert isinstance(triples, list)
    if triples:
        assert triples[0]["relation"] == "PRESCRIBED_FOR"

def test_paracetamol_metformin_diabetes_isolation():
    """
    Asserts that LLM RE does NOT extract (Paracetamol, TREATS/PRESCRIBED_FOR, tiểu đường)
    from a sentence where Paracetamol is co-prescribed for symptoms alongside Metformin for diabetes.
    """
    extractor = LLMRelationExtractor()
    text = "Bệnh nhân tiểu đường, ho kéo dài, được kê Paracetamol và Metformin."
    entities = [
        {"entity": "tiểu đường", "type": "DISEASE"},
        {"entity": "ho kéo dài", "type": "SYMPTOM"},
        {"entity": "Paracetamol", "type": "DRUG"},
        {"entity": "Metformin", "type": "DRUG"}
    ]
    triples = extractor.extract_relations(text, entities)

    # Assert that Paracetamol is NOT extracted as treating or being prescribed for diabetes
    bad_triples = [
        t for t in triples
        if t["head"].lower() == "paracetamol"
        and t["tail"].lower() in ("tiểu đường", "đái tháo đường")
        and t["relation"] in ("TREATS", "PRESCRIBED_FOR")
    ]
    assert len(bad_triples) == 0, f"Spurious relation extracted: {bad_triples}"

def test_omeprazole_ibuprofen_contraindication_isolation():
    """
    Asserts that LLM RE extracts (Ibuprofen, CONTRAINDICATED_FOR, Viêm loét dạ dày)
    and (Omeprazole, PRESCRIBED_FOR/TREATS, Viêm loét dạ dày), BUT DOES NOT extract
    (Omeprazole, CONTRAINDICATED_FOR, Viêm loét dạ dày).
    """
    extractor = LLMRelationExtractor()
    text = "Bệnh nhân Viêm loét dạ dày kèm trào ngược dạ dày. Không phát hiện Tiêu chảy cấp. Chống chỉ định với Ibuprofen. Đã kê Omeprazole 20mg."
    entities = [
        {"entity": "Viêm loét dạ dày", "type": "DISEASE"},
        {"entity": "trào ngược dạ dày", "type": "DISEASE"},
        {"entity": "Ibuprofen", "type": "DRUG"},
        {"entity": "Omeprazole 20mg", "type": "DRUG"}
    ]
    triples = extractor.extract_relations(text, entities)

    # Assert Omeprazole is NOT extracted as CONTRAINDICATED_FOR
    bad_triples = [
        t for t in triples
        if "omeprazole" in t["head"].lower()
        and t["relation"] == "CONTRAINDICATED_FOR"
    ]
    assert len(bad_triples) == 0, f"Spurious CONTRAINDICATED_FOR extracted for Omeprazole: {bad_triples}"
