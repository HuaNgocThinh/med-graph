# Đóng băng Ontology — 4 quyết định cần chốt trước khi gán nhãn tay

**Trạng thái: ĐỀ XUẤT. Chưa quyết định nào được thực hiện.**

Bốn quyết định dưới đây đều đổi **tên node** hoặc **mã node**. Tập gold 100–150 câu gán nhãn
tay sẽ tham chiếu tới tên/mã node; nếu ontology đổi sau khi gán nhãn thì mọi câu đã gán đều
lệch, và công sức gán nhãn mất trắng. Vì vậy phải chốt cả bốn **trước**, một lượt.

Số liệu đo trên đồ thị hiện tại: **197 node / 193 quan hệ / 93 SourceSampleID**, sau khi đã
sửa Meloxicam, dọn 31 synonym ICD-10, đồng bộ RxCUI và đổi sentinel thành `null`.

| # | Quyết định | Node ảnh hưởng | Quan hệ ảnh hưởng | Mức rủi ro |
|---|---|---|---|---|
| 1 | "Cao huyết áp" → "Tăng huyết áp" | 1 | 3 | Thấp |
| 2 | Tên node thuốc = hoạt chất | 49 → 47 | 80 | **Cao** |
| 3 | 3 mã ICD-10 sai | 3 | 15 | Trung bình |
| 4 | `ALIAS_MAP["viêm dạ dày"]` | 0–1 | 0–6 | Trung bình |

---

## Quyết định 1 — Chuẩn hóa "Cao huyết áp" → "Tăng huyết áp"

### Phương án đề xuất
Đổi tên node hiển thị thành **"Tăng huyết áp"** (thuật ngữ chuẩn trong y văn Việt Nam;
"cao huyết áp" là khẩu ngữ). Giữ "cao huyết áp" làm **synonym** để câu hỏi khẩu ngữ vẫn khớp.

### Ảnh hưởng đo được
- **Node:** 1 — `:DISEASE "Cao huyết áp"` (code `I10`, bậc 3). Node `"Tăng huyết áp"` **chưa tồn tại**, nên đây là đổi tên, không phải gộp.
- **Quan hệ:** 3 — `HAS_SYMPTOM → Chóng mặt`, `HAS_SYMPTOM → Đau đầu vùng chẩm` (syn_052), `Amlodipine 5mg -PRESCRIBED_FOR→` (syn_011, syn_052).
- **Corpus:** `"cao huyết áp"` xuất hiện ở **3 mẫu** (syn_001, syn_011, syn_052); `"tăng huyết áp"` xuất hiện **0 mẫu**.

### File/test phải sửa đồng bộ
21 file có nhắc chuỗi này. Nhóm phải sửa:
- `src/entity_linking/entity_normalizer.py` (ALIAS_MAP), `medical_synonyms_vi.json`, `data/dictionaries/icd10_vi.json`
- `src/ner/dictionary_ner.py`, `llm_ner.py`, `phobert_crf_ner.py`, `ner_ensemble.py` (từ điển NER)
- `src/data_generation/synthetic_generator.py`, `src/llm_client.py` (prompt mẫu)
- `app/streamlit_app.py` (câu hỏi gợi ý)
- 7 file test: `test_disease_normalizer`, `test_entity_gate`, `test_entity_linking`, `test_negation`, `test_ner`, `test_synonym_canonicalization`, `test_synonym_expansion`
- `evaluation/evaluate_entity_linking.py`, `evaluate_qa.py`

### Rủi ro nếu làm sai
**Thấp, nhưng có một bẫy:** nếu đổi tên node mà **quên** giữ "cao huyết áp" trong synonym map,
mọi câu hỏi dùng khẩu ngữ sẽ trả về rỗng — và vì corpus chỉ viết "cao huyết áp", NER sẽ không
còn nhận ra thực thể nào. Bắt buộc: đổi tên **và** thêm synonym trong cùng một lần.

---

## Quyết định 2 — Tên node thuốc = hoạt chất, liều thành thuộc tính quan hệ

### Phương án đề xuất
`:DRUG {name: "Meloxicam"}` thay cho `"Meloxicam 15mg"`; liều chuyển thành thuộc tính của
quan hệ: `[:PRESCRIBED_FOR {dosage: "15mg", frequency: "1 vien/ngay"}]`.

**Lý do bản chất:** liều thuộc về **lần kê đơn**, không thuộc về **thuốc**. Đặt liều trong tên
node là gán một thuộc tính của cạnh vào đỉnh — đó là lỗi mô hình hóa, và mọi hệ quả bên dưới
đều bắt nguồn từ đó.

