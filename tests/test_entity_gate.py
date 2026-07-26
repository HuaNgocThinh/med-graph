"""
Unit tests for the generic-entity gate and the fuzzy length guard.

Each test reproduces a defect observed live against Neo4j:

  * 'viêm', lifted by NER out of "giảm viêm"/"kháng viêm", fuzzy-matched to 'Viêm phổi'
    (J18.9) at 0.90 and produced three false 'Meloxicam -PRESCRIBED_FOR-> Viêm phổi' edges
    from samples syn_080/089/091, none of which mention pneumonia at all.
  * 'đau' was already in the linker's stop list, yet a :DISEASE node named 'đau' still got
    built: the stop-word branch returned a dict that still carried a usable standard_name,
    and run_pipeline's `head_info.get("standard_name") or item.get("head")` fell back to the
    raw NER string. The gate has to be enforced at the write path, not only in the linker.
  * MERGE keys on (label, name), so the same name under a different label silently created a
    second node -- a :SYMPTOM 'Viêm loét dạ dày' appeared beside the real :DISEASE one.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.entity_linking.entity_normalizer import is_generic_term
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.fuzzy_matcher import FuzzyMatcher
from src.graph.graph_builder import GraphBuilder


# --- Item 1e: these four must never link ---

def test_generic_terms_are_rejected_by_linker():
    linker = ICD10Linker()
    for term in ("viêm", "đau", "sốt", "bệnh"):
        res = linker.link_disease(term)
        assert res["method"] == "rejected_generic", f"{term}: {res}"
        # Item 3: 'not linked' is null, never the shared string 'ICD-UNKNOWN'. A sentinel
        # made 'REQUIRE code IS UNIQUE' impossible to create, because every unlinked node
        # held the same value and therefore counted as a duplicate.
        assert res["code"] is None, f"{term}: {res}"
        # the crucial part: no usable name may leak back to the caller
        assert not res["standard_name"], (
            f"{term!r} returned standard_name={res['standard_name']!r}; run_pipeline would "
            f"fall back to it and build a node anyway."
        )


def test_viem_no_longer_matches_viem_phoi():
    """The exact defect behind the 3 false Meloxicam edges."""
    res = ICD10Linker().link_disease("viêm")
    assert res["code"] != "J18.9"


def test_therapeutic_intent_phrases_are_rejected():
    """'giảm viêm'/'kháng viêm'/'giảm đau' describe why a drug was given, not a diagnosis."""
    linker = ICD10Linker()
    for term in ("giảm viêm", "kháng viêm", "giảm đau", "hạ sốt"):
        assert linker.link_disease(term)["method"] == "rejected_generic", term


def test_gate_sees_through_disease_prefixes():
    """'Bệnh viêm' must not slip past a check that only knew the bare word."""
    for term in ("Bệnh viêm", "tình trạng viêm", "chứng đau", "Hội chứng viêm"):
        assert is_generic_term(term, "DISEASE"), term


# --- Type awareness: the gate must not destroy legitimate symptom nodes ---

def test_gate_is_type_aware():
    """
    'sốt' and 'ho' are real SYMPTOM nodes in the graph but are never diagnoses. A blanket
    stop list would have deleted correct data; the DISEASE/SYMPTOM split is what prevents that.
    """
    for term in ("sốt", "ho", "đau", "khó thở", "ợ nóng"):
        assert is_generic_term(term, "DISEASE"), f"{term} must be blocked as a DISEASE"
        assert not is_generic_term(term, "SYMPTOM"), f"{term} must be allowed as a SYMPTOM"


def test_never_an_entity_is_blocked_under_every_label():
    """Meta words and contentless pathological processes are invalid under any label."""
    for term in ("bệnh", "viêm", "triệu chứng", "chẩn đoán", "nhiễm"):
        assert is_generic_term(term, "DISEASE"), term
        assert is_generic_term(term, "SYMPTOM"), term


def test_real_clinical_terms_pass_the_gate():
    for term in ("Đái tháo đường týp 2", "tiểu đường", "Viêm phổi", "Viêm loét dạ dày",
                 "Thoái hóa khớp gối", "Rối loạn lipid máu", "Sốt cao", "Đau thượng vị"):
        assert not is_generic_term(term, "DISEASE"), term


def test_real_terms_still_link_after_the_gate():
    linker = ICD10Linker()
    for term, code in [("tiểu đường", "E11"), ("cao huyết áp", "I10"),
                       ("tan máu bẩm sinh", "D56.9"), ("Viêm phổi", "J18.9"),
                       ("mỡ máu cao", "E78.5")]:
        assert linker.link_disease(term)["code"] == code, term


# --- Fuzzy length guard ---

def test_fuzzy_length_guard_blocks_short_query_against_long_candidate():
    """
    WRatio falls back to partial_ratio on length-skewed pairs, scoring ANY substring ~90.
    Measured separation across all 302 terms: legitimate fuzzy hits sit at >=0.62,
    bogus fragments at <=0.56.
    """
    m = FuzzyMatcher()
    choices = [{"code": "J18.9", "name_vi": "Viêm phổi", "synonyms": ["viêm phế quản phổi"]}]
    assert m.find_best_match("viêm", choices) is None


def test_fuzzy_length_guard_still_allows_legitimate_match():
    m = FuzzyMatcher()
    choices = [{"code": "E11", "name_vi": "Đái tháo đường týp 2", "synonyms": ["bệnh tiểu đường"]}]
    assert m.find_best_match("tiểu đường", choices) is not None


# --- Write-path enforcement (the choke point) ---

class _FakeClient:
    """Records writes instead of performing them, and can pretend nodes already exist."""

    def __init__(self, existing=None):
        self.existing = existing or []   # list of {"name":..., "labels":[...]}
        self.writes = []

    def execute_query(self, query, parameters=None):
        # Snapshot reads used by the write-path guards are not writes.
        if "RETURN n.name AS name, labels(n) AS labels" in query:
            return self.existing
        if "n.code AS code" in query:
            return []
        self.writes.append((query, parameters or {}))
        return []


def _triple(head, tail, head_type, tail_type, rel="PRESCRIBED_FOR", sid="syn_test"):
    return {
        "head": head, "tail": tail, "relation": rel, "confidence": 0.9,
        "head_info": {"standard_name": head, "code": "X", "type": head_type},
        "tail_info": {"standard_name": tail, "code": "Y", "type": tail_type},
        "negated": False, "temporal_context": "present", "source_sample_id": sid,
    }


def test_graph_builder_refuses_to_write_generic_entity():
    """
    Even when the linker is bypassed and a raw generic string arrives with a valid-looking
    type, the write path must refuse. This is the guarantee the linker alone could not give.
    """
    client = _FakeClient()
    GraphBuilder(neo4j_client=client).build_graph(
        [_triple("Meloxicam 15mg", "viêm", "DRUG", "DISEASE")]
    )
    assert client.writes == [], f"generic tail was written: {client.writes}"


def test_graph_builder_writes_a_legitimate_triple():
    client = _FakeClient()
    GraphBuilder(neo4j_client=client).build_graph(
        [_triple("Metformin", "Đái tháo đường týp 2", "DRUG", "DISEASE")]
    )
    assert len(client.writes) == 1


def test_graph_builder_refuses_label_conflict():
    """Same name under a different label must not silently create a second node."""
    client = _FakeClient(existing=[{"name": "Viêm loét dạ dày", "labels": ["DISEASE"]}])
    GraphBuilder(neo4j_client=client).build_graph(
        [_triple("Omeprazole 20mg", "Viêm loét dạ dày", "DRUG", "SYMPTOM", rel="TREATS")]
    )
    assert client.writes == [], f"label conflict was written: {client.writes}"


def test_graph_builder_allows_same_label_merge():
    """A matching label is a normal MERGE and must still go through."""
    client = _FakeClient(existing=[{"name": "Viêm loét dạ dày", "labels": ["DISEASE"]}])
    GraphBuilder(neo4j_client=client).build_graph(
        [_triple("Omeprazole 20mg", "Viêm loét dạ dày", "DRUG", "DISEASE")]
    )
    assert len(client.writes) == 1
