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

# ---------------------------------------------------------------------------
# SINGLE AUTHORITY for "is this string too generic to be a clinical entity?"
#
# This is the ONLY place the question is answered. Every entry point -- ICD10Linker,
# GraphBuilder, any future linker -- must call is_generic_term(). It exists because the
# same family of bug has now recurred three times, each time through a different bypass:
#   1. "Bệnh" leaked in as a DISEASE entity.
#   2. "đau" survived the linker's stop-word check because the check returned an
#      "unlinked" dict that STILL carried a usable standard_name, and ALIAS_MAP["đau"]="đau"
#      (a self-map) handed the term straight back. A node named 'đau' was created.
#   3. "viêm" (from "giảm viêm"/"kháng viêm") was never in the stop list at all, so it
#      fuzzy-matched to "Viêm phổi" at 0.90 and produced 3 false PRESCRIBED_FOR edges.
# A local stop-list per module cannot fix this; the gate has to be one function, and the
# graph write path has to enforce it, because that is the only choke point every write
# passes through.
# ---------------------------------------------------------------------------

# Never a clinical entity under ANY label: meta/discourse words, and patient mis-extractions
NEVER_AN_ENTITY: Set[str] = {
    # discourse / meta / patient mis-extractions
    "bệnh", "bệnh nhân", "bệnh nhi", "thuốc", "khám", "chẩn đoán", "tiền sử",
    "hiện tại", "triệu chứng", "lâm sàng", "chứng", "tình trạng", "hội chứng",
    "bị", "trẻ", "người bệnh", "điều trị", "chỉ định", "xét nghiệm", "kết quả",
    "nhân nữ", "nhân nữ 2", "nhân nữ 1", "nhân nam", "bệnh nhân nữ", "bệnh nhân nam",
    # generic pathological process / bare modifier terms
    "viêm", "nhiễm", "nhiễm trùng", "nhiễm khuẩn", "viêm nhiễm", "rối loạn",
    "biến chứng", "tổn thương", "suy", "cấp", "cấp tính", "mạn", "mạn tính",
    # therapeutic-intent phrases and generic drug group terms
    "giảm đau", "giảm viêm", "kháng viêm", "giảm sốt", "hạ sốt", "kháng sinh",
    "thuốc giãn cơ trơn", "giãn cơ trơn", "thuốc hạ áp", "thuốc hạ huyết áp", "hạ huyết áp",
    "thuốc kháng sinh", "thuốc lợi tiểu", "lợi tiểu", "thuốc giảm đau", "thuốc an thần",
    "thuốc dãn mạch", "thuốc giãn mạch", "thuốc chống đông", "chống đông",
    "thuốc bôi", "kem bôi", "thuốc đặt", "corticoid",
}

# Generic procedure terms -- overly broad procedure terms that are not specific procedure names
PROCEDURE_GENERIC_TERMS: Set[str] = {
    "xét nghiệm", "kiểm tra", "theo dõi", "đánh giá", "khám", "đo",
}

# Valid as a SYMPTOM, never as a DISEASE. 'sốt' and 'ho' are legitimate symptom nodes
# in the graph; 'đau' as a DISEASE is not. Keeping this tier separate is what lets the
# gate kill the bogus :DISEASE 'đau' node without destroying the real :SYMPTOM nodes.
NOT_A_DISEASE: Set[str] = {
    "đau", "sốt", "ho", "khó thở", "ngứa", "mệt", "mệt mỏi", "buồn nôn", "nôn",
    "chóng mặt", "hoa mắt", "phù", "sưng", "tê", "run", "ợ nóng", "ợ chua",
    "táo bón", "tiêu chảy", "chán ăn", "sụt cân", "hồi hộp", "đau đầu", "đau bụng",
    "đau khớp", "đau họng", "khát nước",
}

# A 2-character string is too short to fuzzy-match safely against a disease name, but it can
# still be a real symptom -- 'ho' (cough) is a legitimate SYMPTOM node. So the length rule is
# a DISEASE-only rule here; the fuzzy matcher applies its own separate length guard.
MIN_DISEASE_NAME_LENGTH = 3

