"""
Entity Normalizer Module for MedGraph-VI.
Provides uniform entity normalization, alias lookup, and drug class/group categorization.

Normalization Rules:
1. Strips leading/trailing whitespace.
2. Normalizes drug dosage units to lowercase (e.g., '150Mg' -> '150mg', '500Mg' -> '500mg', '10Mg/Tuần' -> '10mg/tuần').
3. Removes inconsistent 'Bệnh ' prefix from disease names for uniform graph matching 
   (e.g., 'Bệnh cao huyết áp' -> 'Cao huyết áp', 'Bệnh Gút' -> 'Gút', 'Bệnh Migraine' -> 'Migraine'), 
   unless preserving the full phrase is necessary.
4. Maps entity string variations to canonical names via ALIAS_MAP.
5. Identifies drug class/group entities (e.g., 'Corticoid', 'Kháng sinh') for proper node classification.
"""

import re
import json
from pathlib import Path
from typing import Dict, Set, Optional

# Drug Class / Group terms
DRUG_GROUPS: Set[str] = {
    "corticoid",
    "corticosteroid",
    "kháng sinh",
    "giãn cơ trơn",
    "thuốc giãn cơ trơn",
    "kháng histamin",
    "thuốc hạ huyết áp",
    "thuốc chẹn beta",
    "thuốc an thần",
    "penicillin",
    "nhóm penicillin",
    "dầu cá",
    "vitamin"
}

