# Cách ly benchmark đánh giá

**Trạng thái: `TEST_EL_BENCHMARK` và `QA_TEST_BENCHMARK` bị CÁCH LY. Không sửa, không xoá.**
Chạy được nhưng phải khai rõ cờ `--allow-unvalidated-benchmark`, và kết quả không dùng được
cho luận văn. Sẽ **dựng lại từ đầu ở Giai đoạn 7** từ nhãn gán tay, không vá.

---

## 1. Vì sao cách ly chứ không sửa

Một benchmark chỉ có giá trị nếu nó được tạo **độc lập** với hệ thống nó chấm. Bằng chứng cho
thấy hai bộ nhãn gold ở đây **không độc lập**.

### 1.1 Bằng chứng lịch sử

```
$ git log --follow --format="%h %ad %an %s" --date=short -- evaluation/evaluate_entity_linking.py
324a149 2026-07-21 HuaNgocThinh first commit

$ git log --follow ... -- evaluation/evaluate_qa.py
324a149 2026-07-21 HuaNgocThinh first commit
```

Cả hai được tạo ở **`324a149` "first commit"** — **cùng commit** với `data/dictionaries/icd10_vi.json`
và `data/dictionaries/rxnorm_vi.json`, cùng tác giả, cùng ngày. Và **chưa từng được sửa** kể từ
đó: commit `e64df49` sửa 24 dòng `icd10_vi.json` + 62 dòng `rxnorm_vi.json` nhưng **không đụng
tới gold**. Không script nào trong repo sinh ra chúng (`grep TEST_EL_BENCHMARK` chỉ ra chính
file định nghĩa và vòng lặp chấm điểm).

### 1.2 Bằng chứng quyết định: `Amlor`

Nhãn gold:
```python
{"entity": "Amlor", "type": "DRUG", "expected_code": "RXCUI:4337"}
```

Bản ghi trong từ điển tại **cùng commit đó**:
```json
{"rxcui": "4337", "name_en": "Amlodipine", "name_vi": "Amlodipine",
 "synonyms": ["amlodipine", "amlor", "amlodipin 5mg", "amlodipin 10mg"]}
```

`4337` là mã RxNorm của **fentanyl**, không phải amlodipine (mã đúng: **17767**, đã xác minh
ngược qua RxNav ở Giai đoạn trước). Nhãn gold mang **đúng cái giá trị sai** đang nằm trong từ
điển, và đó là bản ghi duy nhất chứa chuỗi `"amlor"`.

Không có nguồn độc lập nào (RxNorm, RxNav, dược thư) trả về 4337 cho Amlor. Cách giải thích
khớp với toàn bộ bằng chứng là **gold được chép ra từ chính từ điển**, không được tra cứu độc
lập. Tôi không truy được thao tác cụ thể (không có transcript sinh dữ liệu), nên đây là **suy
luận có căn cứ**, không phải sự thật đã chứng minh — nhưng bằng chứng lịch sử và bằng chứng
giá trị đều chỉ về một hướng.

### 1.3 Vì sao sửa 4 dòng là sai

Sửa `Amlor → 17767` sẽ làm con số đẹp lại **mà không đụng gì tới tính vòng tròn** — 14 dòng
còn lại vẫn "đúng" vì cùng nguồn gốc. Tệ hơn, nó **xoá mất bằng chứng**: sau khi sửa, không
ai còn nhìn thấy dấu vết cho thấy benchmark từng được chép ra từ hệ thống.

Đây cũng là **hướng lây nhiễm ngược nguy hiểm**: sau khi từ điển được sửa đúng, benchmark chấm
Amlor là *sai*. Ai đó nhìn báo cáo tụt điểm hoàn toàn có thể "sửa" từ điển **quay ngược về mã
fentanyl** cho khớp gold. Benchmark sai không chỉ vô dụng — nó **kéo dữ liệu đúng về chỗ sai**.

---

## 2. Bốn ca lệch cụ thể

Đo bằng `scripts/audit_benchmarks.py` → `data/exports/benchmark_audit.csv`.
**17/20 mục gold không truy được về nguồn độc lập nào.**

