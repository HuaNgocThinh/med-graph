"""
Text-to-Cypher Question Answering Engine for MedGraph-VI.
Translates Vietnamese natural language clinical questions into Neo4j Cypher queries,
validates them, executes on Neo4j, handles fallback strategies for empty results, and synthesizes natural language answers.
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List
from src.llm_client import LLMClient
from src.graph.neo4j_client import Neo4jClient
from src.entity_linking.entity_normalizer import (
    get_canonical_name, ALIAS_MAP, normalize_disease_name, get_term_synonyms,
    SYNONYM_MAP, canonicalize_synonyms,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TextToCypherQA")

CYPHER_GENERATION_PROMPT = """Bạn là chuyên gia Neo4j Cypher.

QUY TẮC SINH CYPHER:
1. Khi truy vấn theo tên BỆNH hoặc THUỐC, hãy dùng CONTAINS với toLower(node.name) (VD: WHERE toLower(dis.name) CONTAINS 'đái tháo đường' hoặc 'dạ dày').
2. Khi câu hỏi liên quan đến "thuốc điều trị bệnh gì" hoặc "bệnh gì được kê thuốc gì", LUÔN sinh Cypher tìm CẢ HAI loại quan hệ: [:PRESCRIBED_FOR|TREATS] thay vì chỉ 1 loại, và có thể bỏ qua nhãn Node (labels) của đích để tránh phân loại sai (VD: MATCH (d)-[r:PRESCRIBED_FOR|TREATS]->(b) hoặc sử dụng nhãn kép :DISEASE|SYMPTOM). Thuốc giảm triệu chứng dùng TREATS.
3. Thuốc chống chỉ định với bệnh dùng CONTRAINDICATED_FOR. Bệnh biểu hiện triệu chứng dùng HAS_SYMPTOM. Bệnh gây ra biến chứng/triệu chứng dùng CAUSES.
4. Hãy LUÔN trả về r.source_sample_id AS source_sample_id và coalesce(r.dosage, "") AS Lieu trong câu lệnh RETURN (ví dụ: RETURN d.name AS Thuoc, coalesce(r.dosage, "") AS Lieu, b.name AS Benh, r.source_sample_id AS source_sample_id) để hỗ trợ truy vết nguồn dữ liệu và hiển thị hàm lượng liều dùng.
5. LUÔN lọc bỏ các quan hệ bị phủ định bằng cách thêm điều kiện `coalesce(r.negated, false) = false` (hoặc `r.negated = false`) vào mệnh đề WHERE.

Hãy sinh MỘT câu lệnh Cypher duy nhất (bắt đầu bằng MATCH, MERGE, hoặc WITH; không chứa lời giải thích, không chứa markdown code block) để trả lời câu hỏi:
"{question}"
Cypher Query:"""

ANSWER_SYNTHESIS_PROMPT = """Bạn là trợ lý y tế thông minh.
Dựa trên kết quả truy vấn từ Knowledge Graph y tế và trạng thái kiểm tra dữ liệu bên dưới, hãy trả lời câu hỏi của người dùng một cách chính xác, ngắn gọn và dễ hiểu bằng tiếng Việt (dạng câu nói hoàn chỉnh).

