"""
Unit tests for Phase 3:
- 3.0a: BLOCKED_EXACT loét dạ dày tá tràng
- 3.1a: LLMClient mock fallback banner, source tagging, and evaluate_re batch rejection
- 3.1b: Pipeline empty dataset RuntimeError
- 3.1c: Corrupted JSON counter and warning logging
- 3.1d: Neo4jClient last_error_type classification
"""

import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.entity_linking.icd10_linker import ICD10Linker
from src.llm_client import LLMClient
from src.graph.neo4j_client import Neo4jClient
from evaluation.evaluate_re import evaluate_re

BASE_DIR = Path(__file__).resolve().parent.parent


def test_3_0a_blocked_exact_loet_da_day_ta_trang():
    """loét dạ dày tá tràng must return unlinked, never K25 or K26."""
    linker = ICD10Linker()
    res = linker.link_disease("loét dạ dày tá tràng")
    assert res["code"] is None
    assert res["method"] == "unlinked"
    assert res.get("blocked") is True

    # Confirm loét dạ dày still links to K25
    res_gastric = linker.link_disease("loét dạ dày")
    assert res_gastric["code"] == "K25"
    assert res_gastric["standard_name"] == "Viêm loét dạ dày"


def test_3_1a_llm_client_mock_fallback_and_source_tagging():
    """Simulated API error triggers mock fallback and tags output with source='mock'."""
    client = LLMClient(provider="gemini", api_key="dummy_key")

    with patch.object(client, "_execute_real_api_call", side_effect=Exception("API Quota Exceeded")):
        res = client.generate_json("Trích xuất thực thể từ: Bệnh nhân Đái tháo đường týp 2 kê Metformin.")
        assert client.is_mock_fallback is True
        assert client.mock_calls_count > 0
        if isinstance(res, list) and res:
            assert res[0].get("source") == "mock"


def test_3_1a_evaluate_re_rejects_mock_batch(tmp_path):
    """evaluate_re must raise RuntimeError if mock triples exist in batch."""
    with patch("evaluation.evaluate_re.LLMRelationExtractor") as mock_extractor_cls:
        mock_extractor = MagicMock()
        mock_extractor.extract_relations.return_value = [
            {"head": "metformin", "relation": "PRESCRIBED_FOR", "tail": "đái tháo đường týp 2", "source": "mock"}
        ]
        mock_extractor.llm_client = MagicMock()
        mock_extractor.llm_client.is_mock_fallback = True
        mock_extractor_cls.return_value = mock_extractor

        test_json = tmp_path / "test_set.json"
        test_json.write_text(json.dumps([
            {"id": "test_001", "text": "Bệnh nhân Đái tháo đường týp 2 kê Metformin.", "relations": [], "entities": []}
        ]), encoding="utf-8")

        with patch("evaluation.evaluate_re.ANNOTATED_DATA_DIR", tmp_path):
            with pytest.raises(RuntimeError, match="EVALUATION REJECTED: Batch contains mock triples!"):
                evaluate_re()


def test_3_1b_pipeline_empty_dataset_raises_runtime_error(tmp_path):
    """run_pipeline must raise RuntimeError if empty synthetic data is loaded."""
    empty_json = tmp_path / "synthetic_data.json"
    empty_json.write_text("[]", encoding="utf-8")

    from run_pipeline import run_end_to_end_pipeline
    with patch("run_pipeline.SYNTHETIC_DATA_DIR", tmp_path):
        with patch("run_pipeline.SyntheticDataGenerator") as mock_gen_cls:
            mock_gen = MagicMock()
            mock_gen.generate_batch.return_value = []
            mock_gen_cls.return_value = mock_gen
            with pytest.raises(RuntimeError):
                run_end_to_end_pipeline(total_samples=10)


def test_3_1c_llm_client_corrupted_json_counter():
    """Corrupted JSON response increments corrupted_json_count and adds warning to summary."""
    client = LLMClient(provider="mock")
    client.total_json_attempts = 1

    bad_json = "This is NOT valid JSON {unclosed"
    res = client._extract_json(bad_json)

    assert res == []
    assert client.corrupted_json_count == 1
    stats = client.get_stats_summary()
    assert "triple bị mất do JSON hỏng" in stats


def test_3_1d_neo4j_client_last_error_type_distinction():
    """Neo4jClient distinguishes connection_refused vs auth_failed in last_error_type."""
    client = Neo4jClient()

    # 1. Connection Refused
    with patch("neo4j.GraphDatabase.driver", side_effect=Exception("Connection refused bolt://localhost:7687")):
        online = client.connect()
        assert online is False
        assert client.last_error_type == "connection_refused"

    # 2. Auth Failed
    client._driver = None
    with patch("neo4j.GraphDatabase.driver", side_effect=Exception("Unauthorized: Invalid username or password")):
        online = client.connect()
        assert online is False
        assert client.last_error_type == "auth_failed"