| # | Mục | Gold | Thực tế | Vấn đề |
|---|---|---|---|---|
| 1 | `Amlor` | `RXCUI:4337` | `RXCUI:17767` | Gold mang mã **fentanyl**. Ca chứng minh tính vòng tròn |
| 2 | `đau dạ dày` | `K29.7` | `None` | Synonym đã bị bỏ (đúng y học: đau dạ dày là triệu chứng, không phải chẩn đoán). Còn dính QĐ3: K29.7 sẽ đổi thành K25 |
| 3 | `qa_004` | `["Omeprazole", "Nexium"]` | Đồ thị không có node nào tên `Nexium` | Gold đòi một **biệt dược không tồn tại trong KG** |
| 4 | `qa_005` | `["Đau đầu", "đau ngực"]` | `Cao huyết áp` chỉ có `Chóng mặt`, `Đau đầu vùng chẩm` | Gold đòi một triệu chứng **không có cạnh nào** trong đồ thị |

### 2.1 🔴 Ca 3 và 4 là bằng chứng benchmark đang THƯỞNG ĐIỂM CHO VIỆC BỊA

Đây là lý do tôi **không xoá** hai keyword đó, dù xoá là cách nhanh nhất để hết lệch.

`qa_005` hỏi *"Thực thể Cao huyết áp có gây ra triệu chứng gì?"*. Đồ thị chỉ chứa `Chóng mặt`
và `Đau đầu vùng chẩm`. Gold yêu cầu câu trả lời phải chứa `"đau ngực"`.

Một hệ thống tuân thủ nguyên tắc bất di bất dịch — **chỉ nói cái đồ thị có** — sẽ **không bao
giờ** nói "đau ngực", và do đó **bị trừ điểm**. Một hệ thống rơi về kiến thức chung của LLM
(cao huyết áp *thường* gây đau ngực) sẽ **được điểm**.

> **Benchmark đang chấm điểm ngược với nguyên tắc thiết kế cốt lõi của hệ thống.**
> Nó không đo "có bịa không" — nó **thưởng cho việc bịa**.

`qa_004` cùng dạng: `Nexium` là biệt dược của esomeprazole; đồ thị có node `Esomeprazole 40mg`
nhưng không có `Nexium`. Muốn được điểm, hệ thống phải nói ra một tên thuốc nó chưa từng đọc.

Hai ca này là **tư liệu luận văn**, không phải bug cần vá: chúng cho thấy một benchmark sinh ra
từ kỳ vọng của người viết (thay vì từ dữ liệu) sẽ âm thầm mã hoá **kiến thức ngoài hệ thống**
thành tiêu chí đúng/sai — và đó chính là thứ hệ thống được thiết kế để từ chối.

---

## 3. Cơ chế chấm điểm cũng hỏng (mục B6)

### 3.1 Khớp chuỗi con

```python
kg_pass = any(k.lower() in kg_ans.lower() for k in kw) or len(res["kg_qa"].get("graph_results", [])) > 0
rag_pass = any(k.lower() in rag_ans.lower() for k in kw)
```

`any(...)` + khớp chuỗi con: chỉ cần **một** keyword xuất hiện **ở bất kỳ đâu** trong câu trả
lời tự do là đạt. **6/12 keyword chỉ khớp được ở dạng chuỗi con**, và có keyword mơ hồ tới mức
vô nghĩa:

| Keyword | Khớp được | Ghi chú |
|---|---|---|
| `"tim"` | `Suy tim sung huyết` | 3 ký tự, khớp bất kỳ chỗ nào có "tim" |
| `"não"` | `Nhồi máu não` | 3 ký tự |
| `"dạ dày"` | 3 node khác nhau | không phân biệt được viêm loét / trào ngược |
| `"Omeprazole"` | `Omeprazole 20mg` **và** `Esomeprazole 40mg` | khớp nhầm sang thuốc khác |

**Đo mức thổi phồng — một câu trả lời soạn sẵn, không liên quan gì tới câu hỏi:**

```
0/5 PASS  "Không có thông tin trong cơ sở dữ liệu."
3/5 PASS  "Bệnh nhân bị đau đầu, đau bụng và cần dùng Metformin, Paracetamol, Omeprazole."
5/5 PASS  "Các thuốc thường dùng gồm Metformin, Paracetamol, Omeprazole, Nexium;
           triệu chứng gồm Đau đầu, Cơn đau thắt ngực, Viêm loét dạ dày."
```