Lưu ý quan trọng:
- Nếu kết quả từ DB có dữ liệu, hãy tổng hợp câu trả lời tự nhiên.
- Khi kết quả truy vấn có thông tin liều dùng (Lieu / dosage / r.dosage không rỗng), hãy LUÔN trình trình bày hàm lượng/liều dùng trong ngoặc đơn ngay sau tên thuốc (Ví dụ: 'Meloxicam (15mg)' thay vì 'Meloxicam'). Nếu có nhiều mức liều cho cùng một thuốc (VD: Meloxicam 15mg và Meloxicam 7.5mg), hãy trình bày rõ ràng từng mức liều kèm theo mục đích/quan hệ tương ứng.
- Nếu trong kết quả truy vấn có mã nguồn r.source_sample_id (ví dụ: syn_001, syn_004, syn_015, syn_072), hãy LUÔN đính kèm danh sách các mã nguồn đó trong ngoặc đơn ngay sau tên thực thể/câu trả lời (Ví dụ: 'Đái tháo đường týp 2 (syn_001, syn_004, syn_015, syn_072)') để đảm bảo tính truy vết dữ liệu (Traceability).
- Nếu trạng thái kiểm tra là 'NODE_EXISTS_NO_RELATIONS': Hãy thông báo rõ ràng là 'Cơ sở dữ liệu y tế hiện đã ghi nhận thực thể này, nhưng chưa có dữ liệu quan hệ lâm sàng tương ứng trong Knowledge Graph' để người dùng phân biệt giữa dữ liệu chưa đủ và lỗi hệ thống.
- Nếu trạng thái kiểm tra là 'NODE_NOT_FOUND': Hãy thông báo rõ ràng là 'Cơ sở dữ liệu hiện chưa ghi nhận thực thể này'.
- Nếu trạng thái kiểm tra là 'QUERY_ERROR': Truy vấn KHÔNG chạy được (lỗi hệ thống), nên ta KHÔNG biết dữ liệu có hay không. TUYỆT ĐỐI KHÔNG được nói 'chưa ghi nhận' hay 'không có dữ liệu'. Hãy trả lời đúng một ý: 'Lỗi hệ thống: truy vấn cơ sở dữ liệu không thực hiện được, chưa thể kết luận.'

Câu hỏi: "{question}"
Trạng thái kiểm tra dữ liệu: {fallback_status}
Thông tin Node tìm thấy trong KG: {node_existence_info}
Kết quả truy vấn Cypher: {cypher_results}

