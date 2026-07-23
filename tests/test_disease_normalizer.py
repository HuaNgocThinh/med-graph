"""
Unit tests for normalize_disease_name() function.
Verifies standardized disease prefix stripping, casing, and canonical alias mapping.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.entity_linking.entity_normalizer import normalize_disease_name

def test_normalize_disease_name_hypertension():
    # Case 1: "Bệnh cao huyết áp" and "Cao huyết áp" both normalize to "Cao huyết áp"
    assert normalize_disease_name("Bệnh cao huyết áp") == "Cao huyết áp"
    assert normalize_disease_name("Cao huyết áp") == "Cao huyết áp"
    assert normalize_disease_name("tăng huyết áp") == "Cao huyết áp"

def test_normalize_disease_name_diabetes():
    # Case 2: "Bệnh tiểu đường", "Đái tháo đường", "Tiểu đường tuýp 2" mapping
    assert normalize_disease_name("Bệnh tiểu đường tuýp 2") == "Đái tháo đường týp 2"
    assert normalize_disease_name("Đái tháo đường tuýp 2") == "Đái tháo đường týp 2"
    assert normalize_disease_name("tiểu đường týp 2") == "Đái tháo đường týp 2"

def test_normalize_disease_name_pneumonia():
    # Case 3: "Viêm phổi" and "Bệnh viêm phổi" normalize to "Viêm phổi"
    assert normalize_disease_name("Bệnh viêm phổi") == "Viêm phổi"
    assert normalize_disease_name("viêm phổi") == "Viêm phổi"

def test_normalize_disease_name_irritable_bowel():
    # Case 4: "Hội chứng ruột kích thích" prefix stripping
    assert normalize_disease_name("Hội chứng ruột kích thích") == "Ruột kích thích"

def test_normalize_disease_name_dehydration():
    # Case 5: "Tình trạng mất nước" prefix stripping
    assert normalize_disease_name("Tình trạng mất nước") == "Mất nước"