# --- Unlinked codes (item 3) ---------------------------------------------------------------
# "not linked" used to be written as a STRING sentinel ('ICD-UNKNOWN', 'RXCUI-UNKNOWN', and in
# two other places 'UNKNOWN' / 'N/A'). Three separate costs:
#   1. Neo4j ignores null in a uniqueness constraint but treats equal strings as duplicates, so
#      'REQUIRE d.code IS UNIQUE' could never be created while 15 drugs all held
#      'RXCUI-UNKNOWN'. The constraint was declared, failed silently, and enforced nothing.
#   2. Four different spellings meant every consumer needed its own ad-hoc test.
#   3. A sentinel reads as a value, so an unlinked node can be miscounted as linked.
# The canonical representation is now None (-> a Neo4j node with no `code` property at all).
LEGACY_CODE_SENTINELS = frozenset({"ICD-UNKNOWN", "RXCUI-UNKNOWN", "UNKNOWN", "N/A", ""})


def normalize_code(code) -> Optional[str]:
    """Map any legacy sentinel (or blank) to None. Real codes pass through unchanged."""
    if code is None:
        return None
    text = str(code).strip()
    if text.upper() in LEGACY_CODE_SENTINELS:
        return None
    return text or None


def is_unlinked_code(code) -> bool:
    """True when `code` carries no real identifier, whatever spelling it arrived in."""
    return normalize_code(code) is None


def is_generic_term(name: str, entity_type: str = "DISEASE") -> bool:
    """
    THE gate. True means: refuse to link this string, and refuse to create a node for it.

    entity_type matters -- 'sốt' is a perfectly good SYMPTOM but never a DISEASE, and 'ho'
    is a valid 2-character symptom. Callers that do not know the type get the strict DISEASE
    reading, which fails safe.

    Checks both the lowercased form and the form with the 'Bệnh/Hội chứng/Chứng/Tình trạng'
    prefixes removed, so 'Bệnh viêm' cannot sneak past a check that only knew about 'viêm'.
    """
    if not name or not name.strip():
        return True

    clean = name.strip().lower()
    if re.match(r"^(bệnh\s+)?nhân\s+(nữ|nam)(\s*\d+)?(\s*tuổi)?$", clean):
        return True

    forms = {clean}
    # prefix-stripped form, so 'chứng đau' / 'tình trạng viêm' are caught too
    stripped = re.sub(r"^(bệnh|hội\s+chứng|chứng|tình\s+trạng)\s+", "", clean).strip()
    if stripped:
        forms.add(stripped)

    is_disease = bool(entity_type) and entity_type.upper() == "DISEASE"

    for f in forms:
        if f in NEVER_AN_ENTITY:
            return True
        if is_disease and (f in NOT_A_DISEASE or len(f) < MIN_DISEASE_NAME_LENGTH):
            return True
    return False


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
    "thoái hóa khớp gối": "Thoái hóa khớp gối",
    "thoái hóa khớp": "Thoái hóa khớp gối",
    "đau lưng dưới": "Đau thắt lưng",
    "đau thắt lưng": "Đau thắt lưng",
    "đau thắt lưng cấp": "Đau thắt lưng",
    "đau thắt lưng mạn": "Đau thắt lưng",
    "đau nhói vùng thắt lưng": "Đau thắt lưng",
    "đau thần kinh tọa": "Đau thần kinh tọa",
    "đau dây thần kinh tọa": "Đau thần kinh tọa",
    "rối loạn lipid máu": "Rối loạn lipid máu",
    "mỡ máu cao": "Rối loạn lipid máu",
    "tăng lipid máu": "Rối loạn lipid máu",
    "cơn đau thắt ngực": "Cơn đau thắt ngực",
    "cơn đau thắt ngực cấp tính": "Cơn đau thắt ngực",
    "đau thắt ngực": "Cơn đau thắt ngực",
    "nhồi máu não": "Nhồi máu não",
    # REMOVED (approved 5c): "tai biến mạch máu não" -> "Nhồi máu não".
    # Tai biến mạch máu não (stroke) includes the haemorrhagic forms I60/I61, roughly 15-20%
    # of cases, whose management is the OPPOSITE of infarction (reverse anticoagulation vs
    # thrombolysis). Collapsing it onto I63 is a serious clinical error. Removed from
    # icd10_vi.json in the same pass; kept out of here so the mapping cannot come back via
    # the alias layer.
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

