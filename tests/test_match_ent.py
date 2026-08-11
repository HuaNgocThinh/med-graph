import pytest
import re
from src.entity_linking.entity_normalizer import get_canonical_name

def _match_ent(e: dict, canon_target: str) -> bool:
    raw_name = e.get("entity", "")
    clean_name = re.sub(r"[\.,;:\?!\n].*$", "", raw_name).strip()
    clean_name_no_mod = re.sub(r"\s+\d+\s*(năm|tháng|ngày|tuần)(\s+nay|\s+trước)?.*$", "", clean_name, flags=re.IGNORECASE).strip()
    
    cand1 = get_canonical_name(raw_name)
    cand2 = get_canonical_name(clean_name) if clean_name else ""
    cand3 = get_canonical_name(clean_name_no_mod) if clean_name_no_mod else ""

    return (
        cand1 == canon_target
        or (cand2 != "" and cand2 == canon_target)
        or (cand3 != "" and cand3 == canon_target)
        or raw_name == canon_target
    )

def test_match_ent_trailing_punctuation():
    entity = {"entity": "Đái tháo đường tuýp 2. Hiện", "type": "DISEASE"}
    target = get_canonical_name("Đái tháo đường týp 2")
    assert _match_ent(entity, target) is True

def test_match_ent_temporal_modifier():
    entity = {"entity": "Cao huyết áp 3 năm nay", "type": "DISEASE"}
    target = get_canonical_name("Cao huyết áp")
    assert _match_ent(entity, target) is True

def test_match_ent_negative_mismatch():
    entity = {"entity": "Metformin", "type": "DRUG"}
    target = get_canonical_name("Paracetamol")
    assert _match_ent(entity, target) is False
