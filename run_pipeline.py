"""
End-to-End Pipeline Launcher for MedGraph-VI.
Executes Stages A through H sequentially with batch processing, progress tracking, and transparent logging.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Ensure UTF-8 output encoding for Windows terminal printing
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.config import DATA_DIR, SYNTHETIC_DATA_DIR
from src.llm_client import LLMClient
from src.data_generation.synthetic_generator import SyntheticDataGenerator
from src.ner.ner_ensemble import NEREnsemble
from src.negation_temporal.context_processor import ConTextProcessor
from src.relation_extraction.llm_re import LLMRelationExtractor
from src.relation_extraction.rule_based_re import RuleBasedRelationExtractor
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.rxnorm_linker import RxNormLinker
from src.graph.neo4j_client import Neo4jClient
from src.graph.graph_builder import GraphBuilder
from src.graph.graph_cleaner import GraphCleaner
from src.qa.qa_engine import QAEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MedGraphPipeline")

PROGRESS_FILE = DATA_DIR / ".progress.json"

def load_progress() -> set:
    """Loads set of processed sample IDs from progress file."""
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("processed_ids", []))
        except Exception:
            pass
    return set()

def save_progress(processed_ids: set):
    """Saves set of processed sample IDs to progress file."""
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump({"processed_ids": list(processed_ids)}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Could not save progress file: {e}")

def run_end_to_end_pipeline(batch_size: int = 5, total_samples: int = 10, reset_progress: bool = False):
    logger.info("=== STARTING MEDGRAPH-VI END-TO-END PIPELINE ===")

    if reset_progress and PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()
        logger.info("Reset progress file '.progress.json'. Starting fresh.")

    processed_ids = load_progress()

    # Initialize LLMClient & Connection validation step
    llm_client = LLMClient()
    connected = llm_client.validate_connection()

    if not connected:
        if llm_client.provider != "mock":
            logger.error("❌ Stopping pipeline because LLM connection validation failed.")
            sys.exit(1)
        else:
            logger.info("Operating in Mock mode for pipeline execution.")

    # STAGE A: Load or Generate Synthetic Vietnamese Medical Dataset
    logger.info("[STAGE A] Loading or Generating Synthetic Vietnamese Medical Dataset...")
    generator = SyntheticDataGenerator(llm_client=llm_client)
    
    synthetic_file = SYNTHETIC_DATA_DIR / "synthetic_data.json"
    all_samples = []
    if synthetic_file.exists():
        try:
            with open(synthetic_file, "r", encoding="utf-8") as f:
                all_samples = json.load(f)
            logger.info(f"Loaded {len(all_samples)} existing synthetic samples from '{synthetic_file}'")
        except Exception:
            all_samples = []

    if len(all_samples) < total_samples:
        needed = total_samples - len(all_samples)
        new_samples = generator.generate_batch(num_samples=needed)
        all_samples.extend(new_samples)

    # Re-index all samples sequentially to guarantee 100% unique IDs across entire dataset
    for idx, sample in enumerate(all_samples):
        sample["id"] = f"syn_{idx+1:03d}"
    generator.save_to_file(all_samples)

    # Filter out samples already processed
    all_sample_ids = [s["id"] for s in all_samples]
    completed_ids = [sid for sid in all_sample_ids if sid in processed_ids]
    unprocessed = [s for s in all_samples if s["id"] not in processed_ids]
    remaining_ids = [s["id"] for s in unprocessed]

    logger.info(f"📊 Progress Status: Total={len(all_samples)} samples | Completed={len(completed_ids)} | Remaining={len(unprocessed)}")
    logger.info(f"   ► Completed Sample IDs ({len(completed_ids)}): {completed_ids}")
    logger.info(f"   ► Remaining Sample IDs ({len(remaining_ids)}): {remaining_ids}")

    if not unprocessed:
        logger.info("🎉 All samples in dataset have already been processed! Skipping NLP pipeline stages.")
        current_batch = []
    else:
        current_batch = unprocessed[:batch_size]
        logger.info(f"🚀 Processing current batch of {len(current_batch)} sample(s) (Batch size limit: {batch_size})...")

    # Initialize NLP Modules
    ner_ensemble = NEREnsemble(llm_client=llm_client)
    context_proc = ConTextProcessor()
    llm_re = LLMRelationExtractor(llm_client=llm_client)
    rule_re = RuleBasedRelationExtractor()
    icd_linker = ICD10Linker()
    rx_linker = RxNormLinker()
    graph_builder = GraphBuilder()
    graph_cleaner = GraphCleaner()

    all_triples_with_metadata = []

    # Process each clinical sample in current batch
    for idx, sample in enumerate(current_batch):
        sample_id = sample["id"]
        text = sample["text"]
        logger.info(f"\n--- Processing Sample {idx+1}/{len(current_batch)} (ID: {sample_id}) ---")
        logger.info(f"Text: '{text}'")

        # STAGE B: 3-Source NER & Ensemble
        entities = ner_ensemble.extract_entities(text)
        logger.info(f"[STAGE B] NER Ensemble extracted {len(entities)} entities.")

        # STAGE C: ConText Negation & Temporal Scope
        processed_entities = context_proc.process_entities(text, entities)
        logger.info(f"[STAGE C] ConText tagged negation & temporal contexts.")

        # STAGE D: Relation Extraction (LLM + Baseline Rule-based)
        llm_triples = llm_re.extract_relations(text, processed_entities)
        rule_triples = rule_re.extract_relations(text, processed_entities)
        logger.info(f"[STAGE D] Extracted {len(llm_triples)} LLM triples and {len(rule_triples)} Rule-based baseline triples.")

        # Combine LLM and Rule-based triples
        extracted_triples = llm_triples + [r for r in rule_triples if r not in llm_triples]

        # STAGE E: Entity Linking (ICD-10 + RxNorm/RxNav API + Fuzzy)
        sample_triples = []
        for triple in extracted_triples:
            head_str = triple["head"]
            tail_str = triple["tail"]

            head_type = next((e["type"] for e in processed_entities if e["entity"] == head_str), "Entity")
            tail_type = next((e["type"] for e in processed_entities if e["entity"] == tail_str), "Entity")

            # Entity Linking for Head
            if head_type == "DISEASE":
                head_link = icd_linker.link_disease(head_str)
            elif head_type == "DRUG":
                head_link = rx_linker.link_drug(head_str)
            else:
                head_link = {"standard_name": head_str, "code": "UNKNOWN", "method": "unlinked"}
            head_link["type"] = head_type

            # Entity Linking for Tail
            if tail_type == "DISEASE":
                tail_link = icd_linker.link_disease(tail_str)
            elif tail_type == "DRUG":
                tail_link = rx_linker.link_drug(tail_str)
            else:
                tail_link = {"standard_name": tail_str, "code": "UNKNOWN", "method": "unlinked"}
            tail_link["type"] = tail_type

            head_ent_obj = next((e for e in processed_entities if e["entity"] == head_str), {})
            tail_ent_obj = next((e for e in processed_entities if e["entity"] == tail_str), {})
            is_negated = bool(head_ent_obj.get("negated", False) or tail_ent_obj.get("negated", False))
            
            enriched_triple = {
                "head": head_str,
                "relation": triple["relation"],
                "tail": tail_str,
                "confidence": triple["confidence"],
                "head_info": head_link,
                "tail_info": tail_link,
                "negated": is_negated,
                "temporal_context": head_ent_obj.get("temporal_context", "unknown")
            }
            sample_triples.append(enriched_triple)

        all_triples_with_metadata.extend(sample_triples)

        # STAGE F & G: Insert sample triples into Neo4j immediately
        if sample_triples:
            graph_builder.build_graph(sample_triples)

        # Update progress tracking file after each successfully processed sample
        processed_ids.add(sample_id)
        save_progress(processed_ids)
        logger.info(f"✅ Completed & saved progress for sample '{sample_id}' ({len(processed_ids)}/{len(all_samples)} total completed).")

    # STAGE F: Detect conflicts on all processed batch triples
    conflicts = graph_cleaner.detect_conflicts_in_triples(all_triples_with_metadata) if all_triples_with_metadata else []

    # STAGE H: Question Answering Demo Execution
    logger.info("\n[STAGE H] Running Text-to-Cypher Graph QA vs RAG Baseline Demo...")
    
    neo4j_client = Neo4jClient()
    if not neo4j_client.is_online():
        logger.warning(
            "\n======================================================================\n"
            "⚠️ [CẢNH BÁO CRITICAL] NEO4J DATABASE ĐANG OFFLINE!\n"
            "Neo4j chưa được khởi động (vui lòng chạy: docker-compose up -d).\n"
            "Stage H (QA Demo) sẽ gắn nhãn SIMULATED_OFFLINE và cảnh báo rõ ràng.\n"
            "======================================================================\n"
        )
    
    qa_engine = QAEngine(llm_client=llm_client)
    test_question = "Bệnh nhân Đái tháo đường týp 2 được kê thuốc gì?"
    qa_result = qa_engine.compare_answers(test_question)

    print("\n=======================================================")
    print("=== PIPELINE EXECUTION COMPLETE ===")
    print(f"Batch Processed: {len(current_batch)} sample(s)")
    print(f"Total Completed Progress: {len(processed_ids)}/{len(all_samples)}")
    print(f"Total Triples Extracted in Batch: {len(all_triples_with_metadata)}")
    print(f"Detected Conflicts Logged: {len(conflicts)}")
    print(f"\n{llm_client.get_stats_summary()}")
    print("\n--- SAMPLE QA DEMO OUTPUT ---")
    print(json.dumps(qa_result, ensure_ascii=False, indent=2))
    print("=======================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MedGraph-VI End-to-End Pipeline Launcher")
    parser.add_argument("--batch-size", "-b", type=int, default=5, help="Number of samples to process in this batch (default: 5)")
    parser.add_argument("--total-samples", "-n", type=int, default=10, help="Total synthetic samples in dataset (default: 10)")
    parser.add_argument("--reset-progress", action="store_true", help="Reset progress tracker and start from scratch")
    args = parser.parse_args()

    run_end_to_end_pipeline(batch_size=args.batch_size, total_samples=args.total_samples, reset_progress=args.reset_progress)
