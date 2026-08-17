import json
import random
from collections import Counter
from typing import Dict, List, Any

def check_offsets(item):
    s = item['sentence']
    e1 = item['e1']
    e2 = item['e2']
    s1 = s.find(e1)
    e1_end = s1 + len(e1) if s1 != -1 else -1
    s2 = s.find(e2)
    e2_end = s2 + len(e2) if s2 != -1 else -1
    assert s1 != -1 and s2 != -1, f"Entity not found in sentence: {item}"
    return {
        "sample_id": item['sample_id'],
        "sentence": s,
        "entity_1": {"text": e1, "label": item['l1'], "start": s1, "end": e1_end},
        "entity_2": {"text": e2, "label": item['l2'], "start": s2, "end": e2_end},
        "relation": item['relation'],
        "confidence": item['confidence'],
        "negated": item['negated'],
        "temporal": item['temporal'],
        "head_surface": e1,
        "tail_surface": e2,
        "augmented": True,
        "augment_source": "gemini_paraphrase"
    }

def build_augmented_records():
    contra_aug = [
        {'sample_id': 'syn_003_aug1', 'sentence': 'Bệnh nhân Viêm loét dạ dày tuyệt đối không được dùng Ibuprofen để tránh tổn thương niêm mạc.', 'e1': 'Ibuprofen', 'l1': 'DRUG', 'e2': 'Viêm loét dạ dày', 'l2': 'DISEASE', 'relation': 'CONTRAINDICATED_FOR', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_003_aug2', 'sentence': 'Khi người bệnh bị Viêm loét dạ dày, bác sĩ khuyến cáo tránh dùng Ibuprofen trong quá trình điều trị.', 'e1': 'Ibuprofen', 'l1': 'DRUG', 'e2': 'Viêm loét dạ dày', 'l2': 'DISEASE', 'relation': 'CONTRAINDICATED_FOR', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_003_aug3', 'sentence': 'Đối với bệnh nhân Viêm loét dạ dày, thuốc Ibuprofen là chống chỉ định tuyệt đối.', 'e1': 'Ibuprofen', 'l1': 'DRUG', 'e2': 'Viêm loét dạ dày', 'l2': 'DISEASE', 'relation': 'CONTRAINDICATED_FOR', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_003_aug4', 'sentence': 'Thuốc Ibuprofen có thể gây nguy hiểm khi dùng cùng cho người đang mắc Viêm loét dạ dày.', 'e1': 'Ibuprofen', 'l1': 'DRUG', 'e2': 'Viêm loét dạ dày', 'l2': 'DISEASE', 'relation': 'CONTRAINDICATED_FOR', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_003_aug5', 'sentence': 'Bệnh nhân có tiền sử trào ngược dạ dày không được dùng Ibuprofen vì nguy cơ kích ứng.', 'e1': 'Ibuprofen', 'l1': 'DRUG', 'e2': 'trào ngược dạ dày', 'l2': 'DISEASE', 'relation': 'CONTRAINDICATED_FOR', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_003_aug6', 'sentence': 'Việc sử dụng Ibuprofen bị chống chỉ định ở những người mắc trào ngược dạ dày.', 'e1': 'Ibuprofen', 'l1': 'DRUG', 'e2': 'trào ngược dạ dày', 'l2': 'DISEASE', 'relation': 'CONTRAINDICATED_FOR', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_003_aug7', 'sentence': 'Không nên sử dụng Ibuprofen cho bệnh nhân đang điều trị trào ngược dạ dày.', 'e1': 'Ibuprofen', 'l1': 'DRUG', 'e2': 'trào ngược dạ dày', 'l2': 'DISEASE', 'relation': 'CONTRAINDICATED_FOR', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_003_aug8', 'sentence': 'Chỉ định Ibuprofen không được khuyến cáo đối với tình trạng trào ngược dạ dày.', 'e1': 'Ibuprofen', 'l1': 'DRUG', 'e2': 'trào ngược dạ dày', 'l2': 'DISEASE', 'relation': 'CONTRAINDICATED_FOR', 'confidence': 0.95, 'negated': False, 'temporal': 'present'}
    ]

    causes_aug = [
        {'sample_id': 'syn_065_aug1', 'sentence': 'Bệnh lý Viêm gan vi-rút B mạn là nguyên nhân chính dẫn đến triệu chứng vàng da ở người bệnh.', 'e1': 'Viêm gan vi-rút B mạn', 'l1': 'DISEASE', 'e2': 'vàng da', 'l2': 'SYMPTOM', 'relation': 'CAUSES', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_065_aug2', 'sentence': 'Tình trạng Viêm gan vi-rút B mạn làm xuất hiện dấu hiệu vàng da trên lâm sàng.', 'e1': 'Viêm gan vi-rút B mạn', 'l1': 'DISEASE', 'e2': 'vàng da', 'l2': 'SYMPTOM', 'relation': 'CAUSES', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        # Fixed sentence #3: single tail entity 'vàng da'
        {'sample_id': 'syn_065_aug3', 'sentence': 'Tổn thương gan do Viêm gan vi-rút B mạn có thể gây ra biểu hiện vàng da rõ rệt.', 'e1': 'Viêm gan vi-rút B mạn', 'l1': 'DISEASE', 'e2': 'vàng da', 'l2': 'SYMPTOM', 'relation': 'CAUSES', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_065_aug4', 'sentence': 'Bệnh nhân mắc Viêm gan vi-rút B mạn thường tiến triển dẫn tới biểu hiện vàng da toàn thân.', 'e1': 'Viêm gan vi-rút B mạn', 'l1': 'DISEASE', 'e2': 'vàng da', 'l2': 'SYMPTOM', 'relation': 'CAUSES', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_087_aug1', 'sentence': 'Tổn thương niêm mạc do Viêm loét dạ dày trực tiếp gây ra cơn đau thượng vị dữ dội.', 'e1': 'Viêm loét dạ dày', 'l1': 'DISEASE', 'e2': 'đau thượng vị', 'l2': 'SYMPTOM', 'relation': 'CAUSES', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_087_aug2', 'sentence': 'Bệnh lý Viêm loét dạ dày là nguyên nhân của những đợt đau thượng vị kéo dài.', 'e1': 'Viêm loét dạ dày', 'l1': 'DISEASE', 'e2': 'đau thượng vị', 'l2': 'SYMPTOM', 'relation': 'CAUSES', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_087_aug3', 'sentence': 'Diễn biến của Viêm loét dạ dày thường làm xuất hiện triệu chứng đau thượng vị từng cơn.', 'e1': 'Viêm loét dạ dày', 'l1': 'DISEASE', 'e2': 'đau thượng vị', 'l2': 'SYMPTOM', 'relation': 'CAUSES', 'confidence': 0.95, 'negated': False, 'temporal': 'present'},
        {'sample_id': 'syn_087_aug4', 'sentence': 'Đợt cấp của Viêm loét dạ dày có thể gây biến chứng đau thượng vị nhiều về đêm.', 'e1': 'Viêm loét dạ dày', 'l1': 'DISEASE', 'e2': 'đau thượng vị', 'l2': 'SYMPTOM', 'relation': 'CAUSES', 'confidence': 0.95, 'negated': False, 'temporal': 'present'}
    ]

    aug_records = [check_offsets(x) for x in contra_aug] + [check_offsets(x) for x in causes_aug]
    return aug_records

def main():
    # Load base un-augmented records first to prevent compounding duplicates
    with open('data/student_training/re_pseudo_labels.json', 'r', encoding='utf-8') as f:
        existing_records = json.load(f)

    # Filter out any prior augmented records to cleanly overwrite with updated paraphrases
    base_records = [r for r in existing_records if not r.get('augmented', False)]
    for r in base_records:
        r['augmented'] = False

    aug_records = build_augmented_records()
    all_records = base_records + aug_records

    # Save updated re_pseudo_labels.json
    with open('data/student_training/re_pseudo_labels.json', 'w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)

    # Calculate post-augmentation statistics
    counts = Counter([r['relation'] for r in all_records])
    max_c = max(counts.values())
    min_c = min(counts.values())
    new_imbalance = max_c / min_c if min_c > 0 else 0

    print("="*60)
    print("STEP 2f-B: POST-AUGMENTATION STATISTICS")
    print("="*60)
    print(f"Total RE Records (Base + 16 Augmented): {len(all_records)}")
    print("Label Distribution:")
    for rel, cnt in counts.most_common():
        pct = (cnt / len(all_records)) * 100
        print(f"  - {rel:<20}: {cnt:>3} ({pct:>5.1f}%)")
    print(f"\nNew Imbalance Ratio (Max/Min): {max_c} / {min_c} = {new_imbalance:.2f}")

    # Partition sample_ids (96 original synthetic samples) into 70 / 15 / 15
    with open('data/student_training/ner_pseudo_labels.json', 'r', encoding='utf-8') as f:
        ner_data = json.load(f)

    all_sids = [s['sample_id'] for s in ner_data] # syn_001 to syn_096
    
    # Fixed split assignment for appendectomy duplicate group:
    fixed_assignment = {
        'syn_005': 'train',
        'syn_069': 'train',
        'syn_088': 'train',
        'syn_092': 'dev',
        'syn_095': 'test'
    }

    remaining_sids = [s for s in all_sids if s not in fixed_assignment]

    random.seed(42)
    random.shuffle(remaining_sids)

    train_needed = 67 - 3 # 64
    dev_needed = 14 - 1   # 13
    test_needed = 15 - 1  # 14

    train_sids = set(remaining_sids[:train_needed])
    train_sids.update(['syn_005', 'syn_069', 'syn_088'])

    dev_sids = set(remaining_sids[train_needed:train_needed + dev_needed])
    dev_sids.update(['syn_092'])

    test_sids = set(remaining_sids[train_needed + dev_needed:])
    test_sids.update(['syn_095'])

    print("\nSample ID Split Counts:")
    print(f"  - Train samples: {len(train_sids)}")
    print(f"  - Dev samples  : {len(dev_sids)}")
    print(f"  - Test samples : {len(test_sids)}")

    # Verify zero leakage
    assert len(train_sids.intersection(dev_sids)) == 0
    assert len(train_sids.intersection(test_sids)) == 0
    assert len(dev_sids.intersection(test_sids)) == 0
    print("✓ Zero sample_id overlap between splits confirmed.")

    # Assign RE records to splits
    re_train = []
    re_dev = []
    re_test = []

    for r in all_records:
        sid = r['sample_id']
        is_aug = r.get('augmented', False)

        bert_input = f"[E1] {r['entity_1']['text']} [/E1] {r['sentence']} [E2] {r['entity_2']['text']} [/E2]"
        
        formatted_item = {
            "input": bert_input,
            "label": r['relation'],
            "sample_id": sid,
            "augmented": is_aug,
            "confidence": r['confidence'],
            "entity_1": r['entity_1'],
            "entity_2": r['entity_2']
        }

        if is_aug:
            re_train.append(formatted_item)
        else:
            if sid in train_sids:
                re_train.append(formatted_item)
            elif sid in dev_sids:
                re_dev.append(formatted_item)
            elif sid in test_sids:
                re_test.append(formatted_item)

    # Check augmented constraint in dev and test
    dev_aug_count = sum(1 for x in re_dev if x['augmented'])
    test_aug_count = sum(1 for x in re_test if x['augmented'])
    assert dev_aug_count == 0 and test_aug_count == 0, "Augmented records found in dev/test!"
    print("✓ Dev and Test contain ZERO augmented records.")

    # Save to data/student_training/re_train.json, re_dev.json, re_test.json
    with open('data/student_training/re_train.json', 'w', encoding='utf-8') as f:
        json.dump(re_train, f, ensure_ascii=False, indent=2)
    with open('data/student_training/re_dev.json', 'w', encoding='utf-8') as f:
        json.dump(re_dev, f, ensure_ascii=False, indent=2)
    with open('data/student_training/re_test.json', 'w', encoding='utf-8') as f:
        json.dump(re_test, f, ensure_ascii=False, indent=2)

    print("\nRE Split Distribution:")
    print(f"  - Train records: {len(re_train)} ({(len(re_train)/len(all_records))*100:.1f}%)")
    print(f"  - Dev records  : {len(re_dev)} ({(len(re_dev)/len(all_records))*100:.1f}%)")
    print(f"  - Test records : {len(re_test)} ({(len(re_test)/len(all_records))*100:.1f}%)")

    print("\nTrain Label Breakdown:", Counter([x['label'] for x in re_train]))
    print("Dev Label Breakdown  :", Counter([x['label'] for x in re_dev]))
    print("Test Label Breakdown :", Counter([x['label'] for x in re_test]))

    split_assignment = {}
    for s in train_sids: split_assignment[s] = 'train'
    for s in dev_sids: split_assignment[s] = 'dev'
    for s in test_sids: split_assignment[s] = 'test'

    with open('scratch/sample_split_assignment.json', 'w', encoding='utf-8') as f:
        json.dump(split_assignment, f, indent=2)

if __name__ == "__main__":
    main()
