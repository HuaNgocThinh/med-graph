"""
Guards on the rebuilt RxNorm dictionary and the schema/gate invariants.

Background: 27 of the 49 RxCUIs in the original rxnorm_vi.json named a DIFFERENT drug --
Omeprazole carried 7052 (morphine), Amlodipine 4337 (fentanyl), Lisinopril 6472 (lovastatin),
and Metformin/Methotrexate shared 6809. No code in the repo has ever written that file, so the
codes never came from RxNav. These tests pin the rebuilt values so a hand-edit or a regression
cannot silently reintroduce a plausible-looking wrong id.

The RxCUIs asserted below were each obtained from RxNav and REVERSE-verified
(/rxcui/{id}/properties.json returns the expected drug). They are offline constants here on
purpose: the suite must not depend on network access.
"""

import sys
import json
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import RXNORM_DICT_PATH
from src.entity_linking.entity_normalizer import is_generic_term
from src.entity_linking.rxnorm_linker import RxNormLinker
from src.graph.graph_builder import GraphBuilder


def _dict_payload():
    with open(RXNORM_DICT_PATH, encoding="utf-8") as f:
        return json.load(f)


def _by_vi_name():
    data = _dict_payload()
    drugs = data.get("drugs", data) if isinstance(data, dict) else data
    return {d["name_vi"]: d for d in drugs}


# --- 6a: reverse-verified RxCUIs must point at the right drug ---

# name_vi -> (correct rxcui, RxNorm ingredient name, the wrong value it used to carry)
PINNED = {
    "Omeprazole 20mg":        ("7646",  "omeprazole",   "7052 (morphine)"),
    "Amlodipine 5mg":         ("17767", "amlodipine",   "4337 (fentanyl)"),
    "Lisinopril 10mg":        ("29046", "lisinopril",   "6472 (lovastatin)"),
    "Methotrexate 10mg/tuần": ("6851",  "methotrexate", "6809 (metformin)"),
    "Metformin":              ("6809",  "metformin",    "6809 (was correct)"),
}


@pytest.mark.parametrize("name_vi,expected", [(k, v) for k, v in PINNED.items()])
def test_rxcui_points_at_the_right_drug(name_vi, expected):
    rxcui, ingredient, previously = expected
    rec = _by_vi_name().get(name_vi)
    assert rec is not None, f"{name_vi} missing from the rebuilt dictionary"
    assert rec["rxcui"] == rxcui, (
        f"{name_vi}: rxcui is {rec['rxcui']!r}, expected {rxcui!r} ({ingredient}). "
        f"It previously held {previously}."
    )
    assert ingredient in rec.get("name_en", "").lower(), (
        f"{name_vi}: RxNav name {rec.get('name_en')!r} does not look like {ingredient!r}"
    )


def test_no_duplicate_rxcui():
    """Metformin and Methotrexate both carried 6809, collapsing two unrelated drugs."""
    data = _dict_payload()
    drugs = data.get("drugs", data) if isinstance(data, dict) else data
    seen = {}
    for d in drugs:
        assert d["rxcui"] not in seen, (
            f"rxcui {d['rxcui']} shared by {seen.get(d['rxcui'])!r} and {d['name_vi']!r}"
        )
        seen[d["rxcui"]] = d["name_vi"]


def test_every_record_carries_provenance():
    """A code with no recorded source is exactly what produced this whole class of bug."""
    data = _dict_payload()
    assert isinstance(data, dict) and "_provenance" in data, (
        "rxnorm_vi.json has no _provenance block; rebuild with scripts/rebuild_rxnorm_dict.py"
    )
    for d in data["drugs"]:
        assert d.get("source") == "rxnav_api", f"{d['name_vi']}: source={d.get('source')!r}"
        assert d.get("reverse_verified") is True, f"{d['name_vi']}: not reverse-verified"
        assert d.get("fetch_date"), f"{d['name_vi']}: no fetch_date"


def test_unverified_records_are_never_used_as_cache():
    """
    The poisoned cache beat the API because local-exact ran first. Records without
    provenance must now be skipped, so they fall through to the live lookup instead.
    """
    linker = RxNormLinker()
    linker.records = [
        {"rxcui": "9999", "name_vi": "Fake drug", "name_en": "fakedrug", "synonyms": []},
        {"rxcui": "6809", "name_vi": "Metformin", "name_en": "metformin", "synonyms": [],
         "source": "rxnav_api", "reverse_verified": True, "fetch_date": "2026-07-27"},
    ]
    lookup = linker._build_exact_map()
    assert "fake drug" not in lookup, "un-provenanced record was admitted to the cache"
    assert "metformin" in lookup, "verified record was wrongly excluded"