# --- Orthographic (spelling) normalization ---
# Deliberately a SEPARATE mechanism from the synonym map below. These keys are spellings of
# the same word ('tuýp'/'type' -> 'týp'), not different words for the same concept. Keeping
# them apart matters: they are short, generic, often-English tokens, which is exactly the
# class that bleeds into unrelated words ('prototype'). Different risk profile, different step.
SPELLING_MAP: Dict[str, str] = {}
_SPELL_PATH = Path(__file__).resolve().parent / "spelling_variants_vi.json"
if _SPELL_PATH.exists():
    try:
        with open(_SPELL_PATH, "r", encoding="utf-8") as _f:
            SPELLING_MAP = json.load(_f).get("map", {})
    except Exception as _e:
        print(f"Error loading spelling_variants_vi.json: {_e}")

_SPELL_PATTERN = (
    re.compile(r"\b(?:" + "|".join(re.escape(k) for k in
                                   sorted(SPELLING_MAP, key=len, reverse=True)) + r")\b",
               re.IGNORECASE)
    if SPELLING_MAP else None
)

def normalize_spelling(text: str) -> str:
    """
    Normalizes orthographic variants of the same Vietnamese medical word
    (e.g. 'tuýp'/'type' -> 'týp'). Whole-word anchored, single pass, idempotent.
    """
    if not text or _SPELL_PATTERN is None:
        return text or ""
    return _SPELL_PATTERN.sub(lambda m: SPELLING_MAP[m.group(0).lower()], text)


# --- Directional folk -> medical-standard canonicalization ---
# Distinct from SYNONYM_MAP below: that one is BIDIRECTIONAL and only used to expand a
# term into every variant. Canonicalization needs a single preferred direction, otherwise
# "tiểu đường" -> "đái tháo đường" -> "tiểu đường" ping-pongs and never settles.
CANONICAL_SYNONYM_MAP: Dict[str, str] = {}
_CANON_SYN_PATH = Path(__file__).resolve().parent / "canonical_synonyms_vi.json"
if _CANON_SYN_PATH.exists():
    try:
        with open(_CANON_SYN_PATH, "r", encoding="utf-8") as _f:
            CANONICAL_SYNONYM_MAP = json.load(_f).get("map", {})
    except Exception as _e:
        print(f"Error loading canonical_synonyms_vi.json: {_e}")

# Longest key first, so "mỡ máu cao" wins over "mỡ máu" and we never leave a mangled
# half-replaced phrase like "rối loạn lipid máu cao".
#
# \b...\b anchors each key to whole words. Without it a short key eats the inside of an
# unrelated word: the key "type" turned "prototype" into "prototýp" and "Genotype" into
# "Genotýp". \b is Unicode-aware in Python 3, so Vietnamese letters (đ, ă, ê...) count as
# word characters and anchor correctly.
_CANON_KEYS_BY_LEN = sorted(CANONICAL_SYNONYM_MAP.keys(), key=len, reverse=True)
_CANON_PATTERN = (
    re.compile(r"\b(?:" + "|".join(re.escape(k) for k in _CANON_KEYS_BY_LEN) + r")\b",
               re.IGNORECASE)
    if _CANON_KEYS_BY_LEN else None
)

def canonicalize_synonyms(text: str) -> str:
    """
    Rewrites folk/variant Vietnamese medical phrases to their single medical-standard form
    (e.g. 'Tiểu đường' -> 'Đái tháo đường', 'tuýp' -> 'týp').

    Single-pass: replacements are applied simultaneously so one substitution can never be
    re-matched by another key. Idempotent, because no value in CANONICAL_SYNONYM_MAP is
    also a key (enforced by tests/test_synonym_canonicalization.py).
    """
    if not text or _CANON_PATTERN is None:
        return text or ""

    return _CANON_PATTERN.sub(
        lambda m: CANONICAL_SYNONYM_MAP[m.group(0).lower()],
        text
    )

