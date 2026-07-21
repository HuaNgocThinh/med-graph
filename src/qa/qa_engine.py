"""
Unified QA Engine comparing KG-QA (Text-to-Cypher) vs RAG Baseline side-by-side.
"""

import json
import logging
from typing import Dict, Any, Optional
from src.llm_client import LLMClient
from src.qa.text_to_cypher import TextToCypherQA
from src.qa.rag_baseline import RAGBaseline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QAEngine")

class QAEngine:
    """Orchestrator for comparing Graph QA vs Semantic RAG Baseline."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.kg_qa = TextToCypherQA(llm_client=llm_client)
        self.rag_baseline = RAGBaseline(llm_client=llm_client)

    def compare_answers(self, question: str) -> Dict[str, Any]:
        """Runs question against both KG-QA and RAG systems and formats comparative output."""
        logger.info(f"Running side-by-side comparison for question: '{question}'")
        kg_res = self.kg_qa.answer_question(question)
        rag_res = self.rag_baseline.answer_question(question)

        return {
            "question": question,
            "kg_qa": kg_res,
            "rag_baseline": rag_res
        }

if __name__ == "__main__":
    engine = QAEngine()
    comp = engine.compare_answers("Bệnh nhân Đái tháo đường týp 2 được kê thuốc gì?")
    print("Comparative QA Output:\n", json.dumps(comp, ensure_ascii=False, indent=2))
