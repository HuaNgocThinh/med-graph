"""
Unit tests for Vietnamese ConText Negation, RE negation isolation, and QA Cypher negated filtering.
"""

import pytest
from src.negation_temporal.context_processor import ConTextProcessor
from src.graph.graph_cleaner import GraphCleaner
from src.graph.graph_builder import GraphBuilder
from src.graph.neo4j_client import Neo4jClient
from src.qa.text_to_cypher import TextToCypherQA


def test_context_processor_negation_sot():
    """Test 1: 'Bệnh nhân không sốt' -> context_processor returns 'sốt' with negated=True."""
    processor = ConTextProcessor()
    text = "Bệnh nhân không sốt"
    entities = [{"entity": "sốt", "type": "SYMPTOM", "start": 16, "end": 19}]
    res = processor.process_entities(text, entities)
    assert len(res) == 1
    assert res[0]["entity"] == "sốt"
    assert res[0]["negated"] is True


def test_negated_entity_no_triple_creation():
    """Test 2: 'Không có tiền sử đái tháo đường' -> entity negated=True in processed_entities, NO triple created."""
    processor = ConTextProcessor()
    text = "Bệnh nhân không có tiền sử đái tháo đường."
    entities = [{"entity": "đái tháo đường", "type": "DISEASE", "start": 27, "end": 41}]
    processed = processor.process_entities(text, entities)
    assert len(processed) == 1
    assert processed[0]["negated"] is True

    triples = [{
        "head": "đái tháo đường",
        "relation": "HAS_SYMPTOM",
        "tail": "sốt",
        "negated": processed[0]["negated"]
    }]
    cleaner = GraphCleaner()
    conflicts = cleaner.detect_conflicts_in_triples(triples)
    assert any(c["type"] == "NEGATED_ENTITY_RELATION_CONFLICT" for c in conflicts)

    builder = GraphBuilder()
    inserted_queries = builder.build_graph(triples)
    assert len(inserted_queries) == 0


def test_re_negated_entity_no_drug_triple():
    """Test 3: RE with negated entity does NOT create a triple to a drug in sentence (e.g. Metformin + 'Không thấy dấu hiệu Viêm phổi')."""
    processor = ConTextProcessor()
    text = "Bệnh nhân dùng Metformin 500mg. Khám lâm sàng không thấy dấu hiệu Viêm phổi."
    entities = [
        {"entity": "Metformin 500mg", "type": "DRUG", "start": 15, "end": 30},
        {"entity": "Viêm phổi", "type": "DISEASE", "start": 67, "end": 76}
    ]
    processed = processor.process_entities(text, entities)
    viem_phoi_ent = next(e for e in processed if e["entity"] == "Viêm phổi")
    assert viem_phoi_ent["negated"] is True

    head_obj = next(e for e in processed if e["entity"] == "Metformin 500mg")
    tail_obj = viem_phoi_ent
    is_negated = bool(head_obj.get("negated", False) or tail_obj.get("negated", False))
    assert is_negated is True

    triples = [{
        "head": "Metformin 500mg",
        "relation": "PRESCRIBED_FOR",
        "tail": "Viêm phổi",
        "negated": is_negated
    }]
    cleaner = GraphCleaner()
    conflicts = cleaner.detect_conflicts_in_triples(triples)
    assert any(c["type"] == "NEGATED_ENTITY_RELATION_CONFLICT" for c in conflicts)

    builder = GraphBuilder()
    inserted_queries = builder.build_graph(triples)
    assert len(inserted_queries) == 0


def test_cypher_qa_filters_negated_true():
    """Test 4: Cypher QA filters negated=true; simulates setting r.negated=true, confirms QA result excludes edge, then reverts."""
    client = Neo4jClient()
    if not client.is_online():
        pytest.skip("Neo4j is offline")

    # Set negated=true on an existing HAS_SYMPTOM edge for Cao huyết áp
    client.execute_query(
        "MATCH (b {name:'Cao huyết áp'})-[r:HAS_SYMPTOM]->(s {name:'Đau đầu'}) SET r.negated = true"
    )
    try:
        qa = TextToCypherQA(neo4j_client=client)
        res = qa.answer_question("Cao huyết áp có triệu chứng gì?")
        symptoms = [row.get("TrieuChung") for row in res["graph_results"]]
        assert "Đau đầu" not in symptoms
    finally:
        client.execute_query(
            "MATCH (b {name:'Cao huyết áp'})-[r:HAS_SYMPTOM]->(s {name:'Đau đầu'}) SET r.negated = false"
        )


def test_temporal_detection():
    """ConText Processor temporal classification check."""
    processor = ConTextProcessor()
    text = "Bệnh nhân có tiền sử Cao huyết áp 3 năm trước."
    entities = [{"entity": "Cao huyết áp", "type": "DISEASE", "start": 22, "end": 34}]
    res = processor.process_entities(text, entities)
    assert res[0]["temporal_context"] == "past"
    assert res[0]["negated"] is False
