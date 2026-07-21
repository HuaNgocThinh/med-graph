"""
Streamlit Web Application for MedGraph-VI.
Interactive Thesis Demo for Vietnamese Medical Knowledge Graph Construction and Question Answering.
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path

# Add project root to Python module path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.qa.qa_engine import QAEngine
from src.graph.neo4j_client import Neo4jClient
from src.ner.ner_ensemble import NEREnsemble
from src.relation_extraction.llm_re import LLMRelationExtractor
from src.negation_temporal.context_processor import ConTextProcessor
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.rxnorm_linker import RxNormLinker

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

# Main tabs
tab1, tab2, tab3 = st.tabs(["💬 Hỏi Đáp Y Tế (KG-QA vs RAG)", "🔍 Phân Tích Pipeline NLP (End-to-End)", "🕸️ Trực Quan Hóa Knowledge Graph"])

# Initializer helpers
def load_qa_engine():
    return QAEngine()

qa_engine = load_qa_engine()

# TAB 1: QA Demo
with tab1:
    st.subheader("Hỏi đáp Y tế dựa trên Knowledge Graph & So sánh RAG Baseline")
    
    sample_questions = [
        "Thuốc nào điều trị Đái tháo đường týp 2?",
        "Bệnh nhân bị Viêm loét dạ dày chống chỉ định với thuốc gì?",
        "Thuốc Aspirin 81mg được chỉ định cho bệnh nhân mắc bệnh gì?",
        "Cao huyết áp có những triệu chứng lâm sàng nào?"
    ]
    
    selected_sample = st.selectbox("Chọn câu hỏi mẫu hoặc dùng ô bên dưới:", ["-- Tự nhập câu hỏi --"] + sample_questions)
    input_text_val = st.text_input("Nhập câu hỏi y tế tiếng Việt:", "Bệnh nhân bị Viêm loét dạ dày chống chỉ định với thuốc gì?")
    
    if selected_sample != "-- Tự nhập câu hỏi --":
        user_query = selected_sample
    else:
        user_query = input_text_val
        
    st.info(f"🔍 Debug - câu hỏi đang xử lý: {user_query}")

    if st.button("🚀 Gửi Câu Hỏi", type="primary"):
        with st.spinner("Đang thực thi truy vấn Cypher trên Neo4j và tổng hợp câu trả lời..."):
            res = qa_engine.compare_answers(user_query)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🕸️ Knowledge Graph QA (Text-to-Cypher)")
                st.info(f"**Câu trả lời:** {res['kg_qa']['answer']}")
                
                st.markdown("**Cypher Query được sinh ra:**")
                st.code(res['kg_qa']['cypher_query'], language="cypher")
                
                st.markdown("**Kết quả từ Graph DB:**")
                st.json(res['kg_qa']['graph_results'])
                
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
                elif e["type"] == "DRUG":
                    link_info = rx.link_drug(e["entity"])
                else:
                    link_info = {"standard_name": e["entity"], "code": "N/A", "method": "unlinked"}
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
        {"head": "Metformin", "relation": "TREATS", "tail": "Đái tháo đường týp 2"},
        {"head": "Ibuprofen", "relation": "CONTRAINDICATED_FOR", "tail": "Viêm loét dạ dày"},
        {"head": "Aspirin 81mg", "relation": "PRESCRIBED_FOR", "tail": "Cơn đau thắt ngực"}
    ]
    st.table(sample_nodes)
