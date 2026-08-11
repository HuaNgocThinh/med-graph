"""
Unit tests for NER modules and ensemble voting logic.
"""

import pytest
from src.ner.dictionary_ner import DictionaryNER
from src.ner.phobert_crf_ner import PhoBertCRFNER
from src.ner.ner_ensemble import NEREnsemble

def test_dictionary_ner_extraction():
    dict_ner = DictionaryNER()
    sample = "Bệnh nhân bị Cao huyết áp và dùng Paracetamol."
    entities = dict_ner.extract_entities(sample)
    
    assert len(entities) >= 2
    types = [e["type"] for e in entities]
    assert "DISEASE" in types
    assert "DRUG" in types

def test_phobert_crf_ner_extraction():
    phobert_ner = PhoBertCRFNER()
    sample = "Bệnh nhân bị Viêm họng cấp, uống Paracetamol 500mg."
    entities = phobert_ner.extract_entities(sample)
    
    assert isinstance(entities, list)
    assert any(e["entity"] == "Viêm họng cấp" for e in entities)

def test_ner_ensemble_priority():
    ensemble = NEREnsemble()
    sample = "Bệnh nhân mắc Đái tháo đường týp 2 và dùng Metformin."
    entities = ensemble.extract_entities(sample)
    
    assert len(entities) > 0
    # Verify span boundary order
    for i in range(len(entities) - 1):
        assert entities[i]["end"] <= entities[i+1]["start"] or entities[i]["start"] < entities[i+1]["start"]
