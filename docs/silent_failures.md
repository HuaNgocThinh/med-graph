# Lỗi câm trong MedGraph-VI: bốn biểu hiện của một nguyên nhân

*Tư liệu luận văn — mục 4d.*

## 1. Nguyên nhân gốc

Toàn bộ bốn sự cố dưới đây bắt nguồn từ **một dòng code duy nhất**:

```python
# src/graph/neo4j_client.py  (trước khi sửa)
def execute_query(self, query, parameters=None):
    if not self._driver:
        if not self.connect():
            logger.warning("Query skipped because Neo4j is offline.")
            return []                       # <-- (a)
    try:
        with self._driver.session() as session:
            return [record.data() for record in session.run(query, parameters or {})]
    except Exception as e:
        logger.error(f"Error executing Cypher query: ... {e}")
        return []                           # <-- (b)
```

Hàm này trả về `[]` cho **ba sự kiện có ý nghĩa hoàn toàn khác nhau**:

| Sự kiện | Giá trị trả về | Ý nghĩa thật |
|---|---|---|
| Truy vấn chạy, không khớp gì | `[]` | "Đồ thị **không có** dữ liệu này" |
| Truy vấn lỗi cú pháp / vi phạm ràng buộc | `[]` (b) | "Ta **không biết gì cả**" |
| Database offline | `[]` (a) | "Ta **không biết gì cả**" |

Người gọi không có cách nào phân biệt. Và vì `[]` là giá trị **hợp lệ, thường gặp, trông
bình thường**, không ai nghi ngờ. Đây là định nghĩa của lỗi câm: hệ thống **không im lặng** —
nó có ghi log — nhưng **giá trị trả về nói dối**, và code luôn tin giá trị trả về chứ không
đọc log.

> Một exception làm chương trình dừng là lỗi ồn. Một exception bị nuốt rồi thay bằng giá trị
> hợp lệ là **lỗi câm**: nó không dừng chương trình, nó làm chương trình **tiếp tục chạy với
> một sự thật sai**.

## 2. Bốn biểu hiện

| # | Biểu hiện | Phát hiện ra sao | Hậu quả nếu không phát hiện |
|---|---|---|---|
| 1 | `validate_connection()` báo "connected" trong khi API Gemini trả lỗi | Quan sát tay: banner UI báo xanh nhưng câu trả lời rỗng | Mọi phiên chạy đều tưởng đang gọi LLM thật; số liệu đánh giá thu được từ mock, không dùng được cho luận văn |
| 2 | Neo4j offline nhưng hệ thống **vẫn trả lời** câu hỏi lâm sàng | Tắt Neo4j để thử; hệ thống trả lời trôi chảy | **Nghiêm trọng nhất về mặt an toàn.** Vi phạm trực tiếp nguyên tắc "không fallback sang kiến thức LLM": câu trả lời sinh ra từ trí nhớ mô hình chứ không từ đồ thị, mà không có dấu hiệu nào |
| 3 | `CREATE CONSTRAINT ... IS UNIQUE` **khai mà không tồn tại** | `SHOW CONSTRAINTS` trả về **0** dòng, dù code khai 2 constraint | `drug_code IS UNIQUE` không tồn tại suốt vòng đời dự án → **Metformin và Methotrexate cùng mang `RXCUI:6809`**. Ràng buộc tồn tại trong code, không tồn tại trong DB, và không có cảnh báo nào |
| 4 | Truy vấn Cypher lỗi → trả lời "**cơ sở dữ liệu chưa ghi nhận thực thể này**" | Đọc lại luồng: `graph_results = []` → `fallback_status = "NODE_NOT_FOUND"` | Hệ thống **khẳng định một sự vắng mặt** dựa trên truy vấn chưa từng chạy. Với KG y tế, "không có chống chỉ định nào" là câu trả lời có thể gây hại |

Biểu hiện 3 và 4 đáng chú ý về mặt phương pháp: chúng **nuôi nhau**. Ràng buộc uniqueness
không chạy (3) cho phép mã trùng lọt vào đồ thị; nếu sau đó một truy vấn hỏng (4), hệ thống
lại khẳng định dữ liệu không tồn tại. Lỗi câm không cộng lại — chúng **nhân lên**, vì mỗi lỗi
đều xoá bằng chứng để phát hiện lỗi kia.

