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

def test_i10_alias_entry_is_load_bearing():
    """
    Decision QĐ1. I10's name_vi is now the standard term "Tăng huyết áp"; the corpus, in all
    3 samples that mention it (syn_001, syn_011, syn_052), writes "Cao huyết áp" and never
    "tăng huyết áp". Principle 6: the node name is anchored to the CORPUS, the code to an
    AUTHORITATIVE standard. Two different authorities, two different fields.

    ICD10Linker returns `get_canonical_name(rec["name_vi"])` as the node name, so the only
    thing keeping those two apart is ALIAS_MAP["tăng huyết áp"] = "Cao huyết áp". Delete that
    line as "redundant" and the node silently renames itself to the dictionary term -- the
    exact mechanism by which the node 'Viêm dạ dày' became 'Viêm loét dạ dày' in commit
    e64df49 while keeping K29.7, a code that belongs to a different disease.

    This test exists so that deletion fails loudly instead of drifting silently.
    """
    linker = ICD10Linker()
    for surface in ("Cao huyết áp", "cao huyết áp", "Tăng huyết áp", "tăng huyết áp",
                    "Bệnh cao huyết áp"):
        res = linker.link_disease(surface)
        assert res["code"] == "I10", f"{surface}: {res}"
        assert res["standard_name"] == "Cao huyết áp", (
            f"{surface!r} produced node name {res['standard_name']!r}. The node must keep the "
            f"corpus form 'Cao huyết áp'; check ALIAS_MAP['tăng huyết áp'] still exists."
        )


def test_i10_records_the_authoritative_term_separately():
    """
    The precise WHO/BYT term for I10 is 'Tăng huyết áp vô căn (nguyên phát)' -- I10 is
    ESSENTIAL (primary) hypertension, distinct from I15 secondary hypertension. It is stored
    in name_vi_full rather than name_vi, because name_vi doubles as the node name and that
    string appears nowhere in the corpus. See docs/ontology_freeze.md.
    """
    import json
    from src.config import ICD10_DICT_PATH
    from src.entity_linking.dict_loader import load_records
    rec = [r for r in load_records(ICD10_DICT_PATH) if r["code"] == "I10"][0]
    assert rec["name_vi"] == "Tăng huyết áp"
    assert rec["name_vi_full"] == "Tăng huyết áp vô căn (nguyên phát)"
    assert rec["name_en"] == "Essential (primary) hypertension"
    assert "cao huyết áp" in rec["synonyms"], "the corpus surface form must stay reachable"


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
