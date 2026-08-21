# MedGraph-VI: Hệ thống Tự động Xây dựng Knowledge Graph Y tế Tiếng Việt & Hỏi đáp Tri thức (KG-QA)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/Hugging%20Face-Transformers-FFD21E.svg)](https://huggingface.co/)
[![PhoBERT](https://img.shields.io/badge/Model-PhoBERT--base--v2-green.svg)](https://huggingface.co/vinai/phobert-base-v2)
[![Neo4j](https://img.shields.io/badge/Database-Neo4j%205.x-008CC1.svg)](https://neo4j.com/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)]()

---

## 📌 1. Tổng quan & Mục tiêu Dự án (Overview & Core Goals)

**MedGraph-VI** (**Medical Knowledge Graph System for Vietnamese**) là giải pháp NLP End-to-End toàn diện nhằm tự động khai phá tri thức y tế từ văn bản lâm sàng tiếng Việt không cấu trúc (bệnh án, lịch sử khám bệnh, triệu chứng lâm sàng) và chuẩn hóa thành cơ sở dữ liệu đồ thị tri thức (Knowledge Graph) lưu trữ trên **Neo4j**. Hệ thống đóng vai trò làm nền tảng vững chắc cho mô hình hỏi đáp y tế thông minh dựa trên đồ thị tri thức (**KG-QA**).

### 🎯 Mục tiêu cốt lõi:
- **Tự động hóa luồng NLP y tế (End-to-End Medical NLP Pipeline):** Tự động bóc tách các thực thể y tế (Bệnh, Thuốc, Triệu chứng, Quy trình y tế) và các mối quan hệ đa chiều giữa chúng.
- **Giải quyết bài toán Mất cân bằng dữ liệu & Distribution Shift:** Khắc phục thiên kiến nhãn `NONE` (NONE-label bias) trong Relation Extraction (RE) thông qua kỹ thuật sinh dữ liệu phức hợp với LLM và Oversampling.
- **Chuẩn hóa Thực thể Quốc tế (Entity Linking):** Ánh xạ các thực thể tiếng Việt về mã định danh tiêu chuẩn y tế quốc tế (**ICD-10** cho bệnh lý và **RxNorm** cho dược phẩm).
- **Hỗ trợ Truy vấn Tri thức Y tế & RAG:** Cung cấp giao diện trực quan Streamlit và công cụ dịch câu hỏi tự nhiên sang câu lệnh Cypher (Text-to-Cypher) phục vụ tra cứu chính xác.

---

## 🏗️ 2. Kiến trúc Hệ thống & Luồng Dữ liệu (System Architecture & Data Flow)

Hệ thống được thiết kế theo kiến trúc **Hybrid (Mô hình Kép)** kết hợp giữa **Mô hình học sâu bản địa (Local Fine-tuned PhoBERT-base)** vận hành trên CPU/GPU local và **Lớp trừu tượng API LLM (LLM API Layer)** phục vụ sinh dữ liệu và lập luận phức tạp.

```
                                  +------------------------------------+
                                  |   Văn bản Y tế Tiếng Việt Gốc     |
                                  | (Bệnh án, Triệu chứng lâm sàng)    |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | 1. Tiền xử lý & Tách từ (pyvi)     |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | 2. Named Entity Recognition (NER)  |
                                  |  PhoBERT-base (vinai/phobert-base) |
                                  |  (DISEASE, DRUG, SYMPTOM, PROC)    |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | 3. Vietnamese ConText Rules Engine |
                                  |    (Lọc Negation & Temporal State) |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | 4. Clinical Pair Pairing & RE      |
                                  |    PhoBERT Classification Model    |
                                  | (TREATS, CAUSES, HAS_SYMPTOM, ...) |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | 5. Entity Normalization & Linking  |
                                  |  - ICD-10 Matcher (Diseases)       |
                                  |  - RxNorm / RxNav API (Drugs)      |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | 6. Knowledge Graph Construction    |
                                  |    Neo4j Database (Cypher Engine)  |
                                  +-----------------+------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  | 7. Interactive UI & KG-QA System   |
                                  |    Streamlit App / Text-to-Cypher  |
                                  +------------------------------------+
```

### 🧬 Chi tiết các tầng trong Pipeline:
1. **Stage A - Data Augmentation & Synthesis:** Sinh dữ liệu bệnh án phức hợp với LLM API (`LLMClient`) để gia tăng dữ liệu cho các mẫu hiếm.
2. **Stage B - Named Entity Recognition (NER):** Nhận dạng 4 loại thực thể cốt lõi: `DISEASE` (Bệnh lý), `DRUG` (Thuốc/Dược phẩm), `SYMPTOM` (Triệu chứng), và `PROCEDURE` (Quy trình chẩn đoán/điều trị) sử dụng `PhoBERT-base-v2`.
3. **Stage C - Negation & Temporal Processing:** Áp dụng bộ quy tắc **Vietnamese ConText** loại bỏ các thực thể/triệu chứng bị phủ định (ví dụ: *"bệnh nhân không bị đau ngực"*) hoặc đã thuộc về quá khứ.
4. **Stage D - Relation Extraction (RE):** Phân loại quan hệ giữa các cặp thực thể lâm sàng thành 7 loại nhãn: `TREATS`, `CAUSES`, `HAS_SYMPTOM`, `PRESCRIBED_FOR`, `PERFORMED_FOR`, `CONTRAINDICATED_FOR`, và `NONE`.
5. **Stage E - Entity Linking & Normalization:** Ánh xạ thực thể trích xuất được vào từ điển `icd10_vi.json` và `rxnorm_vi.json` sử dụng kỹ thuật RapidFuzz matching và NIH RxNav API.
6. **Stage F/G - Neo4j Graph Builder & Cleaner:** Tự động tạo Node (`Disease`, `Drug`, `Symptom`, `Procedure`) và Edge (Relationships) trên Neo4j với đầy đủ thuộc tính định danh và nguồn gốc mẫu (`source_sample_id`).
7. **Stage H/J - Knowledge Graph QA & Streamlit Web App:** Giao diện trực quan hóa đồ thị tri thức, phân tích pipeline NLP theo thời gian thực và so sánh KG-QA với RAG Baseline.

---

## ⚡ 3. Các Tính năng Cốt lõi & Giải pháp Kỹ thuật (Key Technical Achievements)

### 1. 🤖 Tự động hóa Pipeline Trích xuất Tri thức (Auto-Pipeline NER & RE)
- Tự động chuyển đổi văn bản lâm sàng tự do thành bộ ba Triplet (`Head Entity` - `Relation` -> `Tail Entity`).
- Đã đóng gói mô hình tiền huấn luyện trong thư mục `models/`:
  - `models/ner_best.pt`: Mô hình PhoBERT-base fine-tune cho tác vụ NER.
  - `models/re_best.pt`: Mô hình PhoBERT-base fine-tune cho tác vụ RE với special tokens `[E1]...[/E1]` và `[E2]...[/E2]`.

### 2. 📈 Xử lý Thiên kiến Nhãn NONE & Distribution Shift (Continuous Training)
- **Vấn đề đặt ra:** Trong các bài toán Relation Extraction thực tế, số lượng cặp thực thể không có quan hệ (`NONE`) chiếm đa số, khiến mô hình bị lệch hướng nghiêm trọng (NONE-label bias) và giảm F1 score trên các nhãn thực tế.
- **Giải pháp:** 
  - Bổ sung **679 câu y tế phức hợp được sinh từ LLM** (`kaggle_train_augmented.py` / `generate_and_merge.py`) với cấu trúc ngữ pháp đảo, mệnh đề nguyên nhân - kết quả.
  - Áp dụng kỹ thuật **4x Oversampling** trên tập dữ liệu gốc, giúp đưa tỉ lệ mất cân bằng (Imbalance Ratio $Max/Min$) giảm mạnh từ **45.0** xuống còn **9.0**.

### 3. 🌐 Lớp Trừu tượng Đa LLM Provider (`LLMClient`)
- Hệ thống hỗ trợ tích hợp linh hoạt nhiều nhà cung cấp LLM thông qua lớp trừu tượng `LLMClient`: **Google Gemini**, **OpenAI**, **Anthropic**, và chế độ **Mock LLM Fallback** cho phép thử nghiệm offline và chạy unit tests mà không tốn chi phí API.

---

## 📊 4. Hiệu năng Mô hình & Kết quả Đánh giá (Performance Metrics)

Mô hình được đánh giá trên tập kiểm thử độc lập (**Blind Test Set**) và kiểm tra theo chiến lược **Stratified Split (70% Train / 15% Dev / 15% Test)** không để rò rỉ dữ liệu (No Data Leakage).

| Tác vụ NLP | Mô hình / Thuật toán | Chỉ số F1 Score (Test Set) | Ghi chú & Mục tiêu |
|---|---|---|---|
| **Named Entity Recognition (NER)** | PhoBERT-base (Fine-tuned) | **~79.00% – 80.00%** | Nhận diện chính xác 4 lớp thực thể (`DISEASE`, `DRUG`, `SYMPTOM`, `PROCEDURE`) |
| **Relation Extraction (RE)** | PhoBERT Sequence Classifier | **84.78% (Micro F1)** | Vượt chỉ tiêu Student/Teacher Ratio benchmark (**Target F1 $\ge$ 80%**) |
| **Annotation Agreement Rate** | Expert Gold Standard vs Teacher | **95.00%** | Kiểm chứng trên 120 mẫu quan hệ được chuyên gia y tế gán nhãn thủ công |

> 💡 **Phân bố nhãn sau Augmentation:** Tỉ lệ token $O$ trong NER đạt **72.2%** (nằm trong khoảng chuẩn 70% – 80%). Toàn bộ tập Dev và Test giữ nguyên 100% dữ liệu lâm sàng gốc để đảm bảo tính khách quan khoa học.

---

## 📁 5. Cấu trúc Thư mục Dự án (Project Directory Structure)

```
med-graph-main/
├── README.md                      # Tài liệu hướng dẫn & Báo cáo kỹ thuật luận văn
├── .env.example                   # Khung cấu hình biến môi trường mẫu
├── .env                           # File lưu cấu hình API Key & Tham số kết nối Neo4j
├── requirements.txt               # Thư viện phụ thuộc Python (3.10+)
├── docker-compose.yml             # Containerization Neo4j 5 Community Edition
├── run_pipeline.py                # Script thực thi toàn bộ Pipeline End-to-End (Stage A -> H)
├── generate_and_merge.py          # Script sinh dữ liệu LLM Augmentation & hợp nhất dataset
├── conftest.py                    # Cấu hình Pytest fixture chung
│
├── models/                        # Thư mục chứa weights mô hình học sâu
│   ├── ner_best.pt                # Checkpoint PyTorch cho PhoBERT NER (~537 MB)
│   └── re_best.pt                 # Checkpoint PyTorch cho PhoBERT RE (~540 MB)
│
├── app/                           # Ứng dụng Web Dashboard & Demo
│   └── streamlit_app.py           # Giao diện Streamlit tương tác 5 tab chức năng
│
├── src/                           # Mã nguồn cốt lõi của hệ thống MedGraph-VI
│   ├── config.py                  # Đường dẫn & tham số cấu hình hệ thống
│   ├── main.py                    # Entry point kiểm thử nhanh pipeline
│   ├── predict.py                 # Hàm trích xuất thông minh (extract_medical_info)
│   ├── api.py                     # Lớp API service
│   ├── llm_client.py              # Lớp trừu tượng đa provider (Gemini, OpenAI, Anthropic, Mock)
│   │
│   ├── ner/                       # Module Nhận diện Thực thể Y tế
│   │   ├── phobert_crf_ner.py     # Local PhoBERT Tagger
│   │   ├── dictionary_ner.py      # Trie/Regex Matcher dựa trên từ điển
│   │   ├── llm_ner.py             # LLM Few-shot NER Fallback
│   │   └── ner_ensemble.py        # Kỹ thuật Ensemble kết hợp 3 nguồn NER
│   │
│   ├── relation_extraction/       # Module Trích xuất Mối quan hệ
│   │   ├── llm_re.py              # LLM-based Relation Extractor
│   │   └── rule_based_re.py       # Pattern Matching Baseline Rules
│   │
│   ├── negation_temporal/         # Module Xử lý Phủ định & Thời gian
│   │   └── context_processor.py   # Vietnamese ConText Rules Engine
│   │
│   ├── entity_linking/            # Module Ánh xạ & Chuẩn hóa Thực thể
│   │   ├── icd10_linker.py        # Ánh xạ mã ICD-10 cho DISEASE
│   │   ├── rxnorm_linker.py       # Ánh xạ mã RxNorm cho DRUG (RxNav API)
│   │   ├── fuzzy_matcher.py       # RapidFuzz String Matching Engine
│   │   └── entity_normalizer.py   # Hàm lấy tên chuẩn (Canonical Name)
│   │
│   ├── graph/                     # Module Kết nối & Quản lý Graph Database
│   │   ├── neo4j_client.py        # Trình kết nối Neo4j Bolt Protocol
│   │   ├── graph_builder.py       # Tạo Node, Edge & Thuộc tính trên Neo4j
│   │   └── graph_cleaner.py       # Dọn dẹp Node mâu thuẫn / cô lập
│   │
│   ├── qa/                        # Module Hỏi đáp Đồ thị Tri thức
│   │   ├── text_to_cypher.py      # Dịch câu hỏi tiếng Việt sang Cypher Query
│   │   ├── rag_baseline.py        # Baseline Retrieval-Augmented Generation
│   │   └── qa_engine.py           # Engine điều phối KG-QA vs RAG
│   │
│   └── data_generation/           # Module Sinh Dữ liệu Tổng hợp
│       └── synthetic_generator.py # Generator sinh dữ liệu bằng LLM
│
├── data/                          # Dữ liệu hệ thống & Từ điển chuẩn
│   ├── raw/                       # Văn bản y tế gốc chưa xử lý
│   ├── synthetic/                 # Dữ liệu tổng hợp (synthetic_data.json)
│   ├── annotated/                 # Tập kiểm thử gán nhãn thủ công (test_set.json)
│   ├── dictionaries/              # Từ điển chuẩn y tế tiếng Việt
│   │   ├── icd10_vi.json          # Danh mục mã ICD-10 tiếng Việt
│   │   └── rxnorm_vi.json         # Danh mục dược phẩm & mã RxNorm
│   ├── exports/                   # Xuất dữ liệu CSV/JSON (all_relationships.csv)
│   ├── kaggle_train_augmented.py  # Dữ liệu huấn luyện đã tăng cường
│   └── kaggle_train_900.py        # Tập dữ liệu 900 câu phức hợp
│
├── evaluation/                    # Thư mục Đánh giá Hiệu năng (Evaluation Suite)
│   ├── evaluate_ner.py            # Đánh giá Precision, Recall, F1 cho NER
│   ├── evaluate_re.py             # Đánh giá F1 score cho Relation Extraction
│   ├── evaluate_entity_linking.py # Kiểm tra tỉ lệ chuẩn hóa ICD-10/RxNorm
│   ├── evaluate_qa.py             # Đánh giá chất lượng KG-QA vs Baseline
│   ├── coverage_analysis.py       # Phân tích độ phủ thực thể & quan hệ
│   └── error_analysis/            # Nhật ký lưu trữ chi tiết lỗi (Error Logs)
│
├── scripts/                       # Các kịch bản bổ trợ & Data Pipeline Utilities
│   ├── export_extended_ner_conll.py # Xuất dữ liệu định dạng CoNLL-2003
│   ├── clean_all_relationships.py # Chuẩn hóa các quan hệ trên CSDL
│   └── audit_benchmarks.py        # Kiểm toán độc lập các bộ benchmark
│
├── docs/                          # Tài liệu kỹ thuật chi tiết
│   ├── quality_report.md          # Báo cáo chất lượng dữ liệu & Annotation
│   ├── ontology_freeze.md         # Quy định đóng khung Schema & Ontology
│   └── annotation_guideline.md    # Hướng dẫn gán nhãn chuẩn y tế
│
└── tests/                         # Bộ Pytest Unit Tests
    ├── test_ner.py                # Test bộ nhận diện thực thể
    ├── test_relation_extraction.py# Test bộ trích xuất quan hệ
    ├── test_entity_linking.py     # Test ánh xạ mã ICD-10/RxNorm
    └── test_negation.py           # Test bộ lọc phủ định ConText
```

---

## 🛠️ 6. Hướng dẫn Cài đặt & Vận hành (Installation & Usage)

### 📋 Yêu cầu Môi trường:
- **Python:** `3.10` trở lên.
- **RAM:** Khuyến nghị từ **8GB - 16GB** (phục vụ load mô hình PhoBERT PyTorch trên CPU/GPU).
- **Docker & Docker Compose:** Phục vụ khởi chạy Neo4j Database.

---

### Bước 1: Khởi tạo Môi trường Ảo (Virtual Environment)
```bash
# Clone dự án hoặc truy cập thư mục làm việc
cd med-graph-main

# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo:
# Trên macOS / Linux:
source venv/bin/activate

# Trên Windows (PowerShell):
.\venv\Scripts\Activate.ps1
```

---

### Bước 2: Cài đặt Các Thư viện Phụ thuộc (Dependencies)
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Bước 3: Cấu hình Biến Môi trường `.env`
Sao chép file cấu hình mẫu `.env.example` thành `.env` và cập nhật thông tin:
```bash
cp .env.example .env
```
Nội dung cấu hình chính trong `.env`:
```env
# Nhà cung cấp LLM: "gemini", "openai", "anthropic", hoặc "mock"
LLM_PROVIDER=gemini
LLM_API_KEY=your_actual_llm_api_key_here

# Cấu hình CSDL Đồ thị Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=medgraph_secret_password
```

---

### Bước 4: Khởi chạy CSDL Neo4j bằng Docker
```bash
docker-compose up -d
```
- **Neo4j Browser Interface:** `http://localhost:7474`
- **Tài khoản mặc định:** User: `neo4j` | Password: `medgraph_secret_password`
- **Bolt Protocol:** `bolt://localhost:7687`

---

### 🚀 Vận hành Hệ thống & Thực thi Pipeline

#### 1. Chạy Toàn bộ Pipeline End-to-End (A $\rightarrow$ H)
Thực thi trích xuất tri thức từ văn bản lâm sàng và nạp tự động vào Neo4j:
```bash
python run_pipeline.py
```
*Để xóa dữ liệu Neo4j cũ và chạy lại từ đầu:*
```bash
python run_pipeline.py --reset
```

#### 2. Sinh Dữ liệu Augmentation bằng LLM (Tùy chọn)
```bash
python generate_and_merge.py
```

#### 3. Chạy Kiểm thử Độc lập (Pytest Unit Tests)
```bash
pytest tests/ -v
```

#### 4. Đánh giá Hiệu năng Chi tiết (Evaluation Suite)
```bash
# Đánh giá mô hình NER
python evaluation/evaluate_ner.py

# Đánh giá mô hình Relation Extraction
python evaluation/evaluate_re.py

# Đánh giá độ phủ & tỉ lệ Ánh xạ Thực thể
python evaluation/evaluate_entity_linking.py

# Đánh giá chất lượng Hỏi đáp KG-QA vs RAG Baseline
python evaluation/evaluate_qa.py
```

#### 5. Khởi động Web App Demo (Streamlit Framework)
Giao diện trực quan tương tác toàn bộ hệ thống:
```bash
streamlit run app/streamlit_app.py
```
Ứng dụng sẽ tự động mở tại trình duyệt web: `http://localhost:8501`

---

## 🔮 7. Định hướng Phát triển trong Tương lai (Future Work)

1. **Mở rộng Quy mô Tập Dữ liệu (Dataset Scaling):**
   - Mở rộng quy mô dataset lên khoảng **~30,000 mẫu văn bản lâm sàng** gán nhãn chất lượng cao nhằm nâng cao F1 score cho các lớp quan hệ hiếm như `CAUSES` (Nguyên nhân) và `CONTRAINDICATED_FOR` (Chống chỉ định).
   
2. **Tích hợp Kiến trúc RAG Nâng cao cho KG-QA (Advanced Hybrid Graph-RAG):**
   - Xây dựng hệ thống **Graph-RAG** kết hợp câu lệnh Cypher động trên Neo4j với Dense Vector Embeddings (Vector Search) để tối ưu khả năng trả lời câu hỏi y tế theo thời gian thực (Real-time Medical Queries).
   
3. **Triển khai RESTful API Service:**
   - Đóng gói pipeline thành dịch vụ RESTful API bằng FastAPI / Docker để kết nối trực tiếp với các hệ thống Quản lý Bệnh viện (HIS/EMR).

---

## 📜 8. Giấy phép & Tác quyền (License & Citation)

Dự án được phát triển phục vụ mục đích nghiên cứu học thuật và luận văn cao học. Tất cả dữ liệu y tế tổng hợp được tuân thủ nghiêm ngặt các quy định bảo mật thông tin sức khỏe.

- **Dự án:** MedGraph-VI (Vietnamese Medical Knowledge Graph)
- **Tác giả:** Hua Ngoc Thinh
- **Mã nguồn:** Được bảo hộ dưới giấy phép MIT License.