# Alias mapping dictionary: variant (lowercased) -> canonical representation
ALIAS_MAP: Dict[str, str] = {
    # Diseases & Symptoms
    "cao huyết áp": "Cao huyết áp",
    "bệnh cao huyết áp": "Cao huyết áp",
    "tăng huyết áp": "Cao huyết áp",
    "bệnh tăng huyết áp": "Cao huyết áp",
    "đái tháo đường týp 2": "Đái tháo đường týp 2",
    "đái tháo đường tuýp 2": "Đái tháo đường týp 2",
    "tiểu đường týp 2": "Đái tháo đường týp 2",
    "tiểu đường tuýp 2": "Đái tháo đường týp 2",
    "đái tháo đường loại 2": "Đái tháo đường týp 2",
    "bệnh tiểu đường tuýp 2": "Đái tháo đường týp 2",
    "đái tháo đường týp 1": "Đái tháo đường týp 1",
    "đái tháo đường tuýp 1": "Đái tháo đường týp 1",
    "tiểu đường týp 1": "Đái tháo đường týp 1",
    "tiểu đường tuýp 1": "Đái tháo đường týp 1",
    "viêm phế quản cấp": "Viêm phế quản cấp",
    "viêm phế quản cấp tính": "Viêm phế quản cấp",
    "viêm phế quản": "Viêm phế quản cấp",
    "viêm ruột thừa cấp": "Viêm ruột thừa cấp",
    "viêm ruột thừa cấp tính": "Viêm ruột thừa cấp",
    "viêm loét dạ dày": "Viêm loét dạ dày",
    "viêm dạ dày": "Viêm loét dạ dày",
    "viêm dạ dày tá tràng": "Viêm loét dạ dày",
    "loét dạ dày tá tràng": "Viêm loét dạ dày",
    "loét dạ dày": "Viêm loét dạ dày",
    "trào ngược dạ dày thực quản": "Trào ngược dạ dày thực quản",
    "trào ngược dạ dày": "Trào ngược dạ dày thực quản",
    "gerd": "Trào ngược dạ dày thực quản",
    "thiếu máu thiếu sắt": "Thiếu máu thiếu sắt",
    "thiếu máu do thiếu sắt": "Thiếu máu thiếu sắt",
    "bệnh gút": "Bệnh Gút",
    "gút": "Bệnh Gút",
    "gout": "Bệnh Gút",
    "bệnh gút cấp": "Bệnh Gút",
    "bệnh phổi tắc nghẽn mạn tính": "Bệnh phổi tắc nghẽn mạn tính",
    "bệnh phổi tắc nghẽn mãn tính": "Bệnh phổi tắc nghẽn mạn tính",
    "copd": "Bệnh phổi tắc nghẽn mạn tính",
    "phổi tắc nghẽn mạn tính": "Bệnh phổi tắc nghẽn mạn tính",
    "thoái hóa khớp gối": "Thoái hóa khớp",
    "thoái hóa khớp": "Thoái hóa khớp",
    "đau thần kinh tọa": "Đau thần kinh tọa",
    "đau dây thần kinh tọa": "Đau thần kinh tọa",
    "rối loạn lipid máu": "Rối loạn lipid máu",
    "mỡ máu cao": "Rối loạn lipid máu",
    "tăng lipid máu": "Rối loạn lipid máu",
    "cơn đau thắt ngực": "Cơn đau thắt ngực",
    "cơn đau thắt ngực cấp tính": "Cơn đau thắt ngực",
    "đau thắt ngực": "Cơn đau thắt ngực",
    "nhồi máu não": "Nhồi máu não",
    "tai biến mạch máu não": "Nhồi máu não",
    "nhồi máu cơ tim cấp": "Nhồi máu cơ tim cấp",
    "nhồi máu cơ tim": "Nhồi máu cơ tim cấp",
    "bệnh migraine": "Bệnh Migraine",
    "migraine": "Bệnh Migraine",
    "đau nửa đầu": "Bệnh Migraine",
    "động kinh": "Động kinh",
    "bệnh động kinh": "Động kinh",
    "suy tim sung huyết": "Suy tim sung huyết",
    "suy tim": "Suy tim sung huyết",
    "hen phế quản": "Hen phế quản",
    "bệnh hen": "Hen phế quản",
    "nhiễm trùng đường tiết niệu": "Nhiễm trùng đường tiết niệu",
    "nhiễm khuẩn đường tiết niệu": "Nhiễm trùng đường tiết niệu",
    "viêm da cơ địa": "Viêm da cơ địa",
    "mụn trứng cá": "Mụn trứng cá",
    "sỏi thận": "Sỏi thận",
    "suy giáp": "Suy giáp",
    "cường giáp": "Cường giáp",
    "viêm khớp dạng thấp": "Viêm khớp dạng thấp",
    "u xơ tử cung": "U xơ tử cung",
    "tiêu chảy cấp": "Tiêu chảy cấp",
    "viêm âm đạo do nấm": "Viêm âm đạo do nấm",
    "viêm âm đạo": "Viêm âm đạo do nấm",
    "phì đại lành tính tuyến tiền liệt": "Phì đại lành tính tuyến tiền liệt",
    "phì đại tuyến tiền liệt": "Phì đại lành tính tuyến tiền liệt",
    "rung nhĩ": "Rung nhĩ",
    "bệnh rung nhĩ": "Rung nhĩ",
    "viêm gan vi-rút B mạn": "Viêm gan vi-rút B mạn",
    "viêm gan vi-rút b mạn": "Viêm gan vi-rút B mạn",
    "viêm gan B mãn tính": "Viêm gan vi-rút B mạn",
    "viêm gan b mãn tính": "Viêm gan vi-rút B mạn",
    "viêm gan B mạn tính": "Viêm gan vi-rút B mạn",
    "viêm gan b mạn tính": "Viêm gan vi-rút B mạn",
    "viêm gan B": "Viêm gan vi-rút B mạn",
    "viêm gan b": "Viêm gan vi-rút B mạn",
    "viêm phổi": "Viêm phổi",
    "viêm phổi cộng đồng": "Viêm phổi",
    "rối loạn lo âu": "Rối loạn lo âu lan tỏa",
    "rối loạn lo âu lan tỏa": "Rối loạn lo âu lan tỏa",
    "đa nang buồng trứng": "Đa nang buồng trứng",
    "hội chứng đa nang buồng trứng": "Đa nang buồng trứng",
    "tiểu đêm": "Tiểu đêm",
    "ho": "ho",
    "đau": "đau",
    "sốt": "sốt",
    "khó thở": "khó thở",
    "ợ nóng": "ợ nóng",

    # Drugs
    "aspirin": "Aspirin 81mg",
    "aspirin 81mg": "Aspirin 81mg",
    "paracetamol": "Paracetamol 500mg",
    "paracetamol 500mg": "Paracetamol 500mg",
    "metformin": "Metformin",
    "metformin 500mg": "Metformin",
    "metformin 850mg": "Metformin",
    "omeprazole": "Omeprazole 20mg",
    "omeprazole 20mg": "Omeprazole 20mg",
    "omeprazol 20mg": "Omeprazole 20mg",
    "esomeprazole": "Esomeprazole 40mg",
    "esomeprazole 40mg": "Esomeprazole 40mg",
    "atorvastatin": "Atorvastatin 20mg",
    "atorvastatin 20mg": "Atorvastatin 20mg",
    "atorvastatin 10mg": "Atorvastatin 20mg",
    "amoxicillin": "Amoxicillin 500mg",
    "amoxicillin 500mg": "Amoxicillin 500mg",
    "bromhexine": "Bromhexine 8mg",
    "bromhexine 8mg": "Bromhexine 8mg",
    "salbutamol": "Salbutamol",
    "furosemide": "Furosemide 40mg",
    "furosemide 40mg": "Furosemide 40mg",
    "lisinopril": "Lisinopril 10mg",
    "lisinopril 10mg": "Lisinopril 10mg",
    "diclofenac": "Diclofenac",
    "diclofenac 50mg": "Diclofenac",
    "celecoxib": "Celecoxib 200mg",
    "celecoxib 200mg": "Celecoxib 200mg",
    "tamsulosin": "Tamsulosin 0.4mg",
    "tamsulosin 0.4mg": "Tamsulosin 0.4mg",
    "sertraline": "Sertraline 50mg",
    "sertraline 50mg": "Sertraline 50mg",
    "cetirizine": "Cetirizine 10mg",
    "cetirizine 10mg": "Cetirizine 10mg",
    "methotrexate": "Methotrexate 10mg/tuần",
    "methotrexate 10mg/tuần": "Methotrexate 10mg/tuần",
    "carbamazepine": "Carbamazepine 200mg",
    "carbamazepine 200mg": "Carbamazepine 200mg",
    "fluconazole": "Fluconazole 150mg",
    "fluconazole 150mg": "Fluconazole 150mg",
    "clotrimazole": "Clotrimazole",
    "desloratadine": "Desloratadine 5mg",
    "desloratadine 5mg": "Desloratadine 5mg",
    "levothyroxine": "Levothyroxine 50mcg",
    "levothyroxine 50mcg": "Levothyroxine 50mcg",
    "methimazole": "Methimazole 5mg",
    "methimazole 5mg": "Methimazole 5mg",
    "tenofovir": "Tenofovir 300mg",
    "tenofovir 300mg": "Tenofovir 300mg",
    "warfarin": "Warfarin 2.5mg",
    "warfarin 2.5mg": "Warfarin 2.5mg",
    "prednisolone": "Prednisolone 5mg",
    "prednisolone 5mg": "Prednisolone 5mg",
    "ciprofloxacin": "Ciprofloxacin 500mg",
    "ciprofloxacin 500mg": "Ciprofloxacin 500mg",
    "augmentin": "Augmentin",
    "amoxicillin/clavulanate 875mg": "Augmentin",
    "oresol": "Oresol",
    "ferrous sulfate": "Ferrous sulfate",
    "ferrous sulfate 325mg": "Ferrous sulfate",
    "ibuprofen": "Ibuprofen"
}

