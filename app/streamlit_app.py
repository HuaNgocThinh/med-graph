"""
Streamlit Web Application for MedGraph-VI.
Interactive Thesis Demo for Vietnamese Medical Knowledge Graph Construction and Question Answering.
"""

import streamlit as st
import json
import logging
import os
import sys
import datetime
from pathlib import Path
from typing import Dict, Any, List

# 1. Base Directory setup and path verification
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MedGraphStreamlitApp")

logger.info(f"🚀 Initializing MedGraph-VI Streamlit App | BASE_DIR: '{BASE_DIR}'")

from src.qa.qa_engine import QAEngine
from src.llm_client import LLMClient
from src.graph.neo4j_client import Neo4jClient
from src.ner.ner_ensemble import NEREnsemble
from src.relation_extraction.llm_re import LLMRelationExtractor
from src.negation_temporal.context_processor import ConTextProcessor
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.rxnorm_linker import RxNormLinker
from src.entity_linking.entity_normalizer import get_canonical_name
from evaluation.coverage_analysis import get_coverage_gaps

# Page configuration
st.set_page_config(
    page_title="MedGraph-VI | Medical Knowledge Graph Demo",
    page_icon="🩺",
    layout="wide"
)

# ----------------------------------------------------
# HELPER FUNCTIONS & DATA LOADERS (Cached)
# ----------------------------------------------------

@st.cache_data(ttl=3600)
def load_synthetic_dataset() -> Dict[str, str]:
    """Loads synthetic data samples mapping sample_id -> original text."""
    syn_path = BASE_DIR / "data" / "synthetic" / "synthetic_data.json"
    if syn_path.exists():
        try:
            with open(syn_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {item["id"]: item.get("text", "") for item in data if "id" in item}
        except Exception as e:
            logger.error(f"Error loading synthetic dataset: {e}")
    return {}

def save_user_feedback(question: str, method: str, answer: str, feedback: str, cypher_query: str = ""):
    """Appends user feedback (correct/incorrect) to data/exports/user_feedback_log.json."""
    log_path = BASE_DIR / "data" / "exports" / "user_feedback_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logs = []
    if log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except Exception as e:
            logger.warning(f"Error loading user feedback log from '{log_path}': {e}")
            logs = []

    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "question": question,
        "method": method,
        "answer": answer,
        "feedback": feedback,
        "cypher_query": cypher_query
    }
    logs.append(entry)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def get_feedback_stats() -> Dict[str, Any]:
    """Reads feedback log and returns summary statistics."""
    log_path = BASE_DIR / "data" / "exports" / "user_feedback_log.json"
    if not log_path.exists():
        return {"total": 0, "correct": 0, "incorrect": 0, "accuracy_pct": 0.0}
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            logs = json.load(f)
            total = len(logs)
            correct = sum(1 for item in logs if item.get("feedback") == "correct")
            incorrect = total - correct
            acc = (correct / total * 100) if total > 0 else 0.0
            return {
                "total": total,
                "correct": correct,
                "incorrect": incorrect,
                "accuracy_pct": acc
            }
    except Exception as e:
        logger.warning(f"Error reading feedback stats from '{log_path}': {e}")
        return {"total": 0, "correct": 0, "incorrect": 0, "accuracy_pct": 0.0}

@st.cache_data(ttl=600)
def get_autocomplete_entities() -> List[str]:
    """Fetches list of known Disease and Drug entities from Neo4j for UI suggestions."""
    client = Neo4jClient()
    if not client.is_online():
        return ["Đái tháo đường týp 2", "Cao huyết áp", "Viêm loét dạ dày", "Metformin", "Aspirin", "Ibuprofen"]
    query = """
    MATCH (n) WHERE n:DISEASE OR n:DRUG OR n:DRUG_GROUP 
    RETURN DISTINCT n.name AS name 
    ORDER BY n.name ASC LIMIT 50
    """
    res = client.execute_query(query)
    return [r["name"] for r in res if r.get("name")]

# Main Header
st.title("🩺 MedGraph-VI: Tự động xây dựng Knowledge Graph Y tế từ Văn bản Tiếng Việt")
st.markdown("*Luận văn Thạc sĩ: Proof-of-Concept tích hợp Hybrid LLM, PhoBERT-CRF NER & Neo4j Database*")
st.divider()

