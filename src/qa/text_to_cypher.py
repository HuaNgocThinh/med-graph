"""
Text-to-Cypher Question Answering Engine for MedGraph-VI.
Translates Vietnamese natural language clinical questions into Neo4j Cypher queries,
validates them, executes on Neo4j, handles fallback strategies for empty results, and synthesizes natural language answers.
"""

import json
import logging
import re
from typing import Dict, Any, List
from src.llm_client import LLMClient
from src.graph.neo4j_client import Neo4jClient
from src.entity_linking.entity_normalizer import get_canonical_name, ALIAS_MAP, normalize_disease_name, get_term_synonyms, SYNONYM_MAP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TextToCypherQA")

CYPHER_GENERATION_PROMPT = """Bạn là chuyên gia Neo4j Cypher. Dựa trên schema đồ thị y tế sau:
- Node labels: DRUG, DISEASE, SYMPTOM, PROCEDURE, DRUG_GROUP
- Relationship types: PRESCRIBED_FOR, CONTRAINDICATED_FOR, TREATS, CAUSES, HAS_SYMPTOM

QUY TẮC SINH CYPHER:
1. Khi truy vấn theo tên BỆNH hoặc THUỐC, hãy dùng CONTAINS với toLower(node.name) (VD: WHERE toLower(dis.name) CONTAINS 'đái tháo đường' hoặc 'dạ dày').
2. Khi câu hỏi liên quan đến "thuốc điều trị bệnh gì" hoặc "bệnh gì được kê thuốc gì", LUÔN sinh Cypher tìm CẢ HAI loại quan hệ: [:PRESCRIBED_FOR|TREATS] thay vì chỉ 1 loại, và có thể bỏ qua nhãn Node (labels) của đích để tránh phân loại sai (VD: MATCH (d)-[:PRESCRIBED_FOR|TREATS]->(b) hoặc sử dụng nhãn kép :DISEASE|SYMPTOM). Thuốc giảm triệu chứng dùng TREATS.
3. Thuốc chống chỉ định với bệnh dùng CONTRAINDICATED_FOR. Bệnh biểu hiện triệu chứng dùng HAS_SYMPTOM.

Hãy sinh MỘT câu lệnh Cypher duy nhất (bắt đầu bằng MATCH, MERGE, hoặc WITH; không chứa lời giải thích, không chứa markdown code block) để trả lời câu hỏi:
"{question}"
Cypher Query:"""

ANSWER_SYNTHESIS_PROMPT = """Bạn là trợ lý y tế thông minh.
Dựa trên kết quả truy vấn từ Knowledge Graph y tế và trạng thái kiểm tra dữ liệu bên dưới, hãy trả lời câu hỏi của người dùng một cách chính xác, ngắn gọn và dễ hiểu bằng tiếng Việt (dạng câu nói hoàn chỉnh).

Lưu ý quan trọng:
- Nếu kết quả từ DB có dữ liệu, hãy tổng hợp câu trả lời tự nhiên.
- Nếu trạng thái kiểm tra là 'NODE_EXISTS_NO_RELATIONS': Hãy thông báo rõ ràng là 'Cơ sở dữ liệu y tế hiện đã ghi nhận thực thể này, nhưng chưa có dữ liệu quan hệ lâm sàng tương ứng trong Knowledge Graph' để người dùng phân biệt giữa dữ liệu chưa đủ và lỗi hệ thống.
- Nếu trạng thái kiểm tra là 'NODE_NOT_FOUND': Hãy thông báo rõ ràng là 'Cơ sở dữ liệu hiện chưa ghi nhận thực thể này'.

Câu hỏi: "{question}"
Trạng thái kiểm tra dữ liệu: {fallback_status}
Thông tin Node tìm thấy trong KG: {node_existence_info}
Kết quả truy vấn Cypher: {cypher_results}

Câu trả lời tự nhiên:"""

VALID_CYPHER_KEYWORDS = ("MATCH", "MERGE", "WITH", "RETURN", "OPTIONAL", "CALL")
OFFLINE_WARNING_PREFIX = "⚠️ [CẢNH BÁO: Neo4j đang offline, đây là kết quả giả lập, KHÔNG dùng để đánh giá/báo cáo]\n\n"