def normalize_disease_name(name: str) -> str:
    """
    Standardizes disease/symptom names:
    - Strips leading/trailing whitespace.
    - Removes common Vietnamese prefixes like: 'Bệnh ', 'Hội chứng ', 'Chứng ', 'Tình trạng '.
    - Rewrites folk synonyms to the medical standard form via CANONICAL_SYNONYM_MAP.
    - Converts back to Sentence Case (first letter capitalized).
    - Resolves to canonical form via ALIAS_MAP if matched.

    Order matters and is deliberate: spelling normalization -> exact ALIAS_MAP hit ->
    prefix strip -> synonym canonicalization -> ALIAS_MAP re-check. Spelling runs first
    because it is orthographic and should settle before any lookup. Prefix stripping must
    run BEFORE synonym canonicalization so that 'Bệnh tiểu đường' reaches 'Đái tháo đường'.
    """
    if not name:
        return ""

    # Step 0: orthographic variants ('tuýp' -> 'týp'), a separate mechanism from synonyms.
    clean = normalize_spelling(name.strip())

    # Try resolving alias first
    lower_name = clean.lower()
    if lower_name in ALIAS_MAP:
        return ALIAS_MAP[lower_name]

    # Remove common prefixes (case-insensitive)
    prefixes = [r"^bệnh\s+", r"^hội\s+chứng\s+", r"^chứng\s+", r"^tình\s+trạng\s+"]
    for prefix in prefixes:
        clean = re.sub(prefix, "", clean, flags=re.IGNORECASE)

    clean = clean.strip()
    if not clean:
        return name.strip()

    # STRIP_BY_CODE for M54.5: strip {"cấp", "nhói", "vùng", "mạn"} when "thắt lưng" is present
    if "thắt lưng" in clean.lower():
        clean = re.sub(r"\b(cấp|nhói|vùng|mạn)\b", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\s+", " ", clean).strip()

    # Alias re-check after prefix stripping, BEFORE synonym rewriting, so an exact
    # alias entry always wins over a generic folk-term substitution.
    if clean.lower() in ALIAS_MAP:
        return ALIAS_MAP[clean.lower()]

    # Folk -> medical standard (the mechanism prefix-stripping cannot provide)
    clean = canonicalize_synonyms(clean).strip()
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


def _build_synonym_classes(pair_map: Dict[str, str]) -> Dict[str, Set[str]]:
    """
    Builds equivalence classes from the pairwise SYNONYM_MAP using union-find.

    The JSON declares synonyms as one-to-one pairs (e.g. 'đau bao tử' -> 'viêm loét dạ dày',
    'đau dạ dày' -> 'viêm loét dạ dày'). Pairwise links alone leave sibling folk terms
    ('đau bao tử' and 'đau dạ dày') mutually unreachable. Computing the transitive closure
    here groups every term that shares a canonical concept into one class, so expanding any
    member yields ALL its equivalents. Returns term(lowercased) -> full set of class members.
    """
    parent: Dict[str, str] = {}

    def find(x: str) -> str:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for _k, _v in pair_map.items():
        union(_k.lower(), _v.lower())

    classes: Dict[str, Set[str]] = {}
    for term in list(parent):
        classes.setdefault(find(term), set()).add(term)

    term_to_class: Dict[str, Set[str]] = {}
    for members in classes.values():
        for m in members:
            term_to_class[m] = members
    return term_to_class


# term(lowercased) -> set of all equivalent terms (transitive closure of SYNONYM_MAP)
SYNONYM_CLASSES: Dict[str, Set[str]] = _build_synonym_classes(SYNONYM_MAP)

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
            
            # 1. Apply folk/standard synonym replacements across the FULL equivalence class,
            #    so every sibling term (e.g. 'đau bao tử' <-> 'đau dạ dày') is reachable,
            #    not just the single pairwise target declared in the JSON.
            for key, members in SYNONYM_CLASSES.items():
                if key in t_lower:
                    pattern = re.compile(re.escape(key), re.IGNORECASE)
                    for val in members:
                        if val == key:
                            continue
                        replaced = pattern.sub(val, t).strip()
                        if replaced:
                            results.add(replaced)
                            results.add(replaced.lower())
                            results.add(replaced[0].upper() + replaced[1:])
            
            # 2. Apply standard alias map lookups
            if t_lower in ALIAS_MAP:
                alias_val = ALIAS_MAP[t_lower]
                results.add(alias_val)
                results.add(alias_val.lower())
                        
    return results

