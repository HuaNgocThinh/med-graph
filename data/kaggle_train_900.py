# File dữ liệu tự động sinh và gộp (kaggle_train_900.py)
# Tổng số mẫu: 700 câu (Tự động sinh từ LLM & PyVi Word Segmentation)

TRAIN_DATA = [
    {
        "sample_id": "aug_001",
        "text": "Ghi_nhận dấu_hiệu đau_đầu ở người_bệnh bị viêm phổi .",
        "entities": [
            {
                "word": "đau_đầu",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_002",
        "text": "Bác_sĩ kê đơn Amoxicillin cho bệnh_nhân chẩn_đoán viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_003",
        "text": "Bệnh_nhân có biểu_hiện sốt cao do đái_tháo_đường gây ra .",
        "entities": [
            {
                "word": "sốt cao",
                "type": "SYMPTOM"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_004",
        "text": "Ghi_nhận dấu_hiệu tiêu_chảy ở người_bệnh bị đái_tháo_đường .",
        "entities": [
            {
                "word": "tiêu_chảy",
                "type": "SYMPTOM"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_005",
        "text": "Bệnh_nhân mắc trào ngược dạ_dày kèm theo triệu_chứng ho_khan .",
        "entities": [
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            },
            {
                "word": "ho_khan",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_006",
        "text": "Bác_sĩ chỉ_định Aspirin để điều_trị viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_007",
        "text": "Bệnh_nhân có biểu_hiện tiêu_chảy do sỏi thận gây ra .",
        "entities": [
            {
                "word": "tiêu_chảy",
                "type": "SYMPTOM"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_008",
        "text": "Bác_sĩ chỉ_định Salbutamol để điều_trị viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_009",
        "text": "Bác_sĩ kê đơn Salbutamol cho bệnh_nhân chẩn_đoán trào ngược dạ_dày .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_010",
        "text": "Bệnh_nhân có biểu_hiện tức ngực do sỏi thận gây ra .",
        "entities": [
            {
                "word": "tức ngực",
                "type": "SYMPTOM"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_011",
        "text": "viêm phổi thường dẫn đến triệu_chứng sốt cao kéo_dài .",
        "entities": [
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            },
            {
                "word": "sốt cao",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_012",
        "text": "Bác_sĩ kê đơn Atorvastatin cho bệnh_nhân chẩn_đoán sốt_xuất_huyết .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_013",
        "text": "cao huyết_áp thường dẫn đến triệu_chứng chóng_mặt kéo_dài .",
        "entities": [
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            },
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_014",
        "text": "Kê đơn Metformin để điều_trị cho trường_hợp bị đái_tháo_đường .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_015",
        "text": "Bệnh_nhân dùng Atorvastatin giúp kiểm_soát hiệu_quả bệnh đái_tháo_đường .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_016",
        "text": "Triệu_chứng khó thở xuất_hiện do bệnh_nhân mắc sỏi thận .",
        "entities": [
            {
                "word": "khó thở",
                "type": "SYMPTOM"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_017",
        "text": "viêm phổi thường dẫn đến triệu_chứng tức ngực kéo_dài .",
        "entities": [
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            },
            {
                "word": "tức ngực",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_018",
        "text": "Aspirin chống chỉ_định đối_với bệnh_nhân có tiền_sử trào ngược dạ_dày .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_019",
        "text": "Bệnh_nhân dùng Salbutamol giúp kiểm_soát hiệu_quả bệnh bệnh gút .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_020",
        "text": "Bác_sĩ chỉ_định mổ nội_soi để chẩn_đoán bệnh sốt_xuất_huyết .",
        "entities": [
            {
                "word": "mổ nội_soi",
                "type": "PROCEDURE"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_021",
        "text": "Bệnh_nhân mắc viêm loét dạ_dày kèm theo triệu_chứng đau_đầu .",
        "entities": [
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            },
            {
                "word": "đau_đầu",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_022",
        "text": "Bác_sĩ chỉ_định Omeprazole để điều_trị bệnh gút .",
        "entities": [
            {
                "word": "Omeprazole",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_023",
        "text": "Bệnh_nhân dùng Omeprazole giúp kiểm_soát hiệu_quả bệnh đái_tháo_đường .",
        "entities": [
            {
                "word": "Omeprazole",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_024",
        "text": "Chống chỉ_định dùng Amoxicillin cho người bị nhồi máu cơ tim .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_025",
        "text": "Ghi_nhận dấu_hiệu khó thở ở người_bệnh bị cao huyết_áp .",
        "entities": [
            {
                "word": "khó thở",
                "type": "SYMPTOM"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_026",
        "text": "Triệu_chứng khó thở xuất_hiện do bệnh_nhân mắc viêm loét dạ_dày .",
        "entities": [
            {
                "word": "khó thở",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_027",
        "text": "Ghi_nhận dấu_hiệu buồn_nôn ở người_bệnh bị đái_tháo_đường .",
        "entities": [
            {
                "word": "buồn_nôn",
                "type": "SYMPTOM"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_028",
        "text": "Bệnh_nhân mắc cao huyết_áp kèm theo triệu_chứng tiêu_chảy .",
        "entities": [
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            },
            {
                "word": "tiêu_chảy",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_029",
        "text": "Bác_sĩ kê đơn Omeprazole cho bệnh_nhân chẩn_đoán cao huyết_áp .",
        "entities": [
            {
                "word": "Omeprazole",
                "type": "DRUG"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_030",
        "text": "Tuyệt_đối không được dùng Atorvastatin đối_với bệnh_nhân mắc bệnh gút .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_031",
        "text": "Thực_hiện thử máu cho bệnh_nhân nghi_ngờ mắc viêm loét dạ_dày .",
        "entities": [
            {
                "word": "thử máu",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_032",
        "text": "Ghi_nhận dấu_hiệu khó thở ở người_bệnh bị viêm phổi .",
        "entities": [
            {
                "word": "khó thở",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_033",
        "text": "Bệnh_nhân có biểu_hiện ho_khan do sốt_xuất_huyết gây ra .",
        "entities": [
            {
                "word": "ho_khan",
                "type": "SYMPTOM"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_034",
        "text": "Chống chỉ_định dùng Amoxicillin cho người bị đái_tháo_đường .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_035",
        "text": "Bệnh_nhân có biểu_hiện đau bụng do sốt_xuất_huyết gây ra .",
        "entities": [
            {
                "word": "đau bụng",
                "type": "SYMPTOM"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_036",
        "text": "Bệnh_nhân có biểu_hiện tức ngực do trào ngược dạ_dày gây ra .",
        "entities": [
            {
                "word": "tức ngực",
                "type": "SYMPTOM"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_037",
        "text": "Thực_hiện đo huyết_áp cho bệnh_nhân nghi_ngờ mắc cao huyết_áp .",
        "entities": [
            {
                "word": "đo huyết_áp",
                "type": "PROCEDURE"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_038",
        "text": "cao huyết_áp thường dẫn đến triệu_chứng chóng_mặt kéo_dài .",
        "entities": [
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            },
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_039",
        "text": "Bác_sĩ kê đơn Salbutamol cho bệnh_nhân chẩn_đoán hen phế_quản .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_040",
        "text": "sỏi thận thường dẫn đến triệu_chứng tê bì chi kéo_dài .",
        "entities": [
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            },
            {
                "word": "tê bì chi",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_041",
        "text": "Thực_hiện mổ nội_soi cho bệnh_nhân nghi_ngờ mắc trào ngược dạ_dày .",
        "entities": [
            {
                "word": "mổ nội_soi",
                "type": "PROCEDURE"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_042",
        "text": "Triệu_chứng chóng_mặt xuất_hiện do bệnh_nhân mắc cao huyết_áp .",
        "entities": [
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_043",
        "text": "Azithromycin chống chỉ_định đối_với bệnh_nhân có tiền_sử đái_tháo_đường .",
        "entities": [
            {
                "word": "Azithromycin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_044",
        "text": "Kê đơn Paracetamol để điều_trị cho trường_hợp bị đái_tháo_đường .",
        "entities": [
            {
                "word": "Paracetamol",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_045",
        "text": "Ibuprofen được sử_dụng phổ_biến trong điều_trị trào ngược dạ_dày .",
        "entities": [
            {
                "word": "Ibuprofen",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_046",
        "text": "Bệnh_nhân mắc đái_tháo_đường kèm theo triệu_chứng tê bì chi .",
        "entities": [
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            },
            {
                "word": "tê bì chi",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_047",
        "text": "Chống chỉ_định dùng Clopidogrel cho người bị nhồi máu cơ tim .",
        "entities": [
            {
                "word": "Clopidogrel",
                "type": "DRUG"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_048",
        "text": "Amoxicillin chống chỉ_định đối_với bệnh_nhân có tiền_sử hen phế_quản .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_049",
        "text": "Bác_sĩ chỉ_định chụp X - quang để chẩn_đoán bệnh đái_tháo_đường .",
        "entities": [
            {
                "word": "chụp X - quang",
                "type": "PROCEDURE"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_050",
        "text": "Ghi_nhận dấu_hiệu tiêu_chảy ở người_bệnh bị bệnh gút .",
        "entities": [
            {
                "word": "tiêu_chảy",
                "type": "SYMPTOM"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_051",
        "text": "Kê đơn Metformin để điều_trị cho trường_hợp bị đái_tháo_đường .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_052",
        "text": "trào ngược dạ_dày thường dẫn đến triệu_chứng sốt cao kéo_dài .",
        "entities": [
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            },
            {
                "word": "sốt cao",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_053",
        "text": "Tuyệt_đối không được dùng Paracetamol đối_với bệnh_nhân mắc bệnh gút .",
        "entities": [
            {
                "word": "Paracetamol",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_054",
        "text": "Ibuprofen chống chỉ_định đối_với bệnh_nhân có tiền_sử hen phế_quản .",
        "entities": [
            {
                "word": "Ibuprofen",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_055",
        "text": "Thực_hiện nội_soi cho bệnh_nhân nghi_ngờ mắc bệnh gút .",
        "entities": [
            {
                "word": "nội_soi",
                "type": "PROCEDURE"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_056",
        "text": "Bác_sĩ chỉ_định thử máu để chẩn_đoán bệnh sỏi thận .",
        "entities": [
            {
                "word": "thử máu",
                "type": "PROCEDURE"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_057",
        "text": "Bệnh_nhân có biểu_hiện sốt cao do sốt_xuất_huyết gây ra .",
        "entities": [
            {
                "word": "sốt cao",
                "type": "SYMPTOM"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_058",
        "text": "Kê đơn Ibuprofen để điều_trị cho trường_hợp bị hen phế_quản .",
        "entities": [
            {
                "word": "Ibuprofen",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_059",
        "text": "Kê đơn Salbutamol để điều_trị cho trường_hợp bị viêm phổi .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_060",
        "text": "Bệnh_nhân mắc sốt_xuất_huyết kèm theo triệu_chứng tức ngực .",
        "entities": [
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            },
            {
                "word": "tức ngực",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_061",
        "text": "Bác_sĩ chỉ_định Aspirin để điều_trị sốt_xuất_huyết .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_062",
        "text": "Thực_hiện khám lâm_sàng cho bệnh_nhân nghi_ngờ mắc viêm loét dạ_dày .",
        "entities": [
            {
                "word": "khám lâm_sàng",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_063",
        "text": "Bác_sĩ chỉ_định Omeprazole để điều_trị sỏi thận .",
        "entities": [
            {
                "word": "Omeprazole",
                "type": "DRUG"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_064",
        "text": "Bệnh_nhân dùng Aspirin giúp kiểm_soát hiệu_quả bệnh nhồi máu cơ tim .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_065",
        "text": "Bác_sĩ chỉ_định nội_soi để chẩn_đoán bệnh hen phế_quản .",
        "entities": [
            {
                "word": "nội_soi",
                "type": "PROCEDURE"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_066",
        "text": "Kê đơn Ibuprofen để điều_trị cho trường_hợp bị cao huyết_áp .",
        "entities": [
            {
                "word": "Ibuprofen",
                "type": "DRUG"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_067",
        "text": "Ghi_nhận dấu_hiệu tức ngực ở người_bệnh bị hen phế_quản .",
        "entities": [
            {
                "word": "tức ngực",
                "type": "SYMPTOM"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_068",
        "text": "Amoxicillin được sử_dụng phổ_biến trong điều_trị hen phế_quản .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_069",
        "text": "Bác_sĩ chỉ_định mổ nội_soi để chẩn_đoán bệnh trào ngược dạ_dày .",
        "entities": [
            {
                "word": "mổ nội_soi",
                "type": "PROCEDURE"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_070",
        "text": "Bệnh_nhân có biểu_hiện tiêu_chảy do viêm loét dạ_dày gây ra .",
        "entities": [
            {
                "word": "tiêu_chảy",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_071",
        "text": "Bác_sĩ kê đơn Amoxicillin cho bệnh_nhân chẩn_đoán trào ngược dạ_dày .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_072",
        "text": "Ghi_nhận dấu_hiệu khó thở ở người_bệnh bị nhồi máu cơ tim .",
        "entities": [
            {
                "word": "khó thở",
                "type": "SYMPTOM"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_073",
        "text": "Thực_hiện thử máu cho bệnh_nhân nghi_ngờ mắc nhồi máu cơ tim .",
        "entities": [
            {
                "word": "thử máu",
                "type": "PROCEDURE"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_074",
        "text": "Bệnh_nhân dùng Omeprazole giúp kiểm_soát hiệu_quả bệnh viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Omeprazole",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_075",
        "text": "Bệnh_nhân dùng Metformin giúp kiểm_soát hiệu_quả bệnh viêm phổi .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_076",
        "text": "Bệnh_nhân mắc hen phế_quản kèm theo triệu_chứng chóng_mặt .",
        "entities": [
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            },
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_077",
        "text": "Bệnh_nhân mắc viêm loét dạ_dày kèm theo triệu_chứng ho_khan .",
        "entities": [
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            },
            {
                "word": "ho_khan",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_078",
        "text": "Bệnh_nhân dùng Paracetamol giúp kiểm_soát hiệu_quả bệnh viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Paracetamol",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_079",
        "text": "Bệnh_nhân dùng Paracetamol giúp kiểm_soát hiệu_quả bệnh sốt_xuất_huyết .",
        "entities": [
            {
                "word": "Paracetamol",
                "type": "DRUG"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_080",
        "text": "Bệnh_nhân dùng Salbutamol giúp kiểm_soát hiệu_quả bệnh viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_081",
        "text": "nhồi máu cơ tim thường dẫn đến triệu_chứng chóng_mặt kéo_dài .",
        "entities": [
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            },
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_082",
        "text": "Ibuprofen chống chỉ_định đối_với bệnh_nhân có tiền_sử sỏi thận .",
        "entities": [
            {
                "word": "Ibuprofen",
                "type": "DRUG"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_083",
        "text": "Bệnh_nhân mắc nhồi máu cơ tim kèm theo triệu_chứng chóng_mặt .",
        "entities": [
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            },
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_084",
        "text": "Kê đơn Azithromycin để điều_trị cho trường_hợp bị trào ngược dạ_dày .",
        "entities": [
            {
                "word": "Azithromycin",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_085",
        "text": "Bệnh_nhân có biểu_hiện đau_đầu do đái_tháo_đường gây ra .",
        "entities": [
            {
                "word": "đau_đầu",
                "type": "SYMPTOM"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_086",
        "text": "Ghi_nhận dấu_hiệu tê bì chi ở người_bệnh bị sốt_xuất_huyết .",
        "entities": [
            {
                "word": "tê bì chi",
                "type": "SYMPTOM"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_087",
        "text": "Chống chỉ_định dùng Atorvastatin cho người bị nhồi máu cơ tim .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_088",
        "text": "Bác_sĩ chỉ_định chụp X - quang để chẩn_đoán bệnh đái_tháo_đường .",
        "entities": [
            {
                "word": "chụp X - quang",
                "type": "PROCEDURE"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_089",
        "text": "Bác_sĩ chỉ_định Atorvastatin để điều_trị sốt_xuất_huyết .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_090",
        "text": "Kê đơn Aspirin để điều_trị cho trường_hợp bị viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_091",
        "text": "Bệnh_nhân có biểu_hiện chóng_mặt do hen phế_quản gây ra .",
        "entities": [
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_092",
        "text": "Tuyệt_đối không được dùng Ibuprofen đối_với bệnh_nhân mắc trào ngược dạ_dày .",
        "entities": [
            {
                "word": "Ibuprofen",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_093",
        "text": "Amoxicillin được sử_dụng phổ_biến trong điều_trị nhồi máu cơ tim .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_094",
        "text": "Bệnh_nhân có biểu_hiện đau_đầu do nhồi máu cơ tim gây ra .",
        "entities": [
            {
                "word": "đau_đầu",
                "type": "SYMPTOM"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_095",
        "text": "Kê đơn Salbutamol để điều_trị cho trường_hợp bị đái_tháo_đường .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_096",
        "text": "Bác_sĩ chỉ_định Salbutamol để điều_trị viêm phổi .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_097",
        "text": "Bệnh_nhân dùng Omeprazole giúp kiểm_soát hiệu_quả bệnh cao huyết_áp .",
        "entities": [
            {
                "word": "Omeprazole",
                "type": "DRUG"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_098",
        "text": "Chống chỉ_định dùng Azithromycin cho người bị nhồi máu cơ tim .",
        "entities": [
            {
                "word": "Azithromycin",
                "type": "DRUG"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_099",
        "text": "Bệnh_nhân có biểu_hiện tê bì chi do viêm phổi gây ra .",
        "entities": [
            {
                "word": "tê bì chi",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_100",
        "text": "Atorvastatin được sử_dụng phổ_biến trong điều_trị viêm phổi .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_101",
        "text": "Chống chỉ_định dùng Amoxicillin cho người bị nhồi máu cơ tim .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_102",
        "text": "trào ngược dạ_dày thường dẫn đến triệu_chứng tiêu_chảy kéo_dài .",
        "entities": [
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            },
            {
                "word": "tiêu_chảy",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_103",
        "text": "Ghi_nhận dấu_hiệu tức ngực ở người_bệnh bị cao huyết_áp .",
        "entities": [
            {
                "word": "tức ngực",
                "type": "SYMPTOM"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_104",
        "text": "Bệnh_nhân có biểu_hiện buồn_nôn do viêm loét dạ_dày gây ra .",
        "entities": [
            {
                "word": "buồn_nôn",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_105",
        "text": "Bác_sĩ chỉ_định Clopidogrel để điều_trị hen phế_quản .",
        "entities": [
            {
                "word": "Clopidogrel",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_106",
        "text": "Bác_sĩ chỉ_định Metformin để điều_trị viêm phổi .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_107",
        "text": "Bác_sĩ chỉ_định Clopidogrel để điều_trị nhồi máu cơ tim .",
        "entities": [
            {
                "word": "Clopidogrel",
                "type": "DRUG"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_108",
        "text": "Salbutamol chống chỉ_định đối_với bệnh_nhân có tiền_sử cao huyết_áp .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_109",
        "text": "Bác_sĩ chỉ_định Salbutamol để điều_trị đái_tháo_đường .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_110",
        "text": "Bác_sĩ chỉ_định xét_nghiệm máu để chẩn_đoán bệnh đái_tháo_đường .",
        "entities": [
            {
                "word": "xét_nghiệm máu",
                "type": "PROCEDURE"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_111",
        "text": "Bệnh_nhân mắc đái_tháo_đường kèm theo triệu_chứng chóng_mặt .",
        "entities": [
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            },
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_112",
        "text": "Chống chỉ_định dùng Aspirin cho người bị sỏi thận .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_113",
        "text": "Bệnh_nhân có biểu_hiện đau bụng do sỏi thận gây ra .",
        "entities": [
            {
                "word": "đau bụng",
                "type": "SYMPTOM"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_114",
        "text": "Bác_sĩ chỉ_định Clopidogrel để điều_trị đái_tháo_đường .",
        "entities": [
            {
                "word": "Clopidogrel",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_115",
        "text": "Chống chỉ_định dùng Clopidogrel cho người bị sỏi thận .",
        "entities": [
            {
                "word": "Clopidogrel",
                "type": "DRUG"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_116",
        "text": "Metformin chống chỉ_định đối_với bệnh_nhân có tiền_sử bệnh gút .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_117",
        "text": "Bệnh_nhân có biểu_hiện khó thở do viêm loét dạ_dày gây ra .",
        "entities": [
            {
                "word": "khó thở",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_118",
        "text": "trào ngược dạ_dày thường dẫn đến triệu_chứng sốt cao kéo_dài .",
        "entities": [
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            },
            {
                "word": "sốt cao",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_119",
        "text": "Ghi_nhận dấu_hiệu buồn_nôn ở người_bệnh bị nhồi máu cơ tim .",
        "entities": [
            {
                "word": "buồn_nôn",
                "type": "SYMPTOM"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_120",
        "text": "Triệu_chứng đau_đầu xuất_hiện do bệnh_nhân mắc viêm phổi .",
        "entities": [
            {
                "word": "đau_đầu",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_121",
        "text": "Tuyệt_đối không được dùng Clopidogrel đối_với bệnh_nhân mắc sỏi thận .",
        "entities": [
            {
                "word": "Clopidogrel",
                "type": "DRUG"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_122",
        "text": "Bệnh_nhân dùng Aspirin giúp kiểm_soát hiệu_quả bệnh hen phế_quản .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_123",
        "text": "Bệnh_nhân có biểu_hiện tiêu_chảy do bệnh gút gây ra .",
        "entities": [
            {
                "word": "tiêu_chảy",
                "type": "SYMPTOM"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_124",
        "text": "Metformin được sử_dụng phổ_biến trong điều_trị đái_tháo_đường .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_125",
        "text": "Thực_hiện siêu_âm cho bệnh_nhân nghi_ngờ mắc sốt_xuất_huyết .",
        "entities": [
            {
                "word": "siêu_âm",
                "type": "PROCEDURE"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_126",
        "text": "cao huyết_áp thường dẫn đến triệu_chứng tức ngực kéo_dài .",
        "entities": [
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            },
            {
                "word": "tức ngực",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_127",
        "text": "Bác_sĩ chỉ_định thử máu để chẩn_đoán bệnh bệnh gút .",
        "entities": [
            {
                "word": "thử máu",
                "type": "PROCEDURE"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_128",
        "text": "Bệnh_nhân mắc hen phế_quản kèm theo triệu_chứng ho_khan .",
        "entities": [
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            },
            {
                "word": "ho_khan",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_129",
        "text": "Ghi_nhận dấu_hiệu tiêu_chảy ở người_bệnh bị bệnh gút .",
        "entities": [
            {
                "word": "tiêu_chảy",
                "type": "SYMPTOM"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_130",
        "text": "Thực_hiện nội_soi cho bệnh_nhân nghi_ngờ mắc cao huyết_áp .",
        "entities": [
            {
                "word": "nội_soi",
                "type": "PROCEDURE"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_131",
        "text": "đái_tháo_đường thường dẫn đến triệu_chứng đau_đầu kéo_dài .",
        "entities": [
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            },
            {
                "word": "đau_đầu",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_132",
        "text": "Bác_sĩ kê đơn Salbutamol cho bệnh_nhân chẩn_đoán cao huyết_áp .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_133",
        "text": "bệnh gút thường dẫn đến triệu_chứng đau bụng kéo_dài .",
        "entities": [
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            },
            {
                "word": "đau bụng",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_134",
        "text": "Bệnh_nhân có biểu_hiện khó thở do viêm loét dạ_dày gây ra .",
        "entities": [
            {
                "word": "khó thở",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_135",
        "text": "Ghi_nhận dấu_hiệu buồn_nôn ở người_bệnh bị hen phế_quản .",
        "entities": [
            {
                "word": "buồn_nôn",
                "type": "SYMPTOM"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_136",
        "text": "Tuyệt_đối không được dùng Amoxicillin đối_với bệnh_nhân mắc viêm phổi .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_137",
        "text": "Bệnh_nhân dùng Atorvastatin giúp kiểm_soát hiệu_quả bệnh bệnh gút .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_138",
        "text": "Bác_sĩ chỉ_định Paracetamol để điều_trị sốt_xuất_huyết .",
        "entities": [
            {
                "word": "Paracetamol",
                "type": "DRUG"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_139",
        "text": "Kê đơn Ibuprofen để điều_trị cho trường_hợp bị bệnh gút .",
        "entities": [
            {
                "word": "Ibuprofen",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_140",
        "text": "Azithromycin được sử_dụng phổ_biến trong điều_trị hen phế_quản .",
        "entities": [
            {
                "word": "Azithromycin",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_141",
        "text": "Bác_sĩ kê đơn Atorvastatin cho bệnh_nhân chẩn_đoán hen phế_quản .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_142",
        "text": "Bác_sĩ chỉ_định Aspirin để điều_trị đái_tháo_đường .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_143",
        "text": "Thực_hiện xét_nghiệm máu cho bệnh_nhân nghi_ngờ mắc hen phế_quản .",
        "entities": [
            {
                "word": "xét_nghiệm máu",
                "type": "PROCEDURE"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_144",
        "text": "Bác_sĩ chỉ_định Metformin để điều_trị sỏi thận .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_145",
        "text": "Ibuprofen chống chỉ_định đối_với bệnh_nhân có tiền_sử trào ngược dạ_dày .",
        "entities": [
            {
                "word": "Ibuprofen",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_146",
        "text": "Paracetamol được sử_dụng phổ_biến trong điều_trị bệnh gút .",
        "entities": [
            {
                "word": "Paracetamol",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_147",
        "text": "Triệu_chứng ho_khan xuất_hiện do bệnh_nhân mắc sốt_xuất_huyết .",
        "entities": [
            {
                "word": "ho_khan",
                "type": "SYMPTOM"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_148",
        "text": "Bệnh_nhân có biểu_hiện chóng_mặt do đái_tháo_đường gây ra .",
        "entities": [
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_149",
        "text": "Triệu_chứng tiêu_chảy xuất_hiện do bệnh_nhân mắc trào ngược dạ_dày .",
        "entities": [
            {
                "word": "tiêu_chảy",
                "type": "SYMPTOM"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_150",
        "text": "Bệnh_nhân mắc cao huyết_áp kèm theo triệu_chứng chóng_mặt .",
        "entities": [
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            },
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_151",
        "text": "Bác_sĩ chỉ_định xét_nghiệm máu để chẩn_đoán bệnh cao huyết_áp .",
        "entities": [
            {
                "word": "xét_nghiệm máu",
                "type": "PROCEDURE"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_152",
        "text": "Thực_hiện chụp CT cho bệnh_nhân nghi_ngờ mắc viêm phổi .",
        "entities": [
            {
                "word": "chụp CT",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_153",
        "text": "Metformin được sử_dụng phổ_biến trong điều_trị trào ngược dạ_dày .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_154",
        "text": "Kê đơn Omeprazole để điều_trị cho trường_hợp bị bệnh gút .",
        "entities": [
            {
                "word": "Omeprazole",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_155",
        "text": "Aspirin được sử_dụng phổ_biến trong điều_trị trào ngược dạ_dày .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_156",
        "text": "Bác_sĩ chỉ_định chụp X - quang để chẩn_đoán bệnh nhồi máu cơ tim .",
        "entities": [
            {
                "word": "chụp X - quang",
                "type": "PROCEDURE"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_157",
        "text": "Bệnh_nhân có biểu_hiện chóng_mặt do nhồi máu cơ tim gây ra .",
        "entities": [
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_158",
        "text": "Triệu_chứng buồn_nôn xuất_hiện do bệnh_nhân mắc viêm loét dạ_dày .",
        "entities": [
            {
                "word": "buồn_nôn",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_159",
        "text": "Bệnh_nhân có biểu_hiện ho_khan do viêm loét dạ_dày gây ra .",
        "entities": [
            {
                "word": "ho_khan",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_160",
        "text": "Chống chỉ_định dùng Metformin cho người bị bệnh gút .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_161",
        "text": "Bác_sĩ chỉ_định nội_soi để chẩn_đoán bệnh bệnh gút .",
        "entities": [
            {
                "word": "nội_soi",
                "type": "PROCEDURE"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_162",
        "text": "Triệu_chứng tiêu_chảy xuất_hiện do bệnh_nhân mắc trào ngược dạ_dày .",
        "entities": [
            {
                "word": "tiêu_chảy",
                "type": "SYMPTOM"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_163",
        "text": "Ghi_nhận dấu_hiệu tiêu_chảy ở người_bệnh bị sốt_xuất_huyết .",
        "entities": [
            {
                "word": "tiêu_chảy",
                "type": "SYMPTOM"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_164",
        "text": "Bác_sĩ chỉ_định Aspirin để điều_trị bệnh gút .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_165",
        "text": "Clopidogrel được sử_dụng phổ_biến trong điều_trị bệnh gút .",
        "entities": [
            {
                "word": "Clopidogrel",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_166",
        "text": "Bác_sĩ chỉ_định Aspirin để điều_trị sỏi thận .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_167",
        "text": "Chống chỉ_định dùng Metformin cho người bị sốt_xuất_huyết .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_168",
        "text": "Chống chỉ_định dùng Clopidogrel cho người bị hen phế_quản .",
        "entities": [
            {
                "word": "Clopidogrel",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_169",
        "text": "Bệnh_nhân dùng Atorvastatin giúp kiểm_soát hiệu_quả bệnh sỏi thận .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_170",
        "text": "Bệnh_nhân có biểu_hiện buồn_nôn do viêm phổi gây ra .",
        "entities": [
            {
                "word": "buồn_nôn",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_171",
        "text": "Bác_sĩ kê đơn Atorvastatin cho bệnh_nhân chẩn_đoán viêm phổi .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_172",
        "text": "Salbutamol chống chỉ_định đối_với bệnh_nhân có tiền_sử viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_173",
        "text": "Triệu_chứng tê bì chi xuất_hiện do bệnh_nhân mắc đái_tháo_đường .",
        "entities": [
            {
                "word": "tê bì chi",
                "type": "SYMPTOM"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_174",
        "text": "Ghi_nhận dấu_hiệu khó thở ở người_bệnh bị sỏi thận .",
        "entities": [
            {
                "word": "khó thở",
                "type": "SYMPTOM"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_175",
        "text": "Triệu_chứng đau_đầu xuất_hiện do bệnh_nhân mắc bệnh gút .",
        "entities": [
            {
                "word": "đau_đầu",
                "type": "SYMPTOM"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_176",
        "text": "Amoxicillin chống chỉ_định đối_với bệnh_nhân có tiền_sử trào ngược dạ_dày .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_177",
        "text": "Triệu_chứng tê bì chi xuất_hiện do bệnh_nhân mắc bệnh gút .",
        "entities": [
            {
                "word": "tê bì chi",
                "type": "SYMPTOM"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_178",
        "text": "Ibuprofen chống chỉ_định đối_với bệnh_nhân có tiền_sử viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Ibuprofen",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_179",
        "text": "Chống chỉ_định dùng Atorvastatin cho người bị cao huyết_áp .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_180",
        "text": "Bệnh_nhân mắc sỏi thận kèm theo triệu_chứng buồn_nôn .",
        "entities": [
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            },
            {
                "word": "buồn_nôn",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_181",
        "text": "Chống chỉ_định dùng Salbutamol cho người bị viêm phổi .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "viêm phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_182",
        "text": "bệnh gút thường dẫn đến triệu_chứng chóng_mặt kéo_dài .",
        "entities": [
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            },
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_183",
        "text": "Chống chỉ_định dùng Clopidogrel cho người bị sỏi thận .",
        "entities": [
            {
                "word": "Clopidogrel",
                "type": "DRUG"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_184",
        "text": "Ghi_nhận dấu_hiệu khó thở ở người_bệnh bị nhồi máu cơ tim .",
        "entities": [
            {
                "word": "khó thở",
                "type": "SYMPTOM"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_185",
        "text": "Tuyệt_đối không được dùng Azithromycin đối_với bệnh_nhân mắc viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Azithromycin",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_186",
        "text": "Azithromycin chống chỉ_định đối_với bệnh_nhân có tiền_sử cao huyết_áp .",
        "entities": [
            {
                "word": "Azithromycin",
                "type": "DRUG"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_187",
        "text": "Ghi_nhận dấu_hiệu đau_đầu ở người_bệnh bị bệnh gút .",
        "entities": [
            {
                "word": "đau_đầu",
                "type": "SYMPTOM"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_188",
        "text": "Clopidogrel chống chỉ_định đối_với bệnh_nhân có tiền_sử sốt_xuất_huyết .",
        "entities": [
            {
                "word": "Clopidogrel",
                "type": "DRUG"
            },
            {
                "word": "sốt_xuất_huyết",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_189",
        "text": "Bệnh_nhân dùng Omeprazole giúp kiểm_soát hiệu_quả bệnh bệnh gút .",
        "entities": [
            {
                "word": "Omeprazole",
                "type": "DRUG"
            },
            {
                "word": "bệnh gút",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_190",
        "text": "Bệnh_nhân có biểu_hiện chóng_mặt do cao huyết_áp gây ra .",
        "entities": [
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_191",
        "text": "Bác_sĩ chỉ_định Paracetamol để điều_trị viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Paracetamol",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_192",
        "text": "Tuyệt_đối không được dùng Clopidogrel đối_với bệnh_nhân mắc đái_tháo_đường .",
        "entities": [
            {
                "word": "Clopidogrel",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_193",
        "text": "Tuyệt_đối không được dùng Atorvastatin đối_với bệnh_nhân mắc sỏi thận .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "sỏi thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_194",
        "text": "Bệnh_nhân có biểu_hiện tê bì chi do nhồi máu cơ tim gây ra .",
        "entities": [
            {
                "word": "tê bì chi",
                "type": "SYMPTOM"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_195",
        "text": "Chống chỉ_định dùng Omeprazole cho người bị cao huyết_áp .",
        "entities": [
            {
                "word": "Omeprazole",
                "type": "DRUG"
            },
            {
                "word": "cao huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_196",
        "text": "Ghi_nhận dấu_hiệu ho_khan ở người_bệnh bị đái_tháo_đường .",
        "entities": [
            {
                "word": "ho_khan",
                "type": "SYMPTOM"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_197",
        "text": "Kê đơn Atorvastatin để điều_trị cho trường_hợp bị viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_198",
        "text": "Salbutamol được sử_dụng phổ_biến trong điều_trị nhồi máu cơ tim .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_199",
        "text": "Bác_sĩ chỉ_định Salbutamol để điều_trị viêm loét dạ_dày .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_200",
        "text": "Thực_hiện nội_soi cho bệnh_nhân nghi_ngờ mắc nhồi máu cơ tim .",
        "entities": [
            {
                "word": "nội_soi",
                "type": "PROCEDURE"
            },
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_201",
        "text": "Do nghi_ngờ mắc hội_chứng vành cấp trên nền tăng huyết_áp lâu năm , người_bệnh nhập_viện trong tình_trạng đau tức ngực trái lan ra sau lưng , có chỉ_định khẩn_cấp chụp mạch vành nhằm chẩn_đoán xác_định .",
        "entities": [
            {
                "word": "hội_chứng vành_cấp",
                "type": "DISEASE"
            },
            {
                "word": "chụp mạch_vành",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_202",
        "text": "Bệnh_nhân hen phế_quản bội_nhiễm xuất_hiện cơn khó thở rít dữ_dội do thời_tiết chuyển mùa , lập_tức được kê đơn phối_hợp Salbutamol khí dung kết_hợp kháng_sinh .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_203",
        "text": "Mặc_dù có tiền_sử xuất_huyết tiêu_hóa nặng , do nghi_ngờ viêm loét dạ_dày tá_tràng mạn tính tiến_triển , bác_sĩ vẫn chỉ_định nội_soi dạ_dày thực_quản để kiểm_tra .",
        "entities": [
            {
                "word": "nội_soi dạ_dày thực_quản",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm loét dạ_dày tá_tràng mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_204",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng Aspirin liều cao ở những bệnh_nhân đang mắc chứng_xuất_huyết giảm tiểu_cầu miễn_dịch do nguy_cơ chảy máu ồ_ạt .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "xuất_huyết giảm tiểu_cầu miễn_dịch",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_205",
        "text": "Nhập_viện trong tình_trạng đau_nhói vùng thắt_lưng lan xuống chân phải , kết_quả chụp cộng_hưởng từ cột_sống thắt_lưng xác_định người_bệnh bị thoát_vị đĩa_đệm L5 - S1 .",
        "entities": [
            {
                "word": "đau_nhói vùng thắt_lưng lan xuống chân phải",
                "type": "SYMPTOM"
            },
            {
                "word": "thoát_vị đĩa_đệm L5 - S1",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_206",
        "text": "Nhằm chẩn_đoán chính_xác nguyên_nhân gây liệt mặt ngoại biên bên trái , bệnh_nhân được chỉ_định chụp cắt_lớp vi_tính sọ não khẩn_cấp .",
        "entities": [
            {
                "word": "chụp cắt_lớp vi_tính sọ não",
                "type": "PROCEDURE"
            },
            {
                "word": "liệt mặt ngoại biên bên trái",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_207",
        "text": "Do biến_chứng võng_mạc tiểu_đường tiến_triển nặng gây suy_giảm thị_lực nghiêm_trọng , bệnh_nhân có chỉ_định khẩn_cấp phẫu_thuật cắt dịch kính .",
        "entities": [
            {
                "word": "phẫu_thuật cắt dịch kính",
                "type": "PROCEDURE"
            },
            {
                "word": "võng_mạc tiểu_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_208",
        "text": "Người_bệnh đái_tháo_đường típ 2 nhiều năm xuất_hiện triệu_chứng tê bì ngọn chi và mờ mắt do tăng đường_huyết kéo_dài gây tổn_thương vi_mạch .",
        "entities": [
            {
                "word": "tê bì ngọn chi",
                "type": "SYMPTOM"
            },
            {
                "word": "đái_tháo_đường típ 2",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_209",
        "text": "Nhập_viện trong tình_trạng ho có đờm xanh , sốt cao từng cơn , bệnh_nhân được kê đơn phối_hợp thuốc kháng_sinh và Acetylcystein để long đờm .",
        "entities": [
            {
                "word": "Acetylcystein",
                "type": "DRUG"
            },
            {
                "word": "ho có đờm xanh",
                "type": "SYMPTOM"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_210",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Metformin cho bệnh_nhân suy thận độ 4 do nguy_cơ tích lũy thuốc gây nhiễm toan chuyển_hóa nặng .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "suy thận độ 4",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_211",
        "text": "Do nghi_ngờ mắc bệnh viêm khớp dạng thấp cấp_tính , bác_sĩ chỉ_định xét_nghiệm định_lượng yếu_tố dạng thấp RF và tốc_độ lắng máu .",
        "entities": [
            {
                "word": "viêm khớp dạng thấp",
                "type": "DISEASE"
            },
            {
                "word": "xét_nghiệm định_lượng yếu_tố dạng thấp RF",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_212",
        "text": "Bệnh_nhân xơ_gan cổ_trướng giai_đoạn cuối nhập_viện trong tình_trạng vàng da , phù hai chi dưới và bụng chướng căng do áp_lực tĩnh_mạch cửa tăng cao .",
        "entities": [
            {
                "word": "vàng da",
                "type": "SYMPTOM"
            },
            {
                "word": "xơ_gan cổ_trướng",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_213",
        "text": "Nhằm chẩn_đoán bệnh_lý nhồi máu cơ tim cấp , có chỉ_định khẩn_cấp thực_hiện điện tâm_đồ 12 chuyển đạo ngay khi bệnh_nhân vừa bước vào phòng cấp_cứu .",
        "entities": [
            {
                "word": "điện tâm_đồ 12 chuyển đạo",
                "type": "PROCEDURE"
            },
            {
                "word": "nhồi máu cơ tim cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_214",
        "text": "Bệnh_nhân hen phế_quản mạn tính xuất_hiện tình_trạng co thắt phế_quản nặng do hít phải khói bụi công_nghiệp , được kê đơn phối_hợp viên nén Corticoid và thuốc giãn phế_quản .",
        "entities": [
            {
                "word": "Corticoid",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_215",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng thuốc kháng_viêm không steroid ( NSAIDs ) ở phụ_nữ mang thai 3 tháng cuối do nguy_cơ đóng ống động_mạch sớm ở thai_nhi .",
        "entities": [
            {
                "word": "thuốc kháng_viêm không steroid ( NSAIDs )",
                "type": "DRUG"
            },
            {
                "word": "mang thai 3 tháng cuối",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_216",
        "text": "Nhập_viện trong tình_trạng đau_đầu dữ_dội kết_hợp buồn_nôn , bệnh_nhân được chẩn_đoán mắc chứng tăng huyết_áp ác_tính và có chỉ_định siêu_âm Doppler mạch cảnh .",
        "entities": [
            {
                "word": "đau_đầu dữ_dội",
                "type": "SYMPTOM"
            },
            {
                "word": "tăng huyết_áp ác_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_217",
        "text": "Do nghi_ngờ mắc hội_chứng ruột kích_thích , người_bệnh được chỉ_định nội_soi đại_tràng toàn_bộ nhằm loại_trừ các tổn_thương thực_thể .",
        "entities": [
            {
                "word": "nội_soi đại_tràng toàn_bộ",
                "type": "PROCEDURE"
            },
            {
                "word": "hội_chứng ruột kích_thích",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_218",
        "text": "Bệnh_nhân đái_tháo_đường thai kỳ xuất_hiện tình_trạng đa ối và nhiễm_trùng đường tiết_niệu do lượng đường_huyết không ổn_định trong suốt thai kỳ .",
        "entities": [
            {
                "word": "đa ối",
                "type": "SYMPTOM"
            },
            {
                "word": "đái_tháo_đường thai kỳ",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_219",
        "text": "Nhằm điều_trị triệt_để căn_bệnh sỏi thận niệu_quản kích_thước lớn , bác_sĩ chỉ_định phẫu_thuật nội_soi tán sỏi qua da .",
        "entities": [
            {
                "word": "phẫu_thuật nội_soi tán sỏi qua da",
                "type": "PROCEDURE"
            },
            {
                "word": "sỏi thận niệu_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_220",
        "text": "Bệnh_nhân suy tim độ III thường_xuyên gặp phải triệu_chứng khó thở khi gắng_sức và phù về chiều do chức_năng bơm máu của tâm_thất trái suy_giảm .",
        "entities": [
            {
                "word": "khó thở khi gắng_sức",
                "type": "SYMPTOM"
            },
            {
                "word": "suy tim độ III",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_221",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Warfarin đối_với bệnh_nhân đang có ổ loét dạ_dày tiến_triển do nguy_cơ gây xuất_huyết tiêu_hóa ồ_ạt .",
        "entities": [
            {
                "word": "Warfarin",
                "type": "DRUG"
            },
            {
                "word": "loét dạ_dày tiến_triển",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_222",
        "text": "Nhập_viện trong tình_trạng mệt_mỏi cực_độ và sụt cân nhanh_chóng , người_bệnh được kê đơn phối_hợp vitamin tổng_hợp và thuốc_bổ gan .",
        "entities": [
            {
                "word": "mệt_mỏi cực_độ",
                "type": "SYMPTOM"
            },
            {
                "word": "vitamin tổng_hợp",
                "type": "DRUG"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_223",
        "text": "Do nghi_ngờ mắc bệnh gút cấp_tính , bệnh_nhân được chỉ_định xét_nghiệm định_lượng acid uric máu và chụp X - quang khớp bàn_chân .",
        "entities": [
            {
                "word": "gút cấp_tính",
                "type": "DISEASE"
            },
            {
                "word": "xét_nghiệm định_lượng acid uric máu",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_224",
        "text": "Bệnh_nhân viêm phế_quản mạn tính đợt cấp có biểu_hiện ho khạc đờm đặc màu vàng xanh , được kê đơn phối_hợp kháng_sinh mạnh và thuốc long đờm Ambroxol .",
        "entities": [
            {
                "word": "Ambroxol",
                "type": "DRUG"
            },
            {
                "word": "viêm phế_quản mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_225",
        "text": "Nhằm chẩn_đoán bệnh_lý thoái_hóa điểm vàng tuổi già , bác_sĩ có chỉ_định khẩn_cấp chụp cắt_lớp quang_học võng_mạc ( OCT ) .",
        "entities": [
            {
                "word": "chụp cắt_lớp quang_học võng_mạc ( OCT )",
                "type": "PROCEDURE"
            },
            {
                "word": "thoái_hóa điểm vàng tuổi già",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_226",
        "text": "Bệnh_nhân thoát_vị đĩa_đệm cột_sống cổ thường_xuyên gặp phải triệu_chứng tê lan xuống cánh_tay và đau mỏi vai gáy do chèn_ép rễ thần_kinh cổ .",
        "entities": [
            {
                "word": "đau mỏi vai gáy",
                "type": "SYMPTOM"
            },
            {
                "word": "thoát_vị đĩa_đệm cột_sống cổ",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_227",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng thuốc chẹn beta giao_cảm ở những bệnh_nhân đang lên_cơn hen phế_quản cấp vì sẽ làm nặng thêm tình_trạng co thắt .",
        "entities": [
            {
                "word": "thuốc chẹn beta giao_cảm",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_228",
        "text": "Nhập_viện trong tình_trạng đau quặn bụng từng cơn kèm theo buồn_nôn , bệnh_nhân được chẩn_đoán mắc hội_chứng tắc ruột cơ_học và có chỉ_định chụp cắt_lớp vi_tính ổ_bụng .",
        "entities": [
            {
                "word": "đau quặn bụng từng cơn",
                "type": "SYMPTOM"
            },
            {
                "word": "tắc ruột cơ_học",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_229",
        "text": "Do nghi_ngờ mắc bệnh viêm cầu thận cấp sau nhiễm liên cầu_khuẩn , bệnh_nhân được chỉ_định làm xét_nghiệm kháng_thể ASLO và tổng_phân_tích nước_tiểu .",
        "entities": [
            {
                "word": "viêm cầu thận cấp",
                "type": "DISEASE"
            },
            {
                "word": "tổng_phân_tích nước_tiểu",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_230",
        "text": "Bệnh_nhân ung_thư phổi biểu_hiện triệu_chứng ho ra máu và tức ngực kéo_dài , được bác_sĩ kê đơn phối_hợp thuốc giảm đau morphin và hóa_trị_liệu bổ_trợ .",
        "entities": [
            {
                "word": "morphin",
                "type": "DRUG"
            },
            {
                "word": "ho ra máu",
                "type": "SYMPTOM"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_231",
        "text": "Nhằm chẩn_đoán xác_định bệnh_lý loãng_xương nặng ở phụ_nữ mãn_kinh , bác_sĩ chỉ_định đo mật_độ xương bằng phương_pháp DXA.",
        "entities": [
            {
                "word": "đo mật_độ xương bằng phương_pháp DXA",
                "type": "PROCEDURE"
            },
            {
                "word": "loãng_xương",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_232",
        "text": "Bệnh_nhân viêm loét đại_tràng mạn tính xuất_hiện triệu_chứng đi_ngoài phân lẫn máu tươi và đau quặn bụng_dưới do niêm_mạc đại_tràng bị tổn_thương sâu .",
        "entities": [
            {
                "word": "đi_ngoài phân lẫn máu tươi",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm loét đại_tràng mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_233",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Statin liều cao khi bệnh_nhân có biểu_hiện men gan tăng cao gấp 3 lần giới_hạn bình_thường do nguy_cơ hoại_tử_tế_bào gan .",
        "entities": [
            {
                "word": "Statin",
                "type": "DRUG"
            },
            {
                "word": "men gan tăng cao",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_234",
        "text": "Nhập_viện trong tình_trạng sốt cao rét run , đau tức vùng hông lưng phải , bệnh_nhân được chẩn_đoán viêm đài bể thận cấp và có chỉ_định siêu_âm thận ổ_bụng .",
        "entities": [
            {
                "word": "sốt cao rét run",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm đài bể thận cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_235",
        "text": "Do nghi_ngờ mắc chứng nhược cơ toàn_thân , bệnh_nhân được chỉ_định thực_hiện test kích_thích lặp lại sợi cơ và đo điện_cơ_đồ .",
        "entities": [
            {
                "word": "nhược cơ toàn_thân",
                "type": "DISEASE"
            },
            {
                "word": "đo điện_cơ_đồ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_236",
        "text": "Bệnh_nhân đái_tháo_đường típ 2 bị biến_chứng loét bàn_chân nhiễm_trùng nặng , được kê đơn phối_hợp kháng_sinh phổ rộng và thuốc kiểm_soát đường_huyết Insulin .",
        "entities": [
            {
                "word": "Insulin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường típ 2",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_237",
        "text": "Nhằm chẩn_đoán bệnh_lý phình động_mạch chủ bụng , bác_sĩ chỉ_định chụp cắt_lớp vi_tính mạch_máu ( CTA ) có tiêm thuốc cản_quang .",
        "entities": [
            {
                "word": "chụp cắt_lớp vi_tính mạch_máu ( CTA )",
                "type": "PROCEDURE"
            },
            {
                "word": "phình động_mạch chủ bụng",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_238",
        "text": "Bệnh_nhân thoái_hóa khớp gối hai bên thường_xuyên gặp phải tình_trạng cứng khớp buổi sáng và đau nhức khi đi_lại nhiều do mòn sụn khớp .",
        "entities": [
            {
                "word": "cứng khớp buổi sáng",
                "type": "SYMPTOM"
            },
            {
                "word": "thoái_hóa khớp gối",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_239",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng thuốc lợi_tiểu giữ kali cho bệnh_nhân suy thận mạn tính có kèm theo tăng kali máu nặng để tránh nguy_cơ ngừng tim .",
        "entities": [
            {
                "word": "thuốc lợi_tiểu giữ kali",
                "type": "DRUG"
            },
            {
                "word": "tăng kali máu nặng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_240",
        "text": "Nhập_viện trong tình_trạng co_giật toàn_thân kèm mất ý_thức , bệnh_nhân được chẩn_đoán mắc động_kinh cục_bộ toàn_thể_hóa và có chỉ_định chụp cộng_hưởng từ não .",
        "entities": [
            {
                "word": "co_giật toàn_thân",
                "type": "SYMPTOM"
            },
            {
                "word": "động_kinh cục_bộ toàn_thể_hóa",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_241",
        "text": "Do nghi_ngờ mắc hội_chứng Cushing do thuốc , người_bệnh được chỉ_định làm xét_nghiệm định_lượng Cortisol máu lúc 8 giờ sáng .",
        "entities": [
            {
                "word": "hội_chứng Cushing",
                "type": "DISEASE"
            },
            {
                "word": "xét_nghiệm định_lượng Cortisol máu",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_242",
        "text": "Bệnh_nhân glaucoma góc mở mạn tính xuất_hiện triệu_chứng đau nhức hốc mắt và nhìn mờ vòng cầu_vồng , được bác_sĩ kê đơn phối_hợp thuốc nhỏ mắt Timolol .",
        "entities": [
            {
                "word": "Timolol",
                "type": "DRUG"
            },
            {
                "word": "glaucoma góc mở mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_243",
        "text": "Nhằm điều_trị triệt_để bệnh_lý u_xơ tử_cung kích_thước lớn gây rong kinh kéo_dài , có chỉ_định khẩn_cấp phẫu_thuật cắt tử_cung toàn_phần .",
        "entities": [
            {
                "word": "phẫu_thuật cắt tử_cung toàn_phần",
                "type": "PROCEDURE"
            },
            {
                "word": "u_xơ tử_cung",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_244",
        "text": "Bệnh_nhân hội_chứng thận hư mạn tính xuất_hiện tình_trạng phù toàn_thân , tiểu ít và lượng protein niệu tăng cao do màng lọc cầu thận bị tổn_thương .",
        "entities": [
            {
                "word": "phù toàn_thân",
                "type": "SYMPTOM"
            },
            {
                "word": "hội_chứng thận hư",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_245",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc kháng_sinh nhóm Aminoglycoside cho bệnh_nhân suy_giảm thính_lực nặng do nguy_cơ gây điếc vĩnh_viễn .",
        "entities": [
            {
                "word": "Aminoglycoside",
                "type": "DRUG"
            },
            {
                "word": "suy_giảm thính_lực nặng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_246",
        "text": "Nhập_viện trong tình_trạng yếu liệt nửa người bên phải kèm theo nói đớ , bệnh_nhân được chẩn_đoán nhồi máu não cấp và có chỉ_định chụp cắt_lớp vi_tính mạch_máu não .",
        "entities": [
            {
                "word": "yếu liệt nửa người bên phải",
                "type": "SYMPTOM"
            },
            {
                "word": "nhồi máu não cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_247",
        "text": "Do nghi_ngờ mắc bệnhBasedow ( bệnh bướu độc lan_tỏa ) , bác_sĩ chỉ_định xét_nghiệm định_lượng hormone tuyến_giáp FT3 , FT4 và TSH.",
        "entities": [
            {
                "word": "Basedow",
                "type": "DISEASE"
            },
            {
                "word": "xét_nghiệm định_lượng hormone tuyến_giáp FT3 , FT4 và TSH",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_248",
        "text": "Bệnh_nhân viêm dạ_dày cấp_tính do vi_khuẩn Helicobacter pylori xuất_hiện triệu_chứng đau thượng_vị dữ_dội sau khi ăn , được kê đơn phối_hợp phác_đồ kháng_sinh tiệt_trừ HP.",
        "entities": [
            {
                "word": "đau thượng_vị dữ_dội",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm dạ_dày cấp_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_249",
        "text": "Nhằm chẩn_đoán xác_định bệnh_lý thiếu máu cơ tim cục_bộ mạn tính , người_bệnh có chỉ_định khẩn_cấp thực_hiện nghiệm pháp gắng_sức điện tâm_đồ .",
        "entities": [
            {
                "word": "nghiệm pháp gắng_sức điện tâm_đồ",
                "type": "PROCEDURE"
            },
            {
                "word": "thiếu máu cơ tim cục_bộ mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_250",
        "text": "Bệnh_nhân viêm gan B mạn tính đợt bùng_phát_biểu_hiện mệt_mỏi , vàng da và chán ăn , được bác_sĩ kê đơn phối_hợp thuốc kháng virus Tenofovir để ức_chế sự nhân lên của virus .",
        "entities": [
            {
                "word": "Tenofovir",
                "type": "DRUG"
            },
            {
                "word": "viêm gan B mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_251",
        "text": "Do nghi_ngờ mắc hội_chứng vành cấp trên nền huyết khối , bệnh_nhân được chỉ_định thực_hiện chụp mạch vành_qua da nhằm chẩn_đoán chính_xác tổn_thương .",
        "entities": [
            {
                "word": "hội_chứng vành_cấp",
                "type": "DISEASE"
            },
            {
                "word": "chụp mạch vành_qua da",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_252",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng Aspirin liều cao đối_với những trường_hợp đang xuất_huyết tiêu_hóa cấp_tính .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "xuất_huyết tiêu_hóa cấp_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_253",
        "text": "Bệnh_nhân nhập_viện trong tình_trạng khó thở dữ_dội kèm theo tiếng rít thanh_quản do cơn hen phế_quản ác_tính bùng_phát .",
        "entities": [
            {
                "word": "hen phế_quản ác_tính",
                "type": "DISEASE"
            },
            {
                "word": "khó thở dữ_dội",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_254",
        "text": "Để kiểm_soát huyết_áp tâm thu tăng cao đột_ngột , bác_sĩ đã kê đơn phối_hợp Amlodipin và Perindopril .",
        "entities": [
            {
                "word": "Amlodipin",
                "type": "DRUG"
            },
            {
                "word": "tăng huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_255",
        "text": "Nhằm chẩn_đoán phân_biệt giữa nhồi máu cơ tim và viêm màng ngoài tim , các bác_sĩ đã tiến_hành đo điện tâm_đồ 12 chuyển đạo .",
        "entities": [
            {
                "word": "nhồi máu cơ tim",
                "type": "DISEASE"
            },
            {
                "word": "điện tâm_đồ 12 chuyển đạo",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_256",
        "text": "Do tình_trạng xơ_gan mất bù diễn tiến nặng , người_bệnh xuất_hiện triệu_chứng cổ chướng căng và vàng da toàn_thân .",
        "entities": [
            {
                "word": "xơ_gan mất bù",
                "type": "DISEASE"
            },
            {
                "word": "cổ chướng căng",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_257",
        "text": "Thuốc Metformin có chỉ_định khẩn_cấp trong việc điều_trị kiểm_soát đường_huyết cho bệnh_nhân đái_tháo_đường týp 2 .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường týp 2",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_258",
        "text": "Vì bệnh_nhân có tiền_sử suy thận mạn độ 4 , việc sử_dụng các kháng_sinh nhóm Aminoglycosid là tuyệt_đối chống chỉ_định .",
        "entities": [
            {
                "word": "Aminoglycosid",
                "type": "DRUG"
            },
            {
                "word": "suy thận mạn",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_259",
        "text": "Nhập_viện trong tình_trạng đau thắt ngực trái lan ra sau lưng , người_bệnh ngay lập_tức được chỉ_định chụp cắt_lớp vi_tính động_mạch chủ .",
        "entities": [
            {
                "word": "đau thắt ngực trái",
                "type": "SYMPTOM"
            },
            {
                "word": "chụp cắt_lớp vi_tính động_mạch chủ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_260",
        "text": "Do áp_lực nội sọ tăng cao đột_ngột sau chấn_thương , bệnh_nhân biểu_hiện triệu_chứng đau_đầu dữ_dội và nôn vọt .",
        "entities": [
            {
                "word": "tăng áp_lực nội sọ",
                "type": "DISEASE"
            },
            {
                "word": "nôn_vọt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_261",
        "text": "Nhằm hạ_sốt và giảm đau tức_thì cho trẻ bị viêm họng cấp , bác_sĩ đã kê đơn sử_dụng Paracetamol gói 250mg .",
        "entities": [
            {
                "word": "Paracetamol",
                "type": "DRUG"
            },
            {
                "word": "viêm họng cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_262",
        "text": "Bệnh_nhân mắc thoái_hóa khớp gối nặng có biểu_hiện sưng nóng đỏ đau và tiếng lục_cục khi vận_động .",
        "entities": [
            {
                "word": "thoái_hóa khớp gối",
                "type": "DISEASE"
            },
            {
                "word": "sưng nóng đỏ đau",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_263",
        "text": "Để phát_hiện sớm các tổn_thương thoái_hóa đĩa_đệm cột_sống thắt_lưng , bác_sĩ chỉ_định thực_hiện chụp cộng_hưởng từ MRI.",
        "entities": [
            {
                "word": "thoái_hóa đĩa_đệm cột_sống thắt_lưng",
                "type": "DISEASE"
            },
            {
                "word": "chụp cộng_hưởng từ MRI",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_264",
        "text": "Do nghi_ngờ mắc bệnh_lý viêm loét đại_tràng mạn tính , người_bệnh có chỉ_định khẩn_cấp thực_hiện nội_soi đại trực_tràng .",
        "entities": [
            {
                "word": "viêm loét đại_tràng mạn tính",
                "type": "DISEASE"
            },
            {
                "word": "nội_soi đại trực_tràng",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_265",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Warfarin đối_với phụ_nữ đang mang thai trong 3 tháng đầu do nguy_cơ gây quái_thai .",
        "entities": [
            {
                "word": "Warfarin",
                "type": "DRUG"
            },
            {
                "word": "quái_thai",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_266",
        "text": "Nhập_viện trong tình_trạng liệt nửa người bên trái do tai_biến mạch_máu não , bệnh_nhân được kê đơn phối_hợp thuốc chống kết tập tiểu_cầu .",
        "entities": [
            {
                "word": "tai_biến mạch_máu não",
                "type": "DISEASE"
            },
            {
                "word": "liệt nửa người",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_267",
        "text": "Nhằm điều_trị triệt_để căn_bệnh viêm phổi cộng_đồng do phế cầu_khuẩn , phác_đồ điều_trị được kê đơn phối_hợp kháng_sinh mạnh .",
        "entities": [
            {
                "word": "viêm phổi cộng_đồng",
                "type": "DISEASE"
            },
            {
                "word": "kháng_sinh",
                "type": "DRUG"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_268",
        "text": "Bệnh_nhân bị hen phế_quản mạn tính tuyệt_đối chống chỉ_định sử_dụng thuốc chẹn beta giao_cảm không chọn_lọc .",
        "entities": [
            {
                "word": "thuốc chẹn beta giao_cảm",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_269",
        "text": "Do mắc chứng loãng_xương nặng ở người cao_tuổi , người_bệnh thường_xuyên chịu_đựng những cơn đau nhức xương khớp và dễ gãy xương .",
        "entities": [
            {
                "word": "loãng_xương",
                "type": "DISEASE"
            },
            {
                "word": "đau nhức xương khớp",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_270",
        "text": "Nhằm chẩn_đoán chính_xác tình_trạng đục thủy_tinh_thể , bác_sĩ nhãn khoa đã chỉ_định thực_hiện siêu_âm mắt toàn_diện .",
        "entities": [
            {
                "word": "đục thủy_tinh_thể",
                "type": "DISEASE"
            },
            {
                "word": "siêu_âm mắt",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_271",
        "text": "Bệnh_nhân có chỉ_định khẩn_cấp thực_hiện phẫu_thuật cắt ruột_thừa nội_soi do chẩn_đoán xác_định viêm ruột_thừa cấp .",
        "entities": [
            {
                "word": "viêm ruột_thừa cấp",
                "type": "DISEASE"
            },
            {
                "word": "phẫu_thuật cắt ruột_thừa nội_soi",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_272",
        "text": "Để điều_trị triệu_chứng viêm mũi dị_ứng theo mùa , bác_sĩ đã kê đơn thuốc kháng Histamin thế_hệ mới kết_hợp xịt mũi .",
        "entities": [
            {
                "word": "kháng Histamin",
                "type": "DRUG"
            },
            {
                "word": "viêm mũi dị_ứng",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_273",
        "text": "Do biến_chứng võng_mạc đái_tháo_đường giai_đoạn nặng , thị_lực của bệnh_nhân suy_giảm nghiêm_trọng kèm theo hiện_tượng ruồi bay trước_mắt .",
        "entities": [
            {
                "word": "võng_mạc đái_tháo_đường",
                "type": "DISEASE"
            },
            {
                "word": "suy_giảm thị_lực",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_274",
        "text": "Nhập_viện trong tình_trạng hôn_mê sâu do đái_tháo_đường nhiễm toan ceton , bệnh_nhân lập_tức được truyền Insulin tĩnh_mạch liên_tục .",
        "entities": [
            {
                "word": "Insulin",
                "type": "DRUG"
            },
            {
                "word": "nhiễm toan ceton",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_275",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc kháng_viêm không steroid ( NSAIDs ) cho người_bệnh đang có tiền_sử loét dạ_dày tá_tràng .",
        "entities": [
            {
                "word": "NSAIDs",
                "type": "DRUG"
            },
            {
                "word": "loét dạ_dày tá_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_276",
        "text": "Nhằm loại_trừ khả_năng ung_thư dạ_dày ác_tính , người_bệnh có chỉ_định thực_hiện nội_soi dạ_dày kèm sinh_thiết mô .",
        "entities": [
            {
                "word": "ung_thư dạ_dày",
                "type": "DISEASE"
            },
            {
                "word": "sinh_thiết mô",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_277",
        "text": "Do hội_chứng thận hư gây tổn_thương cầu thận nặng , bệnh_nhân biểu_hiện triệu_chứng phù toàn_thân và tiểu ít nước_tiểu .",
        "entities": [
            {
                "word": "hội_chứng thận hư",
                "type": "DISEASE"
            },
            {
                "word": "phù toàn_thân",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_278",
        "text": "Bác_sĩ đã kê đơn phối_hợp thuốc Salbutamol và Budesonide nhằm kiểm_soát cơn khó thở cấp cho bệnh_nhân hen_suyễn .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "hen_suyễn",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_279",
        "text": "Nhập_viện trong tình_trạng đau quặn thận phải do sỏi niệu_quản , người_bệnh được chỉ_định thực_hiện chụp X - quang bụng không chuẩn_bị .",
        "entities": [
            {
                "word": "sỏi niệu_quản",
                "type": "DISEASE"
            },
            {
                "word": "chụp X - quang bụng",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_280",
        "text": "Do mắc chứng suy giáp bẩm_sinh , trẻ thường có biểu_hiện chậm phát_triển tâm_thần và thân_nhiệt thấp .",
        "entities": [
            {
                "word": "suy giáp",
                "type": "DISEASE"
            },
            {
                "word": "chậm phát_triển tâm_thần",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_281",
        "text": "Thuốc Levothyroxine có chỉ_định điều_trị thay_thế hormone tuyến_giáp cho những trường_hợp bị suy giáp nguyên_phát .",
        "entities": [
            {
                "word": "Levothyroxine",
                "type": "DRUG"
            },
            {
                "word": "suy giáp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_282",
        "text": "Tuyệt_đối chống chỉ_định thực_hiện_sinh_thiết gan đối_với các bệnh_nhân đang mắc hội_chứng rối_loạn đông máu nặng .",
        "entities": [
            {
                "word": "rối_loạn đông máu",
                "type": "DISEASE"
            },
            {
                "word": "sinh_thiết gan",
                "type": "PROCEDURE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_283",
        "text": "Nhằm chẩn_đoán bệnh_lý xơ_cứng bì toàn_thể , bác_sĩ da_liễu đã chỉ_định thực_hiện xét_nghiệm kháng_thể kháng nhân ANA.",
        "entities": [
            {
                "word": "xơ_cứng bì toàn_thể",
                "type": "DISEASE"
            },
            {
                "word": "xét_nghiệm kháng_thể kháng nhân ANA",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_284",
        "text": "Do bệnh_lý Gout cấp_tính bùng_phát dữ_dội , người_bệnh than_phiền về tình_trạng đau buốt khớp ngón chân cái và sưng đỏ .",
        "entities": [
            {
                "word": "Gout",
                "type": "DISEASE"
            },
            {
                "word": "sưng đỏ",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_285",
        "text": "Để điều_trị hiệu_quả cơn đau cấp do Gout , bác_sĩ đã kê đơn thuốc Colchicine kết_hợp với thuốc giảm đau .",
        "entities": [
            {
                "word": "Colchicine",
                "type": "DRUG"
            },
            {
                "word": "Gout",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_286",
        "text": "Nhập_viện trong tình_trạng nhịp tim nhanh kịch phát trên thất , bệnh_nhân có chỉ_định khẩn_cấp thực_hiện sốc điện chuyển nhịp .",
        "entities": [
            {
                "word": "nhịp tim nhanh kịch phát trên thất",
                "type": "DISEASE"
            },
            {
                "word": "sốc điện chuyển nhịp",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_287",
        "text": "Do bị nhiễm_trùng huyết nặng do vi_khuẩn Gram_âm , bệnh_nhân xuất_hiện triệu_chứng huyết ápụt giảm và sốt cao rét run .",
        "entities": [
            {
                "word": "nhiễm_trùng huyết",
                "type": "DISEASE"
            },
            {
                "word": "sốt cao rét run",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_288",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng thuốc Isotretinoin đường uống đối_với phụ_nữ chuẩn_bị mang thai do độc_tính cao lên thai_nhi .",
        "entities": [
            {
                "word": "Isotretinoin",
                "type": "DRUG"
            },
            {
                "word": "quái_thai",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_289",
        "text": "Nhằm đánh_giá chính_xác mức_độ tổn_thương van tim trong bệnh thấp tim , bác_sĩ chỉ_định siêu_âm tim qua thực_quản .",
        "entities": [
            {
                "word": "thấp tim",
                "type": "DISEASE"
            },
            {
                "word": "siêu_âm tim qua thực_quản",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_290",
        "text": "Bệnh_nhân mắc hội_chứng ruột kích_thích thường_xuyên gặp phải triệu_chứng đau bụng âm_ỉ kèm theo rối_loạn đại_tiện .",
        "entities": [
            {
                "word": "hội_chứng ruột kích_thích",
                "type": "DISEASE"
            },
            {
                "word": "đau bụng âm_ỉ",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_291",
        "text": "Để giải_quyết tình_trạng tắc ruột cơ_học do dây dính , kíp phẫu_thuật đã tiến_hành mổ mở giải_phóng khúc ruột tắc .",
        "entities": [
            {
                "word": "tắc ruột",
                "type": "DISEASE"
            },
            {
                "word": "mổ mở giải_phóng khúc ruột tắc",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_292",
        "text": "Thuốc Omeprazol có chỉ_định điều_trị lành vết loét dạ_dày tá_tràng và ngăn_ngừa hội_chứng trào ngược axit .",
        "entities": [
            {
                "word": "Omeprazol",
                "type": "DRUG"
            },
            {
                "word": "loét dạ_dày tá_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_293",
        "text": "Do biến_chứng của bệnh đái_tháo đường lâu năm , người_bệnh bị suy_giảm chức_năng thận và xuất_hiện bọt trong nước_tiểu .",
        "entities": [
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            },
            {
                "word": "suy_giảm chức_năng thận",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_294",
        "text": "Nhằm chẩn_đoán bệnh_lý glaucoma góc mở mạn tính , bác_sĩ nhãn khoa đã tiến_hành đo nhãn áp_kế Maklakov .",
        "entities": [
            {
                "word": "glaucoma góc mở mạn tính",
                "type": "DISEASE"
            },
            {
                "word": "đo nhãn áp_kế",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_295",
        "text": "Bệnh_nhân bị nhồi máu cơ tim cấp có chỉ_định khẩn_cấp thực_hiện can_thiệp mạch vành_qua da để tái_thông động_mạch .",
        "entities": [
            {
                "word": "nhồi máu cơ tim cấp",
                "type": "DISEASE"
            },
            {
                "word": "can_thiệp mạch vành_qua da",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_296",
        "text": "Do bị viêm khớp dạng thấp tiến_triển nặng , người_bệnh biểu_hiện cứng khớp buổi sáng kéo_dài trên một giờ .",
        "entities": [
            {
                "word": "viêm khớp dạng thấp",
                "type": "DISEASE"
            },
            {
                "word": "cứng khớp buổi sáng",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_297",
        "text": "Bác_sĩ đã kê đơn phối_hợp Methotrexate và Acid_Folic nhằm điều_trị hiệu_quả bệnh_lý viêm khớp dạng thấp .",
        "entities": [
            {
                "word": "Methotrexate",
                "type": "DRUG"
            },
            {
                "word": "viêm khớp dạng thấp",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_298",
        "text": "Nhập_viện trong tình_trạng đau_đầu dữ_dội kèm theo cứng gáy do xuất_huyết dưới nhện , bệnh_nhân được chỉ_định chụp mạch_máu não số hóa xóa_nền DSA.",
        "entities": [
            {
                "word": "xuất_huyết dưới nhện",
                "type": "DISEASE"
            },
            {
                "word": "cứng gáy",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_299",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Furosemid liều cao đối_với bệnh_nhân đang trong tình_trạng mất nước_nặng và vô niệu .",
        "entities": [
            {
                "word": "Furosemid",
                "type": "DRUG"
            },
            {
                "word": "vô niệu",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_300",
        "text": "Nhằm mục_đích chẩn_đoán xác_định bệnh ung_thư biểu mô tuyến vú , bệnh_nhân có chỉ_định thực_hiện_sinh_thiết lõi kim dưới hướng_dẫn siêu_âm .",
        "entities": [
            {
                "word": "ung_thư biểu mô tuyến vú",
                "type": "DISEASE"
            },
            {
                "word": "sinh_thiết lõi kim",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_301",
        "text": "Do nghi_ngờ mắc hội_chứng vành cấp trên nền tăng huyết_áp mãn_tính , bệnh_nhân được chỉ_định thực_hiện chụp mạch vành_qua da nhằm chẩn_đoán chính_xác tổn_thương .",
        "entities": [
            {
                "word": "hội_chứng vành_cấp",
                "type": "DISEASE"
            },
            {
                "word": "chụp mạch vành_qua da",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_302",
        "text": "Mặc_dù có tiền_sử hen phế_quản nặng , bác_sĩ vẫn kê đơn phối_hợp Salbutamol nhằm cắt_cơn khó thở cấp cho người_bệnh .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản nặng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_303",
        "text": "Nhập_viện trong tình_trạng đau thắt ngực dữ_dội kèm theo khó thở , người_bệnh ngay lập_tức có chỉ_định khẩn_cấp chụp cắt_lớp vi_tính mạch vành .",
        "entities": [
            {
                "word": "đau thắt ngực",
                "type": "SYMPTOM"
            },
            {
                "word": "chụp cắt_lớp vi_tính mạch_vành",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_304",
        "text": "Do tình_trạng trào ngược dạ_dày thực_quản tái_phát liên_tục , Omeprazol được bác_sĩ kê đơn nhằm kiểm_soát axit dịch_vị và làm_lành ổ loet .",
        "entities": [
            {
                "word": "Omeprazol",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày thực_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_305",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng Aspirin cho các trường_hợp xuất_huyết tiêu_hóa do nguy_cơ làm trầm_trọng thêm tình_trạng chảy_máu .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "xuất_huyết tiêu_hóa",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_306",
        "text": "Nhằm chẩn_đoán nguyên_nhân gây đau_đầu kéo_dài , bác_sĩ đã yêu_cầu thực_hiện chụp cộng_hưởng từ sọ não cho bệnh_nhân .",
        "entities": [
            {
                "word": "đau_đầu",
                "type": "SYMPTOM"
            },
            {
                "word": "chụp cộng_hưởng từ sọ não",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_307",
        "text": "Bệnh_nhân xuất_hiện triệu_chứng phù hai chi dưới và mệt_mỏi do suy tim mạn tính giai_đoạn cuối .",
        "entities": [
            {
                "word": "suy tim mạn tính",
                "type": "DISEASE"
            },
            {
                "word": "phù hai chi dưới",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_308",
        "text": "Nhập_viện trong tình_trạng đau bụng quặn từng cơn vùng hạ sườn phải , bệnh_nhân được chỉ_định siêu_âm ổ_bụng tổng_quát .",
        "entities": [
            {
                "word": "đau bụng quặn từng cơn",
                "type": "SYMPTOM"
            },
            {
                "word": "siêu_âm ổ_bụng tổng_quát",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_309",
        "text": "Metformin được chỉ_định điều_trị đầu_tay nhằm kiểm_soát đường_huyết ổn_định cho bệnh_nhân đái_tháo_đường týp 2 .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường týp 2",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_310",
        "text": "Do nghi_ngờ viêm ruột_thừa cấp , các bác_sĩ đã tiến_hành phẫu_thuật nội_soi cắt ruột_thừa khẩn_cấp .",
        "entities": [
            {
                "word": "viêm ruột_thừa cấp",
                "type": "DISEASE"
            },
            {
                "word": "phẫu_thuật nội_soi cắt ruột_thừa",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_311",
        "text": "Bệnh_nhân bị viêm khớp dạng thấp thường_xuyên gặp phải tình_trạng cứng khớp buổi sáng kéo_dài hơn một giờ .",
        "entities": [
            {
                "word": "viêm khớp dạng thấp",
                "type": "DISEASE"
            },
            {
                "word": "cứng khớp buổi sáng",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_312",
        "text": "Nhằm mục_đích làm giảm nhanh các triệu_chứng viêm mũi dị_ứng theo mùa , thuốc kháng Histamin thế_hệ mới được kê đơn phối_hợp .",
        "entities": [
            {
                "word": "viêm mũi dị_ứng",
                "type": "DISEASE"
            },
            {
                "word": "kháng Histamin",
                "type": "DRUG"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_313",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Corticoid liều cao khi bệnh_nhân đang mắc các bệnh_lý nhiễm nấm toàn_thân nặng .",
        "entities": [
            {
                "word": "Corticoid",
                "type": "DRUG"
            },
            {
                "word": "nhiễm nấm toàn_thân",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_314",
        "text": "Nhập_viện trong tình_trạng liệt nửa người bên trái do tai_biến mạch_máu não , bệnh_nhân được tập phục_hồi chức_năng sớm .",
        "entities": [
            {
                "word": "tai_biến mạch_máu não",
                "type": "DISEASE"
            },
            {
                "word": "liệt nửa người",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_315",
        "text": "Do nghi_ngờ mắc bệnh glau - côm góc đóng cấp_tính , bác_sĩ nhãn khoa đã chỉ_định đo nhãn áp và soi góc tiền phòng .",
        "entities": [
            {
                "word": "glau - côm góc đóng",
                "type": "DISEASE"
            },
            {
                "word": "đo nhãn áp",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_316",
        "text": "Insulin Glargine được kê đơn điều_trị nhằm duy_trì đường_huyết lúc đói ở mức an_toàn cho người_bệnh đái_tháo_đường .",
        "entities": [
            {
                "word": "Insulin_Glargine",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_317",
        "text": "Bệnh_nhân hen phế_quản biểu_hiện triệu_chứng khò_khè và ho_khan về đêm khi thời_tiết chuyển mùa .",
        "entities": [
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            },
            {
                "word": "ho_khan",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_318",
        "text": "Nhằm chẩn_đoán xác_định bệnh_lý loãng_xương , bác_sĩ chỉ_định đo mật_độ xương bằng phương_pháp DEXA.",
        "entities": [
            {
                "word": "loãng_xương",
                "type": "DISEASE"
            },
            {
                "word": "đo mật_độ xương",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_319",
        "text": "Do có tiền_sử dị_ứng nặng với kháng_sinh nhóm Beta - lactam , tuyệt_đối chống chỉ_định sử_dụng Amoxicillin .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "dị_ứng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_320",
        "text": "Nhập_viện trong tình_trạng sốt cao kèm ho đờm mác màu gỉ sắt do viêm phổi thùy , bệnh_nhân được chỉ_định chụp X - quang ngực thẳng .",
        "entities": [
            {
                "word": "viêm phổi thùy",
                "type": "DISEASE"
            },
            {
                "word": "chụp X - quang ngực thẳng",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_321",
        "text": "Paracetamol được kê đơn phối_hợp nhằm hạ_sốt và giảm đau cơ xương khớp cho người_bệnh .",
        "entities": [
            {
                "word": "Paracetamol",
                "type": "DRUG"
            },
            {
                "word": "đau cơ xương khớp",
                "type": "SYMPTOM"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_322",
        "text": "Bệnh_nhân thoát_vị đĩa_đệm cột_sống thắt_lưng thường_xuyên gánh_chịu cơn đau lan xuống chân .",
        "entities": [
            {
                "word": "thoát_vị đĩa_đệm cột_sống thắt_lưng",
                "type": "DISEASE"
            },
            {
                "word": "đau lan xuống chân",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_323",
        "text": "Nhằm đánh_giá chức_năng thông khí phổi do nghi_ngờ bệnh phổi tắc_nghẽn mạn tính , bệnh_nhân được chỉ_định đo chức_năng hô_hấp .",
        "entities": [
            {
                "word": "bệnh phổi tắc_nghẽn mạn tính",
                "type": "DISEASE"
            },
            {
                "word": "đo chức_năng hô_hấp",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_324",
        "text": "Amlodipin là thuốc hạ_áp được kê đơn nhằm kiểm_soát huyết_áp tâm thu và tâm trương .",
        "entities": [
            {
                "word": "Amlodipin",
                "type": "DRUG"
            },
            {
                "word": "tăng huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_325",
        "text": "Do bệnh_nhân đang mang thai 3 tháng đầu , tuyệt_đối chống chỉ_định kê đơn thuốc Isotretinoin_trị mụn trứng_cá .",
        "entities": [
            {
                "word": "Isotretinoin",
                "type": "DRUG"
            },
            {
                "word": "mụn trứng_cá",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_326",
        "text": "Nhập_viện trong tình_trạng hoa mắt , chóng_mặt và choáng_váng do huyết_áp_thấp , bệnh_nhân nhanh_chóng được truyền dịch .",
        "entities": [
            {
                "word": "huyết_áp_thấp",
                "type": "DISEASE"
            },
            {
                "word": "chóng_mặt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_327",
        "text": "Nhằm chẩn_đoán bệnh_lý động_kinh , bác_sĩ chỉ_định ghi điện não_đồ kéo_dài cho bệnh_nhi .",
        "entities": [
            {
                "word": "động_kinh",
                "type": "DISEASE"
            },
            {
                "word": "điện não_đồ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_328",
        "text": "Salbutamol dạng phun khí dung được chỉ_định điều_trị cắt_cơn co thắt phế_quản cấp_tính .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "co thắt phế_quản",
                "type": "SYMPTOM"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_329",
        "text": "Do nghi_ngờ mắc ung_thư dạ_dày , bác_sĩ chỉ_định thực_hiện nội_soi thực_quản dạ_dày tá_tràng có sinh_thiết .",
        "entities": [
            {
                "word": "ung_thư dạ_dày",
                "type": "DISEASE"
            },
            {
                "word": "nội_soi thực_quản dạ_dày tá_tràng",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_330",
        "text": "Bệnh_nhân suy thận mạn giai_đoạn 3 thường đi kèm triệu_chứng thiếu máu mạn tính và ngứa da .",
        "entities": [
            {
                "word": "suy thận mạn",
                "type": "DISEASE"
            },
            {
                "word": "thiếu máu",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_331",
        "text": "Nhằm mục_đích làm tan cục máu đông , thuốc tiêu_sợi huyết Alteplase có chỉ_định khẩn_cấp trong giờ đầu đột_quỵ nhồi máu não .",
        "entities": [
            {
                "word": "Alteplase",
                "type": "DRUG"
            },
            {
                "word": "đột_quỵ nhồi máu não",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_332",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc chống đông Warfarin đối_với phụ_nữ có_thai vì nguy_cơ gây quái_thai .",
        "entities": [
            {
                "word": "Warfarin",
                "type": "DRUG"
            },
            {
                "word": "mang thai",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_333",
        "text": "Nhập_viện trong tình_trạng đau tức ngực lan ra sau lưng , bệnh_nhân được chỉ_định siêu_âm tim qua thành ngực .",
        "entities": [
            {
                "word": "đau tức ngực",
                "type": "SYMPTOM"
            },
            {
                "word": "siêu_âm tim qua thành ngực",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_334",
        "text": "Levothyroxin được kê đơn nhằm bù_đắp lượng hormone tuyến_giáp thiếu_hụt cho bệnh_nhân suy giáp nguyên_phát .",
        "entities": [
            {
                "word": "Levothyroxin",
                "type": "DRUG"
            },
            {
                "word": "suy giáp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_335",
        "text": "Do nghi_ngờ sỏi niệu_quản gây ứ nước thận , bệnh_nhân được chỉ_định chụp cắt_lớp vi_tính hệ tiết_niệu không tiêm thuốc .",
        "entities": [
            {
                "word": "sỏi niệu_quản",
                "type": "DISEASE"
            },
            {
                "word": "chụp cắt_lớp vi_tính hệ tiết_niệu",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_336",
        "text": "Bệnh_nhân số xuất_huyết Dengue có biểu_hiện triệu_chứng xuất_huyết dưới da và chảy máu chân răng .",
        "entities": [
            {
                "word": "sốt_xuất_huyết Dengue",
                "type": "DISEASE"
            },
            {
                "word": "chảy máu chân_răng",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_337",
        "text": "Nhằm chẩn_đoán bệnh_lý mạch_máu võng_mạc do tiểu_đường , bác_sĩ chỉ_định chụp mạch huỳnh_quang đáy mắt .",
        "entities": [
            {
                "word": "bệnh võng_mạc đái_tháo_đường",
                "type": "DISEASE"
            },
            {
                "word": "chụp mạch huỳnh_quang đáy mắt",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_338",
        "text": "Diclofenac tuyệt_đối chống chỉ_định ở bệnh_nhân có tiền_sử xuất_huyết tiêu_hóa do thuốc kháng_viêm .",
        "entities": [
            {
                "word": "Diclofenac",
                "type": "DRUG"
            },
            {
                "word": "xuất_huyết tiêu_hóa",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_339",
        "text": "Nhập_viện trong tình_trạng khó thở thanh_quản độ II , bệnh_nhân được chỉ_định khí dung Adrenalin để cấp_cứu .",
        "entities": [
            {
                "word": "khó thở thanh_quản",
                "type": "SYMPTOM"
            },
            {
                "word": "Adrenalin",
                "type": "DRUG"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_340",
        "text": "Colchicin được kê đơn nhằm dự_phòng và điều_trị các đợt viêm khớp cấp do bệnh gút .",
        "entities": [
            {
                "word": "Colchicin",
                "type": "DRUG"
            },
            {
                "word": "gút",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_341",
        "text": "Do nghi_ngờ viêm màng não mủ , bác_sĩ chỉ_định chọc dò dịch não tủy nhằm phân_tích tế_bào và sinh_hóa .",
        "entities": [
            {
                "word": "viêm màng não mủ",
                "type": "DISEASE"
            },
            {
                "word": "chọc dò dịch não tủy",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_342",
        "text": "Bệnh_nhân ung_thư vạch giai_đoạn di_căn xương thường_xuyên chịu_đựng những cơn đau nhức xương dữ_dội .",
        "entities": [
            {
                "word": "ung_thư vú",
                "type": "DISEASE"
            },
            {
                "word": "đau nhức xương",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_343",
        "text": "Nhằm chẩn_đoán xác_định bệnh_lý rối_loạn nhịp tim , Holter điện tâm_đồ 24 giờ được chỉ_định thực_hiện .",
        "entities": [
            {
                "word": "rối_loạn nhịp tim",
                "type": "DISEASE"
            },
            {
                "word": "Holter điện tâm_đồ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_344",
        "text": "Atorvastatin được kê đơn phối_hợp nhằm giảm cholesterol máu và phòng_ngừa biến_cố tim_mạch .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "rối_loạn lipid máu",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_345",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc ức_chế men chuyển ( ACEi ) cho phụ_nữ có_thai vì gây dị_tật thai_nhi .",
        "entities": [
            {
                "word": "thuốc ức_chế men chuyển",
                "type": "DRUG"
            },
            {
                "word": "mang thai",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_346",
        "text": "Nhập_viện trong tình_trạng vàng da , vàng mắt tăng dần do ung_thư biểu mô đường_mật , bệnh_nhân được chỉ_định chụp đường_mật ngược dòng qua nội_soi .",
        "entities": [
            {
                "word": "vàng da",
                "type": "SYMPTOM"
            },
            {
                "word": "chụp đường_mật ngược dòng qua nội_soi",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_347",
        "text": "Spiriva ( Tiotropium ) được kê đơn điều_trị duy_trì nhằm cải_thiện chức_năng thông khí cho bệnh_nhân mắc bệnh phổi tắc_nghẽn mạn tính .",
        "entities": [
            {
                "word": "Tiotropium",
                "type": "DRUG"
            },
            {
                "word": "bệnh phổi tắc_nghẽn mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_348",
        "text": "Do nghi_ngờ có khối_u gan ác_tính trên bệnh_nhân xơ_gan , bác_sĩ yêu_cầu chụp cộng_hưởng từ gan có chất tương_phản .",
        "entities": [
            {
                "word": "xơ_gan",
                "type": "DISEASE"
            },
            {
                "word": "chụp cộng_hưởng từ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_349",
        "text": "Bệnh_nhân cường_giáp Basedow thường biểu_hiện triệu_chứng lồi mắt , run tay và nhịp tim nhanh .",
        "entities": [
            {
                "word": "Basedow",
                "type": "DISEASE"
            },
            {
                "word": "run_tay",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_350",
        "text": "Nhằm chẩn_đoán bệnh_lý viêm loét đại_tràng mãn_tính , bác_sĩ chỉ_định nội_soi đại_tràng toàn_bộ kết_hợp sinh_thiết niêm_mạc .",
        "entities": [
            {
                "word": "viêm loét đại_tràng",
                "type": "DISEASE"
            },
            {
                "word": "nội_soi đại_tràng",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_351",
        "text": "Nhập_viện trong tình_trạng đau thắt ngực trái dữ_dội , do nghi_ngờ nhồi máu cơ tim cấp , bệnh_nhân ngay lập_tức được chỉ_định chụp mạch vành_qua da .",
        "entities": [
            {
                "word": "chụp mạch vành_qua da",
                "type": "PROCEDURE"
            },
            {
                "word": "nhồi máu cơ tim cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_352",
        "text": "Nhằm điều_trị triệt_để cơn hen phế_quản ác_tính do dị_ứng thời_tiết , bác_sĩ đã kê đơn phối_hợp Salbutamol cùng với liệu_pháp corticoid liều cao .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản ác_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_353",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng Aspirin cho các trường_hợp xuất_huyết tiêu_hóa do nguy_cơ làm trầm_trọng thêm tình_trạng chảy_máu .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "xuất_huyết tiêu_hóa",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_354",
        "text": "Do bệnh_nhân xuất_hiện triệu_chứng khó thở dữ_dội kèm theo ho có đờm xanh , các bác_sĩ khoa Hô_hấp đã tiến_hành nội_soi phế_quản nhằm chẩn_đoán chính_xác .",
        "entities": [
            {
                "word": "nội_soi phế_quản",
                "type": "PROCEDURE"
            },
            {
                "word": "khó thở",
                "type": "SYMPTOM"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_355",
        "text": "Bệnh_lý viêm khớp dạng thấp mạn tính thường gây ra các cơn đau nhức khớp buổi sáng và cứng khớp kéo_dài trên một giờ .",
        "entities": [
            {
                "word": "viêm khớp dạng thấp mạn tính",
                "type": "DISEASE"
            },
            {
                "word": "cứng khớp",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_356",
        "text": "Nhập_viện trong tình_trạng hôn_mê sâu do biến_chứng tăng áp_lực thẩm_thấu máu , bệnh_nhân có chỉ_định khẩn_cấp truyền insulin tĩnh_mạch liên_tục .",
        "entities": [
            {
                "word": "insulin",
                "type": "DRUG"
            },
            {
                "word": "tăng áp_lực thẩm_thấu máu",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_357",
        "text": "Nhằm loại_trừ khả_năng u não thất bên do hội_chứng tăng áp_lực nội sọ gây ra , bệnh_nhân được chỉ_định chụp cộng_hưởng từ sọ não .",
        "entities": [
            {
                "word": "chụp cộng_hưởng từ sọ não",
                "type": "PROCEDURE"
            },
            {
                "word": "u não",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_358",
        "text": "Do nghi_ngờ mắc đái_tháo_đường típ 2 trên nền bệnh_nhân béo phì độ II , bác_sĩ đã chỉ_định làm nghiệm pháp dung_nạp glucose đường uống .",
        "entities": [
            {
                "word": "nghiệm pháp dung_nạp glucose đường uống",
                "type": "PROCEDURE"
            },
            {
                "word": "đái_tháo_đường típ 2",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_359",
        "text": "Tuyệt_đối chống chỉ_định dùng Metformin cho những bệnh_nhân suy thận độ 4 do nguy_cơ tích_tụ thuốc gây nhiễm toan lactic .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "suy thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_360",
        "text": "Sản_phụ nhập_viện trong tình_trạng đau bụng hạ_vị dữ_dội và ra huyết âm_đạo bất_thường , do nghi_ngờ dọa sảy thai nên được kê đơn phối_hợp thuốc giảm co .",
        "entities": [
            {
                "word": "thuốc giảm co",
                "type": "DRUG"
            },
            {
                "word": "dọa sảy thai",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_361",
        "text": "Bệnh_lý vảy_nến thể mảng lan_tỏa thường dẫn đến triệu_chứng ngứa_ngáy dữ_dội và bong vảy da trắng dày ở vùng khuỷu tay và đầu_gối .",
        "entities": [
            {
                "word": "vảy_nến thể mảng",
                "type": "DISEASE"
            },
            {
                "word": "ngứa",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_362",
        "text": "Nhằm chẩn_đoán xác_định bệnh_lý tăng nhãn áp góc mở , bác_sĩ khoa Nhãn_khoa đã chỉ_định đo nhãn áp_kế và soi góc tiền phòng .",
        "entities": [
            {
                "word": "đo nhãn áp_kế",
                "type": "PROCEDURE"
            },
            {
                "word": "tăng nhãn áp",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_363",
        "text": "Do nghi_ngờ viêm loét dạ_dày tá_tràng mạn tính gây ra các cơn đau thượng_vị âm_ỉ sau khi ăn , bệnh_nhân được chỉ_định nội_soi tiêu_hóa trên .",
        "entities": [
            {
                "word": "nội_soi tiêu_hóa trên",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm loét dạ_dày tá_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_364",
        "text": "Nhập_viện trong tình_trạng liệt nửa người bên phải đột_ngột do tai_biến mạch_máu não thiếu máu cục_bộ , bệnh_nhân được kê đơn phối_hợp Aspirin và Atorvastatin .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "tai_biến mạch_máu não",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_365",
        "text": "Tuyệt_đối chống chỉ_định kê đơn thuốc Warfarin cho phụ_nữ mang thai 3 tháng đầu do nguy_cơ gây quái_thai cao .",
        "entities": [
            {
                "word": "Warfarin",
                "type": "DRUG"
            },
            {
                "word": "mang thai",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_366",
        "text": "Nhằm điều_trị hiệu_quả tình_trạng nhiễm_trùng đường tiết_kiệm do vi_khuẩn gram âm , bác_sĩ đã kê đơn sử_dụng kháng_sinh Ciprofloxacin .",
        "entities": [
            {
                "word": "Ciprofloxacin",
                "type": "DRUG"
            },
            {
                "word": "nhiễm_trùng đường tiết_niệu",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_367",
        "text": "Do bệnh_nhân mắc chứng cao huyết_áp vô căn lâu năm có kèm theo triệu_chứng đau_đầu chóng_mặt buổi sáng , bác_sĩ đã kê đơn Amlodipin 5mg .",
        "entities": [
            {
                "word": "Amlodipin 5mg",
                "type": "DRUG"
            },
            {
                "word": "cao huyết_áp vô căn",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_368",
        "text": "Hội_chứng ruột kích_thích thường biểu_hiện qua các triệu_chứng đầy hơi chướng bụng , đau quặn bụng và rối_loạn đại_tiện kéo_dài .",
        "entities": [
            {
                "word": "Hội_chứng ruột kích_thích",
                "type": "DISEASE"
            },
            {
                "word": "đau quặn bụng",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_369",
        "text": "Nhập_viện trong tình_trạng sốt cao rét run , ho_khan kéo_dài do nghi_ngờ viêm phổi thùy , bệnh_nhân có chỉ_định chụp X - quang phổi thẳng .",
        "entities": [
            {
                "word": "chụp X - quang phổi thẳng",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm phổi thùy",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_370",
        "text": "Nhằm chẩn_đoán phân_biệt hội_chứng ống cổ_tay , bác_sĩ thần_kinh đã chỉ_định đo điện_cơ các chi trên cho bệnh_nhân .",
        "entities": [
            {
                "word": "đo điện_cơ",
                "type": "PROCEDURE"
            },
            {
                "word": "hội_chứng ống cổ_tay",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_371",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc bôi chứa Corticoid mạnh trên vùng da bị tổn_thương do nhiễm nấm sâu .",
        "entities": [
            {
                "word": "Corticoid",
                "type": "DRUG"
            },
            {
                "word": "nhiễm nấm",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_372",
        "text": "Do nghi_ngờ bướu nhân tuyến_giáp ác_tính , bệnh_nhân được chỉ_định thực_hiện_sinh_thiết bằng kim nhỏ dưới hướng_dẫn của siêu_âm .",
        "entities": [
            {
                "word": "sinh_thiết bằng kim nhỏ",
                "type": "PROCEDURE"
            },
            {
                "word": "bướu nhân tuyến_giáp",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_373",
        "text": "Bệnh_nhân suy tim mạn tính giai_đoạn III nhập_viện trong tình_trạng khó thở khi nằm và phù hai chi dưới , được kê đơn phối_hợp Furosemide và Spironolactone .",
        "entities": [
            {
                "word": "Furosemide",
                "type": "DRUG"
            },
            {
                "word": "suy tim mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_374",
        "text": "Nhằm kiểm_soát lượng đường_huyết tăng cao đột_ngột do chế_độ ăn_uống , bệnh_nhân đái tháp đường típ 1 được kê đơn Insulin_Lispro .",
        "entities": [
            {
                "word": "Insulin_Lispro",
                "type": "DRUG"
            },
            {
                "word": "đái tháp đường típ 1",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_375",
        "text": "Triệu_chứng điển_hình của bệnh Parkinson bao_gồm run khi nghỉ_ngơi , đơ cứng cơ và chậm_chạp trong mọi vận_động thể_chất .",
        "entities": [
            {
                "word": "Parkinson",
                "type": "DISEASE"
            },
            {
                "word": "run",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_376",
        "text": "Nhập_viện trong tình_trạng mất thị_lực mắt phải đột_ngột không đau do tắc động_mạch trung_tâm võng_mạc , bệnh_nhân có chỉ_định cấp_cứu nhãn khoa .",
        "entities": [
            {
                "word": "mất thị_lực",
                "type": "SYMPTOM"
            },
            {
                "word": "tắc động_mạch trung_tâm võng_mạc",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_377",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng thuốc chẹn beta giao_cảm như Propranolol cho bệnh_nhân đang lên_cơn hen phế_quản cấp .",
        "entities": [
            {
                "word": "Propranolol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_378",
        "text": "Nhằm loại_trừ khả_năng thoái_hóa khớp gối độ nặng , bác_sĩ cơ xương khớp đã chỉ_định chụp X - quang khớp gối hai bên tư_thế đứng .",
        "entities": [
            {
                "word": "chụp X - quang khớp gối hai bên",
                "type": "PROCEDURE"
            },
            {
                "word": "thoái_hóa khớp gối",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_379",
        "text": "Do nghi_ngờ ung_thư đại trực_tràng , bác_sĩ đã chỉ_định nội_soi đại_tràng toàn_bộ kết_hợp sinh_thiết tổn_thương nhằm chẩn_đoán mô bệnh học .",
        "entities": [
            {
                "word": "nội_soi đại_tràng toàn_bộ",
                "type": "PROCEDURE"
            },
            {
                "word": "ung_thư đại trực_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_380",
        "text": "Bệnh_nhân đái_tháo_đường thai kỳ cần được theo_dõi sát_sao và kê đơn thuốc Insulin khi chế_độ ăn_kiêng không đạt hiệu_quả kiểm_soát đường_huyết .",
        "entities": [
            {
                "word": "Insulin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường thai kỳ",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_381",
        "text": "Triệu_chứng cốt_lõi của hội_chứng trầm_cảm_nặng là khí_sắc trầm buồn kéo_dài , mất hứng_thú trong mọi hoạt_động và rối_loạn giấc_ngủ nặng .",
        "entities": [
            {
                "word": "trầm_cảm_nặng",
                "type": "DISEASE"
            },
            {
                "word": "mất hứng_thú",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_382",
        "text": "Nhập_viện trong tình_trạng đau_đầu dữ_dội kèm theo buồn_nôn do tăng huyết_áp ác_tính , bệnh_nhân có chỉ_định truyền Nicardipine tĩnh_mạch .",
        "entities": [
            {
                "word": "Nicardipine",
                "type": "DRUG"
            },
            {
                "word": "tăng huyết_áp ác_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_383",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc kháng_viêm không steroid ( NSAID ) đối_với những người có tiền_sử suy thận mạn tính nặng .",
        "entities": [
            {
                "word": "NSAID",
                "type": "DRUG"
            },
            {
                "word": "suy thận mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_384",
        "text": "Nhằm đánh_giá chức_năng thông khí phổi ở bệnh_nhân viêm phế_quản mạn tính , bác_sĩ đã chỉ_định đo chức_năng hô_hấp ký .",
        "entities": [
            {
                "word": "đo chức_năng hô_hấp ký",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm phế_quản mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_385",
        "text": "Do nghi_ngờ sỏi đường_mật chính gây sốt và vàng da tắc mật , bệnh_nhân được chỉ_định chụp cộng_hưởng từ mật_tụy ( MRCP ) .",
        "entities": [
            {
                "word": "chụp cộng_hưởng từ mật_tụy",
                "type": "PROCEDURE"
            },
            {
                "word": "sỏi đường_mật",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_386",
        "text": "Bệnh_nhân mắc chứng loãng_xương nặng thường dễ bị gãy xương bệnh_lý ở vùng cổ xương đùi hoặc lún đốt_sống_lưng .",
        "entities": [
            {
                "word": "loãng_xương",
                "type": "DISEASE"
            },
            {
                "word": "gãy xương",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_387",
        "text": "Nhập_viện trong tình_trạng nhịp tim nhanh kịch phát trên thất , bệnh_nhân ngay lập_tức được chỉ_định thực_hiện nghiệm pháp Valsalva và tiêm Adenosine .",
        "entities": [
            {
                "word": "Adenosine",
                "type": "DRUG"
            },
            {
                "word": "nhịp tim nhanh kịch phát trên thất",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_388",
        "text": "Nhằm điều_trị căn_bệnh viêm loét đại_tràng chảy_máu , bác_sĩ tiêu_hóa đã kê đơn phối_hợp Mesalamine đường uống và đường đặt hậu_môn .",
        "entities": [
            {
                "word": "Mesalamine",
                "type": "DRUG"
            },
            {
                "word": "viêm loét đại_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_389",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng thuốc Tetracycline cho trẻ_em dưới 8 tuổi do nguy_cơ gây hỏng men răng và ảnh_hưởng phát_triển xương .",
        "entities": [
            {
                "word": "Tetracycline",
                "type": "DRUG"
            },
            {
                "word": "nhiễm_khuẩn",
                "type": "NONE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_390",
        "text": "Do nghi_ngờ nhồi máu não cấp_tính trên bệnh_nhân liệt mặt trung_ương , bác_sĩ thần_kinh đã chỉ_định chụp cắt_lớp vi_tính sọ não không tiêm thuốc .",
        "entities": [
            {
                "word": "chụp cắt_lớp vi_tính sọ não",
                "type": "PROCEDURE"
            },
            {
                "word": "nhồi máu não",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_391",
        "text": "Bệnh_nhân xơ_gan cổ chướng giai_đoạn cuối thường xuất_hiện các triệu_chứng lâm_sàng như vàng da , tuần_hoàn bàng_hệ và cổ chướng căng .",
        "entities": [
            {
                "word": "xơ_gan cổ chướng",
                "type": "DISEASE"
            },
            {
                "word": "vàng da",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_392",
        "text": "Nhằm chẩn_đoán xác_định bệnh_lý thiếu máu cơ tim cục_bộ mạn tính , bệnh_nhân được chỉ_định làm nghiệm pháp gắng_sức điện tâm_đồ .",
        "entities": [
            {
                "word": "nghiệm pháp gắng_sức điện tâm_đồ",
                "type": "PROCEDURE"
            },
            {
                "word": "thiếu máu cơ tim cục_bộ",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_393",
        "text": "Do nghi_ngờ viêm tụy cấp do sỏi mật , bệnh_nhân được chỉ_định làm xét_nghiệm định_lượng men Amylase và Lipase máu .",
        "entities": [
            {
                "word": "xét_nghiệm định_lượng men Amylase và Lipase máu",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm tụy cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_394",
        "text": "Bệnh_nhân mắc chứng suy giáp nguyên_phát thường có biểu_hiện lâm_sàng là mệt_mỏi , sợ lạnh , tăng cân và da khô .",
        "entities": [
            {
                "word": "suy giáp nguyên_phát",
                "type": "DISEASE"
            },
            {
                "word": "mệt_mỏi",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_395",
        "text": "Nhập_viện trong tình_trạng co_giật toàn_thân kéo_dài do bệnh động_kinh kháng thuốc , bệnh_nhân có chỉ_định truyền tĩnh_mạch Diazepam .",
        "entities": [
            {
                "word": "Diazepam",
                "type": "DRUG"
            },
            {
                "word": "động_kinh",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_396",
        "text": "Nhằm giảm nhanh triệu_chứng phù_nề và nghẹt mũi do viêm mũi dị_ứng quanh_năm , bác_sĩ đã kê đơn thuốc xịt mũi chứa Fluticasone .",
        "entities": [
            {
                "word": "Fluticasone",
                "type": "DRUG"
            },
            {
                "word": "viêm mũi dị_ứng",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_397",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Isotretinoin đường uống cho phụ_nữ đang có dự_định mang thai do độc_tính gây quái_thai cực mạnh .",
        "entities": [
            {
                "word": "Isotretinoin",
                "type": "DRUG"
            },
            {
                "word": "mang thai",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_398",
        "text": "Do nghi_ngờ hội_chứng cushing do dùng thuốc corticoid kéo_dài , bệnh_nhân được chỉ_định làm xét_nghiệm định_lượng Cortisol máu lúc 8 giờ sáng .",
        "entities": [
            {
                "word": "xét_nghiệm định_lượng Cortisol máu",
                "type": "PROCEDURE"
            },
            {
                "word": "hội_chứng cushing",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_399",
        "text": "Bệnh_lý gout mạn tính thường biểu_hiện qua các đợt viêm khớp cấp tái_phát , sưng nóng đỏ đau dữ_dội tại khớp bàn_chân ngón_cái .",
        "entities": [
            {
                "word": "gout mạn tính",
                "type": "DISEASE"
            },
            {
                "word": "sưng nóng đỏ đau",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_400",
        "text": "Nhằm kiểm_soát tốt tình_trạng tăng cholesterol máu gia_đình , bác_sĩ tim_mạch đã kê đơn kết_hợp thuốc Rosuvastatin và Ezetimibe .",
        "entities": [
            {
                "word": "Rosuvastatin",
                "type": "DRUG"
            },
            {
                "word": "tăng cholesterol máu",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_401",
        "text": "Do nghi_ngờ nhồi máu cơ tim cấp trên nền bệnh_nhân tăng huyết_áp lâu năm , bác_sĩ đã chỉ_định chụp mạch vành_qua da để chẩn_đoán chính_xác tổn_thương .",
        "entities": [
            {
                "word": "nhồi máu cơ tim cấp",
                "type": "DISEASE"
            },
            {
                "word": "chụp mạch vành_qua da",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_402",
        "text": "Bệnh_nhân nhập_viện trong tình_trạng khó thở dữ_dội và ho có đờm đặc do đợt cấp bệnh phổi tắc_nghẽn mạn tính .",
        "entities": [
            {
                "word": "khó thở dữ_dội",
                "type": "SYMPTOM"
            },
            {
                "word": "bệnh phổi tắc_nghẽn mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_403",
        "text": "Nhằm điều_trị triệt_để tình_trạng nhiễm_khuẩn huyết nặng , các bác_sĩ đã kê đơn phối_hợp Meropenem 1g kết_hợp Vancomycin .",
        "entities": [
            {
                "word": "Meropenem 1g",
                "type": "DRUG"
            },
            {
                "word": "nhiễm_khuẩn huyết nặng",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_404",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng Aspirin cho các trường_hợp xuất_huyết tiêu_hóa do nguy_cơ làm trầm_trọng thêm tình_trạng chảy_máu .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "xuất_huyết tiêu_hóa",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_405",
        "text": "Vì xuất_hiện các cơn đau thắt ngực ổn_định khi gắng_sức , người_bệnh có chỉ_định khẩn_cấp thực_hiện nghiệm pháp gắng_sức điện tâm_đồ .",
        "entities": [
            {
                "word": "đau thắt ngực ổn_định",
                "type": "SYMPTOM"
            },
            {
                "word": "nghiệm pháp gắng_sức điện tâm_đồ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_406",
        "text": "Do biến_chứng võng_mạc đái_tháo_đường giai_đoạn tăng sinh , bệnh_nhân được chỉ_định nội_soi đáy mắt nhằm đánh_giá chi_tiết tổn_thương vi_mạch .",
        "entities": [
            {
                "word": "võng_mạc đái_tháo_đường",
                "type": "DISEASE"
            },
            {
                "word": "nội_soi đáy mắt",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_407",
        "text": "Nhằm kiểm_soát đường_huyết ổn_định , bác_sĩ nội_tiết đã kê đơn thuốc Metformin 850mg cho người_bệnh đái_tháo_đường tuýp 2 .",
        "entities": [
            {
                "word": "Metformin 850mg",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường tuýp 2",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_408",
        "text": "Bệnh_nhân có biểu_hiện liệt nửa người trái do tai_biến mạch_máu não nhồi máu não cấp_tính .",
        "entities": [
            {
                "word": "liệt nửa người trái",
                "type": "SYMPTOM"
            },
            {
                "word": "tai_biến mạch_máu não",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_409",
        "text": "Nhập_viện trong tình_trạng đau khớp gối dữ_dội kèm sưng đỏ , bệnh_nhân được chẩn_đoán mắc bệnh gout cấp và có chỉ_định chọc dịch khớp .",
        "entities": [
            {
                "word": "đau khớp gối dữ_dội",
                "type": "SYMPTOM"
            },
            {
                "word": "gout cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_410",
        "text": "Do nghi_ngờ ung_thư biểu mô tuyến đại_tràng , bác_sĩ tiêu_hóa đã chỉ_định nội_soi đại_tràng toàn_bộ sinh_thiết tổn_thương .",
        "entities": [
            {
                "word": "ung_thư biểu mô tuyến đại_tràng",
                "type": "DISEASE"
            },
            {
                "word": "nội_soi đại_tràng toàn_bộ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_411",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Warfarin cho phụ_nữ có_thai 3 tháng đầu do nguy_cơ gây quái_thai cao .",
        "entities": [
            {
                "word": "Warfarin",
                "type": "DRUG"
            },
            {
                "word": "mang thai",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_412",
        "text": "Nhằm chẩn_đoán xác_định thoát_vị đĩa_đệm cột_sống thắt_lưng , người_bệnh được chỉ_định chụp cộng_hưởng từ MRI cột_sống .",
        "entities": [
            {
                "word": "thoát_vị đĩa_đệm cột_sống thắt_lưng",
                "type": "DISEASE"
            },
            {
                "word": "chụp cộng_hưởng từ MRI",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_413",
        "text": "Bệnh_nhân hen phế_quản mạn tính thường_xuyên gặp triệu_chứng khò_khè và tức ngực về đêm .",
        "entities": [
            {
                "word": "hen phế_quản mạn tính",
                "type": "DISEASE"
            },
            {
                "word": "khò_khè",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_414",
        "text": "Kê đơn phối_hợp Salbutamol và Budesonide_dạng khí dung nhằm điều_trị hiệu_quả cơn hen cấp_tính .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "hen cấp_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_415",
        "text": "Do mắc chứng suy tim độ III theo phân_loại NYHA , bệnh_nhân xuất_hiện tình_trạng phù hai chi dưới và gan to .",
        "entities": [
            {
                "word": "suy tim độ III",
                "type": "DISEASE"
            },
            {
                "word": "phù hai chi dưới",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_416",
        "text": "Bác_sĩ chuyên_khoa mắt đã chỉ_định đo nhãn áp bằng máy không tiếp_xúc nhằm tầm soát bệnh glaucoma góc mở .",
        "entities": [
            {
                "word": "glaucoma góc mở",
                "type": "DISEASE"
            },
            {
                "word": "đo nhãn áp",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_417",
        "text": "Chống chỉ_định tuyệt_đối việc sử_dụng thuốc Atorvastatin khi bệnh_nhân có biểu_hiện tổn_thương tế_bào gan cấp .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "tổn_thương tế_bào gan cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_418",
        "text": "Nhập_viện trong tình_trạng đau thượng_vị lan sau lưng , người_bệnh được siêu_âm ổ_bụng do nghi_ngờ viêm tụy cấp .",
        "entities": [
            {
                "word": "đau thượng_vị lan sau lưng",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm tụy cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_419",
        "text": "Để điều_trị dứt_điểm hội_chứng dạ_dày tá_tràng , bác_sĩ đã kê đơn thuốc Omeprazol 20mg uống trước ăn sáng .",
        "entities": [
            {
                "word": "Omeprazol 20mg",
                "type": "DRUG"
            },
            {
                "word": "hội_chứng dạ_dày tá_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_420",
        "text": "Do nghi_ngờ mắc hội_chứng ống cổ_tay , bệnh_nhân có chỉ_định thực_hiện điện_cơ_đồ chi trên .",
        "entities": [
            {
                "word": "hội_chứng ống cổ_tay",
                "type": "DISEASE"
            },
            {
                "word": "điện_cơ_đồ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_421",
        "text": "Bệnh_nhân viêm khớp dạng thấp thường_xuyên phàn_nàn về tình_trạng cứng khớp buổi sáng kéo_dài trên một giờ .",
        "entities": [
            {
                "word": "viêm khớp dạng thấp",
                "type": "DISEASE"
            },
            {
                "word": "cứng khớp buổi sáng",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_422",
        "text": "Nhằm chẩn_đoán bệnh_lý mạch_máu não , bác_sĩ chỉ_định chụp cắt_lớp vi_tính mạch_máu não ( CTA ) có cản_quang .",
        "entities": [
            {
                "word": "bệnh_lý mạch_máu não",
                "type": "DISEASE"
            },
            {
                "word": "chụp cắt_lớp vi_tính mạch_máu não",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_423",
        "text": "Chống chỉ_định dùng thuốc ức_chế men chuyển Enalapril đối_với bệnh_nhân hẹp động_mạch thận hai bên .",
        "entities": [
            {
                "word": "Enalapril",
                "type": "DRUG"
            },
            {
                "word": "hẹp động_mạch thận hai bên",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_424",
        "text": "Bệnh_nhân có chỉ_định khẩn_cấp đặt ống nội khí_quản thở máy do suy hô_hấp cấp_tiến_triển .",
        "entities": [
            {
                "word": "suy hô_hấp cấp_tiến_triển",
                "type": "DISEASE"
            },
            {
                "word": "đặt ống nội khí_quản",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_425",
        "text": "Do mắc bệnh béo phì độ II kèm theo rối_loạn chuyển_hóa lipid , người_bệnh được kê đơn thuốc Orlistat 120mg .",
        "entities": [
            {
                "word": "béo phì độ II",
                "type": "DISEASE"
            },
            {
                "word": "Orlistat 120mg",
                "type": "DRUG"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_426",
        "text": "Nhập_viện trong tình_trạng sốt cao kèm theo co_giật toàn_thân do viêm màng não mủ .",
        "entities": [
            {
                "word": "co_giật toàn_thân",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm màng não mủ",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_427",
        "text": "Nhằm điều_trị hiệu_quả bệnh_lý tăng huyết_áp kháng trị , bác_sĩ kê đơn phối_hợp Amlodipin và Valsartan .",
        "entities": [
            {
                "word": "Amlodipin",
                "type": "DRUG"
            },
            {
                "word": "tăng huyết_áp kháng trị",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_428",
        "text": "Bệnh_nhân loãng_xương nặng tuyệt_đối chống chỉ_định sử_dụng các loại thuốc nhóm Corticoid liều cao kéo_dài .",
        "entities": [
            {
                "word": "Corticoid",
                "type": "DRUG"
            },
            {
                "word": "loãng_xương nặng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_429",
        "text": "Do nghi_ngờ có khối_u gan ác_tính , bác_sĩ chỉ_định siêu_âm đàn_hồi mô gan và chụp cắt_lớp vi_tính ổ_bụng .",
        "entities": [
            {
                "word": "u_gan ác_tính",
                "type": "DISEASE"
            },
            {
                "word": "chụp cắt_lớp vi_tính ổ_bụng",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_430",
        "text": "Người_bệnh viêm da cơ_địa thường chịu_đựng những cơn ngứa dữ_dội và xuất_hiện các mảng da đỏ bong vẩy .",
        "entities": [
            {
                "word": "viêm da cơ_địa",
                "type": "DISEASE"
            },
            {
                "word": "ngứa dữ_dội",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_431",
        "text": "Kê đơn thuốc kháng_sinh Levofloxacin 500mg nhằm điều_trị dứt_điểm tình_trạng viêm phổi thùy do vi_khuẩn .",
        "entities": [
            {
                "word": "Levofloxacin 500mg",
                "type": "DRUG"
            },
            {
                "word": "viêm phổi thùy",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_432",
        "text": "Bệnh_nhân có chỉ_định thực_hiện siêu_âm tim qua thực_quản nhằm chẩn_đoán chính_xác bệnh_lý van tim hai lá .",
        "entities": [
            {
                "word": "bệnh_lý van tim hai lá",
                "type": "DISEASE"
            },
            {
                "word": "siêu_âm tim qua thực_quản",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_433",
        "text": "Do biến_chứng xơ_gan cổ_trướng giai_đoạn cuối , người_bệnh nhập_viện trong tình_trạng bụng chướng to và vàng da đậm .",
        "entities": [
            {
                "word": "xơ_gan cổ_trướng",
                "type": "DISEASE"
            },
            {
                "word": "bụng chướng to",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_434",
        "text": "Chống chỉ_định dùng thuốc Metformin cho bệnh_nhân suy thận mòn có mức lọc cầu thận giảm nặng .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "suy thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_435",
        "text": "Nhằm phát_hiện sớm tổn_thương tiền ung_thư cổ tử_cung , phụ_nữ trong độ tuổi sinh_đẻ có chỉ_định làm xét_nghiệm Pap_Smear .",
        "entities": [
            {
                "word": "ung_thư cổ tử_cung",
                "type": "DISEASE"
            },
            {
                "word": "xét_nghiệm Pap_Smear",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_436",
        "text": "Bệnh_nhân suy giáp_trạng nguyên_phát thường biểu_hiện triệu_chứng mệt_mỏi kéo_dài , sợ lạnh và tăng cân .",
        "entities": [
            {
                "word": "suy giáp_trạng nguyên_phát",
                "type": "DISEASE"
            },
            {
                "word": "mệt_mỏi kéo_dài",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_437",
        "text": "Bác_sĩ thần_kinh đã kê đơn thuốc Levodopa cho bệnh_nhân mắc hội_chứng Parkinson nhằm kiểm_soát các cử_động bất_thường .",
        "entities": [
            {
                "word": "Levodopa",
                "type": "DRUG"
            },
            {
                "word": "Parkinson",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_438",
        "text": "Do nghi_ngờ mắc sỏi thận trái gây tắc_nghẽn , người_bệnh được chỉ_định chụp niệu đồ tĩnh_mạch ( IVP ) .",
        "entities": [
            {
                "word": "sỏi thận trái",
                "type": "DISEASE"
            },
            {
                "word": "chụp niệu đồ tĩnh_mạch",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_439",
        "text": "Bệnh_nhân đái_tháo_đường tuyệt_đối chống chỉ_định dùng các loại thuốc nhỏ mắt chứa Corticoid dài ngày do nguy_cơ tăng nhãn áp .",
        "entities": [
            {
                "word": "Corticoid",
                "type": "DRUG"
            },
            {
                "word": "tăng nhãn áp",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_440",
        "text": "Nhập_viện trong tình_trạng nhịp tim nhanh hỗn_loạn , bệnh_nhân được chẩn_đoán rung nhĩ đáp_ứng thất nhanh .",
        "entities": [
            {
                "word": "nhịp tim nhanh hỗn_loạn",
                "type": "SYMPTOM"
            },
            {
                "word": "rung nhĩ",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_441",
        "text": "Nhằm đánh_giá mức_độ tổn_thương sụn khớp gối , bác_sĩ chấn_thương chỉnh_hình chỉ_định chụp cộng_hưởng từ khớp gối .",
        "entities": [
            {
                "word": "tổn_thương sụn khớp gối",
                "type": "DISEASE"
            },
            {
                "word": "chụp cộng_hưởng từ khớp gối",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_442",
        "text": "Kê đơn thuốc Paracetamol 500mg nhằm giảm nhẹ triệu_chứng đau_đầu và sốt cao ở bệnh_nhân cúm mùa .",
        "entities": [
            {
                "word": "Paracetamol 500mg",
                "type": "DRUG"
            },
            {
                "word": "đau_đầu",
                "type": "SYMPTOM"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_443",
        "text": "Bệnh_nhân có chỉ_định khẩn_cấp truyền máu toàn_phần do xuất_huyết tiêu_hóa nặng dẫn đến thiếu máu cấp .",
        "entities": [
            {
                "word": "thiếu máu cấp",
                "type": "DISEASE"
            },
            {
                "word": "truyền máu toàn_phần",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_444",
        "text": "Do mắc hội_chứng ruột kích_thích thể táo_bón , người_bệnh thường_xuyên bị đau quặn bụng và đầy hơi .",
        "entities": [
            {
                "word": "hội_chứng ruột kích_thích",
                "type": "DISEASE"
            },
            {
                "word": "đau quặn bụng",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_445",
        "text": "Chống chỉ_định tuyệt_đối sử_dụng thuốc kháng_viêm không steroid ( NSAIDs ) cho người có tiền_sử loét dạ_dày tá_tràng .",
        "entities": [
            {
                "word": "NSAIDs",
                "type": "DRUG"
            },
            {
                "word": "loét dạ_dày tá_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_446",
        "text": "Nhằm chẩn_đoán bệnh_lý mạch_máu ngoại biên , bác_sĩ chỉ_định siêu_âm Doppler mạch_máu chi dưới .",
        "entities": [
            {
                "word": "bệnh_lý mạch_máu ngoại biên",
                "type": "DISEASE"
            },
            {
                "word": "siêu_âm Doppler mạch_máu chi dưới",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_447",
        "text": "Bệnh_nhân ung_thư vòm họng xuất_hiện triệu_chứng nổi hạch cổ_cứng và chảy máu_cam thường_xuyên .",
        "entities": [
            {
                "word": "ung_thư vòm họng",
                "type": "DISEASE"
            },
            {
                "word": "nổi hạch cổ_cứng",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_448",
        "text": "Để kiểm_soát cơn hen phế_quản ác_tính , bác_sĩ đã kê đơn thuốc Methylprednisolone uống theo phác_đồ giảm dần liều .",
        "entities": [
            {
                "word": "Methylprednisolone",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản ác_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_449",
        "text": "Do nghi_ngờ có tổn_thương thoát_vị đĩa_đệm cổ , bệnh_nhân được chỉ_định chụp X - quang cột_sống cổ thẳng nghiêng .",
        "entities": [
            {
                "word": "thoát_vị đĩa_đệm cổ",
                "type": "DISEASE"
            },
            {
                "word": "chụp X - quang cột_sống cổ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_450",
        "text": "Bệnh_nhân nhồi máu cơ tim cấp có chỉ_định can_thiệp mạch vành_qua da tiên phát nhằm tái_thông động_mạch_vành bị tắc .",
        "entities": [
            {
                "word": "nhồi máu cơ tim cấp",
                "type": "DISEASE"
            },
            {
                "word": "can_thiệp mạch vành_qua da",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_451",
        "text": "Do nghi_ngờ mắc bệnh viêm phổi thùy , bác_sĩ đã chỉ_định thực_hiện chụp X - quang ngực thẳng nhằm chẩn_đoán chính_xác tổn_thương .",
        "entities": [
            {
                "word": "viêm phổi thùy",
                "type": "DISEASE"
            },
            {
                "word": "chụp X - quang ngực thẳng",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_452",
        "text": "Mặc_dù bệnh_nhân nhập_viện trong tình_trạng đau thắt ngực dữ_dội , loại thuốc Aspirin tuyệt_đối chống chỉ_định đối_với người có tiền_sử xuất_huyết tiêu_hóa .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "xuất_huyết tiêu_hóa",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_453",
        "text": "Nhằm điều_trị triệt_để căn_bệnh tăng huyết_áp ác_tính , bác_sĩ đã kê đơn phối_hợp Amlodipin 5mg với các thuốc hạ_áp khác .",
        "entities": [
            {
                "word": "Amlodipin 5mg",
                "type": "DRUG"
            },
            {
                "word": "tăng huyết_áp ác_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_454",
        "text": "Bệnh_nhân xuất_hiện triệu_chứng khó thở khi nằm do biến_chứng suy tim mòn_mỏi kéo_dài .",
        "entities": [
            {
                "word": "khó thở khi nằm",
                "type": "SYMPTOM"
            },
            {
                "word": "suy tim",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_455",
        "text": "Để đánh_giá mức_độ hẹp động_mạch_vành , người_bệnh có chỉ_định khẩn_cấp thực_hiện phương_pháp chụp cắt_lớp vi_tính mạch vành .",
        "entities": [
            {
                "word": "hẹp động_mạch_vành",
                "type": "DISEASE"
            },
            {
                "word": "chụp cắt_lớp vi_tính mạch_vành",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_456",
        "text": "Do hen phế_quản bội_nhiễm gây ho_khan và khò_khè , bệnh_nhân được kê đơn Salbutamol để cắt_cơn hen .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản bội_nhiễm",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_457",
        "text": "Triệu_chứng đau thượng_vị lan sau lưng là biểu_hiện lâm_sàng kinh_điển của viêm tụy cấp .",
        "entities": [
            {
                "word": "đau thượng_vị lan sau lưng",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm tụy cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_458",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Metformin đối_với bệnh_nhân suy thận mạn giai_đoạn cuối vì nguy_cơ nhiễm toan lactic .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "suy thận mạn giai_đoạn cuối",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_459",
        "text": "Nhằm chẩn_đoán xác_định bệnh_lý thoái_hóa khớp gối , bác_sĩ chỉ_định chụp cộng_hưởng từ khớp gối trái .",
        "entities": [
            {
                "word": "thoái_hóa khớp gối",
                "type": "DISEASE"
            },
            {
                "word": "chụp cộng_hưởng từ khớp gối trái",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_460",
        "text": "Vi_khuẩn Helicobacter pylori là nguyên_nhân chính gây ra bệnh viêm loét dạ_dày tá_tràng mạn tính .",
        "entities": [
            {
                "word": "viêm loét dạ_dày tá_tràng",
                "type": "DISEASE"
            },
            {
                "word": "Helicobacter_pylori",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_461",
        "text": "Bệnh_nhân nhập_viện trong tình_trạng liệt nửa người bên phải do nhồi máu não cấp_tính .",
        "entities": [
            {
                "word": "liệt nửa người bên phải",
                "type": "SYMPTOM"
            },
            {
                "word": "nhồi máu não cấp_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_462",
        "text": "Để điều_trị bệnh đái_tháo_đường týp 2 kháng trị , bác_sĩ đã kê đơn Insulin_glargine tiêm dưới da mỗi tối .",
        "entities": [
            {
                "word": "Insulin_glargine",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường týp 2",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_463",
        "text": "Do nghi_ngờ mắc hội_chứng ống cổ_tay , người_bệnh được chỉ_định thực_hiện đo điện_cơ chi trên .",
        "entities": [
            {
                "word": "hội_chứng ống cổ_tay",
                "type": "DISEASE"
            },
            {
                "word": "đo điện_cơ chi trên",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_464",
        "text": "Thuốc kháng_sinh Amoxicillin tuyệt_đối chống chỉ_định cho người có tiền_sử dị_ứng với nhóm penicillin .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "dị_ứng với nhóm penicillin",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_465",
        "text": "Triệu_chứng phù hai chi dưới và tiểu ít thường gặp ở hội_chứng thận hư nguyên_phát .",
        "entities": [
            {
                "word": "phù hai chi dưới và tiểu_ít",
                "type": "SYMPTOM"
            },
            {
                "word": "hội_chứng thận hư",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_466",
        "text": "Nhằm kiểm_soát cơn đau do bệnh gút cấp_tính , bệnh_nhân được kê đơn Colchicine 1mg uống hàng ngày .",
        "entities": [
            {
                "word": "Colchicine 1mg",
                "type": "DRUG"
            },
            {
                "word": "gút cấp_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_467",
        "text": "Tăng huyết_áp kéo_dài là nguyên_nhân trực_tiếp dẫn đến bệnh phì đại thất trái .",
        "entities": [
            {
                "word": "phì đại thất trái",
                "type": "DISEASE"
            },
            {
                "word": "Tăng huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_468",
        "text": "Bệnh_nhân có chỉ_định khẩn_cấp thực_hiện nội_soi dạ_dày thực_quản để tìm nguyên_nhân nôn ra máu .",
        "entities": [
            {
                "word": "nôn ra máu",
                "type": "SYMPTOM"
            },
            {
                "word": "nội_soi dạ_dày thực_quản",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_469",
        "text": "Nhập_viện trong tình_trạng sốt cao kèm theo vàng da vàng mắt , bệnh_nhân được chẩn_đoán mắc viêm gan cấp .",
        "entities": [
            {
                "word": "sốt cao kèm theo vàng da vàng mắt",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm gan cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_470",
        "text": "Để điều_trị triệu_chứng_ngứa da và mề_đay do viêm da cơ_địa , bác_sĩ kê đơn Cetirizine 10mg .",
        "entities": [
            {
                "word": "Cetirizine 10mg",
                "type": "DRUG"
            },
            {
                "word": "viêm da cơ_địa",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_471",
        "text": "Chống chỉ_định tuyệt_đối việc sử_dụng thuốc Warfarin đối_với phụ_nữ có_thai do nguy_cơ quái_thai .",
        "entities": [
            {
                "word": "Warfarin",
                "type": "DRUG"
            },
            {
                "word": "có_thai",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_472",
        "text": "Nhằm tầm soát bệnh ung_thư cổ tử_cung , phụ_nữ trong độ tuổi sinh_sản được chỉ_định làm xét_nghiệm Pap smear .",
        "entities": [
            {
                "word": "ung_thư cổ tử_cung",
                "type": "DISEASE"
            },
            {
                "word": "xét_nghiệm Pap_smear",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_473",
        "text": "Bệnh_nhân mắc chứng glaucoma góc đóng thường biểu_hiện triệu_chứng đau nhức mắt dữ_dội kèm nhìn mờ .",
        "entities": [
            {
                "word": "đau nhức mắt dữ_dội kèm nhìn mờ",
                "type": "SYMPTOM"
            },
            {
                "word": "glaucoma góc đóng",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_474",
        "text": "Do nghi_ngờ nhiễm_trùng đường tiết_niệu , bác_sĩ đã kê đơn phối_hợp Ciprofloxacin cho bệnh_nhân .",
        "entities": [
            {
                "word": "Ciprofloxacin",
                "type": "DRUG"
            },
            {
                "word": "nhiễm_trùng đường tiết_niệu",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_475",
        "text": "Tình_trạng xơ_vữa động_mạch chủ là nguyên_nhân sâu_xa dẫn đến phình động_mạch .",
        "entities": [
            {
                "word": "phình động_mạch",
                "type": "DISEASE"
            },
            {
                "word": "xơ_vữa động_mạch chủ",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_476",
        "text": "Bệnh_nhân nhập_viện trong tình_trạng khó thở thanh_quản , có chỉ_định khẩn_cấp mở khí_quản cấp_cứu .",
        "entities": [
            {
                "word": "khó thở thanh_quản",
                "type": "SYMPTOM"
            },
            {
                "word": "mở khí_quản cấp_cứu",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_477",
        "text": "Nhằm điều_trị chứng mất_ngủ kinh_niên , bác_sĩ đã kê đơn thuốc Zolpidem 10mg uống trước khi ngủ .",
        "entities": [
            {
                "word": "Zolpidem 10mg",
                "type": "DRUG"
            },
            {
                "word": "mất_ngủ",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_478",
        "text": "Chống chỉ_định kê đơn thuốc NSAIDs như Diclofenac cho bệnh_nhân đang mắc bệnh suy tim độ III.",
        "entities": [
            {
                "word": "Diclofenac",
                "type": "DRUG"
            },
            {
                "word": "suy tim độ III",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_479",
        "text": "Biểu_hiện tê bì các đầu ngón tay_chân là triệu_chứng phổ_biến của bệnh_lý đa dây thần_kinh ngoại biên .",
        "entities": [
            {
                "word": "tê bì các đầu ngón tay_chân",
                "type": "SYMPTOM"
            },
            {
                "word": "đa dây thần_kinh ngoại biên",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_480",
        "text": "Do nghi_ngờ mắc đục thủy_tinh_thể , bác_sĩ chỉ_định khám chuyên_khoa mắt và đo khúc_xạ .",
        "entities": [
            {
                "word": "đục thủy_tinh_thể",
                "type": "DISEASE"
            },
            {
                "word": "đo khúc_xạ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_481",
        "text": "Hút thuốc_lá lâu năm là nguyên_nhân trực_tiếp gây ra bệnh phổi tắc_nghẽn mạn tính ( COPD ) .",
        "entities": [
            {
                "word": "bệnh phổi tắc_nghẽn mạn tính",
                "type": "DISEASE"
            },
            {
                "word": "Hút thuốc_lá",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_482",
        "text": "Bệnh_nhân nhập_viện trong tình_trạng hôn_mê sâu do tăng áp_lực thẩm_thấu máu .",
        "entities": [
            {
                "word": "hôn_mê sâu",
                "type": "SYMPTOM"
            },
            {
                "word": "tăng áp_lực thẩm_thấu máu",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_483",
        "text": "Nhằm điều_trị hiệu_quả bệnh nấm da đầu , bác_sĩ kê đơn thuốc uống Ketoconazole .",
        "entities": [
            {
                "word": "Ketoconazole",
                "type": "DRUG"
            },
            {
                "word": "nấm da đầu",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_484",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Propranolol cho bệnh_nhân đang lên_cơn hen phế_quản cấp .",
        "entities": [
            {
                "word": "Propranolol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_485",
        "text": "Để chẩn_đoán xác_định bệnh thiếu máu cơ tim cục_bộ , bệnh_nhân có chỉ_định thực_hiện điện tâm_đồ gắng_sức .",
        "entities": [
            {
                "word": "thiếu máu cơ tim cục_bộ",
                "type": "DISEASE"
            },
            {
                "word": "điện tâm_đồ gắng_sức",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_486",
        "text": "Bệnh_nhân có triệu_chứng run tay khi nghỉ_ngơi , đây là dấu_hiệu đặc_trưng của bệnh Parkinson .",
        "entities": [
            {
                "word": "run tay khi nghỉ_ngơi",
                "type": "SYMPTOM"
            },
            {
                "word": "Parkinson",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_487",
        "text": "Nhằm hạ_sốt và giảm đau cơ xương khớp , bác_sĩ đã kê đơn Paracetamol 500mg .",
        "entities": [
            {
                "word": "Paracetamol 500mg",
                "type": "DRUG"
            },
            {
                "word": "đau cơ xương khớp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_488",
        "text": "Nhiễm virus viêm gan B mạn tính là nguyên_nhân hàng_đầu dẫn đến xơ_gan cổ_trướng .",
        "entities": [
            {
                "word": "xơ_gan cổ_trướng",
                "type": "DISEASE"
            },
            {
                "word": "viêm gan B mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_489",
        "text": "Bệnh_nhân nhập_viện trong tình_trạng xuất_huyết ổ_bụng , có chỉ_định khẩn_cấp phẫu_thuật nội_soi cầm máu .",
        "entities": [
            {
                "word": "xuất_huyết ổ_bụng",
                "type": "SYMPTOM"
            },
            {
                "word": "phẫu_thuật nội_soi cầm máu",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_490",
        "text": "Do nghi_ngờ mắc hội_chứng Cushing do thuốc , bác_sĩ kê đơn xét_nghiệm định_lượng cortisol máu .",
        "entities": [
            {
                "word": "hội_chứng Cushing",
                "type": "DISEASE"
            },
            {
                "word": "xét_nghiệm định_lượng cortisol máu",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_491",
        "text": "Chống chỉ_định dùng thuốc Atorvastatin nếu bệnh_nhân đang mắc bệnh_lý gan tiến_triển .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "bệnh_lý gan tiến_triển",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_492",
        "text": "Nhằm điều_trị chứng loãng_xương ở người cao_tuổi , bác_sĩ kê đơn phối_hợp Acid_Alendronic và canxi .",
        "entities": [
            {
                "word": "Acid_Alendronic",
                "type": "DRUG"
            },
            {
                "word": "loãng_xương",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_493",
        "text": "Triệu_chứng tiêu_chảy kéo dài kèm phân có máu là dấu_hiệu của bệnh viêm loét đại_tràng .",
        "entities": [
            {
                "word": "tiêu_chảy kéo dài kèm phân có máu",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm loét đại_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_494",
        "text": "Sỏi mật kẹt ở ống mật chủ là nguyên_nhân gây ra cơn đau quặn gan dữ_dội và tắc mật .",
        "entities": [
            {
                "word": "cơn đau quặn gan",
                "type": "SYMPTOM"
            },
            {
                "word": "Sỏi_mật",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_495",
        "text": "Bệnh_nhân xuất_hiện triệu_chứng liệt mặt ngoại biên bên trái do biến_chứng viêm tai giữa .",
        "entities": [
            {
                "word": "liệt mặt ngoại biên bên trái",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm tai giữa",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_496",
        "text": "Để chẩn_đoán chính_xác mức_độ tổn_thương sụn chêm , người_bệnh được chỉ_định chụp cộng_hưởng từ khớp gối .",
        "entities": [
            {
                "word": "tổn_thương sụn chêm",
                "type": "DISEASE"
            },
            {
                "word": "chụp cộng_hưởng từ khớp gối",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_497",
        "text": "Nhằm cắt đứt cơn đau nửa đầu Migraine , bác_sĩ đã kê đơn thuốc Sumatriptan cho người_bệnh .",
        "entities": [
            {
                "word": "Sumatriptan",
                "type": "DRUG"
            },
            {
                "word": "đau nửa đầu Migraine",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_498",
        "text": "Chống chỉ_định tuyệt_đối thuốc Spironolactone đối_với bệnh_nhân có nồng_độ kali máu tăng cao .",
        "entities": [
            {
                "word": "Spironolactone",
                "type": "DRUG"
            },
            {
                "word": "kali máu tăng cao",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_499",
        "text": "Nhập_viện trong tình_trạng huyết_áp tụt sâu và sốc phản_vệ , bệnh_nhân có chỉ_định khẩn_cấp tiêm Adrenaline .",
        "entities": [
            {
                "word": "sốc phản_vệ",
                "type": "DISEASE"
            },
            {
                "word": "Adrenaline",
                "type": "DRUG"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_500",
        "text": "Bệnh_béo phì lâu năm là nguyên_nhân trực_tiếp thúc_đẩy sự phát_triển của bệnh thoái_hóa khớp gối sớm .",
        "entities": [
            {
                "word": "thoái_hóa khớp gối sớm",
                "type": "DISEASE"
            },
            {
                "word": "béo phì",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_501",
        "text": "Do nghi_ngờ nhồi máu cơ tim cấp trên nền bệnh_nhân có tiền_sử tăng huyết_áp lâu năm , bác_sĩ đã chỉ_định thực_hiện chụp mạch vành_qua da khẩn_cấp .",
        "entities": [
            {
                "word": "nhồi máu cơ tim cấp",
                "type": "DISEASE"
            },
            {
                "word": "chụp mạch vành_qua da",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_502",
        "text": "Mặc_dù bệnh_nhân nhập_viện trong tình_trạng khó thở dữ_dội do hen phế_quản bội_nhiễm , tuyệt_đối chống chỉ_định sử_dụng Propranolol liều cao .",
        "entities": [
            {
                "word": "Propranolol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản bội_nhiễm",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_503",
        "text": "Nhằm chẩn_đoán chính_xác căn nguyên gây liệt mặt ngoại biên , ê - kip điều_trị đã tiến_hành chụp cộng_hưởng từ sọ não kết_hợp điện_cơ_đồ .",
        "entities": [
            {
                "word": "chụp cộng_hưởng từ sọ não",
                "type": "PROCEDURE"
            },
            {
                "word": "liệt mặt ngoại biên",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_504",
        "text": "Bệnh_nhân xuất_hiện các cơn đau thắt ngực điển_hình khi gắng_sức do tình_trạng xơ_vữa động_mạch_vành tiến_triển .",
        "entities": [
            {
                "word": "xơ_vữa động_mạch_vành",
                "type": "DISEASE"
            },
            {
                "word": "đau thắt ngực",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_505",
        "text": "Để kiểm_soát hiệu_quả chỉ_số đường_huyết tăng cao ở bệnh_nhân đái_tháo_đường týp 2 , bác_sĩ đã kê đơn phối_hợp Metformin và Insulin glargine .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường týp 2",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_506",
        "text": "Do tình_trạng xuất_huyết tiêu_hóa nặng_nề , chỉ_định nội_soi dạ_dày thực_quản cấp_cứu được đặt ra nhằm cầm máu qua kẹp clip .",
        "entities": [
            {
                "word": "nội_soi dạ_dày thực_quản",
                "type": "PROCEDURE"
            },
            {
                "word": "xuất_huyết tiêu_hóa",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_507",
        "text": "Bệnh_nhân bị thoát_vị đĩa_đệm cột_sống thắt_lưng thường_xuyên phàn_nàn vì cơn đau lan dọc xuống chân trái .",
        "entities": [
            {
                "word": "thoát_vị đĩa_đệm cột_sống thắt_lưng",
                "type": "DISEASE"
            },
            {
                "word": "đau lan dọc xuống chân trái",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_508",
        "text": "Nhằm điều_trị triệt_để căn_bệnh viêm loét dạ_dày tá_tràng do vi_khuẩn HP , phác_đồ kháng_sinh chứa Amoxicillin được áp_dụng nghiêm_ngặt .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày tá_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_509",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Aspirin cho phụ_nữ mang thai ở ba tháng đầu do nguy_cơ gây dị_tật bẩm_sinh .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "dị_tật bẩm_sinh",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_510",
        "text": "Do nghi_ngờ mắc hội_chứng Cushing do dùng corticoid kéo_dài , bệnh_nhân được chỉ_định định_lượng nồng_độ cortisol máu buổi sáng .",
        "entities": [
            {
                "word": "hội_chứng Cushing",
                "type": "DISEASE"
            },
            {
                "word": "định_lượng nồng_độ cortisol máu",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_511",
        "text": "Bệnh_nhân hen phế_quản mạn tính thường_xuyên gặp triệu_chứng khò_khè và ho_khan về đêm .",
        "entities": [
            {
                "word": "hen phế_quản mạn tính",
                "type": "DISEASE"
            },
            {
                "word": "khò_khè",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_512",
        "text": "Nhằm giải áp khoang mắt do tăng nhãn áp ác_tính , bác_sĩ đã có chỉ_định khẩn_cấp thực_hiện phẫu_thuật cắt bè củng mạc .",
        "entities": [
            {
                "word": "phẫu_thuật cắt bè củng mạc",
                "type": "PROCEDURE"
            },
            {
                "word": "tăng nhãn áp",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_513",
        "text": "Bệnh_nhân đái_tháo đường lâu năm nay biến_chứng thành suy thận mạn giai_đoạn cuối , bắt_buộc phải lọc máu định_kỳ .",
        "entities": [
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            },
            {
                "word": "suy thận mạn",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_514",
        "text": "Để_hạ huyết_áp nhanh_chóng trong cơn tăng huyết_áp cấp_cứu , thuốc Nicardipine truyền tĩnh_mạch liên_tục đã được kê đơn phối_hợp .",
        "entities": [
            {
                "word": "Nicardipine",
                "type": "DRUG"
            },
            {
                "word": "tăng huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_515",
        "text": "Nhập_viện trong tình_trạng liệt nửa người trái do nhồi máu não cấp , bệnh_nhân được chỉ_định chụp cắt_lớp vi_tính tưới máu não .",
        "entities": [
            {
                "word": "chụp cắt_lớp vi_tính tưới máu não",
                "type": "PROCEDURE"
            },
            {
                "word": "nhồi máu não cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_516",
        "text": "Viêm khớp dạng thấp tiến_triển nặng thường gây ra các cơn đau nhức và sưng tấy tại các khớp nhỏ bàn_tay .",
        "entities": [
            {
                "word": "Viêm khớp dạng thấp",
                "type": "DISEASE"
            },
            {
                "word": "sưng tấy tại các khớp nhỏ bàn_tay",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_517",
        "text": "Tuyệt_đối chống chỉ_định kê đơn Methotrexate cho bệnh_nhân đang mắc bệnh viêm gan cấp_tính .",
        "entities": [
            {
                "word": "Methotrexate",
                "type": "DRUG"
            },
            {
                "word": "viêm gan cấp_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_518",
        "text": "Nhằm chẩn_đoán bệnh_lý xơ_gan cổ_trướng , bác_sĩ chỉ_định siêu_âm Doppler ổ_bụng và xét_nghiệm đánh_giá chức_năng đông máu .",
        "entities": [
            {
                "word": "siêu_âm Doppler ổ_bụng",
                "type": "PROCEDURE"
            },
            {
                "word": "xơ_gan",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_519",
        "text": "Do thiếu máu mạn tính do thiếu sắt kéo_dài , người_bệnh luôn cảm_thấy hoa mắt chóng_mặt và mệt_mỏi .",
        "entities": [
            {
                "word": "thiếu máu mạn tính do thiếu sắt",
                "type": "DISEASE"
            },
            {
                "word": "hoa mắt chóng_mặt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_520",
        "text": "Để điều_trị dứt_điểm triệu_chứng trào ngược dạ_dày thực_quản , bác_sĩ kê đơn thuốc Omeprazole kết_hợp chế_độ ăn_uống khoa_học .",
        "entities": [
            {
                "word": "Omeprazole",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày thực_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_521",
        "text": "Do nghi_ngờ u_xơ tử_cung biến_chứng hoại_tử , bệnh_nhân được chỉ_định chụp cộng_hưởng từ vùng tiểu khung có tiêm thuốc đối quang từ .",
        "entities": [
            {
                "word": "chụp cộng_hưởng từ vùng tiểu_khung",
                "type": "PROCEDURE"
            },
            {
                "word": "u_xơ tử_cung",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_522",
        "text": "Bệnh_nhân suy tim độ III thường biểu_hiện triệu_chứng phù hai chi dưới và khó thở khi nằm .",
        "entities": [
            {
                "word": "suy tim độ III",
                "type": "DISEASE"
            },
            {
                "word": "phù hai chi dưới",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_523",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Sildenafil khi bệnh_nhân đang sử_dụng các loại thuốc chứa nitrat hữu_cơ .",
        "entities": [
            {
                "word": "Sildenafil",
                "type": "DRUG"
            },
            {
                "word": "bệnh tim thiếu máu cục_bộ",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_524",
        "text": "Nhằm tầm soát ung_thư đại trực_tràng sớm , bác_sĩ chỉ_định nội_soi đại_tràng toàn_bộ có sinh_thiết tổn_thương .",
        "entities": [
            {
                "word": "nội_soi đại_tràng toàn_bộ",
                "type": "PROCEDURE"
            },
            {
                "word": "ung_thư đại trực_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_525",
        "text": "Bệnh_nhân gout cấp_tính trải qua những cơn đau dữ_dội tại khớp bàn_chân cái kèm theo sưng nóng đỏ .",
        "entities": [
            {
                "word": "gout cấp_tính",
                "type": "DISEASE"
            },
            {
                "word": "đau dữ_dội tại khớp bàn_chân cái",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_526",
        "text": "Để điều_trị hiệu_quả bệnh_lý viêm phế_quản cấp do virus , bác_sĩ kê đơn thuốc kháng_viêm kết_hợp long đờm Bromhexin .",
        "entities": [
            {
                "word": "Bromhexin",
                "type": "DRUG"
            },
            {
                "word": "viêm phế_quản cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_527",
        "text": "Do nghi_ngờ viêm ruột_thừa cấp , bệnh_nhân được chỉ_định siêu_âm ổ_bụng cấp_cứu và xét_nghiệm công_thức máu toàn_phần .",
        "entities": [
            {
                "word": "siêu_âm ổ_bụng cấp_cứu",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm ruột_thừa cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_528",
        "text": "Tăng huyết_áp không kiểm_soát lâu ngày có_thể gây ra biến_chứng xuất_huyết não đột_ngột .",
        "entities": [
            {
                "word": "Tăng huyết_áp",
                "type": "DISEASE"
            },
            {
                "word": "xuất_huyết não",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_529",
        "text": "Nhằm kiểm_soát nhịp tim cho bệnh_nhân rối_loạn nhịp trên thất , bác_sĩ đã kê đơn phối_hợp thuốc Digoxin .",
        "entities": [
            {
                "word": "Digoxin",
                "type": "DRUG"
            },
            {
                "word": "rối_loạn nhịp trên thất",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_530",
        "text": "Nhập_viện trong tình_trạng đau tức ngực dữ_dội , bệnh_nhân lập_tức có chỉ_định điện tâm_đồ 12 chuyển đạo .",
        "entities": [
            {
                "word": "điện tâm_đồ 12 chuyển đạo",
                "type": "PROCEDURE"
            },
            {
                "word": "đau tức ngực",
                "type": "SYMPTOM"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_531",
        "text": "Bệnh_nhân loãng_xương nặng thường có biểu_hiện đau lưng âm_ỉ và dễ bị gãy xương khi va_chạm nhẹ .",
        "entities": [
            {
                "word": "loãng_xương nặng",
                "type": "DISEASE"
            },
            {
                "word": "đau lưng âm_ỉ",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_532",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Warfarin đối_với các trường_hợp đang có huyết khối tĩnh_mạch sâu .",
        "entities": [
            {
                "word": "Warfarin",
                "type": "DRUG"
            },
            {
                "word": "rối_loạn đông máu nặng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_533",
        "text": "Nhằm chẩn_đoán xác_định viêm phổi thùy , bác_sĩ chỉ_định chụp X - quang phổi thẳng kết_hợp xét_nghiệm đờm tìm vi_khuẩn .",
        "entities": [
            {
                "word": "chụp X - quang phổi thẳng",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm phổi thùy",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_534",
        "text": "Bệnh_nhân viêm xoang mạn tính lâu ngày thường bị triệu_chứng ngạt_mũi kéo_dài và đau vùng trán .",
        "entities": [
            {
                "word": "viêm xoang mạn tính",
                "type": "DISEASE"
            },
            {
                "word": "ngạt_mũi kéo_dài",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_535",
        "text": "Để điều_trị cơn hen phế_quản cấp_tính tại phòng cấp_cứu , bác_sĩ chỉ_định phun khí dung Salbutamol liều cao .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản cấp_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_536",
        "text": "Do nghi_ngờ sỏi niệu_quản gây thận ứ nước độ II , bệnh_nhân được chỉ_định chụp cắt_lớp vi_tính hệ tiết_niệu không tiêm thuốc .",
        "entities": [
            {
                "word": "chụp cắt_lớp vi_tính hệ tiết_niệu",
                "type": "PROCEDURE"
            },
            {
                "word": "sỏi niệu_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_537",
        "text": "Bệnh_lý đái_tháo đường không kiểm_soát tốt có_thể dẫn đến biến_chứng viêm dây thần_kinh ngoại biên .",
        "entities": [
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            },
            {
                "word": "viêm dây thần_kinh ngoại biên",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_538",
        "text": "Nhằm làm giảm nhanh triệu_chứng viêm mũi dị_ứng theo mùa , bác_sĩ kê đơn thuốc kháng histamine Cetirizine .",
        "entities": [
            {
                "word": "Cetirizine",
                "type": "DRUG"
            },
            {
                "word": "viêm mũi dị_ứng",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_539",
        "text": "Nhập_viện trong tình_trạng vàng da vàng mắt do tắc mật , bệnh_nhân có chỉ_định nội_soi mật_tụy ngược dòng .",
        "entities": [
            {
                "word": "nội_soi mật_tụy ngược dòng",
                "type": "PROCEDURE"
            },
            {
                "word": "tắc mật",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_540",
        "text": "Bệnh_nhân tróc vảy da đầu do vẩy_nến thể mảng thường cảm_thấy ngứa_ngáy dữ_dội và khó_chịu .",
        "entities": [
            {
                "word": "vẩy_nến thể mảng",
                "type": "DISEASE"
            },
            {
                "word": "ngứa_ngáy dữ_dội",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_541",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng thuốc Atenolol cho người_bệnh mắc hội_chứng nhịp chậm xoang .",
        "entities": [
            {
                "word": "Atenolol",
                "type": "DRUG"
            },
            {
                "word": "nhịp chậm xoang",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_542",
        "text": "Nhằm đánh_giá mức_độ tổn_thương sụn khớp gối , bác_sĩ chỉ_định chụp cộng_hưởng từ khớp gối trái cho bệnh_nhân .",
        "entities": [
            {
                "word": "chụp cộng_hưởng từ khớp gối trái",
                "type": "PROCEDURE"
            },
            {
                "word": "tổn_thương sụn khớp gối",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_543",
        "text": "Bệnh_nhân thiếu_hụt vitamin B12 kéo_dài thường biểu_hiện triệu_chứng tê bì chân tay và suy_giảm trí_nhớ .",
        "entities": [
            {
                "word": "thiếu_hụt vitamin B12",
                "type": "DISEASE"
            },
            {
                "word": "tê bì chân tay",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_544",
        "text": "Để điều_trị hiệu_quả tình_trạng nhiễm_khuẩn đường tiết_niệu cấp , bác_sĩ đã kê đơn thuốc Levofloxacin .",
        "entities": [
            {
                "word": "Levofloxacin",
                "type": "DRUG"
            },
            {
                "word": "nhiễm_khuẩn đường tiết_niệu cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_545",
        "text": "Do nghi_ngờ mắc bệnh Basedow , bệnh_nhân được chỉ_định định_lượng nồng_độ hormone tuyến_giáp FT3 , FT4 và TSH.",
        "entities": [
            {
                "word": "định_lượng nồng_độ hormone tuyến_giáp",
                "type": "PROCEDURE"
            },
            {
                "word": "Basedow",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_546",
        "text": "Tăng huyết_áp ác_tính kéo_dài không điều_trị sẽ gây ra suy thận tiến_triển nhanh_chóng .",
        "entities": [
            {
                "word": "Tăng huyết_áp",
                "type": "DISEASE"
            },
            {
                "word": "suy thận",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_547",
        "text": "Nhằm hạ_sốt và giảm đau cơ xương khớp hiệu_quả , bác_sĩ đã kê đơn phối_hợp Paracetamol 500mg .",
        "entities": [
            {
                "word": "Paracetamol 500mg",
                "type": "DRUG"
            },
            {
                "word": "đau cơ xương khớp",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_548",
        "text": "Bệnh_nhân nhập_viện trong tình_trạng hôn_mê sâu do đái_tháo_đường biến_chứng nhiễm toan ceton .",
        "entities": [
            {
                "word": "hôn_mê sâu",
                "type": "SYMPTOM"
            },
            {
                "word": "đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_549",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Spironolactone cho các bệnh_nhân đang bị suy thận nặng kèm tăng kali máu .",
        "entities": [
            {
                "word": "Spironolactone",
                "type": "DRUG"
            },
            {
                "word": "suy thận nặng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_550",
        "text": "Nhằm chẩn_đoán chính_xác tình_trạng phình động_mạch chủ bụng , bác_sĩ chỉ_định chụp cắt_lớp vi_tính lồng_ngực ổ_bụng có tiêm thuốc .",
        "entities": [
            {
                "word": "chụp cắt_lớp vi_tính lồng_ngực ổ_bụng",
                "type": "PROCEDURE"
            },
            {
                "word": "phình động_mạch chủ bụng",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_551",
        "text": "Do nghi_ngờ mắc hội_chứng vành cấp trên nền tăng huyết_áp mãn_tính , bệnh_nhân được chỉ_định thực_hiện chụp mạch vành_qua da nhằm chẩn_đoán chính_xác tổn_thương .",
        "entities": [
            {
                "word": "hội_chứng vành_cấp",
                "type": "DISEASE"
            },
            {
                "word": "chụp mạch vành_qua da",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_552",
        "text": "Mặc_dù có tiền_sử hen phế_quản , trường_hợp viêm phổi nặng này tuyệt_đối chống chỉ_định dùng Propranolol do nguy_cơ co thắt phế_quản nguy_hiểm .",
        "entities": [
            {
                "word": "Propranolol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_553",
        "text": "Bệnh_nhân nhập_viện trong tình_trạng đau ngực dữ_dội và khó thở , do đó bác_sĩ đã kê đơn phối_hợp Aspirin để điều_trị nhồi máu cơ tim cấp .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "nhồi máu cơ tim cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_554",
        "text": "Nhằm chẩn_đoán tình_trạng đau_đầu kéo_dài đi kèm chóng_mặt , bác_sĩ đã chỉ_định thực_hiện cộng_hưởng từ sọ não ( MRI ) .",
        "entities": [
            {
                "word": "đau_đầu kéo_dài",
                "type": "SYMPTOM"
            },
            {
                "word": "cộng_hưởng từ sọ não ( MRI )",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_555",
        "text": "Do bệnh_nhân xuất_hiện triệu_chứng ho_khan liên_tục và sốt cao về chiều , các bác_sĩ hô_hấp đã kê đơn Levofloxacin nhằm điều_trị viêm phế_quản cấp .",
        "entities": [
            {
                "word": "Levofloxacin",
                "type": "DRUG"
            },
            {
                "word": "viêm phế_quản cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_556",
        "text": "Khi người_bệnh có biểu_hiện đau thượng_vị dữ_dội và buồn_nôn , việc sử_dụng Diclofenac là tuyệt_đối chống chỉ_định do nguy_cơ làm trầm_trọng thêm tình_trạng xuất_huyết tiêu_hóa .",
        "entities": [
            {
                "word": "Diclofenac",
                "type": "DRUG"
            },
            {
                "word": "xuất_huyết tiêu_hóa",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_557",
        "text": "Nhập_viện trong tình_trạng liệt nửa người và nói đớ do tai_biến mạch_máu não , bệnh_nhân có chỉ_định khẩn_cấp thực_hiện tiêu_sợi huyết .",
        "entities": [
            {
                "word": "tiêu_sợi huyết",
                "type": "PROCEDURE"
            },
            {
                "word": "tai_biến mạch_máu não",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_558",
        "text": "Do mắc chứng đái_tháo_đường tuýp 2 lâu năm , bệnh_nhân thường_xuyên gặp phải tình_trạng tê bì chân tay và mờ mắt .",
        "entities": [
            {
                "word": "đái_tháo_đường tuýp 2",
                "type": "DISEASE"
            },
            {
                "word": "tê bì chân tay",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_559",
        "text": "Bác_sĩ chuyên_khoa cơ xương khớp đã kê đơn Methotrexate nhằm kiểm_soát hiệu_quả bệnh viêm khớp dạng thấp đang tiến_triển nặng .",
        "entities": [
            {
                "word": "Methotrexate",
                "type": "DRUG"
            },
            {
                "word": "viêm khớp dạng thấp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_560",
        "text": "Tuyệt_đối chống chỉ_định kê đơn Metformin cho bệnh_nhân suy thận mạn giai_đoạn cuối vì lý_do tích_tụ thuốc gây nhiễm toan lactic .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "suy thận mạn",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_561",
        "text": "Nhằm chẩn_đoán xác_định bệnh_lý loét dạ_dày tá_tràng , người_bệnh được chỉ_định thực_hiện nội_soi tiêu_hóa trên có gây_tê .",
        "entities": [
            {
                "word": "loét dạ_dày tá_tràng",
                "type": "DISEASE"
            },
            {
                "word": "nội_soi tiêu_hóa trên",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_562",
        "text": "Bệnh_nhân hen phế_quản mãn_tính thường biểu_hiện triệu_chứng khò_khè và khó thở về đêm khi thời_tiết thay_đổi đột_ngột .",
        "entities": [
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            },
            {
                "word": "khò_khè",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_563",
        "text": "Do nghi_ngờ có khối_u gan ác_tính trên nền xơ_gan , bác_sĩ đã chỉ_định chụp cắt_lớp vi_tính ( CT scanner ) ổ_bụng có tiêm thuốc cản_quang .",
        "entities": [
            {
                "word": "xơ_gan",
                "type": "DISEASE"
            },
            {
                "word": "chụp cắt_lớp vi_tính ( CT scanner )",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_564",
        "text": "Kê đơn phối_hợp Salbutamol được chỉ_định nhằm làm giảm nhanh cơn khó thở cấp_tính ở bệnh_nhân mắc bệnh phổi tắc_nghẽn mãn_tính ( COPD ) .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "bệnh phổi tắc_nghẽn mãn_tính ( COPD )",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_565",
        "text": "Phụ_nữ mang thai mắc đái_tháo_đường thai kỳ tuyệt_đối chống chỉ_định sử_dụng thuốc Atorvastatin do nguy_cơ gây dị_tật bẩm_sinh cho thai_nhi .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường thai kỳ",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_566",
        "text": "Nhập_viện trong tình_trạng huyết_áp tăng cao kịch phát và đau_đầu dữ_dội , bệnh_nhân được kê đơn Amlodipin để hạ huyết_áp .",
        "entities": [
            {
                "word": "Amlodipin",
                "type": "DRUG"
            },
            {
                "word": "tăng huyết_áp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_567",
        "text": "Bệnh_nhân thoái_hóa khớp gối lâu ngày thường có triệu_chứng đau nhức khớp và tiếng lục_cục khi vận_động mạnh .",
        "entities": [
            {
                "word": "thoái_hóa khớp gối",
                "type": "DISEASE"
            },
            {
                "word": "đau nhức khớp",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_568",
        "text": "Nhằm chẩn_đoán bệnh_lý glaucoma góc mở , bác_sĩ nhãn khoa đã chỉ_định đo nhãn áp và soi góc tiền phòng cho người_bệnh .",
        "entities": [
            {
                "word": "glaucoma góc mở",
                "type": "DISEASE"
            },
            {
                "word": "đo nhãn áp",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_569",
        "text": "Do mắc chứng suy tim độ III , bệnh_nhân có chỉ_định khẩn_cấp cấy máy tạo nhịp tim nhằm cải_thiện chức_năng bơm máu của cơ tim .",
        "entities": [
            {
                "word": "suy tim",
                "type": "DISEASE"
            },
            {
                "word": "cấy máy tạo nhịp tim",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_570",
        "text": "Viêm cầu thận cấp do liên cầu_khuẩn thường gây ra triệu_chứng phù mặt buổi sáng và tiểu ra máu đại_thể .",
        "entities": [
            {
                "word": "Viêm cầu thận cấp",
                "type": "DISEASE"
            },
            {
                "word": "phù_mặt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_571",
        "text": "Bác_sĩ da_liễu đã kê đơn Isotretinoin để điều_trị mụn trứng_cá bọc nặng , tuy_nhiên thuốc này tuyệt_đối chống chỉ_định cho phụ_nữ có_thai .",
        "entities": [
            {
                "word": "Isotretinoin",
                "type": "DRUG"
            },
            {
                "word": "mụn trứng_cá",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_572",
        "text": "Nhập_viện trong tình_trạng đau bụng quặn từng cơn vùng hạ sườn phải , bệnh_nhân được chỉ_định siêu_âm ổ_bụng tổng_quát .",
        "entities": [
            {
                "word": "đau bụng quặn",
                "type": "SYMPTOM"
            },
            {
                "word": "siêu_âm ổ_bụng tổng_quát",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_573",
        "text": "Do nghi_ngờ mắc hội_chứng ruột kích_thích , người_bệnh được bác_sĩ kê đơn Trimebutine nhằm điều hòa nhu_động ruột .",
        "entities": [
            {
                "word": "Trimebutine",
                "type": "DRUG"
            },
            {
                "word": "hội_chứng ruột kích_thích",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_574",
        "text": "Bệnh_nhân suy thận mạn giai_đoạn đầu thường xuất_hiện các triệu_chứng mệt_mỏi , chán ăn và ngứa da toàn_thân .",
        "entities": [
            {
                "word": "suy thận mạn",
                "type": "DISEASE"
            },
            {
                "word": "mệt_mỏi",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_575",
        "text": "Nhằm chẩn_đoán rách sụn chêm khớp gối sau chấn_thương thể_thao , bác_sĩ chỉ_định chụp cộng_hưởng từ ( MRI ) khớp gối .",
        "entities": [
            {
                "word": "rách sụn chêm",
                "type": "DISEASE"
            },
            {
                "word": "chụp cộng_hưởng từ ( MRI )",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_576",
        "text": "Trường_hợp nhiễm_trùng huyết nặng do vi_khuẩn Gram_âm có chỉ_định khẩn_cấp lọc máu liên_tục tại khoa hồi_sức tích_cực .",
        "entities": [
            {
                "word": "nhiễm_trùng huyết",
                "type": "DISEASE"
            },
            {
                "word": "lọc máu liên_tục",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_577",
        "text": "Kê đơn phối_hợp Insulin glargine được bác_sĩ nội_tiết chỉ_định nhằm kiểm_soát đường_huyết lúc đói ở bệnh_nhân đái_tháo_đường tuýp 1 .",
        "entities": [
            {
                "word": "Insulin_glargine",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường tuýp 1",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_578",
        "text": "Bệnh_nhân loãng_xương nặng tuyệt_đối chống chỉ_định tập vật_lý trị_liệu có động_tác gập cột_sống mạnh do nguy_cơ xẹp đốt_sống .",
        "entities": [
            {
                "word": "loãng_xương",
                "type": "DISEASE"
            },
            {
                "word": "vật_lý trị_liệu",
                "type": "PROCEDURE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_579",
        "text": "Do biểu_hiện hồi_hộp đánh trống_ngực và sụt cân nhanh dù ăn nhiều , bệnh_nhân được chẩn_đoán mắc bệnh Basedow .",
        "entities": [
            {
                "word": "hồi_hộp đánh trống_ngực",
                "type": "SYMPTOM"
            },
            {
                "word": "Basedow",
                "type": "DISEASE"
            }
        ],
        "relation": "NONE"
    },
    {
        "sample_id": "aug_580",
        "text": "Nhập_viện trong tình_trạng sốt cao rét run và vàng da tắc mật , bệnh_nhân được chỉ_định nội_soi mật_tụy ngược dòng ( ERCP ) .",
        "entities": [
            {
                "word": "vàng da tắc mật",
                "type": "SYMPTOM"
            },
            {
                "word": "nội_soi mật_tụy ngược dòng ( ERCP )",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_581",
        "text": "Bác_sĩ thần_kinh đã kê đơn Pregabalin nhằm điều_trị hiệu_quả các cơn đau dây thần_kinh tọa dai_dẳng cho người_bệnh .",
        "entities": [
            {
                "word": "Pregabalin",
                "type": "DRUG"
            },
            {
                "word": "đau dây thần_kinh_tọa",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_582",
        "text": "Do có tiền_sử loét dạ_dày tá_tràng chảy_máu , việc sử_dụng thuốc kháng_viêm không steroid ( NSAIDs ) là tuyệt_đối chống chỉ_định .",
        "entities": [
            {
                "word": "thuốc kháng_viêm không steroid ( NSAIDs )",
                "type": "DRUG"
            },
            {
                "word": "loét dạ_dày tá_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_583",
        "text": "Bệnh_nhân đục thủy_tinh_thể hai mắt có chỉ_định khẩn_cấp phẫu_thuật Phaco nhằm phục_hồi thị_lực rõ_rệt .",
        "entities": [
            {
                "word": "đục thủy_tinh_thể",
                "type": "DISEASE"
            },
            {
                "word": "phẫu_thuật Phaco",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_584",
        "text": "Hội_chứng thận hư thường gây ra các triệu_chứng lâm_sàng điển_hình_như phù toàn_thân , đạm niệu cao và máu nhiễm mỡ .",
        "entities": [
            {
                "word": "Hội_chứng thận hư",
                "type": "DISEASE"
            },
            {
                "word": "phù toàn_thân",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_585",
        "text": "Nhằm chẩn_đoán chính_xác giai_đoạn ung_thư đại trực_tràng , bác_sĩ đã chỉ_định thực_hiện_sinh_thiết tổn_thương qua nội_soi .",
        "entities": [
            {
                "word": "ung_thư đại trực_tràng",
                "type": "DISEASE"
            },
            {
                "word": "sinh_thiết",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_586",
        "text": "Do bệnh_nhân lên_cơn hen phế_quản cấp_tính nặng tại phòng_khám , bác_sĩ đã kê đơn phối_hợp Budesonide_dạng khí dung .",
        "entities": [
            {
                "word": "Budesonide",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_587",
        "text": "Bệnh_nhân cao huyết_áp lâu năm có nguy_cơ cao bị tai_biến mạch_máu nên tuyệt_đối chống chỉ_định dùng các chất kích_thích mạnh .",
        "entities": [
            {
                "word": "tăng huyết_áp",
                "type": "DISEASE"
            },
            {
                "word": "tai_biến mạch_máu",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_588",
        "text": "Nhập_viện trong tình_trạng đau họng dữ_dội , khó nuốt và sốt cao , bệnh_nhân được chẩn_đoán mắc viêm amidan cấp mủ .",
        "entities": [
            {
                "word": "khó nuốt",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm amidan cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_589",
        "text": "Bác_sĩ tim_mạch đã kê đơn Warfarin nhằm phòng_ngừa huyết khối tĩnh_mạch sâu cho bệnh_nhân sau phẫu_thuật thay khớp háng .",
        "entities": [
            {
                "word": "Warfarin",
                "type": "DRUG"
            },
            {
                "word": "huyết khối tĩnh_mạch sâu",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_590",
        "text": "Nhằm chẩn_đoán bệnh_lý động_kinh ở trẻ_em , bác_sĩ đã chỉ_định ghi điện não_đồ ( EEG ) kéo dài ban_đêm .",
        "entities": [
            {
                "word": "động_kinh",
                "type": "DISEASE"
            },
            {
                "word": "điện não_đồ ( EEG )",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_591",
        "text": "Do người_bệnh mắc chứng suy gan nặng độ C , việc kê đơn Paracetamol liều cao là tuyệt_đối chống chỉ_định .",
        "entities": [
            {
                "word": "Paracetamol",
                "type": "DRUG"
            },
            {
                "word": "suy gan nặng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_592",
        "text": "Bệnh_nhân ung_thư vạch tuyến_giáp thường xuất_hiện triệu_chứng khàn tiếng và khối_u vùng cổ lớn dần theo thời_gian .",
        "entities": [
            {
                "word": "ung_thư tuyến_giáp",
                "type": "DISEASE"
            },
            {
                "word": "khàn tiếng",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_593",
        "text": "Nhập_viện trong tình_trạng đau quặn thận trái do sỏi niệu_quản , bệnh_nhân có chỉ_định khẩn_cấp tán sỏi ngoài cơ_thể .",
        "entities": [
            {
                "word": "sỏi niệu_quản",
                "type": "DISEASE"
            },
            {
                "word": "tán sỏi ngoài cơ_thể",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_594",
        "text": "Bác_sĩ chuyên_khoa tiêu_hóa đã kê đơn Omeprazole nhằm làm_lành nhanh các ổ loét dạ_dày tá_tràng đang chảy_máu rả_rích .",
        "entities": [
            {
                "word": "Omeprazole",
                "type": "DRUG"
            },
            {
                "word": "loét dạ_dày tá_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_595",
        "text": "Do nghi_ngờ mắc bệnh viêm phổi thùy , bác_sĩ đã chỉ_định chụp X - quang ngực thẳng nhằm phát_hiện tổn_thương mờ ở phế trường .",
        "entities": [
            {
                "word": "viêm phổi thùy",
                "type": "DISEASE"
            },
            {
                "word": "chụp X - quang ngực thẳng",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_596",
        "text": "Bệnh_nhân sốt_xuất_huyết Dengue ngày thứ tư có triệu_chứng chảy máu chân răng và chấm xuất_huyết ngoài da .",
        "entities": [
            {
                "word": "sốt_xuất_huyết Dengue",
                "type": "DISEASE"
            },
            {
                "word": "chảy máu chân_răng",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_597",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc chẹn beta giao_cảm cho bệnh_nhân đang gặp cơn nhịp chậm xoang nặng .",
        "entities": [
            {
                "word": "thuốc chẹn beta giao_cảm",
                "type": "DRUG"
            },
            {
                "word": "nhịp chậm xoang",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_598",
        "text": "Nhập_viện trong tình_trạng hôn_mê sâu do đái_tháo_đường tuýp 2 , bệnh_nhân được đặt đường truyền tĩnh_mạch trung_tâm để hồi_sức .",
        "entities": [
            {
                "word": "hôn_mê sâu",
                "type": "SYMPTOM"
            },
            {
                "word": "đái_tháo_đường tuýp 2",
                "type": "DISEASE"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_599",
        "text": "Kê đơn phối_hợp Spironolactone được chỉ_định nhằm điều_trị cổ_trướng do xơ_gan mạn tính kháng trị .",
        "entities": [
            {
                "word": "Spironolactone",
                "type": "DRUG"
            },
            {
                "word": "xơ_gan mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_600",
        "text": "Nhằm chẩn_đoán chính_xác mức_độ hẹp van hai lá , bác_sĩ tim_mạch đã chỉ_định siêu_âm tim qua thực_quản .",
        "entities": [
            {
                "word": "hẹp van hai lá",
                "type": "DISEASE"
            },
            {
                "word": "siêu_âm tim qua thực_quản",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_601",
        "text": "Do nghi_ngờ mắc hội_chứng vành cấp trên nền đái_tháo_đường tuýp 2 , bác_sĩ đã chỉ_định chụp mạch vành_qua da nhằm chẩn_đoán chính_xác tổn_thương .",
        "entities": [
            {
                "word": "hội_chứng vành_cấp",
                "type": "DISEASE"
            },
            {
                "word": "chụp mạch vành_qua da",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_602",
        "text": "Mặc_dù bệnh_nhân nhập_viện trong tình_trạng khó thở dữ_dội do hen phế_quản bội_nhiễm , việc kê đơn phối_hợp Salbutamol lại tuyệt_đối chống chỉ_định trên người_bệnh tăng huyết_áp ác_tính .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "tăng huyết_áp ác_tính",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_603",
        "text": "Để điều_trị dứt_điểm cơn đau thắt ngực ổn_định , bệnh_nhân có chỉ_định khẩn_cấp dùng Aspirin kết_hợp Atorvastatin nhằm ngăn_ngừa huyết khối .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "đau thắt ngực ổn_định",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_604",
        "text": "Do người_bệnh xuất_hiện triệu_chứng ho_khan kéo_dài và sốt cao về chiều , bác_sĩ chỉ_định thực_hiện chụp cắt_lớp vi_tính lồng_ngực nhằm chẩn_đoán bệnh viêm phổi lao .",
        "entities": [
            {
                "word": "chụp cắt_lớp vi_tính lồng_ngực",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm phổi lao",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_605",
        "text": "Mặc_dù có chỉ_định khẩn_cấp dùng thuốc kháng_sinh Amoxicillin để trị viêm họng cấp , nhưng nếu bệnh_nhân dị_ứng penicillin thì tuyệt_đối chống chỉ_định loại thuốc này .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "viêm họng cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_606",
        "text": "Nhằm chẩn_đoán hội_chứng ruột kích_thích do rối_loạn hệ vi_sinh đường ruột , bác_sĩ đã chỉ_định nội_soi đại_tràng toàn_bộ .",
        "entities": [
            {
                "word": "nội_soi đại_tràng toàn_bộ",
                "type": "PROCEDURE"
            },
            {
                "word": "hội_chứng ruột kích_thích",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_607",
        "text": "Do nghi_ngờ thoái_hóa khớp gối nặng gây ra những cơn đau nhức dữ_dội ban_đêm , bệnh_nhân được kê đơn phối_hợp Meloxicam và Glucosamin .",
        "entities": [
            {
                "word": "Meloxicam",
                "type": "DRUG"
            },
            {
                "word": "thoái_hóa khớp gối",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_608",
        "text": "Bệnh_nhân nhập_viện trong tình_trạng liệt nửa người do tai_biến mạch_máu não , có chỉ_định khẩn_cấp thực_hiện chụp cộng_hưởng từ sọ não .",
        "entities": [
            {
                "word": "chụp cộng_hưởng từ sọ não",
                "type": "PROCEDURE"
            },
            {
                "word": "tai_biến mạch_máu não",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_609",
        "text": "Tuyệt_đối chống chỉ_định dùng Metformin cho người_bệnh suy thận mạn giai_đoạn cuối do nguy_cơ gây nhiễm toan chuyển_hóa lactic .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "suy thận mạn",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_610",
        "text": "Nhằm điều_trị căn_bệnh đái_tháo_đường tuýp 2 kháng insulin , bác_sĩ tiến_hành kê đơn phối_hợp Insulin_Glargine cùng với chế_độ ăn_kiêng nghiêm_ngặt .",
        "entities": [
            {
                "word": "Insulin_Glargine",
                "type": "DRUG"
            },
            {
                "word": "đái_tháo_đường tuýp 2",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_611",
        "text": "Do mắc chứng tiền sản_giật nặng đe_dọa tính_mạng thai_phụ , sản_phụ có chỉ_định khẩn_cấp thực_hiện phẫu_thuật mổ lấy thai nhằm bảo_vệ an_toàn cho cả mẹ lẫn con .",
        "entities": [
            {
                "word": "phẫu_thuật mổ lấy thai",
                "type": "PROCEDURE"
            },
            {
                "word": "tiền sản_giật",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_612",
        "text": "Bệnh_nhân mắc bệnh vẩy_nến thể mảng lan_tỏa , nhập_viện trong tình_trạng ngứa_ngáy dữ_dội , được kê đơn phối_hợp Cyclosporin nhằm kiểm_soát triệu_chứng .",
        "entities": [
            {
                "word": "Cyclosporin",
                "type": "DRUG"
            },
            {
                "word": "vẩy_nến",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_613",
        "text": "Do nghi_ngờ bị đục thủy_tinh_thể bẩm_sinh gây giảm thị_lực nghiêm_trọng , bệnh_nhi được chỉ_định thực_hiện phẫu_thuật Phaco .",
        "entities": [
            {
                "word": "phẫu_thuật Phaco",
                "type": "PROCEDURE"
            },
            {
                "word": "đục thủy_tinh_thể",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_614",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng thuốc chống viêm không steroid ( NSAIDs ) đối_với các trường_hợp đang bị viêm loét dạ_dày tá_tràng cấp_tính .",
        "entities": [
            {
                "word": "thuốc chống viêm không steroid ( NSAIDs )",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày tá_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_615",
        "text": "Nhằm chẩn_đoán xác_định bệnh hen_suyễn dị_ứng , bác_sĩ đã yêu_cầu bệnh_nhân thực_hiện kỹ_thuật đo chức_năng hô_hấp ký .",
        "entities": [
            {
                "word": "đo chức_năng hô_hấp ký",
                "type": "PROCEDURE"
            },
            {
                "word": "hen_suyễn",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_616",
        "text": "Bệnh_nhân tăng huyết_áp vô căn có triệu_chứng đau_đầu chóng_mặt thường_xuyên , được kê đơn phối_hợp Amlodipin và Valsartan .",
        "entities": [
            {
                "word": "Amlodipin",
                "type": "DRUG"
            },
            {
                "word": "tăng huyết_áp vô căn",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_617",
        "text": "Do biến_chứng nặng của bệnh tiểu_đường gây loét bàn_chân , bệnh_nhân nhập_viện trong tình_trạng hoại_tử ngón chân cái và có chỉ_định khẩn_cấp cắt cụt chi .",
        "entities": [
            {
                "word": "cắt cụt chi",
                "type": "PROCEDURE"
            },
            {
                "word": "loét bàn_chân",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_618",
        "text": "Nhằm điều_trị hiệu_quả căn_bệnh trầm_cảm nặng kèm rối_loạn lo_âu , bác_sĩ chỉ_định dùng Sertraline liều duy_trì mỗi ngày .",
        "entities": [
            {
                "word": "Sertraline",
                "type": "DRUG"
            },
            {
                "word": "trầm_cảm_nặng",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_619",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc chẹn beta giao_cảm như Propranolol cho bệnh_nhân đang lên_cơn hen phế_quản cấp .",
        "entities": [
            {
                "word": "Propranolol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_620",
        "text": "Do nghi_ngờ mắc bệnh viêm tụy cấp do sỏi mật , bệnh_nhân được chỉ_định thực_hiện siêu_âm ổ_bụng tổng_quát .",
        "entities": [
            {
                "word": "siêu_âm ổ_bụng tổng_quát",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm tụy cấp",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_621",
        "text": "Bệnh_nhân suy tim mạng tính xuất_hiện triệu_chứng phù hai chi dưới và khó thở khi nằm , được kê đơn phối_hợp Furosemid và Spironolactone .",
        "entities": [
            {
                "word": "Furosemid",
                "type": "DRUG"
            },
            {
                "word": "suy tim",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_622",
        "text": "Nhằm chẩn_đoán sớm bệnh ung_thư đại trực_tràng , bác_sĩ chỉ_định thực_hiện_sinh_thiết mô tổn_thương qua nội_soi .",
        "entities": [
            {
                "word": "sinh_thiết mô tổn_thương qua nội_soi",
                "type": "PROCEDURE"
            },
            {
                "word": "ung_thư đại trực_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_623",
        "text": "Do người_bệnh bị dị_ứng nặng với kháng_sinh nhóm beta - lactam , bác_sĩ kê đơn phối_hợp Azithromycin nhằm điều_trị viêm phế_quản cấp .",
        "entities": [
            {
                "word": "Azithromycin",
                "type": "DRUG"
            },
            {
                "word": "viêm phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_624",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Warfarin đối_với phụ_nữ mang thai trong 3 tháng đầu do nguy_cơ gây dị_tật bẩm_sinh nghiêm_trọng .",
        "entities": [
            {
                "word": "Warfarin",
                "type": "DRUG"
            },
            {
                "word": "dị_tật bẩm_sinh",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_625",
        "text": "Bệnh_nhân đột_quỵ nhồi máu não cấp_tính nhập_viện trong tình_trạng liệt hoàn_toàn nửa người trái , có chỉ_định khẩn_cấp truyền thuốc tiêu_sợi huyết Alteplase .",
        "entities": [
            {
                "word": "Alteplase",
                "type": "DRUG"
            },
            {
                "word": "nhồi máu não",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_626",
        "text": "Nhằm điều_trị căn_bệnh động_kinh cục_bộ kháng thuốc , bác_sĩ kê đơn phối_hợp Levetiracetam cùng với Carbamazepin .",
        "entities": [
            {
                "word": "Levetiracetam",
                "type": "DRUG"
            },
            {
                "word": "động_kinh",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_627",
        "text": "Do nghi_ngờ mắc bệnh gút mạn tính có hạt tophi , bệnh_nhân được chỉ_định chọc hút dịch khớp gối để xét_nghiệm .",
        "entities": [
            {
                "word": "chọc hút dịch khớp gối",
                "type": "PROCEDURE"
            },
            {
                "word": "gút",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_628",
        "text": "Bệnh_nhân viêm cầu thận cấp nhập_viện trong tình_trạng phù mặt và huyết_áp tăng cao , được kê đơn phối_hợp Nifedipin nhằm_hạ huyết_áp .",
        "entities": [
            {
                "word": "Nifedipin",
                "type": "DRUG"
            },
            {
                "word": "viêm cầu thận",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_629",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Methotrexate cho các bệnh_nhân đang mắc bệnh viêm gan siêu_vi B cấp_tính .",
        "entities": [
            {
                "word": "Methotrexate",
                "type": "DRUG"
            },
            {
                "word": "viêm gan siêu_vi B",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_630",
        "text": "Nhằm chẩn_đoán bệnh_lý mạch_máu não phức_tạp , bác_sĩ chỉ_định thực_hiện chụp cắt_lớp vi_tính mạch_máu não ( CTA ) có tiêm thuốc cản_quang .",
        "entities": [
            {
                "word": "chụp cắt_lớp vi_tính mạch_máu não ( CTA )",
                "type": "PROCEDURE"
            },
            {
                "word": "bệnh_lý mạch_máu não",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_631",
        "text": "Do mắc chứng loãng_xương nặng gây xẹp đốt_sống_lưng , bệnh_nhân có chỉ_định khẩn_cấp thực_hiện thủ_thuật bơm xi_măng sinh_học tạo_hình thân_đốt_sống .",
        "entities": [
            {
                "word": "bơm xi_măng sinh_học tạo_hình thân_đốt_sống",
                "type": "PROCEDURE"
            },
            {
                "word": "loãng_xương",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_632",
        "text": "Bệnh_nhân trào ngược dạ_dày thực_quản nặng có triệu_chứng ợ nóng và ho_khan về đêm , được kê đơn phối_hợp Omeprazole .",
        "entities": [
            {
                "word": "Omeprazole",
                "type": "DRUG"
            },
            {
                "word": "trào ngược dạ_dày thực_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_633",
        "text": "Nhằm điều_trị hiệu_quả căn_bệnh tăng áp động_mạch phổi tiên phát , bác_sĩ kê đơn phối_hợp Sildenafil .",
        "entities": [
            {
                "word": "Sildenafil",
                "type": "DRUG"
            },
            {
                "word": "tăng áp động_mạch phổi",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_634",
        "text": "Do nghi_ngờ thủng tạng rỗng do viêm loét dạ_dày tiến_triển , bệnh_nhân có chỉ_định khẩn_cấp thực_hiện phẫu_thuật nội_soi cấp_cứu .",
        "entities": [
            {
                "word": "phẫu_thuật nội_soi cấp_cứu",
                "type": "PROCEDURE"
            },
            {
                "word": "viêm loét dạ_dày",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_635",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng thuốc Paracetamol liều cao dài ngày đối_với bệnh_nhân đang mắc bệnh xơ_gan cổ_trướng .",
        "entities": [
            {
                "word": "Paracetamol",
                "type": "DRUG"
            },
            {
                "word": "xơ_gan",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_636",
        "text": "Bệnh_nhân suy tuyến_giáp nguyên_phát có triệu_chứng mệt_mỏi và tăng cân đột_ngột , được kê đơn phối_hợp Levothyroxine nhằm bổ_sung hormone .",
        "entities": [
            {
                "word": "Levothyroxine",
                "type": "DRUG"
            },
            {
                "word": "suy tuyến_giáp",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_637",
        "text": "Nhằm chẩn_đoán xác_định bệnh glaucom góc đóng cấp_tính , bác_sĩ nhãn khoa chỉ_định thực_hiện đo nhãn áp_kế và soi góc tiền phòng .",
        "entities": [
            {
                "word": "đo nhãn áp_kế và soi góc tiền phòng",
                "type": "PROCEDURE"
            },
            {
                "word": "glaucom góc đóng",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_638",
        "text": "Do nghi_ngờ u_xơ tử_cung dưới thanh mạc gây rong kinh kéo_dài , bệnh_nhân được chỉ_định thực_hiện siêu_âm ổ_bụng qua đường âm_đạo .",
        "entities": [
            {
                "word": "siêu_âm ổ_bụng qua đường âm_đạo",
                "type": "PROCEDURE"
            },
            {
                "word": "u_xơ tử_cung",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_639",
        "text": "Bệnh_nhân viêm khớp dạng thấp thể hoạt_động mạnh có triệu_chứng sưng đau nhiều khớp nhỏ bàn_tay , được kê đơn phối_hợp Methotrexate .",
        "entities": [
            {
                "word": "Methotrexate",
                "type": "DRUG"
            },
            {
                "word": "viêm khớp dạng thấp",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_640",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Adrenaline cho các bệnh_nhân có tiền_sử bệnh cơ tim phì đại tắc_nghẽn nặng .",
        "entities": [
            {
                "word": "Adrenaline",
                "type": "DRUG"
            },
            {
                "word": "bệnh cơ tim phì đại tắc_nghẽn",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_641",
        "text": "Nhằm điều_trị dứt_điểm căn_bệnh nhiễm_trùng đường tiểu dưới do vi_khuẩn gram âm , bác_sĩ kê đơn phối_hợp Ciprofloxacin .",
        "entities": [
            {
                "word": "Ciprofloxacin",
                "type": "DRUG"
            },
            {
                "word": "nhiễm_trùng đường tiểu",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_642",
        "text": "Do nghi_ngờ mắc chứng nhược cơ toàn_thân gây sụp mí và khó nuốt , bệnh_nhân được chỉ_định thực_hiện điện_cơ_đồ bề_mặt .",
        "entities": [
            {
                "word": "điện_cơ_đồ bề_mặt",
                "type": "PROCEDURE"
            },
            {
                "word": "nhược_cơ",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_643",
        "text": "Bệnh_nhân hen phế_quản mạn tính nhập_viện trong tình_trạng cò cữ và tức ngực , có chỉ_định khẩn_cấp phun khí dung Salbutamol kết_hợp Budesonide .",
        "entities": [
            {
                "word": "Budesonide",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_644",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng thuốc Atorvastatin liều cao đối_với người_bệnh đang mắc bệnh viêm cơ cấp_tính .",
        "entities": [
            {
                "word": "Atorvastatin",
                "type": "DRUG"
            },
            {
                "word": "viêm cơ",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_645",
        "text": "Nhằm chẩn_đoán bệnh ung_thư vòm họng giai_đoạn sớm , bác_sĩ chỉ_định thực_hiện nội_soi tai mũi họng ống mềm kết_hợp sinh_thiết .",
        "entities": [
            {
                "word": "nội_soi tai mũi họng ống mềm kết_hợp sinh_thiết",
                "type": "PROCEDURE"
            },
            {
                "word": "ung_thư vòm họng",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_646",
        "text": "Do bị biến_chứng võng_mạc đái_tháo_đường gây giảm thị_lực đột_ngột , bệnh_nhân có chỉ_định khẩn_cấp thực_hiện quang đông laser võng_mạc .",
        "entities": [
            {
                "word": "quang đông laser võng_mạc",
                "type": "PROCEDURE"
            },
            {
                "word": "võng_mạc đái_tháo_đường",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_647",
        "text": "Bệnh_nhân viêm loét đại_tràng mạn tính xuất_hiện triệu_chứng tiêu_chảy lẫn máu tươi , được kê đơn phối_hợp Mesalazine nhằm kháng_viêm tại_chỗ .",
        "entities": [
            {
                "word": "Mesalazine",
                "type": "DRUG"
            },
            {
                "word": "viêm loét đại_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_648",
        "text": "Nhằm điều_trị hiệu_quả căn_bệnh rối_loạn lipid máu hỗn_hợp , bác_sĩ tiến_hành kê đơn phối_hợp Rosuvastatin cùng với Fenofibrat .",
        "entities": [
            {
                "word": "Rosuvastatin",
                "type": "DRUG"
            },
            {
                "word": "rối_loạn lipid máu",
                "type": "DISEASE"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_649",
        "text": "Do nghi_ngờ mắc bệnh sỏi thận niệu_quản gây thận ứ nước độ II , bệnh_nhân được chỉ_định thực_hiện chụp X - quang niệu đồ tĩnh_mạch ( IVP ) .",
        "entities": [
            {
                "word": "chụp X - quang niệu đồ tĩnh_mạch ( IVP )",
                "type": "PROCEDURE"
            },
            {
                "word": "sỏi thận niệu_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_650",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Spironolactone cho các bệnh_nhân đang gặp tình_trạng tăng kali máu nặng .",
        "entities": [
            {
                "word": "Spironolactone",
                "type": "DRUG"
            },
            {
                "word": "tăng kali máu",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_651",
        "text": "Do nghi_ngờ mắc hội_chứng vành cấp trên nền tăng huyết_áp , bệnh_nhân đã được chỉ_định chụp mạch vành nhằm chẩn_đoán chính_xác tổn_thương .",
        "entities": [
            {
                "word": "hội_chứng vành_cấp",
                "type": "DISEASE"
            },
            {
                "word": "chụp mạch_vành",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_652",
        "text": "Bác_sĩ đã kê đơn phối_hợp Aspirin để điều_trị huyết khối tĩnh_mạch sâu cho người_bệnh .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "huyết khối tĩnh_mạch sâu",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_653",
        "text": "Tuyệt_đối chống chỉ_định sử_dụng Warfarin ở những bệnh_nhân đang bị xuất_huyết tiêu_hóa nặng .",
        "entities": [
            {
                "word": "Warfarin",
                "type": "DRUG"
            },
            {
                "word": "xuất_huyết tiêu_hóa",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_654",
        "text": "Nhập_viện trong tình_trạng khó thở dữ_dội do viêm phổi thùy , người_bệnh ngay lập_tức được thở oxy .",
        "entities": [
            {
                "word": "viêm phổi thùy",
                "type": "DISEASE"
            },
            {
                "word": "khó thở",
                "type": "SYMPTOM"
            }
        ],
        "relation": "HAS_SYMPTOM"
    },
    {
        "sample_id": "aug_655",
        "text": "Để đánh_giá mức_độ tổn_thương gan mật , bác_sĩ tiến_hành siêu_âm ổ_bụng có chuẩn_bị cho bệnh_nhân .",
        "entities": [
            {
                "word": "tổn_thương gan",
                "type": "DISEASE"
            },
            {
                "word": "siêu_âm ổ_bụng",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_656",
        "text": "Bệnh_nhân xuất_hiện cơn đau thắt ngực điển_hình nguyên_nhân do xơ_vữa động_mạch_vành tiến_triển .",
        "entities": [
            {
                "word": "đau thắt ngực",
                "type": "SYMPTOM"
            },
            {
                "word": "xơ_vữa động_mạch_vành",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_657",
        "text": "Nhằm chẩn_đoán xác_định bệnh_lý viêm khớp dạng thấp , các bác_sĩ đã chỉ_định xét_nghiệm yếu_tố dạng thấp .",
        "entities": [
            {
                "word": "viêm khớp dạng thấp",
                "type": "DISEASE"
            },
            {
                "word": "xét_nghiệm yếu_tố dạng thấp",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_658",
        "text": "Do nghi_ngờ thủng ổ loét dạ_dày tá_tràng , bệnh_nhân có chỉ_định khẩn_cấp thực_hiện nội_soi thực_quản dạ_dày .",
        "entities": [
            {
                "word": "thủng ổ loét dạ_dày tá_tràng",
                "type": "DISEASE"
            },
            {
                "word": "nội_soi thực_quản dạ_dày",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_659",
        "text": "Thuốc Metformin được kê đơn phối_hợp nhằm kiểm_soát hiệu_quả tình_trạng tăng đường_huyết ở người_bệnh đái_tháo_đường type 2 .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "tăng đường_huyết",
                "type": "SYMPTOM"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_660",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Metformin cho các trường_hợp suy thận mạn tính giai_đoạn cuối .",
        "entities": [
            {
                "word": "Metformin",
                "type": "DRUG"
            },
            {
                "word": "suy thận mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_661",
        "text": "Bệnh_nhân nhập_viện trong tình_trạng liệt nửa người trái do tai_biến mạch_máu não cấp_tính .",
        "entities": [
            {
                "word": "liệt nửa người",
                "type": "SYMPTOM"
            },
            {
                "word": "tai_biến mạch_máu não",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_662",
        "text": "Nhằm chẩn_đoán hội_chứng ống cổ_tay , bác_sĩ chuyên_khoa thần_kinh đã yêu_cầu đo điện_cơ chi trên .",
        "entities": [
            {
                "word": "hội_chứng ống cổ_tay",
                "type": "DISEASE"
            },
            {
                "word": "đo điện_cơ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_663",
        "text": "Việc sử_dụng Salbutamol dạng phun khí dung có tác_dụng điều_trị cơn hen phế_quản cấp_tính rất hiệu_quả .",
        "entities": [
            {
                "word": "Salbutamol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_664",
        "text": "Do nghi_ngờ u_xơ tử_cung biến_chứng , bệnh_nhân được chỉ_định chụp cộng_hưởng từ vùng tiểu khung .",
        "entities": [
            {
                "word": "u_xơ tử_cung",
                "type": "DISEASE"
            },
            {
                "word": "chụp cộng_hưởng từ vùng tiểu_khung",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_665",
        "text": "Bệnh_nhân có triệu_chứng phù toàn_thân do hội_chứng thận hư kháng corticosteroid .",
        "entities": [
            {
                "word": "phù toàn_thân",
                "type": "SYMPTOM"
            },
            {
                "word": "hội_chứng thận hư",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_666",
        "text": "Kê đơn phối_hợp Insulin glargine nhằm mục_đích hạ đường_huyết đói cho bệnh_nhân đái_tháo_đường .",
        "entities": [
            {
                "word": "Insulin_glargine",
                "type": "DRUG"
            },
            {
                "word": "hạ đường_huyết",
                "type": "SYMPTOM"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_667",
        "text": "Chống chỉ_định dùng thuốc Amlodipin khi người_bệnh có biểu_hiện sốc tim hoặc huyết_áp quá thấp .",
        "entities": [
            {
                "word": "Amlodipin",
                "type": "DRUG"
            },
            {
                "word": "sốc tim",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_668",
        "text": "Nhập_viện trong tình_trạng đau_đầu dữ_dội và nôn vọt do tăng áp_lực nội sọ .",
        "entities": [
            {
                "word": "đau_đầu",
                "type": "SYMPTOM"
            },
            {
                "word": "tăng áp_lực nội sọ",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_669",
        "text": "Nhằm chẩn_đoán bệnh_lý glôcôm góc mở , bác_sĩ nhãn khoa đã chỉ_định đo nhãn áp_kế cho người_bệnh .",
        "entities": [
            {
                "word": "glôcôm góc mở",
                "type": "DISEASE"
            },
            {
                "word": "đo nhãn áp",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_670",
        "text": "Bác_sĩ kê đơn thuốc Omeprazol nhằm điều_trị bệnh viêm loét dạ_dày tá_tràng mạn tính .",
        "entities": [
            {
                "word": "Omeprazol",
                "type": "DRUG"
            },
            {
                "word": "viêm loét dạ_dày tá_tràng",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_671",
        "text": "Tuyệt_đối chống chỉ_định tiêm corticoid nội khớp khi vùng da quanh khớp đang có tình_trạng nhiễm_trùng .",
        "entities": [
            {
                "word": "corticoid",
                "type": "DRUG"
            },
            {
                "word": "nhiễm_trùng",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_672",
        "text": "Do nghi_ngờ mắc bệnh viêm mủ màng phổi , bệnh_nhân được chỉ_định chọc hút dịch màng phổi .",
        "entities": [
            {
                "word": "viêm mủ màng phổi",
                "type": "DISEASE"
            },
            {
                "word": "chọc hút dịch màng phổi",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_673",
        "text": "Bệnh_nhân xuất_hiện tình_trạng ho khạc đờm mủ xanh vàng do bội_nhiễm viêm phế_quản mạn .",
        "entities": [
            {
                "word": "ho khạc đờm mủ",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm phế_quản mạn",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_674",
        "text": "Có chỉ_định khẩn_cấp phẫu_thuật cắt ruột_thừa viêm cho bệnh_nhân đau hố_chậu phải .",
        "entities": [
            {
                "word": "viêm ruột_thừa",
                "type": "DISEASE"
            },
            {
                "word": "phẫu_thuật cắt ruột_thừa",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_675",
        "text": "Kê đơn phối_hợp Paracetamol nhằm giảm sốt và giảm đau cơ xương khớp cho người_bệnh .",
        "entities": [
            {
                "word": "Paracetamol",
                "type": "DRUG"
            },
            {
                "word": "giảm sốt",
                "type": "SYMPTOM"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_676",
        "text": "Nhập_viện trong tình_trạng vàng da tắc mật do sỏi ống mật chủ , bệnh_nhân được chỉ_định nội_soi mật_tụy ngược dòng .",
        "entities": [
            {
                "word": "vàng da tắc mật",
                "type": "SYMPTOM"
            },
            {
                "word": "nội_soi mật_tụy ngược dòng",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_677",
        "text": "Chống chỉ_định tuyệt_đối sử_dụng thuốc Aspirin cho trẻ_em bị sốt_xuất_huyết dengue .",
        "entities": [
            {
                "word": "Aspirin",
                "type": "DRUG"
            },
            {
                "word": "sốt_xuất_huyết dengue",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_678",
        "text": "Bệnh_nhân có triệu_chứng mất_ngủ kéo dài nguyên_nhân do rối_loạn loãng âu toàn_thể .",
        "entities": [
            {
                "word": "mất_ngủ",
                "type": "SYMPTOM"
            },
            {
                "word": "rối_loạn lo_âu",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_679",
        "text": "Nhằm chẩn_đoán bệnh ung_thư biểu mô tuyến_giáp , bác_sĩ đã thực_hiện_sinh_thiết kim nhỏ tuyến_giáp .",
        "entities": [
            {
                "word": "ung_thư biểu mô tuyến_giáp",
                "type": "DISEASE"
            },
            {
                "word": "sinh_thiết kim nhỏ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_680",
        "text": "Thuốc Levothyroxine được bác_sĩ nội_tiết kê đơn điều_trị bệnh suy giáp nguyên_phát .",
        "entities": [
            {
                "word": "Levothyroxine",
                "type": "DRUG"
            },
            {
                "word": "suy giáp",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_681",
        "text": "Do nghi_ngờ nhồi máu cơ tim cấp , bệnh_nhân được chỉ_định thực_hiện điện tâm_đồ 12 chuyển đạo ngay .",
        "entities": [
            {
                "word": "nhồi máu cơ tim cấp",
                "type": "DISEASE"
            },
            {
                "word": "điện tâm_đồ",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_682",
        "text": "Bệnh_nhân nhập_viện trong tình_trạng nhịp tim nhanh kịch phát trên thất do hội_chứng WPW.",
        "entities": [
            {
                "word": "nhịp tim nhanh kịch_phát",
                "type": "SYMPTOM"
            },
            {
                "word": "hội_chứng WPW",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_683",
        "text": "Kê đơn phối_hợp thuốc kháng_sinh Amoxicillin nhằm điều_trị tình_trạng viêm tai giữa cấp ở trẻ nhỏ .",
        "entities": [
            {
                "word": "Amoxicillin",
                "type": "DRUG"
            },
            {
                "word": "viêm tai giữa",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_684",
        "text": "Chống chỉ_định dùng thuốc Isotretinoin đối_với phụ_nữ có_thai vì nguy_cơ gây dị_tật bẩm_sinh .",
        "entities": [
            {
                "word": "Isotretinoin",
                "type": "DRUG"
            },
            {
                "word": "có_thai",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_685",
        "text": "Nhằm chẩn_đoán xác_định thoái_hóa khớp gối , người_bệnh có chỉ_định chụp X - quang khớp gối hai bên .",
        "entities": [
            {
                "word": "thoái_hóa khớp gối",
                "type": "DISEASE"
            },
            {
                "word": "chụp X - quang",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_686",
        "text": "Bệnh_nhân gặp tình_trạng ban đỏ da toàn_thân do dị_ứng thuốc kháng_sinh nhóm beta - lactam .",
        "entities": [
            {
                "word": "ban đỏ da",
                "type": "SYMPTOM"
            },
            {
                "word": "dị_ứng thuốc",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_687",
        "text": "Có chỉ_định khẩn_cấp đặt ống nội khí_quản hỗ_trợ thông khí cho bệnh_nhân suy hô_hấp độ III.",
        "entities": [
            {
                "word": "suy hô_hấp",
                "type": "DISEASE"
            },
            {
                "word": "đặt ống nội khí_quản",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_688",
        "text": "Thuốc Spironolactone được kê đơn nhằm giảm triệu_chứng phù do xơ_gan cổ chướng .",
        "entities": [
            {
                "word": "Spironolactone",
                "type": "DRUG"
            },
            {
                "word": "phù",
                "type": "SYMPTOM"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_689",
        "text": "Do nghi_ngờ loét giác_mạc do vi_khuẩn , bác_sĩ nhãn khoa đã chỉ_định nhuộm soi tìm vi_sinh_vật .",
        "entities": [
            {
                "word": "loét giác_mạc",
                "type": "DISEASE"
            },
            {
                "word": "nhuộm soi",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_690",
        "text": "Bệnh_nhân xuất_hiện triệu_chứng run tay khi cầm nắm do bệnh Parkinson giai_đoạn sớm .",
        "entities": [
            {
                "word": "run_tay",
                "type": "SYMPTOM"
            },
            {
                "word": "Parkinson",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_691",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc Propranolol ở bệnh_nhân có tiền_sử hen phế_quản co thắt .",
        "entities": [
            {
                "word": "Propranolol",
                "type": "DRUG"
            },
            {
                "word": "hen phế_quản",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    },
    {
        "sample_id": "aug_692",
        "text": "Nhập_viện trong tình_trạng đau tức ngực lan ra sau lưng do bóc tách động_mạch chủ ngực .",
        "entities": [
            {
                "word": "đau tức ngực",
                "type": "SYMPTOM"
            },
            {
                "word": "bóc tách động_mạch chủ ngực",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_693",
        "text": "Nhằm chẩn_đoán chính_xác bệnh_lý viêm cầu thận mạn , bác_sĩ chỉ_định thực_hiện_sinh_thiết thận dưới hướng_dẫn siêu_âm .",
        "entities": [
            {
                "word": "viêm cầu thận mạn",
                "type": "DISEASE"
            },
            {
                "word": "sinh_thiết thận",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_694",
        "text": "Kê đơn phối_hợp thuốc Montelukast nhằm kiểm_soát triệu_chứng khó thở về đêm ở bệnh_nhân hen .",
        "entities": [
            {
                "word": "Montelukast",
                "type": "DRUG"
            },
            {
                "word": "khó thở",
                "type": "SYMPTOM"
            }
        ],
        "relation": "PRESCRIBED_FOR"
    },
    {
        "sample_id": "aug_695",
        "text": "Có chỉ_định khẩn_cấp phẫu_thuật lấy thai cấp_cứu do rau tiền_đạo trung_tâm chảy máu ồ_ạt .",
        "entities": [
            {
                "word": "rau tiền_đạo",
                "type": "DISEASE"
            },
            {
                "word": "phẫu_thuật lấy thai",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_696",
        "text": "Bệnh_nhân mắc chứng tăng nhãn áp ác_tính và được chỉ_định phẫu_thuật cắt bè củng mạc .",
        "entities": [
            {
                "word": "tăng nhãn áp",
                "type": "DISEASE"
            },
            {
                "word": "phẫu_thuật cắt bè củng mạc",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_697",
        "text": "Thuốc Allopurinol được kê đơn điều_trị bệnh gút mạn tính nhằm hạ nồng_độ axit uric máu .",
        "entities": [
            {
                "word": "Allopurinol",
                "type": "DRUG"
            },
            {
                "word": "gút mạn tính",
                "type": "DISEASE"
            }
        ],
        "relation": "TREATS"
    },
    {
        "sample_id": "aug_698",
        "text": "Do nghi_ngờ áp - xe phổi thùy dưới , bệnh_nhân được chỉ_định chụp cắt_lớp vi_tính lồng_ngực có tiêm thuốc cản_quang .",
        "entities": [
            {
                "word": "áp - xe phổi",
                "type": "DISEASE"
            },
            {
                "word": "chụp cắt_lớp vi_tính lồng_ngực",
                "type": "PROCEDURE"
            }
        ],
        "relation": "PERFORMED_FOR"
    },
    {
        "sample_id": "aug_699",
        "text": "Bệnh_nhân bị rụng tóc từng mảng do bệnh_lý tự miễn viêm tuyến_giáp Hashimoto .",
        "entities": [
            {
                "word": "rụng tóc",
                "type": "SYMPTOM"
            },
            {
                "word": "viêm tuyến_giáp Hashimoto",
                "type": "DISEASE"
            }
        ],
        "relation": "CAUSES"
    },
    {
        "sample_id": "aug_700",
        "text": "Tuyệt_đối chống chỉ_định dùng thuốc kháng_viêm NSAIDs khi người_bệnh bị suy tim độ IV.",
        "entities": [
            {
                "word": "NSAIDs",
                "type": "DRUG"
            },
            {
                "word": "suy tim",
                "type": "DISEASE"
            }
        ],
        "relation": "CONTRAINDICATED_FOR"
    }
]
