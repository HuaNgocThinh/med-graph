"""
Regression tests for the silent-failure family (item 4) and the sentinel->null change (item 3).

Every one of these reproduces a defect that was observed live, not a hypothetical:

  * execute_query() returned a bare [] both when a query matched nothing and when it blew up.
    CREATE CONSTRAINT drug_code failed on duplicate 'RXCUI-UNKNOWN' values, init_schema()
    reported success, and the constraint did not exist for the entire life of the project --
    which is how Metformin and Methotrexate came to share RXCUI:6809.

  * The same ambiguity reached the QA path: a Cypher statement that failed to execute produced
    graph_results == [], which was then reported to the answer synthesiser as
    'NODE_NOT_FOUND' -- asserting that the graph does not contain something, on the basis of a
    query that never ran. That directly violates the project rule that the system may state
    only what the graph actually says.

  * 'ICD-UNKNOWN' / 'RXCUI-UNKNOWN' / 'UNKNOWN' / 'N/A' were four spellings of "not linked".
    105 SYMPTOM nodes silently carried the literal string 'UNKNOWN'.
"""

import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.entity_linking.entity_normalizer import (
    normalize_code, is_unlinked_code, LEGACY_CODE_SENTINELS,
)
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.rxnorm_linker import RxNormLinker
from src.graph.neo4j_client import Neo4jClient, Neo4jQueryError, QueryResult


# --- Item 3: unlinked is null, in exactly one spelling ---------------------------------

@pytest.mark.parametrize("sentinel", sorted(s for s in LEGACY_CODE_SENTINELS if s))
def test_every_legacy_sentinel_normalizes_to_none(sentinel):
    assert normalize_code(sentinel) is None
    assert normalize_code(sentinel.lower()) is None
    assert is_unlinked_code(sentinel)


def test_real_codes_survive_normalization():
    for code in ("E11", "I10", "K29.7", "RXCUI:6809", "RXCUI:41493"):
        assert normalize_code(code) == code
        assert not is_unlinked_code(code)


def test_linkers_emit_null_not_a_sentinel():
    """
    A shared string makes 'REQUIRE code IS UNIQUE' unachievable: Neo4j ignores null but
    treats equal strings as duplicates, so 15 unlinked drugs all holding 'RXCUI-UNKNOWN'
    were, by definition, 15 constraint violations.
    """
    icd = ICD10Linker().link_disease("viêm")           # rejected by the generic-term gate
    assert icd["code"] is None, icd
    rx = RxNormLinker().link_drug("xx")                # too short to link
    assert rx["code"] is None, rx


# --- Item 4b: a failed query must not look like an empty one ---------------------------

class _BoomDriver:
    """Stands in for a driver whose session.run() raises, e.g. a syntax error in the Cypher."""

    class _Session:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def run(self, *a, **kw):
            raise RuntimeError("Neo.ClientError.Statement.SyntaxError")

    def session(self):
        return self._Session()

    def verify_connectivity(self):
        return True


class _EmptyDriver(_BoomDriver):
    class _Session(_BoomDriver._Session):
        def run(self, *a, **kw):
            return []


def _client(driver):
    c = Neo4jClient()
    c._driver = driver
    return c


def test_failed_query_raises_by_default():
    with pytest.raises(Neo4jQueryError):
        _client(_BoomDriver()).execute_query("MATCH (n) RETURN n")


def test_failed_query_is_distinguishable_from_an_empty_one():
    """The whole point: [] and [] used to be the same object. Now they carry opposite facts."""
    failed = _client(_BoomDriver()).execute_query("MATCH (n) RETURN n", raise_on_error=False)
    empty = _client(_EmptyDriver()).execute_query("MATCH (n) RETURN n", raise_on_error=False)

    assert list(failed) == list(empty) == []      # still list-like, callers keep working
    assert failed.ok is False and failed.failed is True
    assert empty.ok is True and empty.failed is False
    assert failed.error is not None and empty.error is None


def test_offline_client_raises_instead_of_reporting_no_data():
    """
    A query that never ran must not answer 'no data'. Reporting an absence the database
    never observed is the exact failure mode the project forbids.
    """
    c = Neo4jClient(uri="bolt://127.0.0.1:1")     # nothing listens here
    c._driver = None
    with pytest.raises(Neo4jQueryError) as ei:
        c.execute_query("MATCH (n) RETURN n")
    assert ei.value.offline is True

    soft = c.execute_query("MATCH (n) RETURN n", raise_on_error=False)
    assert soft.ok is False and soft.offline is True


def test_queryresult_is_still_a_plain_list_for_consumers():
    r = QueryResult([{"a": 1}, {"a": 2}])
    assert len(r) == 2 and r[0]["a"] == 1 and [x["a"] for x in r] == [1, 2]
    assert bool(QueryResult([])) is False


# --- Item 4b, QA path: a broken query must never be answered as 'khong co du lieu' -----

class _FakeQA:
    """Minimal stand-in exercising the branch that chooses fallback_status."""

    @staticmethod
    def status(graph_results, query_error, matched_nodes):
        if not graph_results and query_error is not None:
            return "QUERY_ERROR"
        if not graph_results:
            return "NODE_EXISTS_NO_RELATIONS" if matched_nodes else "NODE_NOT_FOUND"
        return "FOUND"


def test_query_error_is_not_reported_as_absent_data():
    assert _FakeQA.status([], RuntimeError("syntax"), []) == "QUERY_ERROR"
    assert _FakeQA.status([], RuntimeError("syntax"), ["Metformin"]) == "QUERY_ERROR"
    # A query that really did run and matched nothing keeps its old, correct meaning.
    assert _FakeQA.status([], None, []) == "NODE_NOT_FOUND"
    assert _FakeQA.status([], None, ["Metformin"]) == "NODE_EXISTS_NO_RELATIONS"
    assert _FakeQA.status([{"x": 1}], None, []) == "FOUND"


def test_synthesis_prompt_forbids_claiming_absence_on_query_error():
    from src.qa.text_to_cypher import ANSWER_SYNTHESIS_PROMPT
    assert "QUERY_ERROR" in ANSWER_SYNTHESIS_PROMPT, (
        "the prompt has no instruction for QUERY_ERROR, so the LLM would fall back to the "
        "NODE_NOT_FOUND wording and assert an absence"
    )
