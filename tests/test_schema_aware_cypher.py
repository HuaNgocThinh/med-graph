"""
Unit tests for Schema-Aware Text2Cypher, Schema Caching, Pruning, and Cypher filters.
"""

import time
from unittest.mock import patch
import pytest
from src.graph.neo4j_client import Neo4jClient
from src.qa.text_to_cypher import TextToCypherQA, prune_schema, build_schema_context, generate_cypher


def test_1_schema_loads_from_neo4j():
    client = Neo4jClient()
    schema = client.get_graph_schema()
    assert "nodes" in schema and "relationships" in schema
    assert len(schema["nodes"]) == 3
    labels = [n["label"] for n in schema["nodes"]]
    assert "DISEASE" in labels and "DRUG" in labels and "SYMPTOM" in labels
    assert len(schema["relationships"]) == 5


def test_2_schema_cache_ttl():
    client = Neo4jClient()
    client._schema_cache = None
    client._schema_cache_time = 0.0

    with patch.object(client, "execute_query", wraps=client.execute_query) as mock_exec:
        schema1 = client.get_graph_schema()
        count1 = mock_exec.call_count
        assert count1 > 0

        schema2 = client.get_graph_schema()
        count2 = mock_exec.call_count
        assert count2 == count1  # Uses cache, zero new execute_query calls
        assert schema1 == schema2


def test_3_schema_force_refresh():
    client = Neo4jClient()
    schema1 = client.get_graph_schema()
    
    with patch.object(client, "execute_query", wraps=client.execute_query) as mock_exec:
        schema2 = client.get_graph_schema(force_refresh=True)
        assert mock_exec.call_count > 0  # Re-queries Neo4j regardless of TTL
        assert schema1 == schema2


def test_4_pruning_drug_question():
    client = Neo4jClient()
    full_schema = client.get_graph_schema()
    pruned = prune_schema(full_schema, "Thuốc nào điều trị đái tháo đường?")
    rel_types = [r["type"] for r in pruned["relationships"]]
    assert "PRESCRIBED_FOR" in rel_types
    assert "TREATS" in rel_types


def test_5_pruning_symptom_question():
    client = Neo4jClient()
    full_schema = client.get_graph_schema()
    pruned = prune_schema(full_schema, "Bệnh này có triệu chứng gì?")
    rel_types = [r["type"] for r in pruned["relationships"]]
    assert "HAS_SYMPTOM" in rel_types


def test_6_pruning_never_empty():
    client = Neo4jClient()
    full_schema = client.get_graph_schema()
    pruned = prune_schema(full_schema, "xyzabc không có nghĩa gì")
    assert len(pruned["relationships"]) == len(full_schema["relationships"])


def test_7_cypher_contains_negated_filter():
    cypher_resp = generate_cypher("Thuốc nào điều trị cao huyết áp?")
    cypher = cypher_resp["cypher"]
    assert "coalesce(r.negated, false) = false" in cypher


def test_8_schema_source_in_response():
    response = generate_cypher("Metformin điều trị bệnh gì?")
    assert "schema_source" in response
    assert response["schema_source"].startswith("neo4j_live |") or response["schema_source"].startswith("neo4j_offline |")