class TextToCypherQA:
    """Natural Language to Cypher Translator and Answer Generator with 3-tier fallback for empty results."""

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
                    raw_cypher = "MATCH (d)-[r:CONTRAINDICATED_FOR]->(b:DISEASE) WHERE toLower(b.name) CONTAINS 'dạ dày' RETURN d.name AS ThuocChongChiDinh, b.name AS Benh"
                else:
                    raw_cypher = "MATCH (d)-[r:CONTRAINDICATED_FOR]->(b:DISEASE) RETURN d.name AS ThuocChongChiDinh, b.name AS Benh"
            elif "thuốc" in q_lower or "kê" in q_lower or "điều trị" in q_lower:
                if "dạ dày" in q_lower:
                    raw_cypher = "MATCH (d)-[r:PRESCRIBED_FOR|TREATS]->(b) WHERE toLower(b.name) CONTAINS 'dạ dày' RETURN d.name AS Thuoc, b.name AS Benh"
                elif "huyết áp" in q_lower:
                    raw_cypher = "MATCH (d)-[r:PRESCRIBED_FOR|TREATS]->(b) WHERE toLower(b.name) CONTAINS 'huyết áp' RETURN d.name AS Thuoc, b.name AS Benh"
                else:
                    raw_cypher = "MATCH (d)-[r:PRESCRIBED_FOR|TREATS]->(b:DISEASE) WHERE toLower(b.name) CONTAINS 'đái tháo đường' RETURN d.name AS Thuoc, b.name AS Benh"
            elif "triệu chứng" in q_lower:
                raw_cypher = "MATCH (b:DISEASE)-[r:HAS_SYMPTOM|CAUSES]->(s:SYMPTOM) RETURN b.name AS Benh, s.name AS TrieuChung"
            else:
                raw_cypher = "MATCH (head)-[r]->(tail) RETURN head.name, type(r), tail.name LIMIT 10"

        return raw_cypher

    def check_node_existence(self, question: str) -> List[Dict[str, Any]]:
        """Queries Neo4j to audit if nodes matching terms in question exist in Knowledge Graph."""
        if not self.neo4j.is_online():
            return []

        question_lower = question.lower()
        
        # 1. Match known terms (synonyms, aliases, database nodes) directly from the question
        found_terms = set()
        
        # All node names from Neo4j
        all_nodes_query = "MATCH (n) RETURN n.name AS name, labels(n) AS labels"
        all_nodes = self.neo4j.execute_query(all_nodes_query)
        
        for node in all_nodes:
            name = node.get("name", "")
            if name.lower() in question_lower:
                found_terms.add(name.lower())
                
        for key in SYNONYM_MAP.keys():
            if key in question_lower:
                found_terms.add(key)
                
        for key in ALIAS_MAP.keys():
            if key in question_lower:
                found_terms.add(key)

        # 2. Add word-based candidate keywords (original logic fallback/extension)
        words = re.findall(r'\b\w{3,}\b', question_lower)
        for w in words:
            if w not in ("bệnh nhân", "được", "thuốc", "bị", "nào", "gì", "những", "triệu chứng", "lâm sàng"):
                found_terms.add(w)

        # Remove generic short terms if a longer term containing them is matched
        # (e.g. if we have "đau bao tử", we don't need to keep "đau" and "bao tử" separately as candidates)
        candidates = list(found_terms)
        candidates_to_keep = []
        for c in candidates:
            # If c is a substring of any other longer candidate, we skip it unless it's a key term
            is_sub = False
            for other in candidates:
                if c != other and c in other:
                    is_sub = True
                    break
            if not is_sub or c in ("đau", "sốt", "ho"):
                candidates_to_keep.append(c)

        # Fallback to all found terms if empty
        if not candidates_to_keep:
            candidates_to_keep = candidates

        matched_nodes = []
        for term in candidates_to_keep[:5]:
            term_syns = get_term_synonyms(term)

            for node in all_nodes:
                node_name = node.get("name", "")
                node_name_lower = node_name.lower()
                norm_node = normalize_disease_name(node_name)
                norm_node_lower = norm_node.lower()

                # Flexible substring match in both directions for all synonym variations
                is_match = False
                for var in term_syns:
                    var_lower = var.lower()
                    norm_var = normalize_disease_name(var)
                    norm_var_lower = norm_var.lower()

                    if (var_lower in node_name_lower or 
                        node_name_lower in var_lower or
                        norm_var_lower in norm_node_lower or 
                        norm_node_lower in norm_var_lower):
                        is_match = True
                        break

                if is_match:
                    if node not in matched_nodes:
                        matched_nodes.append(node)

        return matched_nodes

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Translates question -> Cypher -> Query Neo4j -> Fallback Audit -> Synthesize Answer.
        """
        is_online = self.neo4j.is_online()
        data_source = "LIVE_NEO4J" if is_online else "SIMULATED_OFFLINE"

        cypher_query = self.generate_cypher(question)
        logger.info(f"Generated Cypher query: {cypher_query} (Neo4j Status: {data_source})")

        graph_results = []
        fallback_status = "FOUND"
        fallback_used = False
        matched_nodes = []

        if is_online:
            # Pre-evaluate node existence for auditing and synonym query substitution
            matched_nodes = self.check_node_existence(question)
            
            graph_results = self.neo4j.execute_query(cypher_query)

            # FALLBACK STRATEGY 1: Literal Canonicalization and Alias Expansion
            if not graph_results:
                logger.info("ℹ️ Initial Cypher returned empty results. Executing Fallback Tier 1 (Alias & Relation Type Expansion)...")
                fallback_used = True

                expanded_cypher = cypher_query
                literals = re.findall(r"['\"]([^'\"]+)['\"]", cypher_query)
                for lit in literals:
                    # Match synonym against candidate nodes in DB
                    lit_syns = get_term_synonyms(lit)
                    matched_db_name = None
                    for node in matched_nodes:
                        node_name = node.get("name", "")
                        if node_name.lower() in [s.lower() for s in lit_syns]:
                            matched_db_name = node_name
                            break
                    
                    if matched_db_name:
                        expanded_cypher = expanded_cypher.replace(f"'{lit}'", f"'{matched_db_name.lower()}'").replace(f'"{lit}"', f'"{matched_db_name.lower()}"')
                    else:
                        norm_lit = normalize_disease_name(lit)
                        if norm_lit.lower() != lit.lower():
                            expanded_cypher = expanded_cypher.replace(f"'{lit}'", f"'{norm_lit}'").replace(f'"{lit}"', f'"{norm_lit}"')

                # FALLBACK STRATEGY 2: Broaden Relation Types & Node Labels
                if "HAS_SYMPTOM" in expanded_cypher and "|CAUSES" not in expanded_cypher:
                    expanded_cypher = expanded_cypher.replace(":HAS_SYMPTOM", ":HAS_SYMPTOM|CAUSES|TREATS|RELATED_TO")
                if "PRESCRIBED_FOR" in expanded_cypher and "|TREATS" not in expanded_cypher:
                    expanded_cypher = expanded_cypher.replace(":PRESCRIBED_FOR", ":PRESCRIBED_FOR|TREATS|CONTRAINDICATED_FOR|RELATED_TO")

                # Broaden node labels to handle disease-symptom-drug group classification variations
                if ":DISEASE" in expanded_cypher and "|SYMPTOM" not in expanded_cypher:
                    expanded_cypher = expanded_cypher.replace(":DISEASE", ":DISEASE|SYMPTOM")
                if ":SYMPTOM" in expanded_cypher and "|DISEASE" not in expanded_cypher:
                    expanded_cypher = expanded_cypher.replace(":SYMPTOM", ":DISEASE|SYMPTOM")
                if ":DRUG" in expanded_cypher and "|DRUG_GROUP" not in expanded_cypher:
                    expanded_cypher = expanded_cypher.replace(":DRUG", ":DRUG|DRUG_GROUP")

                graph_results = self.neo4j.execute_query(expanded_cypher)
                if graph_results:
                    cypher_query = expanded_cypher

            # Set correct fallback_status based on audit results
            if not graph_results:
                if matched_nodes:
                    fallback_status = "NODE_EXISTS_NO_RELATIONS"
                    logger.info(f"🔍 DEBUG LOG [Node Existence]: Nodes EXIST in KG: {matched_nodes}, but no matching relation edges found.")
                else:
                    fallback_status = "NODE_NOT_FOUND"
                    logger.info("🔍 DEBUG LOG [Node Existence]: No matching Disease/Drug nodes found in Knowledge Graph.")
            else:
                fallback_status = "FOUND"
        else:
            logger.warning("⚠️ Neo4j is OFFLINE. Running in SIMULATED_OFFLINE mode without live DB results.")
            matched_nodes = []
            fallback_status = "FOUND"  # Simulated offline defaults to found or synthesizes mock answer

        # Synthesize Answer via LLM with explicit node existence context
        synth_prompt = ANSWER_SYNTHESIS_PROMPT.format(
            question=question,
            fallback_status=fallback_status,
            node_existence_info=json.dumps(matched_nodes, ensure_ascii=False) if matched_nodes else "None",
            cypher_results=json.dumps(graph_results, ensure_ascii=False)
        )
        raw_answer = self.llm.generate(synth_prompt, temperature=0.2)

        if not is_online:
            final_answer = OFFLINE_WARNING_PREFIX + raw_answer
        else:
            final_answer = raw_answer

        return {
            "question": question,
            "cypher_query": cypher_query,
            "graph_results": graph_results,
            "fallback_status": fallback_status,
            "fallback_used": fallback_used,
            "node_existence_info": matched_nodes,
            "answer": final_answer,
            "data_source": data_source,
            "method": "KG-QA"
        }

if __name__ == "__main__":
    qa = TextToCypherQA()
    res = qa.answer_question("Bệnh nhân Đái tháo đường týp 2 được kê thuốc gì?")
    print("KG-QA Result:\n", json.dumps(res, ensure_ascii=False, indent=2))
