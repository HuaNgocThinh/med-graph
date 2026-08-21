# File dữ liệu tự động sinh ra từ script Augmentation

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
    }
]