**Một câu duy nhất, dùng lại cho cả 5 câu hỏi, đạt 100%.** Điểm số hiện tại không đo năng lực
trả lời — nó đo mật độ từ khoá.

### 3.2 🔴 Mệnh đề `or` làm phép so sánh KG-QA vs RAG mất công bằng

Chú ý vế sau của `kg_pass`:

```python
... or len(res["kg_qa"].get("graph_results", [])) > 0
```

**KG-QA đạt nếu Cypher trả về BẤT KỲ dòng nào** — kể cả dòng sai, kể cả khi câu trả lời chữ
hoàn toàn lệch. RAG baseline **không có** mệnh đề miễn trừ này; nó phải khớp keyword thật.

Hệ quả: `kg_qa_accuracy` được tính bằng một luật **dễ hơn** `rag_baseline_accuracy`, rồi hai
con số được đem trừ nhau thành `kg_improvement_over_rag` — **kết quả chính của luận văn được đo
bằng một cây thước lệch**. Với 5/5 câu hiện đều trả về `graph_results` không rỗng, KG-QA đạt
100% **bất kể nó trả lời gì**.

Đây là lỗi nghiêm trọng nhất trong mục B, và nó độc lập với chuyện gold có vòng tròn hay không.

---

## 4. Đề xuất cách chấm cho Giai đoạn 7 (CHỈ ĐỀ XUẤT)

1. **Bỏ mệnh đề `or graph_results`.** KG-QA và RAG phải chấm bằng **cùng một luật**, nếu không phép so sánh vô nghĩa. Muốn báo cáo tỉ lệ truy hồi được dữ liệu thì để thành một chỉ số **riêng** (`retrieval_rate`), đừng trộn vào accuracy.
2. **Chấm theo TẬP THỰC THỂ, không theo chuỗi.** Gold là tập `node_id` (hoặc `(label, name)`) mà câu trả lời phải nêu; chấm bằng **precision / recall / F1** trên tập đó. Hết cảnh `"tim"` khớp `Suy tim sung huyết`.
3. **Chấm cả phần THỪA.** Luật hiện tại chỉ phạt thiếu, không phạt thừa — nên nói càng nhiều càng lợi. Precision xử lý được việc này: nêu thực thể không có trong gold thì bị trừ. Đây là chỗ *bịa* bị bắt.
4. **Thêm nhóm câu hỏi có đáp án ĐÚNG LÀ "không có dữ liệu".** Ít nhất 15–20% tập gold nên là câu mà đồ thị **thật sự không chứa** câu trả lời; đạt = hệ thống nói không có. Không có nhóm này thì nguyên tắc "không bịa" **không được đo lần nào**, và ca `qa_005` cho thấy hiện tại nó đang bị đo **ngược dấu**.
5. **Mọi nhãn gold phải mang trường `source`**: `corpus:syn_0xx` hoặc `icd10:K25` / `rxnav:17767`. Nhãn không truy được nguồn thì không vào tập gold. Bất biến này một mình đã đủ chặn toàn bộ sự cố lần này.
6. **Neo tên vào corpus, mã vào chuẩn** (nguyên tắc 6) — áp dụng cho gold y hệt như cho node.

---

## 5. Cổng cách ly

`evaluation/benchmark_guard.py`:

```python
BENCHMARK_VALIDATED = False          # bật khi đã dựng lại và xác thực độc lập
require_validated_benchmark(name, module)   # exit 2 kèm giải thích, trừ khi có cờ
```

Đã gắn vào cả `evaluate_entity_linking.py` và `evaluate_qa.py`. Chạy trần → **exit 2**. Muốn
chạy phải viết ra `--allow-unvalidated-benchmark`, và khi đó banner cảnh báo vẫn in.

Cùng nguyên tắc với `execute_query(raise_on_error=True)` và với việc bỏ sentinel: **một giá trị
không đáng tin thì không được im lặng trôi qua như thể nó đáng tin.** Muốn bỏ qua thì phải khai
ra trong code hoặc trên dòng lệnh — review được, không mặc định.
