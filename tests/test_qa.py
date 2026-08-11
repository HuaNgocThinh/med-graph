"""
Unit tests for Text-to-Cypher QA module.
"""

import pytest
from src.qa.text_to_cypher import TextToCypherQA

def test_generate_cypher_valid_keyword():
    qa = TextToCypherQA()
    sample_question = "Bệnh nhân Đái tháo đường týp 2 được kê thuốc gì?"
    
    cypher_query = qa.generate_cypher(sample_question)
    
    assert isinstance(cypher_query, str)
    assert len(cypher_query) > 0
    
    # Assert query contains a valid Cypher keyword
    upper_query = cypher_query.upper()
    valid_keywords = ["MATCH", "MERGE", "WITH", "RETURN", "OPTIONAL"]
    assert any(kw in upper_query for kw in valid_keywords), f"Cypher query does not contain valid keywords: '{cypher_query}'"

def test_answer_question_structure():
    qa = TextToCypherQA()
    sample_question = "Thuốc Ibuprofen chống chỉ định với bệnh nào?"
    
    res = qa.answer_question(sample_question)
    
    assert isinstance(res, dict)
    assert "cypher_query" in res
    assert "graph_results" in res
    assert "answer" in res
    assert "data_source" in res
    assert res["data_source"] in ("LIVE_NEO4J", "SIMULATED_OFFLINE")
    assert res["method"] == "KG-QA"