# Sidebar controls
st.sidebar.header("⚙️ Cấu hình Môi trường")
if st.sidebar.button("🔄 Xóa Cache & Khởi tạo lại Engine", use_container_width=True):
    st.cache_resource.clear()
    st.cache_data.clear()
    st.sidebar.success("✅ Đã xóa toàn bộ Cache Streamlit!")
    st.rerun()

provider = st.sidebar.selectbox("LLM Provider", ["gemini", "openai", "anthropic", "mock"], index=0)
api_key_input = st.sidebar.text_input("API Key (để trống nếu dùng env key hoặc Mock)", type="password")

if api_key_input:
    os.environ["LLM_API_KEY"] = api_key_input
os.environ["LLM_PROVIDER"] = provider

st.sidebar.success(f"Chế độ hiện tại: **{provider.upper()}**")

# Sidebar: Feedback Statistics (A2)
st.sidebar.divider()
st.sidebar.markdown("### 📊 Thống kê Phản hồi Demo (A2)")
stats = get_feedback_stats()
st.sidebar.info(
    f"**Đã đánh giá:** {stats['total']} câu\n\n"
    f"👍 **Đúng:** {stats['correct']} ({stats['accuracy_pct']:.1f}%)\n\n"
    f"👎 **Sai:** {stats['incorrect']}"
)

# Sidebar: Question Session History (B1)
st.sidebar.divider()
st.sidebar.markdown("### 📜 Lịch sử câu hỏi trong phiên (B1)")
if "question_history" not in st.session_state:
    st.session_state.question_history = []

if st.session_state.question_history:
    for idx, q_hist in enumerate(reversed(st.session_state.question_history[-5:])):
        if st.sidebar.button(f"🔍 {q_hist[:25]}...", key=f"hist_btn_{idx}"):
            st.session_state.custom_query_input = q_hist
            st.session_state.selectbox_val = "-- Tự nhập câu hỏi --"
            st.rerun()
else:
    st.sidebar.caption("Chưa có lịch sử câu hỏi.")

# Cached QA Engine Loader
@st.cache_resource(show_spinner="Đang khởi tạo QA Engine & LLM Client...")
def get_qa_engine(llm_provider: str, api_key: str):
    logger.info(f"🔄 Creating new QAEngine instance for provider='{llm_provider}'")
    llm_client = LLMClient(provider=llm_provider, api_key=api_key)
    return QAEngine(llm_client=llm_client)

qa_engine = get_qa_engine(provider, api_key_input)
synthetic_data_map = load_synthetic_dataset()

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "💬 Hỏi Đáp Y Tế (KG-QA vs RAG)", 
    "🔍 Phân Tích Pipeline NLP (End-to-End)", 
    "📊 Coverage Dashboard", 
    "🕸️ Trực Quan Hóa Knowledge Graph"
])

