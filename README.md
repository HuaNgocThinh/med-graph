# MedGraph-VI: Tự động Xây dựng Knowledge Graph Y Tế Tiếng Việt bằng LLM

---

## 📌 1. Giới thiệu Kiến trúc & Thiết kế Pipeline

Dự án **MedGraph-VI** là một giải pháp Proof-of-Concept (POC) phục vụ bảo vệ luận văn Thạc sĩ với mục tiêu tự động trích xuất thực thể, quan hệ y tế từ văn bản tiếng Việt và xây dựng cơ sở dữ liệu đồ thị tri thức (Knowledge Graph) trên Neo4j.

### Chiến lược Hybrid
- **Chiến lược Hybrid**:
  - **Local CPU Execution**: Chạy các tác vụ NLP nhỏ/pretrained nhẹ (PhoBERT-CRF NER sequence tagger, ConText Negation rule engine, RapidFuzz string matcher, Local ICD-10 & RxNorm dictionary mapping).
  - **LLM API Layer**: Sử dụng LLM (Gemini / OpenAI / Anthropic) thông qua lớp trừu tượng `LLMClient` cho các tác vụ cần lập luận phức tạp (Synthetic Data Generation, Few-shot Relation Extraction, Text-to-Cypher QA).
  - **Mock LLM Fallback**: Hỗ trợ chế độ giả lập offline để thử nghiệm và chạy unit test end-to-end mà không bắt buộc có API key ngay lập tức.

---

## 🏗️ 2. Cấu trúc Thư mục Dự án

```
medical-kg-vi/ (MedGraph)
├── README.md                      # Hướng dẫn cài đặt, vận hành & tài liệu luận văn
├── .env.example                   # Biến môi trường mẫu
├── requirements.txt               # Thư viện phụ thuộc Python 3.10+
├── docker-compose.yml             # Neo4j Community Edition Service
├── run_pipeline.py                # Script chạy toàn bộ pipeline End-to-End
├── data/
│   ├── raw/                       # Văn bản y tế gốc
│   ├── synthetic/                 # Dữ liệu synthetic tự sinh (Giai đoạn A)
│   ├── annotated/                 # Tập test gán nhãn tay (100-150 câu) (Giai đoạn I)
│   └── dictionaries/              # Từ điển ICD-10 & RxNorm tiếng Việt
│       ├── icd10_vi.json
│       └── rxnorm_vi.json
├── src/
│   ├── config.py                  # Cấu hình chung hệ thống
│   ├── llm_client.py              # Lớp trừu tượng đa provider (Gemini, OpenAI, Anthropic, Mock)
│   ├── data_generation/
│   │   └── synthetic_generator.py # Giai đoạn A: Sinh dữ liệu synthetic
│   ├── ner/                       # Giai đoạn B: NER 3 nguồn & Ensemble
│   │   ├── dictionary_ner.py
│   │   ├── phobert_crf_ner.py
│   │   ├── llm_ner.py
│   │   └── ner_ensemble.py
│   ├── negation_temporal/         # Giai đoạn C: Vietnamese ConText rules
│   │   └── context_processor.py
│   ├── relation_extraction/       # Giai đoạn D: Relation Extraction
│   │   ├── llm_re.py
│   │   └── rule_based_re.py       # Baseline pattern matching
│   ├── entity_linking/            # Giai đoạn E: Entity Linking
│   │   ├── icd10_linker.py
│   │   ├── rxnorm_linker.py       # NIH RxNav API + local fallback
│   │   └── fuzzy_matcher.py
│   ├── graph/                     # Giai đoạn F & G: Neo4j Builder & Cleaner
│   │   ├── neo4j_client.py
│   │   ├── graph_builder.py
│   │   └── graph_cleaner.py
│   └── qa/                        # Giai đoạn H: Text-to-Cypher & RAG Baseline
│       ├── text_to_cypher.py
│       ├── rag_baseline.py
│       └── qa_engine.py
├── evaluation/                    # Giai đoạn I: Script Đánh giá Chi tiết
│   ├── evaluate_ner.py
│   ├── evaluate_re.py
│   ├── evaluate_entity_linking.py
│   ├── evaluate_qa.py
│   └── error_analysis/            # Log phân loại lỗi
├── app/
│   └── streamlit_app.py           # Giai đoạn J: Streamlit Web UI Demo
└── tests/                         # Pytest Unit Tests
    ├── test_ner.py
    ├── test_relation_extraction.py
    ├── test_entity_linking.py
    └── test_negation.py
```

---

## ⚙️ 3. Hướng dẫn Cài đặt & Chuẩn bị Môi trường

### Bước 1: Tạo môi trường ảo Python 3.10+
```bash
python -m venv venv
# Mở môi trường ảo (Windows PowerShell):
.\venv\Scripts\Activate.ps1
```

### Bước 2: Cài đặt Dependencies
```bash
pip install -r requirements.txt
```

### Bước 3: Cấu hình File Môi trường `.env`
Sao chép mẫu `.env.example` thành `.env`:
```bash
cp .env.example .env
```
Điền `LLM_PROVIDER` (gemini / openai / anthropic / mock) và `LLM_API_KEY` tương ứng vào `.env`.

### Bước 4: Khởi động Neo4j Database bằng Docker
```bash
docker-compose up -d
```
Neo4j Web UI sẽ sẵn sàng tại: `http://localhost:7474` (User: `neo4j`, Password: `medgraph_secret_password`).

---

## 🚀 4. Hướng dẫn Chạy Pipeline & Đánh Giá

### 1. Chạy Toàn Bộ Pipeline End-to-End (Giai đoạn A $\rightarrow$ H)
```bash
python run_pipeline.py
```

### 2. Chạy Bộ Unit Test (Pytest)
```bash
pytest tests/ -v
```

### 3. Chạy Đánh Giá Chi Tiết (Giai đoạn I Evaluation Suite)
```bash
# Đánh giá NER Ensemble
python evaluation/evaluate_ner.py

# Đánh giá Relation Extraction (Tiêu chí F1 >= 0.6)
python evaluation/evaluate_re.py

# Đánh giá Entity Linking (Tiêu chí Độ chính xác >= 70%)
python evaluation/evaluate_entity_linking.py

# Đánh giá Hỏi đáp KG-QA vs RAG Baseline (Tiêu chí >= 60%)
python evaluation/evaluate_qa.py
```
Các kết quả phân tích lỗi sẽ tự động được ghi vào thư mục `evaluation/error_analysis/`.

### 4. Khởi động Web App Demo (Streamlit)
```bash
streamlit run app/streamlit_app.py
```

---

