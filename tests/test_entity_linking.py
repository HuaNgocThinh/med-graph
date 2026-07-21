"""
Unit tests for Entity Linking modules and RapidFuzz matching.
"""

import pytest
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.rxnorm_linker import RxNormLinker
from src.entity_linking.fuzzy_matcher import FuzzyMatcher

def test_icd10_exact_and_fuzzy_linking():
    linker = ICD10Linker()
    
    exact_res = linker.link_disease("Cao huyết áp")
    assert exact_res["code"] == "I10"
    assert exact_res["method"] == "exact"
    
    fuzzy_res = linker.link_disease("bệnh tiểu đường tuýp 2")
    assert fuzzy_res["code"] == "E11"
    assert fuzzy_res["method"] in ["exact", "fuzzy"]

def test_rxnorm_linking():
    linker = RxNormLinker()
    
    res = linker.link_drug("Paracetamol 500mg")
    assert "161" in res["code"]
    assert res["method"] in ["exact", "fuzzy", "rxnav_api"]

def test_fuzzy_matcher_threshold():
    matcher = FuzzyMatcher(score_cutoff=70.0)
    choices = [{"name_vi": "Viêm họng cấp", "synonyms": []}]
    
    res = matcher.find_best_match("viêm họng", choices)
    assert res is not None
    item, score = res
    assert item["name_vi"] == "Viêm họng cấp"
    assert score >= 0.70