Câu trả lời tự nhiên:"""

VALID_CYPHER_KEYWORDS = ("MATCH", "MERGE", "WITH", "RETURN", "OPTIONAL", "CALL")

# Quoted string literals inside a generated Cypher query
_CYPHER_LITERAL_RE = re.compile(r"['\"]([^'\"]+)['\"]")

DRUG_KEYWORDS = ["thuốc", "kê", "điều trị bằng", "chống chỉ định", "dùng", "uống", "tiêm", "chỉ định"]
SYMPTOM_KEYWORDS = ["triệu chứng", "biểu hiện", "dấu hiệu", "cảm thấy", "đau", "sốt", "ho"]
DISEASE_KEYWORDS = ["bệnh", "chẩn đoán", "mắc", "gây ra", "biến chứng", "tiền sử"]


def generate_cypher(question: str) -> Dict[str, Any]:
    """
    Module-level helper to generate Cypher query and return dictionary with schema metadata.
    """
    qa = TextToCypherQA()
    schema_details = qa.get_schema_details(question)
    cypher_str = qa.generate_cypher(question)
    return {
        "cypher": cypher_str,
        "schema_source": schema_details["schema_source"],
        "schema_pruned": schema_details["schema_pruned"]
    }



def build_schema_context(schema: Dict[str, Any], timestamp_str: str = "") -> str:
    """Converts a schema dictionary into a structured text prompt snippet."""
    ts_suffix = f" lúc {timestamp_str}" if timestamp_str else ""
    lines = [f"=== SCHEMA ĐỒ THỊ (live từ Neo4j{ts_suffix}) ==="]
    lines.append("NODES:")
    for n in schema.get("nodes", []):
        lbl = n.get("label", "")
        props = ", ".join(n.get("properties", []))
        lines.append(f"- (:{lbl} {{{props}}})")

    lines.append("\nRELATIONSHIPS:")
    for r in schema.get("relationships", []):
        r_type = r.get("type", "")
        r_from = r.get("from", "ANY")
        r_to = r.get("to", "ANY")
        props = ", ".join(r.get("properties", []))
        lines.append(f"- (:{r_from})-[:{r_type} {{{props}}}]->(:{r_to})")

    lines.append("\nBẮT BUỘC trong Cypher:")
    lines.append("- Lọc negated: AND coalesce(r.negated, false) = false")
    lines.append("- Trả về: source_sample_id cho traceability")
    lines.append("=== KẾT THÚC SCHEMA ===")
    return "\n".join(lines)


def prune_schema(schema: Dict[str, Any], question: str) -> Dict[str, Any]:
    """Filters schema relationships and nodes based on question intent keywords."""
    if not schema or not schema.get("relationships"):
        return schema

    q_lower = question.lower()
    has_drug = any(kw in q_lower for kw in DRUG_KEYWORDS)
    has_symptom = any(kw in q_lower for kw in SYMPTOM_KEYWORDS)

    all_rels = schema.get("relationships", [])
    all_nodes = schema.get("nodes", [])

    if has_drug and not has_symptom:
        q_type = "DRUG"
        pruned_rels = [r for r in all_rels if r.get("from") == "DRUG" or r.get("to") == "DRUG"]
    elif has_symptom and not has_drug:
        q_type = "SYMPTOM"
        pruned_rels = [
            r for r in all_rels
            if r.get("type") in ("HAS_SYMPTOM", "TREATS", "CAUSES") or r.get("from") == "SYMPTOM" or r.get("to") == "SYMPTOM"
        ]
    else:
        q_type = "ALL"
        pruned_rels = list(all_rels)

    if not pruned_rels:
        logger.info(f"Schema pruned: {len(all_rels)}/{len(all_rels)} relations kept for question type: [{q_type}]")
        return schema

    active_labels = set()
    for r in pruned_rels:
        active_labels.add(r.get("from"))
        active_labels.add(r.get("to"))
    if q_type == "DRUG":
        active_labels.add("DRUG")
    elif q_type == "SYMPTOM":
        active_labels.add("SYMPTOM")

    pruned_nodes = [n for n in all_nodes if n.get("label") in active_labels]

    logger.info(f"Schema pruned: {len(pruned_rels)}/{len(all_rels)} relations kept for question type: [{q_type}]")
    return {
        "nodes": pruned_nodes,
        "relationships": pruned_rels
    }


def terms_match(term: str, node_name: str) -> bool:
    """
    True if `term` and `node_name` denote the same concept through any synonym variant.

    Uses BIDIRECTIONAL containment, not equality: a question term ('tiểu đường') must match
    a more specific graph node ('Đái tháo đường týp 2'), and a specific question term must
    match a broader node. Comparing with `==` was the original defect — it silently failed
    whenever the node name merely CONTAINED the synonym.
    """
    if not term or not node_name:
        return False

    node_l = node_name.strip().lower()
    node_norm = normalize_disease_name(node_name).lower()

    for var in get_term_synonyms(term):
        v = var.strip().lower()
        if not v:
            continue
        v_norm = normalize_disease_name(var).lower()
        if (v in node_l or node_l in v or
                (v_norm and (v_norm in node_norm or node_norm in v_norm))):
            return True
    return False


def canonicalize_cypher_literals(cypher: str) -> str:
    """
    Rewrites folk-term string literals in a generated Cypher query to their medical-standard
    form ('tiểu đường' -> 'đái tháo đường') BEFORE the query is first executed.

    This is the query-side half of the synonym guarantee; graph_builder applies the same
    canonicalization at write time. Applying it up front (rather than only in the empty-result
    fallback) is what makes a folk-term question and its medical-term twin produce the SAME
    Cypher and therefore the SAME result set.

    Literals are emitted lowercase because the generated queries compare against
    toLower(node.name); substituting Sentence Case here would never match.
    """
    if not cypher:
        return cypher

    out = cypher
    for lit in set(_CYPHER_LITERAL_RE.findall(cypher)):
        canonical = normalize_disease_name(lit).lower()
        if canonical and canonical != lit.strip().lower():
            out = out.replace(f"'{lit}'", f"'{canonical}'").replace(f'"{lit}"', f'"{canonical}"')
            logger.info(f"🔤 Synonym canonicalization of Cypher literal: '{lit}' -> '{canonical}'")
    return out
def ensure_negated_filter(cypher: str) -> str:
    """
    Ensures that any generated Cypher query containing a relationship variable [r...]
    filters out negated relationships with coalesce(r.negated, false) = false.
    """
    if not cypher or "negated" in cypher.lower():
        return cypher

    if not re.search(r'-\[\s*r\b', cypher):
        return cypher

    match = re.search(r'\b(RETURN|WITH)\b', cypher, re.IGNORECASE)
    if match:
        idx = match.start()
        prefix = cypher[:idx].rstrip()
        suffix = cypher[idx:]
        if " WHERE " in prefix.upper():
            return f"{prefix} AND coalesce(r.negated, false) = false {suffix}"
        else:
            return f"{prefix} WHERE coalesce(r.negated, false) = false {suffix}"
    else:
        if " WHERE " in cypher.upper():
            return f"{cypher} AND coalesce(r.negated, false) = false"
        else:
            return f"{cypher} WHERE coalesce(r.negated, false) = false"


OFFLINE_WARNING_PREFIX = "⚠️ [CẢNH BÁO: Neo4j đang offline, đây là kết quả giả lập, KHÔNG dùng để đánh giá/báo cáo]\n\n"

class TextToCypherQA:
    """Natural Language to Cypher Translator and Answer Generator with 3-tier fallback for empty results."""

    def __init__(self, llm_client: LLMClient = None, neo4j_client: Neo4jClient = None):
        self.llm = llm_client or LLMClient()
        self.neo4j = neo4j_client or Neo4jClient()

    def get_schema_details(self, question: str) -> Dict[str, Any]:
        """
        Fetches live schema, applies pruning, and builds schema context string.
        Returns metadata dict containing schema_context, schema_source, schema_pruned.
        """
        try:
            full_schema = self.neo4j.get_graph_schema()
            ts_iso = datetime.now().isoformat()
            schema_source = f"neo4j_live | {ts_iso}"
        except Exception as e:
            logger.warning(f"Could not fetch live Neo4j schema ({e}). Falling back to static schema.")
            ts_iso = datetime.now().isoformat()
            schema_source = f"neo4j_offline | {ts_iso}"
            full_schema = {
                "nodes": [
                    {"label": "DISEASE", "properties": ["name", "code", "first_surface", "created_at"]},
                    {"label": "DRUG", "properties": ["name", "code", "first_surface", "created_at"]},
                    {"label": "SYMPTOM", "properties": ["name", "first_surface", "created_at"]}
                ],
                "relationships": [
                    {"type": "PRESCRIBED_FOR", "from": "DRUG", "to": "DISEASE", "properties": ["confidence", "negated", "temporal", "source_sample_id", "head_surface", "tail_surface"]},
                    {"type": "TREATS", "from": "DRUG", "to": "SYMPTOM", "properties": ["confidence", "negated", "temporal", "source_sample_id", "head_surface", "tail_surface"]},
                    {"type": "CONTRAINDICATED_FOR", "from": "DRUG", "to": "DISEASE", "properties": ["confidence", "negated", "temporal", "source_sample_id", "head_surface", "tail_surface"]},
                    {"type": "HAS_SYMPTOM", "from": "DISEASE", "to": "SYMPTOM", "properties": ["confidence", "negated", "temporal", "source_sample_id", "head_surface", "tail_surface"]},
                    {"type": "CAUSES", "from": "DISEASE", "to": "SYMPTOM", "properties": ["confidence", "negated", "temporal", "source_sample_id", "head_surface", "tail_surface"]}
                ]
            }

        pruned = prune_schema(full_schema, question)
        total_rels = len(full_schema.get("relationships", []))
        kept_rels = len(pruned.get("relationships", []))
        schema_context = build_schema_context(pruned, ts_iso)

        return {
            "full_schema": full_schema,
            "pruned_schema": pruned,
            "schema_context": schema_context,
            "schema_source": schema_source,
            "schema_pruned": f"{kept_rels}/{total_rels}"
        }

    def generate_cypher(self, question: str) -> str:
        """
        Translates a natural language question into a validated Cypher query.
        Validates that the output starts with a valid Cypher keyword.
        """
        schema_details = self.get_schema_details(question)
        schema_context = schema_details["schema_context"]

        prompt = f"{schema_context}\n\n{CYPHER_GENERATION_PROMPT.format(question=question)}"
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
                    raw_cypher = "MATCH (d)-[r:CONTRAINDICATED_FOR]->(b:DISEASE) WHERE toLower(b.name) CONTAINS 'dạ dày' AND coalesce(r.negated, false) = false RETURN d.name AS ThuocChongChiDinh, coalesce(r.dosage, '') AS Lieu, b.name AS Benh, r.source_sample_id AS source_sample_id"
                else:
                    raw_cypher = "MATCH (d)-[r:CONTRAINDICATED_FOR]->(b:DISEASE) WHERE coalesce(r.negated, false) = false RETURN d.name AS ThuocChongChiDinh, coalesce(r.dosage, '') AS Lieu, b.name AS Benh, r.source_sample_id AS source_sample_id"
            elif "thuốc" in q_lower or "kê" in q_lower or "điều trị" in q_lower:
                if "dạ dày" in q_lower:
                    raw_cypher = "MATCH (d)-[r:PRESCRIBED_FOR|TREATS]->(b) WHERE toLower(b.name) CONTAINS 'dạ dày' AND coalesce(r.negated, false) = false RETURN d.name AS Thuoc, coalesce(r.dosage, '') AS Lieu, b.name AS Benh, r.source_sample_id AS source_sample_id"
                elif "huyết áp" in q_lower:
                    raw_cypher = "MATCH (d)-[r:PRESCRIBED_FOR|TREATS]->(b) WHERE toLower(b.name) CONTAINS 'huyết áp' AND coalesce(r.negated, false) = false RETURN d.name AS Thuoc, coalesce(r.dosage, '') AS Lieu, b.name AS Benh, r.source_sample_id AS source_sample_id"
                else:
                    raw_cypher = "MATCH (d)-[r:PRESCRIBED_FOR|TREATS]->(b:DISEASE) WHERE toLower(b.name) CONTAINS 'đái tháo đường' AND coalesce(r.negated, false) = false RETURN d.name AS Thuoc, coalesce(r.dosage, '') AS Lieu, b.name AS Benh, r.source_sample_id AS source_sample_id"
            elif "triệu chứng" in q_lower:
                raw_cypher = "MATCH (b:DISEASE)-[r:HAS_SYMPTOM|CAUSES]->(s:SYMPTOM) WHERE coalesce(r.negated, false) = false RETURN b.name AS Benh, s.name AS TrieuChung, r.source_sample_id AS source_sample_id"
            else:
                raw_cypher = "MATCH (head)-[r]->(tail) WHERE coalesce(r.negated, false) = false RETURN head.name, type(r), tail.name, coalesce(r.dosage, '') AS Lieu, r.source_sample_id AS source_sample_id LIMIT 10"

        # Ensure query has RETURN clause
        if "RETURN" not in raw_cypher.upper():
            logger.warning(f"⚠️ Generated Cypher lacks RETURN clause: '{raw_cypher}'. Appending default RETURN clause.")
            if "-[r" in raw_cypher or "-[r:" in raw_cypher:
                raw_cypher = f"{raw_cypher} RETURN d.name AS Thuoc, coalesce(r.dosage, '') AS Lieu, b.name AS Benh, r.source_sample_id AS source_sample_id"
            else:
                raw_cypher = f"{raw_cypher} RETURN *"

        return ensure_negated_filter(raw_cypher)

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
            for node in all_nodes:
                # Same rule as the Cypher-literal rewrite below. Keeping both call sites on
                # one helper is deliberate: they previously used different rules (containment
                # here, equality there), which is why synonym questions found the node but
                # still queried the un-rewritten folk term and returned nothing.
                if terms_match(term, node.get("name", "")):
                    if node not in matched_nodes:
                        matched_nodes.append(node)

        return matched_nodes

    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Translates question -> Cypher -> Query Neo4j -> Fallback Audit -> Synthesize Answer.
        """
        schema_details = self.get_schema_details(question)
        is_online = self.neo4j.is_online()
        data_source = "LIVE_NEO4J" if is_online else "SIMULATED_OFFLINE"

        cypher_query = self.generate_cypher(question)
        # Apply folk -> medical-standard synonym canonicalization to the query literals
        # before first execution, mirroring what graph_builder does at write time.
        cypher_query = canonicalize_cypher_literals(cypher_query)
        logger.info(f"Generated Cypher query: {cypher_query} (Neo4j Status: {data_source})")

        graph_results = []
        fallback_status = "FOUND"
        fallback_used = False
        matched_nodes = []

        if is_online:
            # Pre-evaluate node existence for auditing and synonym query substitution
            matched_nodes = self.check_node_existence(question)
            
            # raise_on_error=False on purpose: this Cypher is LLM-generated and may not parse.
            # But a statement that FAILED is not the same fact as a statement that matched
            # nothing, and the old code collapsed both into []. That made a broken query
            # indistinguishable from an empty graph, and the synthesis prompt then answered
            # "khong co du lieu" -- asserting an absence the database never reported.
            first_run = self.neo4j.execute_query(cypher_query, raise_on_error=False)
            query_error = None if first_run.ok else first_run.error
            graph_results = list(first_run)

            # FALLBACK STRATEGY 1: Literal Canonicalization and Alias Expansion
            if not graph_results:
                logger.info("ℹ️ Initial Cypher returned empty results. Executing Fallback Tier 1 (Alias & Relation Type Expansion)...")
                fallback_used = True

                expanded_cypher = cypher_query
                literals = _CYPHER_LITERAL_RE.findall(cypher_query)
                for lit in literals:
                    # Literals were already canonicalized before the first execution, so if we
                    # are here the concept-level form did not resolve. Fall back to a concrete
                    # DB node reachable from the literal through any synonym variant, matched
                    # with the SAME bidirectional rule check_node_existence() uses.
                    replacement = None
                    for node in matched_nodes:
                        node_name = node.get("name", "")
                        if terms_match(lit, node_name):
                            replacement = node_name.lower()
                            break

                    # Substituted lowercase: the generated queries compare toLower(node.name).
                    if replacement and replacement != lit.strip().lower():
                        expanded_cypher = expanded_cypher.replace(f"'{lit}'", f"'{replacement}'").replace(f'"{lit}"', f'"{replacement}"')

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

                second_run = self.neo4j.execute_query(expanded_cypher, raise_on_error=False)
                if not second_run.ok:
                    query_error = query_error or second_run.error
                graph_results = list(second_run)
                if graph_results:
                    cypher_query = expanded_cypher
                    query_error = None   # a later run succeeded; the earlier failure is moot

            # Set correct fallback_status based on audit results
            if not graph_results and query_error is not None:
                # Neither run executed. We know NOTHING about the graph, so we must not claim
                # the entity is absent -- that would be inventing an absence.
                fallback_status = "QUERY_ERROR"
                logger.error(
                    f"❌ Cypher did not execute: {query_error}. Reporting a system error, NOT "
                    f"'khong co du lieu' -- an empty result was never observed."
                )
            elif not graph_results:
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

        # Extract source_sample_ids for Traceability
        source_sample_ids = []
        if graph_results:
            for rec in graph_results:
                sid = rec.get("source_sample_id") or rec.get("r.source_sample_id")
                if sid:
                    for part in str(sid).split(","):
                        cleaned = part.strip()
                        if cleaned and cleaned not in source_sample_ids:
                            source_sample_ids.append(cleaned)

        return {
            "question": question,
            "cypher_query": cypher_query,
            "graph_results": graph_results,
            "source_sample_ids": source_sample_ids,
            "fallback_status": fallback_status,
            "fallback_used": fallback_used,
            "node_existence_info": matched_nodes,
            "answer": final_answer,
            "data_source": data_source,
            "schema_source": schema_details["schema_source"],
            "schema_pruned": schema_details["schema_pruned"],
            "method": "KG-QA"
        }


if __name__ == "__main__":
    qa = TextToCypherQA()
    res = qa.answer_question("Bệnh nhân Đái tháo đường týp 2 được kê thuốc gì?")
    print("KG-QA Result:\n", json.dumps(res, ensure_ascii=False, indent=2))
