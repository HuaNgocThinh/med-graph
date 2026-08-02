"""
Fast non-LLM generator for RE and EL annotation sets for MedGraph-VI (Phase 7).
Ensures relation_gold and code_gold columns are strictly left BLANK.
"""

import csv
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

SYNTHETIC_PATH = BASE_DIR / "data" / "synthetic" / "synthetic_data.json"
RELATIONSHIPS_PATH = BASE_DIR / "data" / "exports" / "all_relationships.csv"
ANNOTATION_DIR = BASE_DIR / "data" / "annotation"
ANNOTATION_DIR.mkdir(parents=True, exist_ok=True)

from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.rxnorm_linker import RxNormLinker
from src.entity_linking.entity_normalizer import get_canonical_name, normalize_disease_name

def generate_re_set():
    print("Generating RE annotation set from synthetic data & exported relationships...")
    with open(SYNTHETIC_PATH, "r", encoding="utf-8") as f:
        samples = json.load(f)
        sample_map = {s["id"]: (s["text"], s.get("template_type", "Chung")) for s in samples}

    raw_rels = []
    with open(RELATIONSHIPS_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for r in reader:
            raw_rels.append(r)

    re_rows = []
    seen_pairs = set()
    counter = 1

    # 1. First load positive relationships from exported CSV
    for row in raw_rels:
        h = get_canonical_name(row["Head"])
        t = get_canonical_name(row["Tail"])
        rel = row["Relation"]
        sids = [s.strip() for s in row["SourceSampleID"].split(",") if s.strip()]

        for sid in sids:
            if sid not in sample_map:
                continue
            text, spec = sample_map[sid]

            # Find specific sentence containing head or tail
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
            target_sent = text
            for sent in sentences:
                if h.lower() in sent.lower() or t.lower() in sent.lower():
                    target_sent = sent
                    break

            key = (h.lower(), rel, t.lower(), sid)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)

            notes = []
            sent_lower = target_sent.lower()
            if any(w in sent_lower for w in ["không", "chưa", "không thấy", "bình thường"]):
                notes.append("Có phủ định")
            if any(w in sent_lower for w in ["tiền sử", "tiền căn"]):
                notes.append("Có tiền sử")
            if not notes:
                notes.append(f"Chuyên khoa {spec}")

            re_rows.append({
                "sentence_id": f"RE_{counter:03d}",
                "sample_id": sid,
                "sentence_text": target_sent,
                "entity_1": h,
                "entity_2": t,
                "relation_predicted": rel,
                "relation_gold": "",  # STRICTLY BLANK FOR HUMAN ANNOTATION
                "note": "; ".join(notes)
            })
            counter += 1

    # 2. Add negative (NONE) relation candidates from sentence pairs
    for sid, (text, spec) in sample_map.items():
        if len(re_rows) >= 140:
            break
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        for sent in sentences:
            sent_lower = sent.lower()
            if "bệnh nhân" in sent_lower and ("dùng" in sent_lower or "chẩn đoán" in sent_lower):
                # Form a non-connected pair
                if "tiền sử" in sent_lower:
                    re_rows.append({
                        "sentence_id": f"RE_{counter:03d}",
                        "sample_id": sid,
                        "sentence_text": sent,
                        "entity_1": "Tiền sử bệnh",
                        "entity_2": "Triệu chứng",
                        "relation_predicted": "NONE",
                        "relation_gold": "",
                        "note": "Có tiền sử; Cụm từ không liên kết"
                    })
                    counter += 1

    # Balance into exactly 120 rows
    final_re_rows = re_rows[:120]
    for idx, r in enumerate(final_re_rows, 1):
        r["sentence_id"] = f"RE_{idx:03d}"

    out_path = ANNOTATION_DIR / "re_annotation_set.csv"
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "sentence_id", "sample_id", "sentence_text", "entity_1", "entity_2",
            "relation_predicted", "relation_gold", "note"
        ])
        writer.writeheader()
        writer.writerows(final_re_rows)

    print(f"✅ Created {len(final_re_rows)} rows in '{out_path}'")
    return final_re_rows


