"""
Unit tests for Vietnamese ConText Negation & Temporal Processor.
"""

import pytest
from src.negation_temporal.context_processor import ConTextProcessor

def test_negation_detection():
    processor = ConTextProcessor()
    text = "Bệnh nhân khám không thấy dấu hiệu Viêm phổi, khám lâm sàng bình thường."
    entities = [{"entity": "Viêm phổi", "type": "DISEASE", "start": 35, "end": 44}]
    
    res = processor.process_entities(text, entities)
    assert res[0]["negated"] is True

def test_temporal_detection():
    processor = ConTextProcessor()
    text = "Bệnh nhân có tiền sử Cao huyết áp 3 năm trước."
    entities = [{"entity": "Cao huyết áp", "type": "DISEASE", "start": 22, "end": 34}]
    
    res = processor.process_entities(text, entities)
    assert res[0]["temporal_context"] == "past"
    assert res[0]["negated"] is False
