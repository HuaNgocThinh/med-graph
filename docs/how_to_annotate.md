# 🚀 Hướng Dẫn Nhanh 5 Bước Gán Nhãn & Đánh Giá Dữ Liệu (MedGraph-VI)

Tài liệu hướng dẫn thực hành nhanh 5 bước dành cho Người gán nhãn dữ liệu (Annotator).

---

### Bước 1: Mở File CSV Cần Gán Nhãn
* Sử dụng Microsoft Excel, Google Sheets, hoặc VS Code để mở 1 trong 2 file dữ liệu tại thư mục `data/annotation/`:
  - **Tập Rút ra Quan hệ (RE)**: `data/annotation/re_annotation_set.csv` (120 câu)
  - **Tập Liên kết Thực thể (EL)**: `data/annotation/el_annotation_set.csv` (50 thực thể)

---

### Bước 2: Chọn Đúng Cột Để Điền Nhãn Chuẩn (Gold Label)
* **KHÔNG** sửa đổi bất kỳ cột nào chứa dữ liệu gốc hoặc dự đoán của hệ thống.
* Chỉ tiến hành nhập dữ liệu nhãn chuẩn vào đúng cột được quy định:
  - Trên file `re_annotation_set.csv`: Điền nhãn chuẩn vào cột **`relation_gold`**
  - Trên file `el_annotation_set.csv`: Điền mã chuẩn vào cột **`code_gold`**

---

### Bước 3: Nhập Các Giá Trị Hợp Lệ Theo Chuẩn
* Đối với tập **RE** (Cột `relation_gold`), chỉ nhập duy nhất 1 trong 6 nhãn sau:
  1. `PRESCRIBED_FOR` (Chỉ định điều trị bệnh)
  2. `TREATS` (Điều trị / giảm nhẹ triệu chứng)
  3. `HAS_SYMPTOM` (Biểu hiện triệu chứng)
  4. `CONTRAINDICATED_FOR` (Chống chỉ định)
  5. `CAUSES` (Căn nguyên / gây ra bệnh khác)
  6. `NONE` (Không có quan hệ hoặc bị phủ định)

* Đối với tập **EL** (Cột `code_gold`), nhập mã chuẩn hóa tương ứng:
  - Nhập mã ICD-10 cho Bệnh (Ví dụ: `E11`, `I10`, `K25`, `D56.9`, `M17`)
  - Nhập mã RxCUI cho Thuốc (Ví dụ: `RXCUI:6809`, `RXCUI:161`)
  - Nhập `UNLINKED` nếu thực thể không có trong từ điển chuẩn hóa.
  *(Nếu không chắc chắn, điền nhãn suy đoán và ghi cụm từ `uncertain` ở cột `note`).*

---

### Bước 4: Lưu File Gán Nhãn Đúng Vị Trí
* Lưu trực tiếp đè lên file CSV ban đầu theo chuẩn encoding **UTF-8** (hoặc `UTF-8 with BOM` trên Excel):
  - `data/annotation/re_annotation_set.csv`
  - `data/annotation/el_annotation_set.csv`

---

### Bước 5: Chạy Lệnh Tính Điểm Đánh Giá (Evaluation)
* Sau khi hoàn tất điền nhãn, mở Terminal tại thư mục gốc dự án và chạy lệnh:
  ```bash
  python evaluation/run_annotation_eval.py
  ```
* Hệ thống sẽ tự động đối sánh cột `relation_predicted` vs `relation_gold` và `code_predicted` vs `code_gold` để in báo cáo điểm **Precision, Recall, F1-Score (RE)** và **Exact Match Accuracy % (EL)**.
