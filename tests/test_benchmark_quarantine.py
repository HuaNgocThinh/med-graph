"""
Item B3/B5/B6: pin the benchmark quarantine and the evidence behind it.

The four mismatched gold rows are deliberately NOT repaired. Repairing them would make the
numbers look right while leaving the circularity intact, and would delete the evidence that
the gold labels were derived from the system they grade (see docs/benchmark_quarantine.md).
These tests therefore assert that the broken rows are STILL BROKEN, so nobody quietly
"fixes" them before Phase 7 rebuilds the benchmark from hand-assigned labels.
"""

import subprocess
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from evaluation.benchmark_guard import (
    BENCHMARK_VALIDATED, ALLOW_FLAG, require_validated_benchmark,
)
from evaluation.evaluate_entity_linking import TEST_EL_BENCHMARK
from evaluation.evaluate_qa import QA_TEST_BENCHMARK


# --- B3: the gate ---------------------------------------------------------------------

def test_benchmark_is_still_flagged_unvalidated():
    assert BENCHMARK_VALIDATED is False, (
        "BENCHMARK_VALIDATED was flipped to True. It may only be set once the benchmark has "
        "been rebuilt from independently-sourced labels (Phase 7), not by editing rows."
    )


def test_guard_aborts_without_the_flag():
    with pytest.raises(SystemExit) as ei:
        require_validated_benchmark("X", "evaluate_qa", argv=["evaluate_qa.py"])
    assert ei.value.code == 2


def test_guard_allows_explicit_opt_in():
    require_validated_benchmark("X", "evaluate_qa", argv=["evaluate_qa.py", ALLOW_FLAG])


@pytest.mark.parametrize("module", ["evaluate_entity_linking", "evaluate_qa"])
def test_running_an_evaluator_bare_exits_2(module):
    """End-to-end: the real entry point must refuse, not just the helper."""
    p = subprocess.run([sys.executable, "-m", f"evaluation.{module}"],
                       cwd=BASE_DIR, capture_output=True, timeout=180)
    assert p.returncode == 2, f"{module} did not refuse to run: rc={p.returncode}"
    assert b"CACH LY" in p.stdout, "the refusal did not explain why"


# --- B5: the evidence must survive ------------------------------------------------------

def test_amlor_gold_still_holds_the_fentanyl_code():
    """
    THE evidence for circularity: gold says RXCUI:4337, and at commit 324a149 the dictionary
    record whose synonyms contained 'amlor' held rxcui 4337. 4337 is fentanyl; amlodipine is
    17767. Both files were created in that same commit. Do not "correct" this row -- the
    mismatch IS the finding.
    """
    row = [r for r in TEST_EL_BENCHMARK if r["entity"] == "Amlor"]
    assert row, "the Amlor row was deleted; docs/benchmark_quarantine.md depends on it"
    assert row[0]["expected_code"] == "RXCUI:4337", (
        "the Amlor gold was silently corrected. Keep it: it is the proof that gold and "
        "dictionary share an origin. The benchmark is rebuilt in Phase 7, not patched."
    )


def test_qa_gold_still_rewards_fabrication():
    """
    qa_005 asks what symptoms 'Cao huyết áp' causes. The graph holds only 'Chóng mặt' and
    'Đau đầu vùng chẩm'. Gold demands 'đau ngực' -- a symptom with no edge in the graph.
    A system obeying the no-fabrication rule loses this point; a system falling back on LLM
    general knowledge wins it. The benchmark scores AGAINST the core design principle.

    qa_004 is the same shape: it demands the brand name 'Nexium', which is not a node.
    """
    qa005 = [q for q in QA_TEST_BENCHMARK if q["id"] == "qa_005"][0]
    assert "đau ngực" in qa005["expected_keywords"], (
        "'đau ngực' was removed from qa_005. Do not delete it -- it is the evidence that the "
        "benchmark rewards answering beyond the graph. See docs/benchmark_quarantine.md §2.1."
    )
    qa004 = [q for q in QA_TEST_BENCHMARK if q["id"] == "qa_004"][0]
    assert "Nexium" in qa004["expected_keywords"]


# --- B6: the scoring rule is unfair, and that must stay visible -------------------------

def _kg_pass(answer, graph_results, keywords):
    """The scoring rule exactly as evaluate_qa.py implements it today."""
    return any(k.lower() in answer.lower() for k in keywords) or len(graph_results) > 0


def _rag_pass(answer, keywords):
    return any(k.lower() in answer.lower() for k in keywords)


def test_kg_scoring_rule_is_easier_than_rag_scoring_rule():
    """
    kg_pass has an extra `or len(graph_results) > 0` clause that rag_pass does not. So KG-QA
    scores a point for a completely wrong answer as long as the Cypher returned any row,
    while the RAG baseline is held to the keyword rule. kg_improvement_over_rag is then the
    difference of two numbers measured with DIFFERENT rulers.
    """
    wrong = "Xin lỗi, tôi không rõ."
    kws = ["Metformin"]
    assert _kg_pass(wrong, [{"anything": 1}], kws) is True, "the unfair clause is gone -- good"
    assert _rag_pass(wrong, kws) is False
    # Same answer, same keywords, opposite verdicts purely because of the extra clause.


def test_one_canned_sentence_passes_every_question():
    """Substring + any() means keyword density beats actually answering."""
    canned = ("Các thuốc thường dùng gồm Metformin, Paracetamol, Omeprazole, Nexium; "
              "triệu chứng gồm Đau đầu, Cơn đau thắt ngực, Viêm loét dạ dày.")
    passed = [q["id"] for q in QA_TEST_BENCHMARK
              if _rag_pass(canned, q["expected_keywords"])]
    assert len(passed) == len(QA_TEST_BENCHMARK), (
        f"only {len(passed)}/{len(QA_TEST_BENCHMARK)} passed; the benchmark changed"
    )


@pytest.mark.parametrize("kw", ["tim", "não"])
def test_gold_contains_keywords_too_short_to_identify_anything(kw):
    """3-character keywords match any node containing them; they identify nothing."""
    allkw = [k for q in QA_TEST_BENCHMARK for k in q["expected_keywords"]]
    assert kw in allkw
    assert len(kw) <= 3