## 3. Quy mô trong repo

Quét AST toàn repo (`scripts/scan_swallowed_exceptions.py`, bỏ `scratch/`):

```
Tổng số except handler: 39
  SWALLOW  : 15   (nuốt lỗi, người gọi không biết)
  LOG_ONLY : 22   (ghi log nhưng vẫn trả giá trị trông bình thường)
  OK       :  2   (ném lại)
```

**2/39 = 5%** số handler để lỗi nổi lên. Con số này, chứ không phải bốn sự cố cụ thể, mới là
kết quả đáng báo cáo: kiến trúc mặc định của dự án là **che lỗi**.

## 4. Cách sửa

Không phải "thêm log" — cả bốn ca **đã có log** rồi. Vấn đề là **kiểu giá trị trả về không
biểu diễn được trạng thái lỗi**.

```python
class QueryResult(list):
    """Danh sách bản ghi, ĐỒNG THỜI cho biết truy vấn có thật sự chạy hay không."""
    def __init__(self, records=(), ok=True, error=None, query="", offline=False): ...

def execute_query(self, query, parameters=None, raise_on_error=True) -> QueryResult:
    ...
    raise Neo4jQueryError(query, e)        # mặc định: lỗi NỔI LÊN
```

Ba tính chất:
1. **Mặc định ném exception.** Muốn bỏ qua lỗi phải viết ra `raise_on_error=False` — biến sự
   im lặng thành một quyết định hiển thị trong code, review được.
2. **`QueryResult` kế thừa `list`.** Mọi `if not rows:` và `for r in rows:` cũ vẫn chạy;
   không phải sửa 22 chỗ gọi. Nhưng `rows.ok` nói ra sự thật.
3. **Nơi buộc phải chịu lỗi thì phải xử lý lỗi.** `text_to_cypher` chạy Cypher do LLM sinh nên
   không thể ném; nó dùng `raise_on_error=False` **và** thêm trạng thái `QUERY_ERROR` riêng:

```
Nếu trạng thái là 'QUERY_ERROR': Truy vấn KHÔNG chạy được, nên ta KHÔNG biết dữ liệu
có hay không. TUYỆT ĐỐI KHÔNG được nói 'chưa ghi nhận' hay 'không có dữ liệu'.
```

Đây là điểm mấu chốt về mặt luận điểm: nguyên tắc "không bịa" thường được hiểu là *không bịa
ra dữ liệu*. Ca số 4 cho thấy **bịa ra một sự vắng mặt cũng là bịa** — và nguy hiểm hơn, vì
một khẳng định phủ định nghe có vẻ thận trọng.

## 5. Test bảo vệ

`tests/test_silent_failures.py` — 14 test. Test cốt lõi:

```python
def test_failed_query_is_distinguishable_from_an_empty_one():
    failed = _client(_BoomDriver()).execute_query(q, raise_on_error=False)
    empty  = _client(_EmptyDriver()).execute_query(q, raise_on_error=False)
    assert list(failed) == list(empty) == []       # vẫn giống nhau khi nhìn như list
    assert failed.ok is False and empty.ok is True # nhưng không còn lẫn lộn được
```

Cùng `verify_schema()` trong `neo4j_client.py`: sau mỗi `CREATE CONSTRAINT`, đối chiếu lại với
`SHOW CONSTRAINTS` và cảnh báo ồn ào nếu lệch — **khai không phải là tạo**.

## 6. Bài học phương pháp

1. **Không tin báo cáo thành công, hãy hỏi lại hệ thống.** `init_schema()` in "Initialized" mỗi lần chạy; `SHOW CONSTRAINTS` trả về 0. Chỉ câu hỏi thứ hai nói thật.
2. **Giá trị trả về phải biểu diễn được mọi trạng thái mà nó đại diện.** Nếu `[]` phải mang cả "rỗng" lẫn "hỏng", kiểu dữ liệu đã sai — và không lượng log nào bù được.
3. **Sentinel là cùng một lỗi ở tầng dữ liệu.** `'RXCUI-UNKNOWN'` cũng là một giá trị trông hợp lệ đại diện cho "không biết", và nó khiến ràng buộc uniqueness **không thể tạo được** (mục 3). Cùng một sai lầm: dùng một giá trị hợp lệ để biểu diễn sự vắng mặt của giá trị.
