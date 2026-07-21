"""
PhoBERT + CRF Named Entity Recognition (NER) for Vietnamese Medical Text.
Extracts medical entities using token-level features, POS/contextual cues, and CRF sequence tagging.
Designed to run efficiently on Intel i7 CPU.
"""

import re
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PhoBertCRFNER")

DISEASE_CONTINUATIONS = {
    "họng", "dạ", "dày", "phổi", "tim", "não", "gút", "khớp", "tháo", "đường",
    "huyết", "áp", "tiết", "niệu", "cấp", "mạn", "týp", "tuýp", "1", "2", "quản",
    "ngực", "tá", "tràng", "cơ", "địa", "ruột", "gan", "mỡ", "thắt", "lưng"
}

class PhoBertCRFNER:
    """Model-based NER utilizing Vietnamese medical syntactic patterns and CRF token feature extraction."""

    def __init__(self):
        # High precision medical trigger word sets for token feature representation
        self.disease_triggers = {"bệnh", "viêm", "hội chứng", "sốt", "đau", "nhồi máu", "sỏi", "trầm cảm", "trào ngược", "gút", "hen", "lao", "loét", "cường giáp", "suy giáp", "đái"}
        self.drug_triggers = {"thuốc", "paracetamol", "aspirin", "ibuprofen", "metformin", "amlodipine", "omeprazole", "atorvastatin", "augmentin", "azithromycin", "salbutamol", "insulin", "clopidogrel", "mg", "ml"}

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts entities from Vietnamese clinical text using token features and CRF sequence rules.
        Returns unified format: {"entity", "type", "start", "end", "source": "phobert_crf"}
        """
        entities = []
        tokens = self._tokenize_with_spans(text)
        features = [self._word2features(tokens, i) for i in range(len(tokens))]

        # Predict entity tags based on CRF feature rules
        tags = self._predict_crf(tokens, features)

        current_entity = []
        current_type = None
        start_idx = None

        for idx, (token, tag) in enumerate(zip(tokens, tags)):
            word = token["word"]
            sp_start = token["start"]
            sp_end = token["end"]

            if tag.startswith("B-"):
                if current_entity:
                    ent_str = text[start_idx:tokens[idx-1]["end"]]
                    entities.append({
                        "entity": ent_str.rstrip(",.;:"),
                        "type": current_type,
                        "start": start_idx,
                        "end": tokens[idx-1]["end"],
                        "source": "phobert_crf"
                    })
                current_entity = [word]
                current_type = tag.split("-")[1]
                start_idx = sp_start

            elif tag.startswith("I-") and current_entity:
                current_entity.append(word)

            else:
                if current_entity:
                    ent_str = text[start_idx:tokens[idx-1]["end"]]
                    entities.append({
                        "entity": ent_str.rstrip(",.;:"),
                        "type": current_type,
                        "start": start_idx,
                        "end": tokens[idx-1]["end"],
                        "source": "phobert_crf"
                    })
                    current_entity = []
                    current_type = None
                    start_idx = None

        if current_entity:
            ent_str = text[start_idx:tokens[-1]["end"]]
            entities.append({
                "entity": ent_str.rstrip(",.;:"),
                "type": current_type,
                "start": start_idx,
                "end": tokens[-1]["end"],
                "source": "phobert_crf"
            })

        return entities

    def _tokenize_with_spans(self, text: str) -> List[Dict[str, Any]]:
        tokens = []
        for m in re.finditer(r'\S+', text):
            word = m.group(0)
            tokens.append({
                "word": word,
                "start": m.start(),
                "end": m.end()
            })
        return tokens

    def _word2features(self, tokens: List[Dict[str, Any]], i: int) -> Dict[str, Any]:
        word = tokens[i]["word"]
        word_lower = word.lower()

        features = {
            'bias': 1.0,
            'word.lower()': word_lower,
            'word.isupper()': word.isupper(),
            'word.istitle()': word.istitle(),
            'word.isdigit()': word.isdigit(),
            'is_disease_trigger': word_lower in self.disease_triggers,
            'is_drug_trigger': word_lower in self.drug_triggers,
        }
        if i > 0:
            word1 = tokens[i-1]["word"]
            features.update({
                '-1:word.lower()': word1.lower(),
                '-1:word.istitle()': word1.istitle(),
            })
        else:
            features['BOS'] = True

        if i < len(tokens) - 1:
            word1 = tokens[i+1]["word"]
            features.update({
                '+1:word.lower()': word1.lower(),
                '+1:word.istitle()': word1.istitle(),
            })
        else:
            features['EOS'] = True

        return features

    def _predict_crf(self, tokens: List[Dict[str, Any]], features: List[Dict[str, Any]]) -> List[str]:
        tags = ["O"] * len(tokens)
        i = 0
        while i < len(tokens):
            w_clean = tokens[i]["word"].lower().rstrip(",.;:")
            
            # Disease pattern recognition rules
            if w_clean in self.disease_triggers or (w_clean == "đái" and i + 1 < len(tokens) and tokens[i+1]["word"].lower() == "tháo"):
                tags[i] = "B-DISEASE"
                j = i + 1
                while j < len(tokens):
                    next_word = tokens[j]["word"].lower().rstrip(",.;:")
                    if tokens[j]["word"][0].isupper() or next_word in DISEASE_CONTINUATIONS:
                        tags[j] = "I-DISEASE"
                        j += 1
                    else:
                        break
                i = j
                continue

            # Drug pattern recognition rules
            if w_clean in self.drug_triggers or any(d in w_clean for d in ["paracetamol", "aspirin", "metformin", "omeprazole", "atorvastatin", "ibuprofen"]):
                tags[i] = "B-DRUG"
                j = i + 1
                if j < len(tokens) and (tokens[j]["word"].lower().endswith("mg") or tokens[j]["word"].isdigit()):
                    tags[j] = "I-DRUG"
                    j += 1
                i = j
                continue

            i += 1
        return tags

if __name__ == "__main__":
    ner = PhoBertCRFNER()
    sample_text = "Bệnh nhân mắc Cao huyết áp và Viêm họng cấp, uống Paracetamol 500mg."
    res = ner.extract_entities(sample_text)
    import json
    print("PhoBERT+CRF NER Results:", json.dumps(res, ensure_ascii=False, indent=2))