def normalize_entity_name(name: str, entity_type: str = "AUTO") -> str:
    """
    Normalizes raw entity string:
    - Strips whitespace.
    - Lowercases dosage units (e.g. '150Mg' -> '150mg', '500Mg' -> '500mg', '10Mg/Tuần' -> '10mg/tuần').
    - Standardizes 'Bệnh ' prefix for diseases.
    """
    if not name:
        return ""

    clean = name.strip()

    # 1. Lowercase dosage units using regex (e.g. '150Mg' -> '150mg', '10Mg' -> '10mg', '500MG' -> '500mg')
    clean = re.sub(r'(\d+)\s*(Mg|MG|mg|MCG|Mcg|ml|ML)\b', lambda m: f"{m.group(1)}{m.group(2).lower()}", clean)
    clean = re.sub(r'(\d+)\s*(Mg|MG|mg)/(Tuần|tuần|TUẦN)\b', lambda m: f"{m.group(1)}mg/tuần", clean)

    # 2. Normalize 'Bệnh ' prefix if present at start of string
    if clean.lower().startswith("bệnh ") and len(clean.split()) > 2:
        # Strip 'Bệnh ' prefix unless it's 'Bệnh Gút' or 'Bệnh Migraine'
        stripped = clean[5:].strip()
        if stripped.lower() in ("gút", "gout", "migraine"):
            clean = f"Bệnh {stripped.title()}"
        else:
            clean = stripped[0].upper() + stripped[1:]

    return clean

