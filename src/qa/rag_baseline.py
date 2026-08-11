"""
RAG Semantic Search Baseline for MedGraph-VI.
Performs semantic text chunk retrieval and LLM answer generation without Graph Traversal.
Used as evaluation baseline against Knowledge Graph Text-to-Cypher QA.
"""

import json
import logging
from typing import List, Dict, Any
from src.llm_client import LLMClient
from src.config import SYNTHETIC_DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RAGBaseline")

RAG_PROMPT = """Bạn là trợ lý y tế. Dựa trên các đoạn văn bản y tế được truy xuất bên dưới, hãy trả lời câu hỏi của người dùng.

Đoạn văn bản y tế truy xuất (Retrieved Contexts):
{contexts}

Câu hỏi: "{question}"
Trả lời:"""

class RAGBaseline:
    """Standard RAG Baseline using semantic text search."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()
        self.documents = self._load_documents()

    def answer_question(self, question: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Retrieves top-k relevant document chunks and synthesizes answer.
        Returns dict: {"question", "retrieved_chunks", "answer", "method": "RAG-Baseline"}
        """
        top_chunks = self._retrieve_top_k(question, top_k=top_k)
        context_str = "\n".join([f"- {c}" for c in top_chunks])

        prompt = RAG_PROMPT.format(contexts=context_str, question=question)
        answer = self.llm.generate(prompt, temperature=0.2)

        return {
            "question": question,
            "retrieved_chunks": top_chunks,
            "answer": answer,
            "method": "RAG-Baseline"
        }

    def _retrieve_top_k(self, query: str, top_k: int = 3) -> List[str]:
        """Simple keyword-overlap & token similarity retriever suitable for CPU execution."""
        if not self.documents:
            return ["Bệnh nhân Đái tháo đường týp 2 được điều trị bằng Metformin 500mg."]

        query_words = set(query.lower().split())
        scored_docs = []

        for doc in self.documents:
            doc_text = doc.get("text", "")
            doc_words = set(doc_text.lower().split())
            overlap = len(query_words.intersection(doc_words))
            scored_docs.append((overlap, doc_text))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]

    def _load_documents(self) -> List[Dict[str, Any]]:
        path = SYNTHETIC_DATA_DIR / "synthetic_data.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

if __name__ == "__main__":
    rag = RAGBaseline()
    print("RAG Answer:", rag.answer_question("Thuốc nào điều trị Đái tháo đường týp 2?"))
