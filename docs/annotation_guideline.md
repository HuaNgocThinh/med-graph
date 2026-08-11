# Hướng Dẫn Gán Nhãn Dữ Liệu Lâm Sàng (MedGraph-VI Annotation Guideline)

> **Tài liệu hướng dẫn chuẩn hóa dành cho người gán nhãn dữ liệu Y tế (Annotators)**  
> *Dự án: MedGraph-VI — Đồ thị tri thức y tế tiếng Việt*

---

## 📋 MỤC LỤC
1. [Giới thiệu & Mục tiêu](#1-giới-thiệu--mục-tiêu)
2. [Định nghĩa các loại Quan hệ (Relation Types)](#2-định-nghĩa-các-loại-quan-hệ-relation-types)
   - 2.1. `PRESCRIBED_FOR` (Chỉ định điều trị bệnh)
   - 2.2. `TREATS` (Điều trị triệu chứng / giảm nhẹ)
   - 2.3. `HAS_SYMPTOM` (Triệu chứng của bệnh)
   - 2.4. `CONTRAINDICATED_FOR` (Chống chỉ định)
   - 2.5. `CAUSES` (Căn nguyên / Biến chứng gây ra)
   - 2.6. `NONE` (Không có quan hệ lâm sàng)
3. [Quy tắc xử lý Phủ định (Negation)](#3-quy-tắc-xử-lý-phủ-định-negation)
4. [Quy tắc xử lý Tiền sử bệnh (Medical History)](#4-quy-tắc-xử-lý-tiền-sử-bệnh-medical-history)
5. [Quy tắc xử lý khi Không chắc chắn (Uncertainty)](#5-quy-tắc-xử-lý-khi-không-chắc-chắn-uncertainty)
6. [Ví dụ Mẫu 5 Câu Đã Gán Nhãn Khái Niệm](#6-ví-dụ-mẫu-5-câu-đã-gán-nhãn-khái-niệm)

---

## 1. Giới thiệu & Mục tiêu
Tài liệu này cung cấp quy tắc chuẩn hóa để người gán nhãn xác định quan hệ giữa các thực thể Y tế (Thuốc, Bệnh, Triệu chứng) trong các câu văn lâm sàng tiếng Việt.  
Cột cần gán nhãn thủ công là `relation_gold` trong tập **RE** và `code_gold` trong tập **EL**.

---

## 2. Định nghĩa các loại Quan hệ (Relation Types)

### 2.1. `PRESCRIBED_FOR`
* **Định nghĩa**: Thuốc được kê đơn hoặc chỉ định cụ thể để điều trị một bệnh căn nguyên (DISEASE).
* **Ví dụ ĐÚNG (YES)**: 
  - *"Bệnh nhân Đái tháo đường týp 2 đang dùng Metformin 500mg."* $\rightarrow$ `(Metformin, PRESCRIBED_FOR, Đái tháo đường týp 2)`
* **Ví dụ SAI (NO)**: 
  - *"Bệnh nhân bị ho kéo dài được uống Paracetamol."* $\rightarrow$ ❌ Không dùng `PRESCRIBED_FOR` cho triệu chứng (dùng `TREATS`).

### 2.2. `TREATS`
* **Định nghĩa**: Thuốc hoặc phương pháp dùng để giảm nhẹ một triệu chứng lâm sàng (SYMPTOM) hoặc tình trạng khó chịu.
* **Ví dụ ĐÚNG (YES)**:
  - *"Dùng Paracetamol 500mg để giảm sốt cao."* $\rightarrow$ `(Paracetamol, TREATS, sốt cao)`
* **Ví dụ SAI (NO)**:
  - *"Dùng Omeprazole cho bệnh Viêm loét dạ dày."* $\rightarrow$ ❌ Đây là điều trị bệnh gốc (dùng `PRESCRIBED_FOR`).

### 2.3. `HAS_SYMPTOM`
* **Định nghĩa**: Bệnh biểu hiện hoặc kèm theo một triệu chứng lâm sàng cụ thể.
* **Ví dụ ĐÚNG (YES)**:
  - *"Viêm ruột thừa cấp gây đau âm ỉ vùng hố chậu phải."* $\rightarrow$ `(Viêm ruột thừa cấp, HAS_SYMPTOM, đau âm ỉ vùng hố chậu phải)`
* **Ví dụ SAI (NO)**:
  - *"Bệnh nhân bị Đái tháo đường và kèm theo Cao huyết áp."* $\rightarrow$ ❌ Cao huyết áp là Bệnh đồng mắc, không phải triệu chứng (dùng `NONE`).

### 2.4. `CONTRAINDICATED_FOR`
* **Định nghĩa**: Thuốc chống chỉ định (không được dùng) khi bệnh nhân mắc một bệnh hoặc tình trạng cụ thể.
* **Ví dụ ĐÚNG (YES)**:
  - *"Bệnh nhân Viêm loét dạ dày không được dùng Ibuprofen."* $\rightarrow$ `(Ibuprofen, CONTRAINDICATED_FOR, Viêm loét dạ dày)`
* **Ví dụ SAI (NO)**:
  - *"Bệnh nhân chưa từng dùng Ibuprofen."* $\rightarrow$ ❌ Chỉ là câu hành vi, không phải chống chỉ định y khoa.

### 2.5. `CAUSES`
* **Định nghĩa**: Một bệnh hoặc tình trạng trực tiếp dẫn đến/gây ra một bệnh khác hoặc biến chứng.
* **Ví dụ ĐÚNG (YES)**:
  - *"Cao huyết áp kéo dài gây ra Nhồi máu não."* $\rightarrow$ `(Cao huyết áp, CAUSES, Nhồi máu não)`
* **Ví dụ SAI (NO)**:
  - *"Bệnh nhân vừa bị Cao huyết áp vừa bị Viêm phế quản."* $\rightarrow$ ❌ Hai bệnh ngẫu nhiên đồng mắc (dùng `NONE`).

### 2.6. `NONE`
* **Định nghĩa**: Hai thực thể xuất hiện trong cùng một câu nhưng KHÔNG có mối quan hệ lâm sàng trực tiếp, hoặc mối quan hệ đã bị phủ định hoàn toàn.
* **Ví dụ ĐÚNG (YES)**:
  - *"Bệnh nhân không thấy dấu hiệu Viêm phổi."* $\rightarrow$ `(Bệnh nhân, NONE, Viêm phổi)`

---

## 3. Quy tắc xử lý Phủ định (Negation)
* Khi văn bản chứa từ phủ định rõ ràng (`"không"`, `"chưa ghi nhận"`, `"bình thường"`, `"không thấy"`):
  - **Quy tắc**: Không tạo quan hệ khẳng định. Gán nhãn `NONE` cho cặp thực thể bị phủ định.
  - **Ví dụ**: *"Bệnh nhân chưa ghi nhận biến chứng bàn chân."* $\rightarrow$ `relation_gold = NONE`.

---

## 4. Quy tắc xử lý Tiền sử bệnh (Medical History)
* Khi văn bản đề cập `"tiền sử"` hoặc `"tiền căn"`:
  - Nếu thuốc đang dùng HIỆN TẠI để điều trị bệnh trong tiền sử $\rightarrow$ Vẫn gán `PRESCRIBED_FOR`.
  - Nếu bệnh trong tiền sử chỉ được liệt kê ngẫu nhiên mà không liên quan đến thuốc/triệu chứng trong câu $\rightarrow$ Gán `NONE`.

---

## 5. Quy tắc xử lý khi Không chắc chắn (Uncertainty)
* Nếu gặp câu văn mơ hồ, không đủ thông tin chuyên môn y khoa để quyết định:
  - Gán nhãn dự đoán tốt nhất vào `relation_gold` hoặc `code_gold`.
  - **BẮT BUỘC**: Ghi cụm từ `uncertain` vào cột `note` kèm lý do ngắn gọn (Ví dụ: `uncertain: không rõ thuốc điều trị bệnh nào`).

---

## 6. Ví dụ Mẫu 5 Câu Đã Gán Nhãn Khái Niệm

| sentence_id | sentence_text | entity_1 | entity_2 | relation_predicted | relation_gold | note |
|---|---|---|---|---|---|---|
| `RE_001` | *"Bệnh nhân nam 54 tuổi, có tiền sử Đái tháo đường týp 2 và Cao huyết áp 3 năm nay. Đang dùng Metformin."* | `Metformin` | `Đái tháo đường týp 2` | `PRESCRIBED_FOR` | `PRESCRIBED_FOR` | Câu chuẩn, điều trị bệnh gốc |
| `RE_002` | *"Dùng Paracetamol 500mg để giảm bớt sốt cao và đau đầu."* | `Paracetamol 500mg` | `sốt cao` | `TREATS` | `TREATS` | Điều trị triệu chứng |
| `RE_003` | *"Bệnh nhân Viêm loét dạ dày tuyệt đối không được tự ý sử dụng Ibuprofen."* | `Ibuprofen` | `Viêm loét dạ dày` | `CONTRAINDICATED_FOR` | `CONTRAINDICATED_FOR` | Chống chỉ định rõ ràng |
| `RE_004` | *"Viêm ruột thừa cấp gây biểu hiện đau âm ỉ vùng hố chậu phải."* | `Viêm ruột thừa cấp` | `đau âm ỉ vùng hố chậu phải` | `HAS_SYMPTOM` | `HAS_SYMPTOM` | Biểu hiện triệu chứng bệnh |
| `RE_005` | *"Bệnh nhân hiện tại không thấy dấu hiệu Viêm phổi hay sốt."* | `Bệnh nhân` | `Viêm phổi` | `NONE` | `NONE` | Phủ định hoàn toàn |