def get_canonical_name(name: str) -> str:
    """
    Looks up canonical name from ALIAS_MAP for a given entity string.
    Returns canonical string if matched, otherwise returns normalized string.
    """
    normalized = normalize_entity_name(name)
    lower_norm = normalized.lower()
    if lower_norm in ALIAS_MAP:
        return ALIAS_MAP[lower_norm]
    
    # Try raw lowercased
    raw_lower = name.strip().lower()
    if raw_lower in ALIAS_MAP:
        return ALIAS_MAP[raw_lower]

    return normalized

def is_drug_group(name: str) -> bool:
    """
    Determines if an entity name represents a Drug Group / Class (e.g. 'Corticoid', 'Kháng sinh')
    rather than a specific single drug product.
    """
    if not name:
        return False

    clean_lower = name.strip().lower()
    if clean_lower in DRUG_GROUPS:
        return True

    if any(keyword in clean_lower for keyword in ["giãn cơ", "kháng sinh", "nhóm ", "corticoid", "kháng histamin"]):
        return True

    return False

def normalize_disease_name(name: str) -> str:
    """
    Standardizes disease/symptom names:
    - Strips leading/trailing whitespace.
    - Removes common Vietnamese prefixes like: 'Bệnh ', 'Hội chứng ', 'Chứng ', 'Tình trạng '.
    - Converts back to Sentence Case (first letter capitalized).
    - Resolves to canonical form via ALIAS_MAP if matched.
    """
    if not name:
        return ""
    
    clean = name.strip()
    
    # Try resolving alias first
    lower_name = clean.lower()
    if lower_name in ALIAS_MAP:
        clean = ALIAS_MAP[lower_name]
    
    # Remove common prefixes (case-insensitive)
    prefixes = [r"^bệnh\s+", r"^hội\s+chứng\s+", r"^chứng\s+", r"^tình\s+trạng\s+"]
    for prefix in prefixes:
        clean = re.sub(prefix, "", clean, flags=re.IGNORECASE)
    
    clean = clean.strip()
    if not clean:
        return name.strip()
    
    # Sentence Case
    clean = clean[0].upper() + clean[1:]
    
    # Re-check alias map with clean normalized name
    lower_clean = clean.lower()
    if lower_clean in ALIAS_MAP:
        return ALIAS_MAP[lower_clean]
        
    return clean

# --- Vietnamese Medical Synonyms Mapping ---
SYNONYM_MAP: Dict[str, str] = {}
_SYN_PATH = Path(__file__).resolve().parent / "medical_synonyms_vi.json"
if _SYN_PATH.exists():
    try:
        with open(_SYN_PATH, "r", encoding="utf-8") as _f:
            SYNONYM_MAP = json.load(_f)
    except Exception as _e:
        print(f"Error loading medical_synonyms_vi.json: {_e}")

def get_term_synonyms(term: str) -> Set[str]:
    """
    Generates alternative synonym variations for a given term by replacing 
    folk or standard words/phrases using the bidirectional SYNONYM_MAP.
    Does up to 2 expansion passes to resolve combinations like "tiểu đường type 2" -> "đái tháo đường týp 2".
    """
    if not term:
        return set()

    results = {term, term.strip(), term.strip().lower()}
    
    # Pre-add standard canonical alias mapping
    canon = get_canonical_name(term)
    results.add(canon)
    results.add(canon.lower())
    
    for _ in range(3):
        current = list(results)
        for t in current:
            t_lower = t.lower()
            
            # 1. Apply folk/standard synonym map replacements
            for key, val in SYNONYM_MAP.items():
                if key in t_lower:
                    pattern = re.compile(re.escape(key), re.IGNORECASE)
                    replaced = pattern.sub(val, t).strip()
                    results.add(replaced)
                    results.add(replaced.lower())
                    if replaced:
                        results.add(replaced[0].upper() + replaced[1:])
            
            # 2. Apply standard alias map lookups
            if t_lower in ALIAS_MAP:
                alias_val = ALIAS_MAP[t_lower]
                results.add(alias_val)
                results.add(alias_val.lower())
                        
    return results