# ====================================================
# TAB 1: QA Demo with Traceability & Feedback
# ====================================================
with tab1:
    st.subheader("Hỏi đáp Y tế dựa trên Knowledge Graph & So sánh RAG Baseline")
    
    sample_questions = [
        "Bệnh nhân Đái tháo đường týp 2 được kê thuốc gì?",
        "Thuốc nào điều trị Đái tháo đường týp 2?",
        "Bệnh nhân bị Viêm loét dạ dày chống chỉ định với thuốc gì?",
        "Thuốc Aspirin được chỉ định cho bệnh nhân mắc bệnh gì?",
        "Cao huyết áp có những triệu chứng lâm sàng nào?"
    ]
    
    # Initialize session state keys if not present
    if "custom_query_input" not in st.session_state:
        st.session_state.custom_query_input = ""
    if "selectbox_val" not in st.session_state:
        st.session_state.selectbox_val = "-- Tự nhập câu hỏi --"

    # Entity Autocomplete / Suggestions (B2)
    known_entities = get_autocomplete_entities()
    if known_entities:
        st.markdown("**💡 Gợi ý thực thể có trong Knowledge Graph (B2):**")
        sug_cols = st.columns(min(len(known_entities[:5]), 5))
        for idx, ent in enumerate(known_entities[:5]):
            with sug_cols[idx]:
                if st.button(f"📌 {ent}", key=f"sug_btn_{idx}"):
                    st.session_state.custom_query_input = f"Thuốc nào điều trị {ent}?" if "đường" in ent.lower() or "dạ dày" in ent.lower() or "huyết áp" in ent.lower() else f"Thuốc {ent} được chỉ định cho bệnh gì?"
                    st.session_state.selectbox_val = "-- Tự nhập câu hỏi --"
                    st.rerun()

    def on_selectbox_change():
        if st.session_state.selectbox_val != "-- Tự nhập câu hỏi --":
            st.session_state.custom_query_input = ""

    def on_custom_change():
        if st.session_state.custom_query_input.strip() != "":
            st.session_state.selectbox_val = "-- Tự nhập câu hỏi --"

    selected_sample = st.selectbox(
        "Chọn câu hỏi mẫu hoặc dùng ô bên dưới:",
        ["-- Tự nhập câu hỏi --"] + sample_questions,
        key="selectbox_val",
        on_change=on_selectbox_change
    )
    
    input_text_val = st.text_input(
        "Nhập câu hỏi y tế tiếng Việt:",
        key="custom_query_input",
        on_change=on_custom_change
    )
    
    # Prioritize custom query if it has content, otherwise use selected sample
    custom_val = input_text_val.strip()
    if custom_val != "":
        user_query = custom_val
    else:
        user_query = selected_sample
        
    st.info(f"🔍 Debug - câu hỏi đang xử lý: {user_query}")

    if st.button("🚀 Gửi Câu Hỏi", type="primary"):
        # Save to question history (B1)
        if user_query not in st.session_state.question_history:
            st.session_state.question_history.append(user_query)

        with st.spinner("Đang thực thi truy vấn Cypher trên Neo4j và tổng hợp câu trả lời..."):
            res = qa_engine.compare_answers(user_query)
            kg_res = res.get("kg_qa", {})
            rag_res = res.get("rag_baseline", {})
            
            st.session_state["last_qa_result"] = res

    # Render results if available in session state
    if "last_qa_result" in st.session_state:
        res = st.session_state["last_qa_result"]
        kg_res = res.get("kg_qa", {})
        rag_res = res.get("rag_baseline", {})
        query_asked = res.get("question", user_query)

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🕸️ Knowledge Graph QA (Text-to-Cypher)")
            st.info(f"**Câu trả lời:** {kg_res.get('answer', '')}")
            
            # TRACEABILITY DISPLAY (A1)
            source_sample_ids = kg_res.get("source_sample_ids", [])
            st.markdown("#### 📄 Nguồn gốc dữ liệu (Traceability - A1)")
            if source_sample_ids:
                st.caption("✨ **KG-QA vs RAG**: KG-QA trả lời NGẮN GỌN + truy vết CHÍNH XÁC 1-2 câu bệnh án nguồn, không cần đọc đoạn dài.")
                pop_cols = st.columns(len(source_sample_ids))
                for idx, sid in enumerate(source_sample_ids):
                    with pop_cols[idx]:
                        orig_text = synthetic_data_map.get(sid, "Không tìm thấy nguyên văn mẫu dữ liệu.")
                        with st.popover(f"📄 Nguồn: {sid}"):
                            st.markdown(f"**Mẫu dữ liệu gốc ({sid}):**")
                            st.write(orig_text)
            else:
                st.caption("ℹ️ Không tìm thấy ID nguồn trực tiếp trong kết quả truy vấn.")

            st.markdown("**Cypher Query được sinh ra:**")
            st.code(kg_res.get("cypher_query", ""), language="cypher")
            if kg_res.get("schema_source"):
                st.caption(f"📐 Schema được dùng: {kg_res.get('schema_source')}")

            
            graph_results = kg_res.get("graph_results", [])
            fallback_status = kg_res.get("fallback_status", "OK")
            node_info = kg_res.get("node_existence_info", [])

            if not graph_results:
                if fallback_status == "NODE_EXISTS_NO_RELATIONS":
                    st.warning("⚠️ **[Trạng thái: NO_DATA]** Thực thể y tế CÓ TỒN TẠI trong Knowledge Graph, nhưng chưa có dữ liệu quan hệ lâm sàng tương ứng.")
                elif fallback_status == "NODE_NOT_FOUND":
                    st.info("ℹ️ **[Trạng thái: NO_DATA / NOT_FOUND]** Không tìm thấy node Bệnh/Thuốc nào khớp với câu hỏi trong Knowledge Graph.")
                elif fallback_status == "QUERY_ERROR":
                    st.error("❌ **[Trạng thái: QUERY_ERROR - Lỗi Hệ Thống]** Truy vấn Cypher không thể thực thi. Chưa thể kết luận dữ liệu.")
                else:
                    st.warning("⚠️ **[Trạng thái: NO_DATA]** Kết quả truy vấn Graph DB rỗng.")
            else:
                st.success(f"✅ **[Trạng thái: FOUND]** Đã tìm thấy {len(graph_results)} bản ghi quan hệ phù hợp trong Knowledge Graph.")

            st.markdown("**Kết quả từ Graph DB:**")
            st.json(graph_results)

            # FEEDBACK BUTTONS FOR KG-QA (A2)
            st.markdown("**Đánh giá câu trả lời KG-QA (A2):**")
            fb_col1, fb_col2 = st.columns(2)
            with fb_col1:
                if st.button("👍 Đúng (KG-QA)", key=f"btn_kg_correct_{query_asked}"):
                    save_user_feedback(query_asked, "KG-QA", kg_res.get('answer', ''), "correct", kg_res.get('cypher_query', ''))
                    st.toast("Đã ghi nhận phản hồi ĐÚNG cho KG-QA!", icon="✅")
                    st.rerun()
            with fb_col2:
                if st.button("👎 Sai (KG-QA)", key=f"btn_kg_incorrect_{query_asked}"):
                    save_user_feedback(query_asked, "KG-QA", kg_res.get('answer', ''), "incorrect", kg_res.get('cypher_query', ''))
                    st.toast("Đã ghi nhận phản hồi SAI cho KG-QA!", icon="❌")
                    st.rerun()

            with st.expander("🔍 Chi tiết Debug Audit Log", expanded=False):
                st.json({
                    "fallback_status": fallback_status,
                    "fallback_used": kg_res.get("fallback_used", False),
                    "node_existence_info": node_info,
                    "data_source": kg_res.get("data_source"),
                    "schema_source": kg_res.get("schema_source"),
                    "schema_pruned": kg_res.get("schema_pruned")
                })

        with col2:
            st.markdown("### 📄 RAG Baseline (Semantic Search)")
            st.warning(f"**Câu trả lời:** {rag_res.get('answer', '')}")
            
            st.markdown("**Đoạn văn bản truy xuất (Contexts):**")
            for chunk in rag_res.get('retrieved_chunks', []):
                st.write(f"- {chunk}")

            # FEEDBACK BUTTONS FOR RAG (A2)
            st.markdown("**Đánh giá câu trả lời RAG Baseline (A2):**")
            rfb_col1, rfb_col2 = st.columns(2)
            with rfb_col1:
                if st.button("👍 Đúng (RAG)", key=f"btn_rag_correct_{query_asked}"):
                    save_user_feedback(query_asked, "RAG", rag_res.get('answer', ''), "correct")
                    st.toast("Đã ghi nhận phản hồi ĐÚNG cho RAG!", icon="✅")
                    st.rerun()
            with rfb_col2:
                if st.button("👎 Sai (RAG)", key=f"btn_rag_incorrect_{query_asked}"):
                    save_user_feedback(query_asked, "RAG", rag_res.get('answer', ''), "incorrect")
                    st.toast("Đã ghi nhận phản hồi SAI cho RAG!", icon="❌")
                    st.rerun()

        # EXPORT ANSWER REPORT (B3)
        st.divider()
        report_md = f"""# Báo cáo So sánh Trả lời Y tế (MedGraph-VI)
**Thời gian tạo:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Câu hỏi người dùng
> {query_asked}

## 2. Kết quả Knowledge Graph QA (KG-QA)
- **Câu trả lời:** {kg_res.get('answer', '')}
- **Cypher Query:**
```cypher
{kg_res.get('cypher_query', '')}
```
- **Nguồn gốc dữ liệu (Traceability):** {', '.join(source_sample_ids) if source_sample_ids else 'N/A'}

## 3. Kết quả RAG Baseline
- **Câu trả lời:** {rag_res.get('answer', '')}
- **Retrieved Context Chunks:**
{chr(10).join(['- ' + c for c in rag_res.get('retrieved_chunks', [])])}
"""
        st.download_button(
            label="📥 Tải báo cáo câu trả lời (.md) (B3)",
            data=report_md,
            file_name=f"medgraph_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )

# ====================================================
# TAB 2: NLP Pipeline Inspection
# ====================================================
with tab2:
    st.subheader("Phân tích từng bước Pipeline NLP Y tế")

    with st.expander("📊 Schema đồ thị hiện tại", expanded=False):
        client_ui = Neo4jClient()
        if client_ui.is_online():
            try:
                schema = client_ui.get_graph_schema()
                ts_val = client_ui._schema_cache_time
                ts_str = datetime.datetime.fromtimestamp(ts_val).strftime("%Y-%m-%d %H:%M:%S") if ts_val else "N/A"
                st.write(f"🕐 Schema đọc từ Neo4j lúc: {ts_str}")


                counts_res = client_ui.execute_query("MATCH (n) RETURN labels(n)[0] AS label, count(*) AS count")
                count_map = {r["label"]: r["count"] for r in counts_res if r.get("label")}

                node_table = []
                for n in schema.get("nodes", []):
                    lbl = n.get("label", "")
                    node_table.append({
                        "Label": lbl,
                        "Số node": count_map.get(lbl, 0),
                        "Thuộc tính chính": ", ".join(n.get("properties", []))
                    })

                rel_table = []
                for r in schema.get("relationships", []):
                    rel_table.append({
                        "Type": r.get("type", ""),
                        "From": r.get("from", ""),
                        "To": r.get("to", ""),
                        "Thuộc tính quan trọng": ", ".join(r.get("properties", []))
                    })

                st.markdown("##### Bảng 1 — Nodes")
                st.dataframe(node_table, use_container_width=True)

                st.markdown("##### Bảng 2 — Relationships")
                st.dataframe(rel_table, use_container_width=True)

                if st.button("🔄 Làm mới Schema"):
                    client_ui.get_graph_schema(force_refresh=True)
                    st.toast("Đã làm mới schema từ Neo4j!", icon="✅")
                    st.rerun()
            except Exception as e_sc:
                st.warning(f"⚠️ Không thể đọc schema từ Neo4j: {e_sc}")
        else:
            st.warning("⚠️ Neo4j đang offline. Không thể hiển thị schema đồ thị động.")

    input_text = st.text_area(
        "Nhập văn bản y tế lâm sàng:",
        "Bệnh nhân nam 54 tuổi có tiền sử Đái tháo đường týp 2 và Cao huyết áp 3 năm nay. Hiện tại không thấy dấu hiệu Viêm phổi. Bác sĩ chỉ định Paracetamol 500mg và Metformin."
    )

    
    if st.button("🔬 Phân Tích Pipeline", type="secondary"):
        with st.spinner("Đang chạy 3-source NER Ensemble, ConText Negation, RE và Entity Linking..."):
            # 1. NER
            ensemble = NEREnsemble()
            raw_ents = ensemble.extract_entities(input_text)
            
            # 2. ConText
            context_proc = ConTextProcessor()
            processed_ents = context_proc.process_entities(input_text, raw_ents)
            
            # 3. RE
            re_extractor = LLMRelationExtractor()
            triples = re_extractor.extract_relations(input_text, processed_ents)
            
            # 4. Entity Linking
            icd = ICD10Linker()
            rx = RxNormLinker()
            
            linked_ents = []
            for e in processed_ents:
                if e["type"] == "DISEASE":
                    link_info = icd.link_disease(e["entity"])
                elif e["type"] in ("DRUG", "DRUG_GROUP"):
                    link_info = rx.link_drug(e["entity"])
                else:
                    link_info = {"standard_name": get_canonical_name(e["entity"]), "code": None, "method": "unlinked"}
                e["linking"] = link_info
                linked_ents.append(e)

            st.markdown("#### 1. Thực thể nhận dạng (NER 3-Source Ensemble + Entity Linking)")
            st.dataframe(linked_ents)

            st.markdown("#### 2. Quan hệ rút ra (Relation Extraction Triples)")
            st.json(triples)

# ====================================================
# TAB 3: Coverage Dashboard (A3)
# ====================================================
with tab3:
    st.subheader("📊 Coverage Dashboard - Đánh giá Độ phủ Dữ liệu Knowledge Graph (A3)")
    st.markdown("Thống kê mức độ đầy đủ của các thực thể và quan hệ lâm sàng trong Neo4j Database.")

    if st.button("🔄 Cập nhật/Chạy Coverage Analysis"):
        st.cache_data.clear()

    @st.cache_data(ttl=300)
    def compute_coverage_metrics():
        client = Neo4jClient()
        if not client.is_online():
            return None
        
        gaps = get_coverage_gaps()
        
        # Query total node counts
        disease_res = client.execute_query("MATCH (d:DISEASE) RETURN count(d) AS cnt")
        drug_res = client.execute_query("MATCH (d) WHERE d:DRUG OR d:DRUG_GROUP RETURN count(d) AS cnt")
        symptom_res = client.execute_query("MATCH (s:SYMPTOM) RETURN count(s) AS cnt")
        
        total_diseases = disease_res[0]["cnt"] if disease_res else 0
        total_drugs = drug_res[0]["cnt"] if drug_res else 0
        total_symptoms = symptom_res[0]["cnt"] if symptom_res else 0

        # Query criteria met
        dis_criteria_query = """
        MATCH (d:DISEASE)
        OPTIONAL MATCH (d)-[:HAS_SYMPTOM]->(s:SYMPTOM)
        WITH d, count(s) AS s_count
        OPTIONAL MATCH (d)<-[:PRESCRIBED_FOR|TREATS]-(drug)
        WITH d, s_count, count(drug) AS t_count
        WHERE s_count >= 2 AND t_count >= 1
        RETURN count(d) AS qualified_count
        """
        qualified_res = client.execute_query(dis_criteria_query)
        qualified_diseases = qualified_res[0]["qualified_count"] if qualified_res else 0

        drug_conn_query = """
        MATCH (d) WHERE d:DRUG OR d:DRUG_GROUP
        MATCH (d)-[:PRESCRIBED_FOR|TREATS|CONTRAINDICATED_FOR]-(t)
        RETURN count(DISTINCT d) AS conn_count
        """
        conn_res = client.execute_query(drug_conn_query)
        connected_drugs = conn_res[0]["conn_count"] if conn_res else 0

        dis_pct = (qualified_diseases / max(1, total_diseases)) * 100
        drug_pct = (connected_drugs / max(1, total_drugs)) * 100

        return {
            "total_diseases": total_diseases,
            "total_drugs": total_drugs,
            "total_symptoms": total_symptoms,
            "qualified_diseases": qualified_diseases,
            "dis_pct": dis_pct,
            "connected_drugs": connected_drugs,
            "drug_pct": drug_pct,
            "gaps": gaps
        }

    cov_data = compute_coverage_metrics()

    if cov_data is None:
        st.error("❌ Neo4j đang offline. Không thể tải metrics Coverage Dashboard.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Tổng Thực Thể", f"{cov_data['total_diseases'] + cov_data['total_drugs'] + cov_data['total_symptoms']}")
            st.caption(f"Bệnh: {cov_data['total_diseases']} | Thuốc: {cov_data['total_drugs']} | Triệu chứng: {cov_data['total_symptoms']}")
        with m2:
            st.metric("Bệnh đạt chuẩn tiêu chí", f"{cov_data['qualified_diseases']}/{cov_data['total_diseases']}", f"{cov_data['dis_pct']:.1f}%")
            st.caption("Tiêu chí: ≥2 triệu chứng & ≥1 điều trị")
        with m3:
            st.metric("Thuốc không mồ côi", f"{cov_data['connected_drugs']}/{cov_data['total_drugs']}", f"{cov_data['drug_pct']:.1f}%")
            st.caption("Có liên kết chỉ định/chống chỉ định")
        with m4:
            st.metric("Coverage Gaps còn lại", f"{len(cov_data['gaps'])} gaps")
            st.caption("Cần bổ sung qua expansion loop")

        st.divider()
        st.markdown("#### 📈 So sánh Độ phủ Dữ liệu hiện tại")
        chart_data = {
            "Chỉ số": ["Tỷ lệ Bệnh Đạt Chuẩn (%)", "Tỷ lệ Thuốc Đã Kết Nối (%)"],
            "Độ phủ (%)": [round(cov_data['dis_pct'], 1), round(cov_data['drug_pct'], 1)]
        }
        st.bar_chart(data=chart_data, x="Chỉ số", y="Độ phủ (%)")

        with st.expander("📋 Chi tiết danh sách Coverage Gaps cần bổ sung", expanded=False):
            st.dataframe(cov_data['gaps'])

# ====================================================
# TAB 4: Graph Visualization with Filters (C1)
# ====================================================
with tab4:
    st.subheader("🕸️ Trực quan hóa Knowledge Graph có Bộ lọc (C1)")
    st.write("Bộ lọc cho phép tùy chỉnh nhóm nút và loại quan hệ cần hiển thị:")

    f_col1, f_col2 = st.columns(2)
    with f_col1:
        selected_nodes = st.multiselect(
            "Chọn loại Node (Node Labels):",
            ["DISEASE", "DRUG", "DRUG_GROUP", "SYMPTOM", "PROCEDURE"],
            default=["DISEASE", "DRUG", "SYMPTOM"]
        )
    with f_col2:
        selected_rels = st.multiselect(
            "Chọn loại Quan hệ (Relationship Types):",
            ["PRESCRIBED_FOR", "TREATS", "CONTRAINDICATED_FOR", "HAS_SYMPTOM", "CAUSES"],
            default=["PRESCRIBED_FOR", "TREATS", "CONTRAINDICATED_FOR", "HAS_SYMPTOM"]
        )

    client = Neo4jClient()
    if not client.is_online():
        st.warning("⚠️ Neo4j đang offline. Hiển thị bảng mẫu tĩnh:")
        sample_nodes = [
            {"head": "Paracetamol", "relation": "TREATS", "tail": "Viêm họng cấp", "source": "syn_001"},
            {"head": "Metformin", "relation": "PRESCRIBED_FOR", "tail": "Đái tháo đường týp 2", "source": "syn_004"},
            {"head": "Ibuprofen", "relation": "CONTRAINDICATED_FOR", "tail": "Viêm loét dạ dày", "source": "syn_003"},
            {"head": "Aspirin", "relation": "PRESCRIBED_FOR", "tail": "Cơn đau thắt ngực", "source": "syn_002"}
        ]
        st.table(sample_nodes)
    else:
        if not selected_nodes or not selected_rels:
            st.info("Vui lòng chọn ít nhất 1 loại Node và 1 loại Quan hệ.")
        else:
            filter_cypher = """
            MATCH (h)-[r]->(t)
            WHERE any(l IN labels(h) WHERE l IN $nodes)
              AND type(r) IN $rels
              AND any(l IN labels(t) WHERE l IN $nodes)
            RETURN h.name AS `Nút Đầu (Head)`, 
                   labels(h)[0] AS `Loại Head`, 
                   type(r) AS `Quan Hệ (Relation)`, 
                   t.name AS `Nút Đích (Tail)`, 
                   labels(t)[0] AS `Loại Tail`,
                   r.source_sample_id AS `Nguồn Dữ Liệu`
            LIMIT 100
            """
            graph_data = client.execute_query(filter_cypher, {"nodes": selected_nodes, "rels": selected_rels})
            st.success(f"🔍 Đã tìm thấy {len(graph_data)} bộ 3 quan hệ (triples) phù hợp bộ lọc.")
            st.dataframe(graph_data, use_container_width=True)
