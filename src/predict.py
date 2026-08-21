import os
import sys
from pathlib import Path
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification

# ==========================================
# 1. CẤU HÌNH ĐƯỜNG DẪN & NHÃN
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
NER_MODEL_PATH = BASE_DIR / "models" / "ner_best.pt"
RE_MODEL_PATH = BASE_DIR / "models" / "re_best.pt"
BASE_MODEL = "vinai/phobert-base-v2"

NER_LABELS = [
    "B-DISEASE", "B-DRUG", "B-PROCEDURE", "B-SYMPTOM", 
    "I-DISEASE", "I-DRUG", "I-PROCEDURE", "I-SYMPTOM", "O"
]
RE_LABELS = ["CAUSES", "CONTRAINDICATED_FOR", "HAS_SYMPTOM", "NONE", "PERFORMED_FOR", "PRESCRIBED_FOR", "TREATS"]

# ==========================================
# 2. KHỞI TẠO MÔ HÌNH
# ==========================================
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, clean_up_tokenization_spaces=True)
special_tokens = ["[E1]", "[/E1]", "[E2]", "[/E2]"]
tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})

ner_model = AutoModelForTokenClassification.from_pretrained(BASE_MODEL, num_labels=len(NER_LABELS))
id2label = {i: label for i, label in enumerate(NER_LABELS)}
ner_model.load_state_dict(torch.load(NER_MODEL_PATH, map_location="cpu"))
ner_model.eval()

re_model = AutoModelForSequenceClassification.from_pretrained(BASE_MODEL, num_labels=len(RE_LABELS))
re_model.resize_token_embeddings(len(tokenizer))
re_model.load_state_dict(torch.load(RE_MODEL_PATH, map_location="cpu"))
re_model.eval()

# ==========================================
# 3. HÀM TRÍCH XUẤT THÔNG MINH
# ==========================================
def extract_medical_info(text: str):
    # --- BƯỚC 1: NHẬN DIỆN THỰC THỂ (NER) ---
    inputs = tokenizer(text, return_tensors="pt")
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    
    with torch.no_grad():
        outputs = ner_model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=-1)[0].numpy()
        
    words_labels = []
    curr_word, curr_lbl = "", None
    
    for i, token in enumerate(tokens):
        if token in ['<s>', '</s>', '<pad>']: continue
        lbl = id2label[predictions[i]]
        if token.endswith('@@'):
            curr_word += token[:-2]
            if curr_lbl is None: curr_lbl = lbl
        else:
            curr_word += token
            if curr_lbl is None: curr_lbl = lbl
            words_labels.append((curr_word, curr_lbl))
            curr_word, curr_lbl = "", None

    entities = []
    curr_ent_words, curr_ent_type = [], None

    for word, lbl in words_labels:
        if lbl == 'O':
            if curr_ent_type:
                entities.append({"word": " ".join(curr_ent_words), "type": curr_ent_type})
                curr_ent_words, curr_ent_type = [], None
        else:
            prefix, ent_type = lbl[:2], lbl[2:]
            if prefix == 'B-':
                if curr_ent_type:
                    entities.append({"word": " ".join(curr_ent_words), "type": curr_ent_type})
                curr_ent_words, curr_ent_type = [word], ent_type
            elif prefix == 'I-':
                if curr_ent_type == ent_type:
                    curr_ent_words.append(word)
                else:
                    if curr_ent_type:
                        # FIXED: Sửa lỗi chính tả biến ở đây
                        entities.append({"word": " ".join(curr_ent_words), "type": curr_ent_type})
                    curr_ent_words, curr_ent_type = [word], ent_type

    if curr_ent_type:
        entities.append({"word": " ".join(curr_ent_words), "type": curr_ent_type})

    for e in entities:
        e["word"] = e["word"].strip(".,:;() ")

    if len(entities) < 2:
        return {"text": text, "entity_1": None, "entity_2": None, "relation": "NONE", "confidence": 0.0, "marked_text": text}

    # --- BƯỚC 2: GHÉP CẶP LÂM SÀNG THÔNG MINH ---
    drugs = [e for e in entities if e['type'] in ['DRUG', 'DRUG_GROUP']]
    procs = [e for e in entities if e['type'] == 'PROCEDURE']
    diseases = [e for e in entities if e['type'] == 'DISEASE']
    symps = [e for e in entities if e['type'] == 'SYMPTOM']
    
    e1, e2 = None, None
    
    if procs and diseases:
        e1, e2 = procs[-1], diseases[-1]
    elif drugs and symps:
        e1, e2 = drugs[-1], symps[-1]
    elif drugs and diseases:
        e1, e2 = drugs[-1], diseases[-1]
    elif diseases and symps:
        e1, e2 = diseases[-1], symps[-1]
    else:
        e1, e2 = entities[0], entities[1]

    # --- BƯỚC 3: DỰ ĐOÁN QUAN HỆ (RE) ---
    marked_text = text.replace(e1["word"], f"[E1] {e1['word']} [/E1]", 1).replace(e2["word"], f"[E2] {e2['word']} [/E2]", 1)
    
    re_inputs = tokenizer(marked_text, return_tensors="pt", truncation=True, max_length=256, padding=True)
    with torch.no_grad():
        re_outputs = re_model(**re_inputs)
        probs = F.softmax(re_outputs.logits, dim=-1)
        pred_id = torch.argmax(re_outputs.logits, dim=-1).item()
        confidence = probs[0][pred_id].item()

    return {
        "text": text,
        "entity_1": {"text": e1["word"], "type": e1["type"]},
        "entity_2": {"text": e2["word"], "type": e2["type"]},
        "marked_text": marked_text,
        "relation": RE_LABELS[pred_id],
        "confidence": confidence,
    }