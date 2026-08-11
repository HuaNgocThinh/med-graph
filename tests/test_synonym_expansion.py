"""
Unit tests for get_term_synonyms() function.
Verifies bidirectional medical synonym mapping expansion for Vietnamese terms.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.entity_linking.entity_normalizer import get_term_synonyms, SYNONYM_CLASSES

def test_get_term_synonyms_diabetes():
    syns = get_term_synonyms("Tiểu đường type 2")
    # Verify that the canonical Vietnamese medical term "Đái tháo đường týp 2" is found
    assert "Đái tháo đường týp 2" in syns
    assert "đái tháo đường tuýp 2" in syns

def test_get_term_synonyms_hypertension():
    syns = get_term_synonyms("Cao huyết áp")
    assert "tăng huyết áp" in syns
    assert "Tăng huyết áp" in syns

def test_get_term_synonyms_stomachache():
    syns = get_term_synonyms("Đau bao tử")
    assert "đau dạ dày" in syns
    assert "Đau dạ dày" in syns

def test_get_term_synonyms_heart_attack():
    syns = get_term_synonyms("Đau tim")
    assert "nhồi máu cơ tim" in syns
    assert "Nhồi máu cơ tim" in syns


def test_sibling_folk_terms_are_mutually_reachable():
    # Root-cause regression: two folk terms sharing one canonical concept
    # ('đau bao tử' and 'đau dạ dày' both -> 'viêm loét dạ dày') must reach EACH OTHER,
    # not only the canonical. Pairwise 1-1 mapping used to break this link.
    from_bao_tu = get_term_synonyms("Đau bao tử")
    assert "đau dạ dày" in from_bao_tu
    assert "viêm loét dạ dày" in from_bao_tu

    from_da_day = get_term_synonyms("đau dạ dày")
    assert "đau bao tử" in from_da_day
    assert "viêm loét dạ dày" in from_da_day


def test_synonym_classes_are_transitively_closed():
    # Every member of an equivalence class must map to the SAME complete set of members,
    # guaranteeing symmetry + transitivity regardless of how pairs are declared in the JSON.
    for term, members in SYNONYM_CLASSES.items():
        assert term in members
        for other in members:
            assert SYNONYM_CLASSES[other] == members
