"""
Targeted Knowledge Graph Data Expansion Loop for MedGraph-VI.
Iteratively analyzes coverage gaps, calls LLM to generate targeted clinical text,
processes it through the NLP pipeline, and measures progress.
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Ensure UTF-8 output encoding for Windows terminal printing
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.llm_client import LLMClient
from evaluation.coverage_analysis import get_coverage_gaps

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CoverageLoop")

SYNTHETIC_PATH = BASE_DIR / "data" / "synthetic" / "synthetic_data.json"

def get_next_syn_id() -> int:
    if not SYNTHETIC_PATH.exists():
        return 1
    try:
        with open(SYNTHETIC_PATH, "r", encoding="utf-8") as f:
            samples = json.load(f)
            if not samples:
                return 1
            # Parse IDs like 'syn_050' -> 50
            ids = []
            for s in samples:
                sid = s.get("id", "")
                match = re.match(r'syn_(\d+)', sid)
                if match:
                    ids.append(int(match.group(1)))
            return max(ids) + 1 if ids else len(samples) + 1
    except Exception:
        return 1

import re

def expand_coverage():
    logger.info("=== STARTING TARGETED KNOWLEDGE GRAPH COVERAGE EXPANSION LOOP ===")
    
    llm_client = LLMClient()
    if llm_client.provider == "mock":
        logger.warning("⚠️ Running in Mock LLM mode. Targeted text generation will use template text.")

    max_rounds = 5
    round_num = 1

    while round_num <= max_rounds:
        print(f"\n--- 🔄 LOOP ROUND {round_num}/{max_rounds} ---")
        
        # Step 1: Run Coverage Analysis and get gaps
        gaps = get_coverage_gaps()
        gap_count = len(gaps)
        
        if gap_count == 0:
            print("🎉 SUCCESS: Zero coverage gaps remaining in the Knowledge Graph! Terminating loop.")
            break
            
        print(f"Current Gaps remaining: {gap_count}. Sorting and selecting top unique targets...")

        # Step 2: Prioritize diseases with lowest degree first, then drugs
        # Group and deduplicate to avoid generating multiple texts for the same entity in a single round
        seen_targets = set()
        target_gaps = []
        for gap in sorted(gaps, key=lambda x: x.get("degree", 0)):
            name = gap["entity_name"]
            if name not in seen_targets:
                seen_targets.add(name)
                target_gaps.append(gap)
                if len(target_gaps) >= 15:
                    break

        print(f"Targeting {len(target_gaps)} unique entities in this round: {[g['entity_name'] for g in target_gaps]}")

        # Load existing synthetic dataset
        if SYNTHETIC_PATH.exists():
            with open(SYNTHETIC_PATH, "r", encoding="utf-8") as f:
                samples = json.load(f)
        else:
            samples = []

        new_samples_added = 0
        next_id = get_next_syn_id()

        for gap in target_gaps:
            entity_name = gap["entity_name"]
            entity_type = gap["entity_type"]
            missing_rel = gap["missing_relation_type"]

            print(f"Generating clinical sample for {entity_type} '{entity_name}' (missing: {missing_rel})")

            # Generate prompt based on type
            if entity_type == "DISEASE":
                prompt = f"""Bạn là một bác sĩ chuyên khoa viết bệnh án mẫu.
Hãy viết một đoạn bệnh án tiếng Việt cực kỳ ngắn gọn, súc tích (khoảng 2-3 câu) mô tả một ca lâm sàng thực tế.
YÊU CẦU BẮT BUỘC:
1. Phải bao gồm đầy đủ và chính xác tên bệnh: '{entity_name}'.
2. Mô tả ít nhất 2 triệu chứng lâm sàng cụ thể của bệnh này.
3. Kê đơn ít nhất 1 loại thuốc (kèm hàm lượng/liều dùng) cho bệnh nhân này với mục đích điều trị rõ ràng.

Ví dụ: "Bệnh nhân nam 54 tuổi, chẩn đoán xác định {entity_name}. Triệu chứng lâm sàng gồm triệu_chứng_1 và triệu_chứng_2. Bác sĩ chỉ định dùng thuốc_A để điều trị."

Đoạn bệnh án mẫu:"""
            else:
                prompt = f"""Bạn là một bác sĩ chuyên khoa viết bệnh án mẫu.
Hãy viết một đoạn bệnh án tiếng Việt cực kỳ ngắn gọn, súc tích (khoảng 2-3 câu) mô tả một ca lâm sàng thực tế.
YÊU CẦU BẮT BUỘC:
1. Phải bao gồm đầy đủ và chính xác tên thuốc: '{entity_name}'.
2. Chỉ định rõ ràng thuốc này được kê cho bệnh nhân mắc bệnh gì (hoặc dùng để giảm triệu chứng cụ thể nào).

Ví dụ: "Bệnh nhân nam 35 tuổi, chẩn đoán suy tim. Đang điều trị bằng {entity_name} 10mg hằng ngày để kiểm soát triệu chứng."

Đoạn bệnh án mẫu:"""

            try:
                if llm_client.provider != "mock":
                    generated_text = llm_client.generate(prompt, temperature=0.3).strip()
                else:
                    # Mock Fallback template
                    if entity_type == "DISEASE":
                        generated_text = f"Bệnh nhân khám vì nghi ngờ {entity_name}. Triệu chứng gồm mệt mỏi và sốt. Kê đơn Paracetamol 500mg để giảm sốt."
                    else:
                        generated_text = f"Bệnh nhân được chẩn đoán Viêm loét dạ dày tá tràng. Bác sĩ kê {entity_name} uống trước ăn để điều trị."

                # Verify generation is not empty or too short
                if len(generated_text) > 20:
                    new_id = f"syn_{next_id:03d}"
                    samples.append({
                        "id": new_id,
                        "template_type": "targeted_gap_fill",
                        "text": generated_text
                    })
                    print(f"   ► Successfully generated new sample {new_id}: '{generated_text}'")
                    next_id += 1
                    new_samples_added += 1
                else:
                    logger.warning(f"Generated text for '{entity_name}' was too short. Skipping.")
            except Exception as e:
                logger.error(f"Error generating text for '{entity_name}': {e}")

        if new_samples_added == 0:
            print("No new samples generated. Breaking loop.")
            break

        # Save synthetic data
        SYNTHETIC_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SYNTHETIC_PATH, "w", encoding="utf-8") as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)

        print(f"Saved {new_samples_added} new targeted clinical samples to synthetic dataset.")

        # Step 3: Run pipeline for the new batch of samples
        print("🚀 Executing NLP Pipeline on newly added samples...")
        try:
            # We run run_pipeline.py with batch-size = new_samples_added so it processes exactly these new samples
            subprocess.run(["python", "run_pipeline.py", "--batch-size", str(new_samples_added)], check=True)
            
            print("🧹 Running CSV cleaning script...")
            subprocess.run(["python", "scripts/clean_all_relationships.py"], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Pipeline or cleaner command failed: {e}")
            break

        # Step 4: Run Coverage Analysis again to log progress
        new_gaps = get_coverage_gaps()
        new_gap_count = len(new_gaps)
        
        print(f"📊 Vòng {round_num}: {gap_count} gap -> còn {new_gap_count} gap sau khi thêm {new_samples_added} mẫu mới.")
        
        round_num += 1

    print("\n=======================================================")
    print("🏁 AUTOMATED TARGETED COVERAGE LOOP COMPLETE")
    print(f"   ► Total Loop Rounds Run: {round_num - 1}")
    print("=======================================================\n")

if __name__ == "__main__":
    expand_coverage()