### Ảnh hưởng đo được
- **Node:** 49 → **47** (giảm 2). 36/49 node có liều trong tên, 13 không có.
- **Quan hệ:** **80** quan hệ chạm vào node `:DRUG` — tất cả đều phải mang thêm thuộc tính liều nếu muốn giữ thông tin.
- **Hoạt chất đang bị tách node: 2**
  - `Meloxicam 15mg` (bậc 6) + `Meloxicam 7.5mg` (bậc 1) — **cả hai cùng trỏ tới `Đau lưng dưới`**, tức là trùng thật.
  - `Hydrocortisone` (bậc 3) + `Hydrocortisone 10mg` (bậc 1).

### 🔴 Bằng chứng mới từ mục 2 và 3 — quyết định này đang **chặn một ràng buộc**
Sau khi đồng bộ RxCUI đúng, `Meloxicam 15mg` và `Meloxicam 7.5mg` **đều nhận `RXCUI:41493`** —
tất nhiên, chúng là một thuốc. Kết quả: `CREATE CONSTRAINT drug_code IS UNIQUE` **thất bại**,
và giờ **chỉ còn đúng nguyên nhân này**:

```
DRUG.code:
  [CUNG HOAT CHAT, TACH NODE THEO LIEU] 'RXCUI:5492'  x2  Hydrocortisone / Hydrocortisone 10mg
  [CUNG HOAT CHAT, TACH NODE THEO LIEU] 'RXCUI:41493' x2  Meloxicam 15mg / Meloxicam 7.5mg
```

Trước đây constraint này thất bại vì sentinel `'RXCUI-UNKNOWN'`, một lỗi kỹ thuật đã sửa xong.
Bây giờ nó thất bại vì **ontology sai** — mã đúng, mô hình sai. `disease_code IS UNIQUE` đã
tạo được; `drug_code` sẽ tạo được **ngay khi** quyết định 2 được thực hiện.

### File/test phải sửa đồng bộ
- `src/graph/graph_builder.py` — tách liều khỏi tên trước `MERGE`, ghi liều vào thuộc tính quan hệ
- `src/entity_linking/rxnorm_linker.py` — đã có `DOSAGE_RE`, dùng lại
- `src/qa/text_to_cypher.py` — `ANSWER_SYNTHESIS_PROMPT` phải đọc thêm `r.dosage`, nếu không câu trả lời sẽ mất thông tin liều
- `app/streamlit_app.py:111` — danh sách câu hỏi gợi ý có hard-code `"Aspirin 81mg"`
- `tests/test_rxnorm_provenance.py` — 5 mã đang pin theo `name_vi` có liều
- `data/dictionaries/rxnorm_vi.json` — `name_vi` nên bỏ liều luôn cho nhất quán

### Ảnh hưởng tới 4 câu hỏi gốc (mục 4b vòng trước)
Cả 4 câu **không lọc theo tên thuốc**, chúng lọc theo tên *bệnh* và trả về `d.name` bất kỳ.
Nên Cypher không đổi. Nhưng **câu trả lời sẽ đổi** từ `"Meloxicam 15mg"` thành `"Meloxicam"`.

### Rủi ro nếu làm sai
**Cao — đây là quyết định nặng nhất.**
1. Nếu gộp node mà **không** chuyển liều sang quan hệ, ta **mất vĩnh viễn** thông tin liều của 36 node. Không khôi phục được từ đồ thị, phải chạy lại pipeline.
2. Nếu tách liều bằng regex quá tham, tên thuốc có số hợp lệ sẽ bị cắt sai (`Diane-35`, `Salmeterol/Fluticasone 50/250 mcg`, `Digoxin 0.25mg`). Phải chạy thử regex trên toàn bộ 49 tên và in bảng trước/sau **trước khi** động vào đồ thị.
3. `Meloxicam 15mg` và `Meloxicam 7.5mg` cùng trỏ `Đau lưng dưới` → khi gộp sẽ thành **một** quan hệ; `source_sample_id` phải được **hợp nhất** chứ không ghi đè, nếu không mất truy vết.

---

## Quyết định 3 — Ba mã ICD-10 gán sai bệnh

Chi tiết xác minh ở mục 1a của báo cáo. Tóm tắt: cả 3 node đang mang mã của **một bệnh khác**.

| Node | Mã hiện tại | Mã đó thật ra là | Mã đúng | Bậc |
|---|---|---|---|---|
| `Viêm loét dạ dày` | `K29.7` | Viêm dạ dày (gastritis) — K25 loại trừ K29 type-1 | **K25** (Loét dạ dày) | 6 |
| `Thoái hóa khớp` | `M19.9` | Thoái hóa khớp *không xác định vị trí* | **M17** (Thoái hóa khớp gối) | 5 |
| `Viêm âm đạo do nấm` | `N76.0` | Viêm âm đạo cấp *không do nấm* | **B37.3** (Candida âm hộ–âm đạo) | 4 |

