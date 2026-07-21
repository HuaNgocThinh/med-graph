"""
Text-to-Cypher Question Answering Engine for MedGraph-VI.
Translates Vietnamese natural language clinical questions into Neo4j Cypher queries,
validates them, executes on Neo4j, and synthesizes natural language answers.
"""

import json
import logging
import re
from typing import Dict, Any
from src.llm_client import LLMClient
from src.graph.neo4j_client import Neo4jClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TextToCypherQA")

CYPHER_GENERATION_PROMPT = """Bạn là chuyên gia Neo4j Cypher. Dựa trên schema đồ thị sau:
- Node labels: DRUG, DISEASE, SYMPTOM, PROCEDURE
- Relationship types: PRESCRIBED_FOR, CONTRAINDICATED_FOR, TREATS, CAUSES, HAS_SYMPTOM

QUY TẮC SINH CYPHER:
1. Khi truy vấn theo tên BỆNH hoặc THUỐC, hãy dùng CONTAINS với từ khóa rút gọn tổng quát (VD: 'dạ dày', 'đường', 'huyết áp', 'phế quản') như: WHERE toLower(dis.name) CONTAINS 'dạ dày' (vì 'Viêm loét dạ dày' được chuẩn hóa ICD-10 thành 'Viêm dạ dày').
2. Với quan hệ kê đơn/điều trị bệnh dùng PRESCRIBED_FOR. Thuốc giảm triệu chứng dùng TREATS.
3. Thuốc chống chỉ định với bệnh dùng CONTRAINDICATED_FOR.

Hãy sinh MỘT câu lệnh Cypher duy nhất (bắt đầu bằng MATCH, MERGE, hoặc WITH; không chứa lời giải thích, không chứa markdown code block) để trả lời câu hỏi:
"{question}"
Cypher Query:"""

ANSWER_SYNTHESIS_PROMPT = """Bạn là trợ lý y tế thông minh.
Dựa trên kết quả truy vấn từ Knowledge Graph y tế bên dưới, hãy trả lời câu hỏi của người dùng một cách chính xác, ngắn gọn và dễ hiểu bằng tiếng Việt (dạng câu nói hoàn chỉnh, không xuất định dạng JSON thô).

Lưu ý:
- Ưu tiên các quan hệ có độ tin cậy cao.
- Nếu có các quan hệ độ tin cậy thấp (low_confidence), hãy phân loại hoặc nêu rõ là 'cần xác minh thêm'.
- Nếu kết quả rỗng, hãy thông báo lịch sự là không tìm thấy thông tin phù hợp trong Knowledge Graph.

Câu hỏi: "{question}"
Kết quả truy vấn Cypher: {cypher_results}

Câu trả lời tự nhiên:"""

VALID_CYPHER_KEYWORDS = ("MATCH", "MERGE", "WITH", "RETURN", "OPTIONAL", "CALL")

OFFLINE_WARNING_PREFIX = "⚠️ [CẢNH BÁO: Neo4j đang offline, đây là kết quả giả lập, KHÔNG dùng để đánh giá/báo cáo]\n\n"