def generate_el_set():
    print("Generating EL annotation set...")
    icd_linker = ICD10Linker()
    rx_linker = RxNormLinker()

    raw_entities = [
        ("tiểu đường", "DISEASE", "Tên dân gian (Folk synonym)"),
        ("cao huyết áp", "DISEASE", "Tên dân gian (Folk synonym)"),
        ("đau bao tử", "DISEASE", "Tên dân gian (Folk synonym)"),
        ("nấm da", "DISEASE", "Tên dân gian ngắn"),
        ("đau ngực", "SYMPTOM", "Triệu chứng phổ biến"),
        ("tiểu đêm", "SYMPTOM", "Triệu chứng tiết niệu"),
        ("ho kéo dài", "SYMPTOM", "Triệu chứng hô hấp"),
        ("khó thở", "SYMPTOM", "Triệu chứng hô hấp"),
        ("sốt cao", "SYMPTOM", "Triệu chứng chung"),
        ("đau đầu", "SYMPTOM", "Triệu chứng thần kinh"),
        ("chóng mặt", "SYMPTOM", "Triệu chứng thần kinh"),
        ("buồn nôn", "SYMPTOM", "Triệu chứng tiêu hóa"),
        ("xuất huyết tiêu hóa", "DISEASE", "Tên y khoa chính thức"),
        ("Thalassemia", "DISEASE", "Mã ICD cô lập D56.9"),
        ("Tan máu bẩm sinh", "DISEASE", "Tên tiếng Việt của Thalassemia"),
        ("Viêm loét dạ dày", "DISEASE", "Tên y khoa ICD-10 (K25)"),
        ("Đái tháo đường týp 2", "DISEASE", "Tên y khoa ICD-10 (E11)"),
        ("Cao huyết áp", "DISEASE", "Tên y khoa ICD-10 (I10)"),
        ("Thoái hóa khớp gối", "DISEASE", "Tên y khoa ICD-10 (M17)"),
        ("Viêm phế quản cấp", "DISEASE", "Tên y khoa ICD-10 (J20.9)"),
        ("Rung nhĩ", "DISEASE", "Tên y khoa ICD-10 (I48)"),
        ("Suy tim sung huyết", "DISEASE", "Tên y khoa ICD-10 (I50.9)"),
        ("Rối loạn lipid máu", "DISEASE", "Tên y khoa ICD-10 (E78.5)"),
        ("Trào ngược dạ dày thực quản", "DISEASE", "Tên y khoa ICD-10 (K21.9)"),
        ("Viêm da cơ địa", "DISEASE", "Tên y khoa ICD-10 (L20.9)"),
        ("Hen phế quản", "DISEASE", "Tên y khoa ICD-10 (J45.9)"),
        ("Bệnh phổi tắc nghẽn mạn tính", "DISEASE", "Tên y khoa ICD-10 (J44.9)"),
        ("Phì đại lành tính tuyến tiền liệt", "DISEASE", "Tên y khoa ICD-10 (N40)"),
        ("Nhiễm trùng đường tiết niệu", "DISEASE", "Tên y khoa ICD-10 (N39.0)"),
        ("Đau thắt lưng", "DISEASE", "Tên y khoa ICD-10 (M54.5)"),
        ("Meloxicam 15mg", "DRUG", "Thuốc có hàm lượng 15mg"),
        ("Meloxicam 7.5mg", "DRUG", "Thuốc có hàm lượng 7.5mg"),
        ("Hydrocortisone 10mg", "DRUG", "Thuốc có hàm lượng 10mg"),
        ("Paracetamol 500mg", "DRUG", "Thuốc biệt dược kèm hàm lượng"),
        ("Aspirin 81mg", "DRUG", "Thuốc kèm hàm lượng 81mg"),
        ("Omeprazole 20mg", "DRUG", "Thuốc kèm hàm lượng 20mg"),
        ("Metformin 500mg", "DRUG", "Thuốc kèm hàm lượng 500mg"),
        ("Warfarin 2.5mg", "DRUG", "Thuốc kèm hàm lượng 2.5mg"),
        ("Atorvastatin 20mg", "DRUG", "Thuốc kèm hàm lượng 20mg"),
        ("Lisinopril 10mg", "DRUG", "Thuốc kèm hàm lượng 10mg"),
        ("Tamsulosin 0.4mg", "DRUG", "Thuốc kèm hàm lượng 0.4mg"),
        ("Panadol Extra", "DRUG", "Biệt dược thương mại Việt Nam"),
        ("Amlor 5mg", "DRUG", "Biệt dược thương mại Việt Nam"),
        ("Eugica", "DRUG", "Biệt dược thương mại Việt Nam"),
        ("Hapacol", "DRUG", "Biệt dược thương mại Việt Nam"),
        ("Tanamol", "DRUG", "Biệt dược thương mại Việt Nam"),
        ("Clopidogrel 75mg", "DRUG", "Thuốc kháng tiểu cầu"),
        ("Salbutamol xịt", "DRUG", "Thuốc dạng xịt"),
        ("Insulin Glargine", "DRUG", "Thuốc sinh học insulin"),
        ("Ciprofloxacin 500mg", "DRUG", "Thuốc kháng sinh")
    ]

    el_rows = []
    for idx, (ent_text, ent_type, note) in enumerate(raw_entities, 1):
        if ent_type == "DISEASE" or ent_type == "SYMPTOM":
            res = icd_linker.link_disease(ent_text)
            pred_code = res.get("code") or "UNLINKED"
            source = "ICD10"
            conf = res.get("confidence", 0.9)
        else:
            res = rx_linker.link_drug(ent_text)
            pred_code = res.get("code") or "UNLINKED"
            source = "RxNorm"
            conf = res.get("confidence", 0.9)

        el_rows.append({
            "entity_id": f"EL_{idx:03d}",
            "entity_text": ent_text,
            "entity_type": ent_type,
            "code_predicted": pred_code,
            "code_source": source,
            "confidence": f"{conf:.2f}",
            "code_gold": "",  # STRICTLY BLANK FOR HUMAN ANNOTATION
            "note": note
        })

    out_path = ANNOTATION_DIR / "el_annotation_set.csv"
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "entity_id", "entity_text", "entity_type", "code_predicted",
            "code_source", "confidence", "code_gold", "note"
        ])
        writer.writeheader()
        writer.writerows(el_rows)

    print(f"✅ Created {len(el_rows)} rows in '{out_path}'")
    return el_rows

if __name__ == "__main__":
    generate_re_set()
    generate_el_set()