- **Node:** 3. **Quan hệ:** 15 (6 + 5 + 4). Không quan hệ nào bị xoá — chỉ đổi thuộc tính `code`.
- Từ điển hiện **có K25**, nhưng **không có M17 và B37.3** → phải bổ sung 2 record mới.
- Riêng `Thoái hóa khớp`: corpus viết `"Thoái hóa khớp gối"` ở **cả 2 mẫu** (syn_014, syn_080), không mẫu nào viết `"Thoái hóa khớp"` trơn. Nên **tên node cũng nên đổi thành `"Thoái hóa khớp gối"`** cho khớp cả văn bản gốc lẫn mã M17.

### File/test phải sửa đồng bộ
`data/dictionaries/icd10_vi.json` (sửa 3 record + thêm M17, B37.3);
`src/entity_linking/entity_normalizer.py` (ALIAS_MAP, xem quyết định 4);
`tests/test_entity_gate.py::test_real_terms_still_link_after_the_gate`;
**và danh sách hồi quy** — xem mục 1d.

### Rủi ro nếu làm sai
**Trung bình.** Sai mã ICD-10 trong một KG y tế là sai *lâm sàng*, không phải sai kỹ thuật:
K29.7 và K25 có quan hệ **Excludes1** trong ICD-10, nghĩa là hai chẩn đoán loại trừ nhau. Nếu
để nguyên, mọi truy vấn/thống kê theo mã đều sai và không ai phát hiện được, vì tên node vẫn
đúng — đúng kiểu lỗi câm mà mục 4 đang dọn.

---

## Quyết định 4 — `ALIAS_MAP["viêm dạ dày"] = "Viêm loét dạ dày"`

### Vấn đề
Đây là **cùng loại lỗi lệch chẩn đoán** ta đã dọn ở mọi tầng khác (`tai biến mạch máu não` →
`Nhồi máu não`, `đột quỵ não` → I63…). Viêm dạ dày (gastritis) và loét dạ dày (gastric ulcer)
là **hai chẩn đoán khác nhau, loại trừ nhau trong ICD-10**. Ánh xạ này khẳng định chúng là một.

Nó còn nguy hiểm hơn các ca khác vì **nó nằm ở tầng đặt tên node**, không phải tầng tra cứu —
xem mục 1d: chính entry này đã **âm thầm đổi tên node** từ `"Viêm dạ dày"` sang
`"Viêm loét dạ dày"` mà không đổi mã.

### Phương án đề xuất
Bỏ `"viêm dạ dày" -> "Viêm loét dạ dày"`. Hai chuỗi trở thành hai khái niệm độc lập:
`viêm dạ dày → K29.7`, `viêm loét dạ dày → K25`.

Ba entry còn lại trong cùng khối cũng phải xem lại cùng lúc, vì chúng gộp theo hướng ngược:
```python
"viêm dạ dày tá tràng": "Viêm loét dạ dày",   # viêm ≠ loét — cùng lỗi
"loét dạ dày tá tràng": "Viêm loét dạ dày",   # loét tá tràng K26 ≠ loét dạ dày K25
"loét dạ dày":          "Viêm loét dạ dày",   # HỢP LÝ, giữ
```

### Ảnh hưởng đo được
- **Node:** 0–1. Corpus **không có mẫu nào** viết `"viêm dạ dày"` trơn (chuỗi duy nhất khớp là
  `"Viêm dạ dày ruột nhiễm khuẩn"` = A09, một bệnh khác và đã có node riêng).
  → Bỏ entry này **không sinh node mới và không mất node nào** trên corpus hiện tại.
- **Quan hệ:** 0 trên corpus hiện tại. Nhưng nếu quyết định 3 đổi node sang K25, thì 6 quan hệ
  của `Viêm loét dạ dày` sẽ đi cùng node đó.

### Rủi ro nếu làm sai
**Trung bình.** Rủi ro không nằm ở corpus hôm nay mà ở **corpus tương lai**: mọi bệnh án mới
viết "viêm dạ dày" sẽ bị gộp nhầm vào node loét dạ dày, và vì tên node trông hợp lý nên sẽ
không ai phát hiện. Đây chính là cơ chế đã sinh ra bug hiện tại.

---

## Thứ tự thực hiện đề xuất (sau khi anh duyệt)

1. **Quyết định 4** trước — nó là tầng đặt tên, mọi thứ khác phụ thuộc vào tên node.
2. **Quyết định 3** — sửa mã, thêm M17/B37.3, đổi tên `Thoái hóa khớp gối`.
3. **Quyết định 1** — độc lập, rủi ro thấp, làm lúc nào cũng được.
4. **Quyết định 2** cuối cùng — nặng nhất, và làm xong thì `drug_code IS UNIQUE` tạo được, đóng lại toàn bộ mục 3.

Mỗi bước: `before_*.csv` / `after_*.csv`, log lý do từng dòng, chạy lại toàn bộ hồi quy.