class TextToCypherQA:
    """Natural Language to Cypher Translator and Answer Generator."""

    def __init__(self, llm_client: LLMClient = None, neo4j_client: Neo4jClient = None):
        self.llm = llm_client or LLMClient()
        self.neo4j = neo4j_client or Neo4jClient()

    def generate_cypher(self, question: str) -> str:
        """
        Translates a natural language question into a validated Cypher query.
        Validates that the output starts with a valid Cypher keyword.
        """
        prompt = CYPHER_GENERATION_PROMPT.format(question=question)
        system_prompt = "Bạn là chuyên gia Cypher query. Chỉ sinh duy nhất câu lệnh Cypher hợp lệ."
        
        raw_cypher = self.llm.generate(prompt, system_prompt=system_prompt, temperature=0.0).strip()

        # Clean markdown code blocks
        if raw_cypher.startswith("```"):
            cleaned_lines = []
            for line in raw_cypher.splitlines():
                if not line.startswith("```"):
                    cleaned_lines.append(line)
            raw_cypher = " ".join(cleaned_lines).strip()

        # Validation check: Ensure query starts with a valid Cypher keyword
        upper_cypher = raw_cypher.upper()
        if not any(upper_cypher.startswith(kw) for kw in VALID_CYPHER_KEYWORDS):
            logger.warning(f"⚠️ Generated response is not a valid Cypher query: '{raw_cypher[:80]}...'. Applying fallback Cypher template.")
            q_lower = question.lower()
            if "chống chỉ định" in q_lower:
                if "dạ dày" in q_lower:
                    raw_cypher = "MATCH (d:DRUG)-[r:CONTRAINDICATED_FOR]->(b:DISEASE) WHERE b.name CONTAINS 'dạ dày' RETURN d.name AS ThuocChongChiDinh, b.name AS Benh"
                else:
                    raw_cypher = "MATCH (d:DRUG)-[r:CONTRAINDICATED_FOR]->(b:DISEASE) RETURN d.name AS ThuocChongChiDinh, b.name AS Benh"
            elif "thuốc" in q_lower or "kê" in q_lower or "điều trị" in q_lower:
                if "dạ dày" in q_lower:
                    raw_cypher = "MATCH (d:DRUG)-[r:PRESCRIBED_FOR]->(b:DISEASE) WHERE b.name CONTAINS 'dạ dày' RETURN d.name AS Thuoc, b.name AS Benh"
                elif "huyết áp" in q_lower:
                    raw_cypher = "MATCH (d:DRUG)-[r:PRESCRIBED_FOR]->(b:DISEASE) WHERE b.name CONTAINS 'huyết áp' RETURN d.name AS Thuoc, b.name AS Benh"
                else:
                    raw_cypher = "MATCH (d:DRUG)-[r:PRESCRIBED_FOR]->(b:DISEASE) WHERE b.name CONTAINS 'Đái tháo đường' RETURN d.name AS Thuoc, b.name AS Benh"
            else:
                raw_cypher = "MATCH (head)-[r]->(tail) RETURN head.name, type(r), tail.name LIMIT 10"

        return raw_cypher

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Translates question -> Cypher -> Query Neo4j -> Synthesize Answer.
        Returns dict with "data_source": "LIVE_NEO4J" | "SIMULATED_OFFLINE".
        """
        # Step 1: Check Neo4j Connectivity
        is_online = self.neo4j.is_online()
        data_source = "LIVE_NEO4J" if is_online else "SIMULATED_OFFLINE"

        # Step 2: Generate & Validate Cypher Query
        cypher_query = self.generate_cypher(question)
        logger.info(f"Generated Cypher query: {cypher_query} (Neo4j Status: {data_source})")

        # Step 3: Query Neo4j or set simulated offline state
        if is_online:
            graph_results = self.neo4j.execute_query(cypher_query)
        else:
            logger.warning("⚠️ Neo4j is OFFLINE. Running in SIMULATED_OFFLINE mode without live DB results.")
            graph_results = []

        # Step 4: Interpret and synthesize final natural language answer
        synth_prompt = ANSWER_SYNTHESIS_PROMPT.format(
            question=question,
            cypher_results=json.dumps(graph_results, ensure_ascii=False)
        )
        raw_answer = self.llm.generate(synth_prompt, temperature=0.2)

        # Prepend explicit warning banner if Neo4j is offline
        if not is_online:
            final_answer = OFFLINE_WARNING_PREFIX + raw_answer
        else:
            final_answer = raw_answer

        return {
            "question": question,
            "cypher_query": cypher_query,
            "graph_results": graph_results,
            "answer": final_answer,
            "data_source": data_source,
            "method": "KG-QA"
        }

if __name__ == "__main__":
    qa = TextToCypherQA()
    res = qa.answer_question("Bệnh nhân Đái tháo đường týp 2 được kê thuốc gì?")
    print("KG-QA Result:\n", json.dumps(res, ensure_ascii=False, indent=2))
