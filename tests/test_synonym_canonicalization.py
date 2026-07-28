"""
Unit tests for the folk <-> medical synonym canonicalization layer.

Each test here reproduces a defect that was observed running live against Neo4j, or pins an
invariant whose violation would silently reintroduce one:

  * "Tiểu đường có triệu chứng gì?" returned NODE_EXISTS_NO_RELATIONS with an empty result
    set while "Đái tháo đường có triệu chứng gì?" returned 2 symptoms, because the Cypher
    literal 'tiểu đường' was never rewritten to the medical standard form.
  * The rewrite failed because the fallback compared DB node names to synonym variants with
    `==`, so 'Đái tháo đường týp 2' never matched the variant 'đái tháo đường'.
  * Synonym canonicalization must compose WITH prefix stripping, not replace it.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.entity_linking.entity_normalizer import (
    normalize_disease_name,
    canonicalize_synonyms,
    normalize_spelling,
    get_term_synonyms,
    CANONICAL_SYNONYM_MAP,
)
from src.qa.text_to_cypher import terms_match, canonicalize_cypher_literals


# --- The pair that motivated the work: Tiểu đường <-> Đái tháo đường ---

def test_folk_diabetes_canonicalizes_to_medical_standard():
    assert canonicalize_synonyms("tiểu đường") == "đái tháo đường"
    assert normalize_disease_name("Tiểu đường") == "Đái tháo đường"


def test_diabetes_folk_and_medical_forms_converge():
    """The core requirement: both spellings must normalize to the SAME string."""
    assert normalize_disease_name("Tiểu đường") == normalize_disease_name("Đái tháo đường")


def test_diabetes_typed_variants_still_converge():
    for variant in ("Tiểu đường týp 2", "Tiểu đường tuýp 2", "Đái tháo đường tuýp 2",
                    "Bệnh tiểu đường tuýp 2", "đái tháo đường loại 2"):
        assert normalize_disease_name(variant) == "Đái tháo đường týp 2", variant


# --- The exact live failure: folk question vs medical question must build the same Cypher ---

def test_cypher_literal_rewritten_for_folk_term():
    """Reproduces the Q1/Q3 failure: 'tiểu đường' left in the query returned 0 rows."""
    folk = ("MATCH (d:DISEASE)-[r:HAS_SYMPTOM]->(s:SYMPTOM) "
            "WHERE toLower(d.name) CONTAINS 'tiểu đường' RETURN d.name, s.name")
    assert "'đái tháo đường'" in canonicalize_cypher_literals(folk)


def test_folk_and_medical_cypher_become_identical():
    folk = "MATCH (d) WHERE toLower(d.name) CONTAINS 'tiểu đường' RETURN d.name"
    med = "MATCH (d) WHERE toLower(d.name) CONTAINS 'đái tháo đường' RETURN d.name"
    assert canonicalize_cypher_literals(folk) == canonicalize_cypher_literals(med)


def test_substituted_literal_is_lowercase():
    """Generated Cypher compares toLower(node.name); a Sentence Case literal never matches."""
    q = "MATCH (d) WHERE toLower(d.name) CONTAINS 'tiểu đường' RETURN d.name"
    out = canonicalize_cypher_literals(q)
    assert "'Đái tháo đường'" not in out
    assert "'đái tháo đường'" in out


def test_terms_match_is_bidirectional_not_equality():
    """The original defect: `==` missed a node whose name CONTAINS the synonym."""
    assert terms_match("tiểu đường", "Đái tháo đường týp 2")
    assert terms_match("Đái tháo đường týp 2", "tiểu đường")
    assert not terms_match("tiểu đường", "Viêm phổi")


# --- Second confirmed pair from the 96-sample scan: Thalassemia <-> tan máu bẩm sinh ---

def test_thalassemia_folk_and_medical_forms_converge():
    assert normalize_disease_name("Tan máu bẩm sinh") == normalize_disease_name("Thalassemia")


def test_thalassemia_cypher_literal_rewritten():
    q = "MATCH (d) WHERE toLower(d.name) CONTAINS 'tan máu bẩm sinh' RETURN d.name"
    assert "'thalassemia'" in canonicalize_cypher_literals(q)


# --- The two mechanisms must stack, in the right order ---

def test_synonym_map_does_not_break_prefix_stripping():
    """
    normalize_disease_name()'s prefix stripping and the synonym map are independent
    mechanisms and must compose: 'Bệnh tiểu đường' needs BOTH (strip 'Bệnh ', then fold
    'tiểu đường' -> 'đái tháo đường'). Prefix-only or synonym-only would each fail.
    """
    assert normalize_disease_name("Bệnh tiểu đường") == "Đái tháo đường"
    # prefix stripping alone, on a term with no synonym entry, is unchanged
    assert normalize_disease_name("Hội chứng ruột kích thích") == "Ruột kích thích"
    assert normalize_disease_name("Tình trạng mất nước") == "Mất nước"
    # synonym folding alone, with no prefix present
    assert normalize_disease_name("Tiểu đường") == "Đái tháo đường"


def test_prefix_stripping_regressions_still_hold():
    """Pins the pre-existing behaviour the synonym layer must not disturb."""
    assert normalize_disease_name("Bệnh cao huyết áp") == "Cao huyết áp"
    assert normalize_disease_name("Cao huyết áp") == "Cao huyết áp"
    assert normalize_disease_name("tăng huyết áp") == "Cao huyết áp"
    assert normalize_disease_name("Bệnh viêm phổi") == "Viêm phổi"


# --- Invariants that keep canonicalization safe to run at write time ---

def test_canonicalization_is_idempotent():
    """
    Applying canonicalization twice must equal applying it once. If a value were also a key
    the rewrite would ping-pong and graph nodes would flip names between pipeline runs.
    """
    for term in ("Tiểu đường", "Đái tháo đường", "Bệnh tiểu đường tuýp 2", "Cao huyết áp",
                 "Đau bao tử", "Viêm loét dạ dày", "Tan máu bẩm sinh", "Thalassemia"):
        once = normalize_disease_name(term)
        assert normalize_disease_name(once) == once, term


def test_no_canonical_value_is_also_a_key():
    """Structural guarantee behind idempotency; fails loudly if someone edits the JSON badly."""
    keys = set(CANONICAL_SYNONYM_MAP.keys())
    values = set(CANONICAL_SYNONYM_MAP.values())
    assert keys & values == set(), f"ping-pong entries: {keys & values}"


def test_canonical_map_is_directional_not_bidirectional():
    """'đái tháo đường' must never map back to the folk form."""
    assert "tiểu đường" in CANONICAL_SYNONYM_MAP
    assert "đái tháo đường" not in CANONICAL_SYNONYM_MAP


def test_longest_key_wins_no_mangled_phrases():
    """'mỡ máu cao' must not become 'rối loạn lipid máu cao' via the shorter 'mỡ máu' key."""
    assert canonicalize_synonyms("mỡ máu cao") == "rối loạn lipid máu"


def test_synonym_key_inside_a_longer_word_is_not_rewritten():
    """
    Reproduces a confirmed defect: without \\b anchoring, the short key 'type' ate the inside
    of unrelated words — 'prototype' became 'prototýp', 'Genotype' became 'Genotýp'.
    """
    for word in ("prototype", "Prototype", "datatype", "typescript", "Genotype", "stereotype"):
        assert canonicalize_synonyms(word) == word, word


def test_standalone_key_is_still_rewritten_after_boundary_fix():
    """The \\b anchoring must not disable legitimate whole-word replacement."""
    assert normalize_spelling("type 2 diabetes") == "týp 2 diabetes"
    assert canonicalize_synonyms("Tiểu đường tuýp 2") == "đái tháo đường tuýp 2"


# --- Spelling normalization is a SEPARATE mechanism from synonym canonicalization ---

def test_spelling_and_synonym_layers_are_separate():
    """
    canonicalize_synonyms() handles different WORDS for one concept; normalize_spelling()
    handles different SPELLINGS of one word. Each must stay out of the other's job -- mixing
    them put the short generic key 'type' in the same alternation as multi-word medical
    phrases, which is what let it corrupt 'prototype'.
    """
    # synonym layer folds the concept but leaves the spelling alone
    assert canonicalize_synonyms("tiểu đường tuýp 2") == "đái tháo đường tuýp 2"
    # spelling layer fixes the spelling but knows nothing about concepts
    assert normalize_spelling("tiểu đường tuýp 2") == "tiểu đường týp 2"
    assert "type" not in CANONICAL_SYNONYM_MAP
    assert "tuýp" not in CANONICAL_SYNONYM_MAP


def test_spelling_layer_is_whole_word_anchored():
    for word in ("prototype", "Genotype", "datatype", "typescript"):
        assert normalize_spelling(word) == word, word


def test_both_layers_compose_in_normalize_disease_name():
    """After the split, the two layers must still stack to the same end result."""
    assert normalize_disease_name("Đái tháo đường tuýp 2") == "Đái tháo đường týp 2"
    assert normalize_disease_name("Tiểu đường tuýp 2") == "Đái tháo đường týp 2"
    assert normalize_disease_name("Bệnh tiểu đường tuýp 2") == "Đái tháo đường týp 2"


def test_canonicalize_cypher_literals_touches_only_quoted_literals():
    """
    Property names, labels and aliases must survive untouched — only the quoted literal is
    rewritten. Here 'type' appears as a property name (n.type) and as a RETURN alias.
    """
    q = "MATCH (n:DISEASE) WHERE n.type = 'tiểu đường' RETURN n.type AS type"
    out = canonicalize_cypher_literals(q)
    assert out == "MATCH (n:DISEASE) WHERE n.type = 'đái tháo đường' RETURN n.type AS type"
    assert "n.type" in out          # property name intact
    assert out.endswith("AS type")  # alias intact


def test_canonicalize_cypher_literals_leaves_query_without_synonyms_unchanged():
    q = ("MATCH (d:DRUG)-[r:PRESCRIBED_FOR]->(b:DISEASE) "
         "WHERE toLower(b.name) CONTAINS 'viêm phổi' RETURN d.name, r.source_sample_id")
    assert canonicalize_cypher_literals(q) == q


def test_canonicalization_leaves_unrelated_terms_untouched():
    """Guards against over-eager substring rewriting damaging correct node names."""
    for term in ("Viêm phổi", "Metformin", "Đau thượng vị", "Cơn đau thắt ngực",
                 "Trào ngược dạ dày thực quản", "Nhiễm trùng đường tiết niệu"):
        assert normalize_disease_name(term) == term, term


def test_rejected_entries_are_not_in_the_canonical_map():
    """
    These mappings were reviewed and rejected as medically wrong. Pinned so they cannot be
    re-added silently:
      - 'loạn nhịp tim' -> 'rung nhĩ'          narrows a category to one of its members
      - 'đau dạ dày'    -> 'viêm loét dạ dày'  promotes a SYMPTOM to a DIAGNOSIS
      - 'đau tim'       -> 'nhồi máu cơ tim'   over-commits to an acute diagnosis
      - 'mỡ máu', 'tăng huyết áp'              already handled one layer down, and the sole
                                                remaining substring-collision risk

    On 'tăng huyết áp' specifically -- the earlier note called it "redundant". That word was
    wrong and worth correcting, because it invites deletion of the thing doing the work.
    It is kept OUT of the canonical synonym map because ALIAS_MAP already handles it, and
    ALIAS_MAP["tăng huyết áp"] = "Cao huyết áp" is LOAD-BEARING, not redundant: ICD10Linker
    names a node `get_canonical_name(rec["name_vi"])`, and I10's name_vi is now the standard
    term "Tăng huyết áp". Remove that ALIAS entry and the node silently renames itself away
    from the corpus form -- exactly how 'Viêm dạ dày' became 'Viêm loét dạ dày' while keeping
    the wrong K29.7 code. See test_i10_alias_entry_is_load_bearing in test_entity_linking.py.
    """
    for rejected in ("loạn nhịp tim", "đau dạ dày", "đau tim", "mỡ máu", "tăng huyết áp"):
        assert rejected not in CANONICAL_SYNONYM_MAP, (
            f"'{rejected}' was rejected on medical review; see _rules in "
            f"canonical_synonyms_vi.json before re-adding."
        )


def test_removed_entries_still_resolve_via_the_layer_that_owns_them():
    """Removing the redundant entries must not change any existing behaviour."""
    # ALIAS_MAP owns this one, which is exactly why the map entry was redundant
    assert normalize_disease_name("tăng huyết áp") == "Cao huyết áp"
    assert normalize_disease_name("mỡ máu cao") == "Rối loạn lipid máu"


def test_folk_symptom_maps_to_a_symptom_not_a_diagnosis():
    """
    'đau bao tử' is regional slang for the SYMPTOM 'đau dạ dày'. It must stop there and not
    be escalated to the diagnosis 'Viêm loét dạ dày'.
    """
    assert canonicalize_synonyms("đau bao tử") == "đau dạ dày"
    assert normalize_disease_name("Đau bao tử") == "Đau dạ dày"
    assert normalize_disease_name("Đau bao tử") != "Viêm loét dạ dày"


def test_no_multiword_key_bleeds_into_a_longer_phrase():
    """
    The 'cụm-trong-cụm' hazard: a multi-word key that is a prefix of a longer, different
    concept. After the review removals, no remaining key exhibits it.
    """
    for phrase in ("đau tim mạch", "mỡ máu não", "loạn nhịp tim hoàn toàn", "viêm loét dạ dày"):
        assert canonicalize_synonyms(phrase) == phrase, phrase
    # and a legitimate longer phrase still canonicalizes correctly
    assert canonicalize_synonyms("tiểu đường thai kỳ") == "đái tháo đường thai kỳ"


def test_no_synonym_class_merges_a_disease_with_a_symptom():
    """
    Guard on the union-find equivalence classes. Transitive closure is only safe while every
    declared pair is a true same-concept synonym: if a BỆNH↔TRIỆU CHỨNG pair (e.g.
    'viêm họng'↔'đau họng', which ICD-10 lists as a synonym but is really HAS_SYMPTOM) were
    ever added to medical_synonyms_vi.json, closure would silently fold a disease and its
    symptom into one class and the graph would lose a correct relationship.

    Fails loudly if such a pair is introduced. Listed terms are the disease↔symptom pairs
    rejected during the 96-sample review.
    """
    from src.entity_linking.entity_normalizer import SYNONYM_CLASSES

    REJECTED_PAIRS = [
        ("viêm họng", "đau họng"),
        ("động kinh", "cơn co giật"),
        ("viêm dạ dày ruột nhiễm khuẩn", "tiêu chảy cấp"),
        ("thiếu máu thiếu sắt", "thiếu máu nặng"),
    ]
    for disease, symptom in REJECTED_PAIRS:
        cls = SYNONYM_CLASSES.get(disease, set())
        assert symptom not in cls, (
            f"'{symptom}' is a SYMPTOM of '{disease}', not a synonym; merging them "
            f"would destroy a correct HAS_SYMPTOM relationship."
        )


def test_bidirectional_expansion_map_still_reaches_siblings():
    """get_term_synonyms stays bidirectional; it is expansion, not canonicalization."""
    syns = {s.lower() for s in get_term_synonyms("Đau bao tử")}
    assert "đau dạ dày" in syns
    assert "viêm loét dạ dày" in syns