# --- 6b: the 5 dangerous ALIAS_MAP self-maps ---

DANGEROUS_SELF_MAPS = ["ho", "đau", "sốt", "khó thở", "ợ nóng"]


@pytest.mark.parametrize("term", DANGEROUS_SELF_MAPS)
def test_self_mapped_term_cannot_become_a_disease(term):
    """
    ALIAS_MAP still contains "đau" -> "đau" etc. Those entries handed the term straight back
    and a :DISEASE node named 'đau' got built. They stay (the symptom nodes are real data),
    but the gate must make a DISEASE node impossible.
    """
    assert is_generic_term(term, "DISEASE"), f"{term!r} must be rejected as a DISEASE"

    client = _FakeClient()
    GraphBuilder(neo4j_client=client).build_graph([{
        "head": "Paracetamol 500mg", "tail": term, "relation": "TREATS", "confidence": 0.9,
        "head_info": {"standard_name": "Paracetamol 500mg", "code": "X", "type": "DRUG"},
        "tail_info": {"standard_name": term, "code": "Y", "type": "DISEASE"},
        "negated": False, "temporal_context": "present", "source_sample_id": "syn_test",
    }])
    assert client.writes == [], f"a DISEASE node was written for {term!r}"


@pytest.mark.parametrize("term", DANGEROUS_SELF_MAPS)
def test_self_mapped_term_is_still_allowed_as_a_symptom(term):
    """The other half: 'sốt'/'ho' are legitimate SYMPTOM nodes and must survive."""
    assert not is_generic_term(term, "SYMPTOM"), f"{term!r} must remain valid as a SYMPTOM"

    client = _FakeClient()
    GraphBuilder(neo4j_client=client).build_graph([{
        "head": "Paracetamol 500mg", "tail": term, "relation": "TREATS", "confidence": 0.9,
        "head_info": {"standard_name": "Paracetamol 500mg", "code": "X", "type": "DRUG"},
        "tail_info": {"standard_name": term, "code": "Y", "type": "SYMPTOM"},
        "negated": False, "temporal_context": "present", "source_sample_id": "syn_test",
    }])
    assert len(client.writes) == 1, f"legitimate SYMPTOM {term!r} was blocked"


# --- 6c: duplicate drug_code must be refused at the write layer ---

class _FakeClient:
    def __init__(self, existing=None, codes=None):
        self.existing = existing or []
        self.codes = codes or []
        self.writes = []

    def execute_query(self, query, parameters=None):
        if "RETURN n.name AS name, labels(n) AS labels" in query:
            return self.existing
        if "n.code AS code" in query:
            return self.codes
        self.writes.append((query, parameters or {}))
        return []


def test_duplicate_drug_code_is_refused_at_write_layer():
    """
    'drug_code IS UNIQUE' is declared at neo4j_client.py but does NOT exist in the database --
    CREATE CONSTRAINT fails on the shared 'RXCUI-UNKNOWN' sentinel and execute_query swallows
    the error. Until the sentinel is replaced by null the DB cannot enforce this, so the write
    layer must.
    """
    client = _FakeClient(codes=[{"name": "Metformin", "code": "RXCUI:6809", "label": "DRUG"}])
    GraphBuilder(neo4j_client=client).build_graph([{
        "head": "Methotrexate 10mg/tuần", "tail": "Viêm khớp dạng thấp",
        "relation": "PRESCRIBED_FOR", "confidence": 0.9,
        "head_info": {"standard_name": "Methotrexate 10mg/tuần", "code": "RXCUI:6809", "type": "DRUG"},
        "tail_info": {"standard_name": "Viêm khớp dạng thấp", "code": "M06.9", "type": "DISEASE"},
        "negated": False, "temporal_context": "present", "source_sample_id": "syn_test",
    }])
    assert client.writes == [], (
        "a second DRUG reusing RXCUI:6809 was written; duplicate codes must be refused"
    )


def test_distinct_drug_code_still_writes():
    client = _FakeClient(codes=[{"name": "Metformin", "code": "RXCUI:6809", "label": "DRUG"}])
    GraphBuilder(neo4j_client=client).build_graph([{
        "head": "Methotrexate 10mg/tuần", "tail": "Viêm khớp dạng thấp",
        "relation": "PRESCRIBED_FOR", "confidence": 0.9,
        "head_info": {"standard_name": "Methotrexate 10mg/tuần", "code": "RXCUI:6851", "type": "DRUG"},
        "tail_info": {"standard_name": "Viêm khớp dạng thấp", "code": "M06.9", "type": "DISEASE"},
        "negated": False, "temporal_context": "present", "source_sample_id": "syn_test",
    }])
    assert len(client.writes) == 1
