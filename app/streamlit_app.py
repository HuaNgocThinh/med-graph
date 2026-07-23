"""
Streamlit Web Application for MedGraph-VI.
Interactive Thesis Demo for Vietnamese Medical Knowledge Graph Construction and Question Answering.
"""

import streamlit as st
import json
import logging
import os
import sys
from pathlib import Path

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

st.set_page_config(
    page_title="MedGraph-VI | Medical Knowledge Graph Demo",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 MedGraph-VI: Tự động xây dựng Knowledge Graph Y tế từ Văn bản Tiếng Việt")
st.markdown("*Luận văn Thạc sĩ: Proof-of-Concept tích hợp Hybrid LLM, PhoBERT-CRF NER & Neo4j Database*")
st.divider()

# Sidebar controls
st.sidebar.header("⚙️ Cấu hình Môi trường")
provider = st.sidebar.selectbox("LLM Provider", ["gemini", "openai", "anthropic", "mock"], index=0)
api_key_input = st.sidebar.text_input("API Key (để trống nếu dùng env key hoặc Mock)", type="password")

if api_key_input:
    os.environ["LLM_API_KEY"] = api_key_input
os.environ["LLM_PROVIDER"] = provider

st.sidebar.success(f"Chế độ hiện tại: **{provider.upper()}**")

# 2. Cached QA Engine Loader (invalidates when provider or api_key changes)
@st.cache_resource(show_spinner="Đang khởi tạo QA Engine & LLM Client...")
def get_qa_engine(llm_provider: str, api_key: str):
    logger.info(f"🔄 Creating new QAEngine instance for provider='{llm_provider}'")
    llm_client = LLMClient(provider=llm_provider, api_key=api_key)
    return QAEngine(llm_client=llm_client)

qa_engine = get_qa_engine(provider, api_key_input)

# Main tabs
tab1, tab2, tab3 = st.tabs(["💬 Hỏi Đáp Y Tế (KG-QA vs RAG)", "🔍 Phân Tích Pipeline NLP (End-to-End)", "🕸️ Trực Quan Hóa Knowledge Graph"])

# TAB 1: QA Demo
with tab1:
    st.subheader("Hỏi đáp Y tế dựa trên Knowledge Graph & So sánh RAG Baseline")
    
    sample_questions = [
        "Thuốc nào điều trị Đái tháo đường týp 2?",
        "Bệnh nhân bị Viêm loét dạ dày chống chỉ định với thuốc gì?",
        "Thuốc Aspirin 81mg được chỉ định cho bệnh nhân mắc bệnh gì?",
        "Cao huyết áp có những triệu chứng lâm sàng nào?"
    ]
    
    # Initialize session state keys if not present
    if "custom_query_input" not in st.session_state:
        st.session_state.custom_query_input = ""
    if "selectbox_val" not in st.session_state:
        st.session_state.selectbox_val = "-- Tự nhập câu hỏi --"

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
        with st.spinner("Đang thực thi truy vấn Cypher trên Neo4j và tổng hợp câu trả lời..."):
            res = qa_engine.compare_answers(user_query)
            kg_res = res.get("kg_qa", {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🕸️ Knowledge Graph QA (Text-to-Cypher)")
                st.info(f"**Câu trả lời:** {kg_res.get('answer', '')}")
                
                st.markdown("**Cypher Query được sinh ra:**")
                st.code(kg_res.get("cypher_query", ""), language="cypher")
                
                graph_results = kg_res.get("graph_results", [])
                fallback_status = kg_res.get("fallback_status", "OK")
                node_info = kg_res.get("node_existence_info", [])

                # 4. Handle Empty Results in Streamlit UI cleanly
                if not graph_results:
                    if fallback_status == "NODE_EXISTS_NO_RELATIONS":
                        st.warning("⚠️ **Không có quan hệ trong DB:** Thực thể y tế CÓ TỒN TẠI trong Knowledge Graph, nhưng chưa có dữ liệu quan hệ lâm sàng tương ứng cho câu hỏi này.")
                    elif fallback_status == "NODE_NOT_FOUND":
                        st.error("❌ **Thực thể không tồn tại trong DB:** Không tìm thấy node Bệnh/Thuốc nào khớp với câu hỏi trong Knowledge Graph (chưa được link hoặc sai tên).")
                    else:
                        st.warning("⚠️ Kết quả truy vấn Graph DB rỗng.")
                else:
                    st.success(f"✅ Đã tìm thấy {len(graph_results)} bản ghi quan hệ phù hợp trong Knowledge Graph.")

                st.markdown("**Kết quả từ Graph DB:**")
                st.json(graph_results)

                with st.expander("🔍 Chi tiết Debug Audit Log (Node Existence & Fallback Status)", expanded=False):
                    st.json({
                        "fallback_status": fallback_status,
                        "fallback_used": kg_res.get("fallback_used", False),
                        "node_existence_info": node_info,
                        "data_source": kg_res.get("data_source")
                    })

            with col2:
                st.markdown("### 📄 RAG Baseline (Semantic Search)")
                st.warning(f"**Câu trả lời:** {res['rag_baseline']['answer']}")
                
                st.markdown("**Đoạn văn bản truy xuất (Contexts):**")
                for chunk in res['rag_baseline']['retrieved_chunks']:
                    st.write(f"- {chunk}")

# TAB 2: NLP Pipeline Inspection
with tab2:
    st.subheader("Phân tích từng bước Pipeline NLP Y tế")
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
                    link_info = {"standard_name": get_canonical_name(e["entity"]), "code": "N/A", "method": "unlinked"}
                e["linking"] = link_info
                linked_ents.append(e)

            st.markdown("#### 1. Thực thể nhận dạng (NER 3-Source Ensemble + Entity Linking)")
            st.dataframe(linked_ents)

            st.markdown("#### 2. Quan hệ rút ra (Relation Extraction Triples)")
            st.json(triples)

# TAB 3: Graph Visualization
with tab3:
    st.subheader("Trực quan hóa Subgraph Y tế")
    st.write("Dữ liệu các nút và cạnh tiêu biểu trong Neo4j Database:")
    
    sample_nodes = [
        {"head": "Paracetamol 500mg", "relation": "TREATS", "tail": "Viêm họng cấp"},
        {"head": "Metformin", "relation": "PRESCRIBED_FOR", "tail": "Đái tháo đường týp 2"},
        {"head": "Ibuprofen", "relation": "CONTRAINDICATED_FOR", "tail": "Viêm loét dạ dày"},
        {"head": "Aspirin 81mg", "relation": "PRESCRIBED_FOR", "tail": "Cơn đau thắt ngực"}
    ]
    st.table(sample_nodes)
