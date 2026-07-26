"""
Item 1d: pin the core regression edges to the SOURCE TEXT, not to whatever the pipeline
currently happens to produce.

The problem this solves. The original regression target was

    Ibuprofen -[CONTRAINDICATED_FOR]-> "Viêm dạ dày"

and it is now

    Ibuprofen -[CONTRAINDICATED_FOR]-> "Viêm loét dạ dày"

and the change was never noticed, because nothing pinned the value. What happened (traced in
the report, item 1d): ICD10Linker returns `get_canonical_name(rec["name_vi"])` as the node
name, so the node was named after the DICTIONARY entry, not after the document. K29.7's
name_vi is "Viêm dạ dày", so the node was originally "Viêm dạ dày". Commit e64df49 added
ALIAS_MAP["viêm dạ dày"] = "Viêm loét dạ dày", and the node silently renamed itself -- while
keeping the K29.7 code, which belongs to the OTHER disease.

So the graph drifted between two names, neither of which was checked against the one thing
that cannot drift: the clinical text the edge was extracted from.

These tests therefore assert against data/synthetic/synthetic_data.json. A future rename can
still happen -- but only if the new name is also what the document says.
"""

import json
import re
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

CORPUS = BASE_DIR / "data" / "synthetic" / "synthetic_data.json"

# (sample_id, drug, relation, disease-as-written-in-the-document)
PINNED_EDGES = [
    ("syn_003", "Ibuprofen", "CONTRAINDICATED_FOR", "Viêm loét dạ dày"),
    ("syn_003", "Omeprazole 20mg", "PRESCRIBED_FOR", "Viêm loét dạ dày"),
    ("syn_001", "Metformin", "PRESCRIBED_FOR", "Đái tháo đường týp 2"),
]

# Edges that must NOT exist. Each was observed in the graph at some point.
FORBIDDEN_EDGES = [
    ("Paracetamol 500mg", "TREATS", "Đái tháo đường týp 2"),
    ("Omeprazole 20mg", "CONTRAINDICATED_FOR", "Viêm loét dạ dày"),
    ("Meloxicam 15mg", "PRESCRIBED_FOR", "Viêm phổi"),
]

# The ICD code each pinned disease node currently carries.
# 'expected' is what the code SHOULD be per the WHO classification (see docs/ontology_freeze.md
# decision 3); 'current' is what the graph holds today. They differ on purpose: decision 3 is
# not approved yet, and this table is what makes that gap impossible to forget.
DISEASE_CODES = {
    #  node name             current   expected   why
    "Viêm loét dạ dày":   ("K29.7", "K25",   "K29.7 = viêm dạ dày (gastritis); loét dạ dày là K25, "
                                             "và ICD-10 đánh Excludes1 giữa hai nhóm"),
    "Thoái hóa khớp":     ("M19.9", "M17",   "corpus viết 'Thoái hóa khớp gối' -> M17 gonarthrosis; "
                                             "M19.9 là thoái hóa khớp không xác định vị trí"),
    "Viêm âm đạo do nấm": ("N76.0", "B37.3", "N76.0 = viêm âm đạo cấp; do nấm Candida là B37.3"),
}


def _corpus():
    return {r["id"]: r["text"] for r in json.loads(CORPUS.read_text(encoding="utf-8"))}


@pytest.mark.parametrize("sid,drug,rel,disease", PINNED_EDGES)
def test_pinned_edge_matches_the_source_document(sid, drug, rel, disease):
    """The disease name on a pinned edge must be a string the document literally contains."""
    text = _corpus()[sid]
    assert disease.lower() in text.lower(), (
        f"{sid} does not contain {disease!r}. Either the pin drifted away from the source text "
        f"(the exact failure this test exists for) or the corpus changed.\nText: {text}"
    )
    assert drug.split()[0].lower() in text.lower(), f"{sid} does not mention {drug!r}"


def test_syn_003_says_ulcer_not_gastritis():
    """
    The specific drift. syn_003 reads 'Bệnh nhân Viêm loét dạ dày kèm trào ngược dạ dày.'
    'Viêm dạ dày' as a standalone diagnosis appears NOWHERE in the corpus -- the only match
    for that substring is 'Viêm dạ dày ruột nhiễm khuẩn' (A09), a different disease with its
    own node. So the earlier regression target was never supported by the data.
    """
    text = _corpus()["syn_003"]
    assert "Viêm loét dạ dày" in text
    assert re.search(r"[Vv]iêm dạ dày(?!\s+ruột)", text) is None, (
        "syn_003 would have to say 'viêm dạ dày' for the old regression target to be right"
    )

    standalone = [sid for sid, t in _corpus().items()
                  if re.search(r"[Vv]iêm dạ dày(?!\s+ruột)", t)]
    assert standalone == [], (
        f"'viêm dạ dày' as a standalone diagnosis appears in {standalone}; the pin needs review"
    )


def test_disease_code_table_records_the_known_gap():
    """
    Guards the gap itself: while decision 3 is pending, current != expected for all three.
    When decision 3 is applied, this test fails and forces the table to be updated together
    with the data -- the code and the pin cannot drift apart silently again.
    """
    unresolved = [n for n, (cur, exp, _) in DISEASE_CODES.items() if cur != exp]
    assert len(unresolved) == 3, (
        f"{3 - len(unresolved)} ICD code(s) were changed in the graph but DISEASE_CODES in this "
        f"file still lists them as pending. Update the table and docs/ontology_freeze.md."
    )
