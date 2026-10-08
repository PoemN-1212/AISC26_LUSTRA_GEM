# HƯỚNG DẪN GÁN NHÃN KỸ NĂNG — GEM ANNOTATION GUIDELINE v1.0
## Dự án GEM (LUSTRA_GEM) — AISC 2026 (UIT)
## Chuẩn hóa dữ liệu trích xuất kỹ năng từ Tin tuyển dụng (TopCV) & Đồ án sinh viên (GitHub)

---

## 1. Mục đích và phạm vi tài liệu

Tài liệu này là **quy chuẩn vận hành duy nhất (Canonical Operational Guideline)** dành cho:
1. **Con người (Human Annotators)**: Thực hiện gán nhãn và kiểm định tập dữ liệu chuẩn mực (**Gold Set**).
2. **Mô hình AI (LLM / Prompt Engineering)**: Đóng vai trò là System Prompt và tiêu chuẩn trích xuất cho các mô hình AI (Qwen / Gemini).
3. **Bộ kiểm tra (Verifier)**: Làm thước đo logic tất định để phát hiện và loại bỏ các trường hợp trích xuất ảo giác (hallucination) hoặc sai lệch ranh giới (boundary drift).

---

## 2. Hệ thống nhãn cốt lõi (MVP Taxonomy)

Trong phạm vi MVP của dự án GEM, toàn bộ năng lực được phân loại thành **2 nhãn duy nhất**:

```text
┌────────────────────────────────────────────────────────┐
│                   NĂNG LỰC ỨNG VIÊN                    │
├──────────────────────────┬─────────────────────────────┤
│       TECHNOLOGY         │           ABILITY           │
│  (Công nghệ / Công cụ)   │    (Hành động / Năng lực)   │
└──────────────────────────┴─────────────────────────────┘
```

### 2.1 Nhãn `TECHNOLOGY` (Công nghệ & Công cụ)

* **Định nghĩa**: Là các thực thể kỹ thuật hữu hình, bao gồm: ngôn ngữ lập trình, framework, thư viện, hệ quản trị cơ sở dữ liệu, nền tảng cloud, công cụ DevOps, hệ điều hành, giao thức mạng, tiêu chuẩn API.
* **Các nhóm chính & Ví dụ**:
  * **Ngôn ngữ lập trình**: `Python`, `Java`, `JavaScript`, `TypeScript`, `C++`, `C#`, `Golang`, `PHP`, `Dart`...
  * **Framework / Thư viện**: `React`, `FastAPI`, `Spring Boot`, `Django`, `Node.js`, `ExpressJS`, `Vue.js`, `Flutter`, `PyTorch`, `TensorFlow`...
  * **Cơ sở dữ liệu / Bộ nhớ đệm**: `PostgreSQL`, `MySQL`, `MongoDB`, `Redis`, `Elasticsearch`, `SQLite`...
  * **Cloud & DevOps**: `Docker`, `Kubernetes`, `AWS`, `Google Cloud (GCP)`, `Azure`, `CI/CD`, `GitHub Actions`, `Git`...
  * **Giao thức & Kiến trúc**: `REST API`, `GraphQL`, `gRPC`, `WebSocket`, `Microservices`...

### 2.2 Nhãn `ABILITY` (Năng lực / Hành động kỹ thuật)

* **Định nghĩa**: Là hành động hoặc khả năng kỹ thuật cụ thể mà ứng viên cần thực hiện trong công việc, thường có cấu trúc: `[Động từ kỹ thuật] + [Đối tượng / Mục tiêu kỹ thuật]`.
* **Ví dụ điển hình**:
  * `phát triển REST API` (thay vì chỉ biết REST API)
  * `thiết kế cơ sở dữ liệu`
  * `tối ưu hóa truy vấn SQL`
  * `viết unit test`
  * `xây dựng kiến trúc microservices`
  * `phân tích yêu cầu nghiệp vụ`
  * `debug lỗi hệ thống trên môi trường production`
  * `huấn luyện mô hình học máy`
  * `bảo mật hệ thống thông tin`

---

## 3. Quy tắc xác định ranh giới (Span Boundary Rules)

### 3.1 Quy tắc Ranh giới tối thiểu có nghĩa (Minimal Meaningful Span)
* **Tuyệt đối loại bỏ các từ kích hoạt / từ đệm (Trigger / Filler words)**:
  * Từ đệm tiếng Việt: *có kinh nghiệm*, *thành thạo*, *hiểu biết về*, *nắm vững*, *có khả năng*, *ưu tiên ứng viên biết*, *quen thuộc với*...
  * Từ đệm tiếng Anh: *experience with*, *strong knowledge of*, *proficient in*, *familiar with*, *good understanding of*...

| Câu gốc trong JD | ❌ Span SAI (ôm đồm cả câu/filler) | ✅ Span ĐÚNG (Minimal Meaningful) | Nhãn |
|---|---|---|---|
| *"Có trên 2 năm kinh nghiệm với Python"* | `"Có trên 2 năm kinh nghiệm với Python"` | `"Python"` | `TECHNOLOGY` |
| *"Thành thạo phát triển REST API"* | `"Thành thạo phát triển REST API"` | `"phát triển REST API"` | `ABILITY` |
| *"Strong experience in database design"* | `"Strong experience in database design"` | `"database design"` | `ABILITY` |

### 3.2 Quy tắc Một câu chứa nhiều kỹ năng (Multiple Skills in One Sentence)
Khi một câu chứa nhiều công nghệ hoặc hành động, **phải tách thành các bản ghi riêng biệt**, không được gom gộp thành một chuỗi dài.

* **Ví dụ**:
  > *"Xây dựng web application sử dụng React, FastAPI và cơ sở dữ liệu PostgreSQL."*
  * Record 1: `"Xây dựng web application"` ➔ `ABILITY`
  * Record 2: `"React"` ➔ `TECHNOLOGY`
  * Record 3: `"FastAPI"` ➔ `TECHNOLOGY`
  * Record 4: `"PostgreSQL"` ➔ `TECHNOLOGY`

### 3.3 Quy tắc Bảo toàn nguyên văn bằng chứng (Evidence Preservation)
* `evidence` là **chuỗi con chính xác 100%** trích từ văn bản gốc, không tự ý sửa đổi hoa-thường, không bỏ dấu tiếng Việt.
* Việc ánh xạ sang tên chuẩn (Canonical Skill) là bước tiếp theo ở Module Normalization, không được thực hiện đè lên `evidence`.
  * *Ví dụ*: JD viết `"ReactJS"` ➔ `evidence = "ReactJS"`, sau này chuẩn hóa thành `canonical_skill = "React"`.

---

## 4. Những điều TUYỆT ĐỐI KHÔNG gán nhãn (Negative Rules)

1. **KHÔNG gán nhãn chức danh / vị trí công việc (Job Title / Role)**:
   * ❌ Bỏ qua: `Backend Developer`, `Frontend Engineer`, `Lập trình viên AI`, `Data Scientist`, `Tech Lead`...
2. **KHÔNG gán nhãn tên công ty, tổ chức hoặc sản phẩm nội bộ**:
   * ❌ Bỏ qua: `TopCV`, `FPT`, `Viettel`, `Shopee`, `Hệ thống ERP của công ty`...
3. **KHÔNG gán nhãn công nghệ chỉ xuất hiện ở phần giới thiệu doanh nghiệp**:
   * Nếu công ty viết: *"Công ty chúng tôi dùng SAP để quản lý nội bộ"* nhưng JD tuyển lập trình viên React ➔ Không gán nhãn SAP.
4. **KHÔNG gán nhãn chế độ, quyền lợi và thông tin hành chính**:
   * ❌ Bỏ qua: `Lương tháng 13`, `BHXH`, `Du lịch hàng năm`, `Phụ cấp cơm trưa`, `MacBook Pro`...
5. **KHÔNG gán nhãn kỹ năng mềm chung chung (Soft Skills ngoài phạm vi MVP)**:
   * ❌ Bỏ qua: `Giao tiếp tốt`, `Chăm chỉ`, `Hòa đồng`, `Chịu được áp lực cao`, `Có trách nhiệm`...

---

## 5. Quy trình gán nhãn cho Golden Set (Gold Set Workflow)

Để tạo tập nhãn vàng chuẩn mực (Gold Set) dùng cho đánh giá mà không bị thiên lệch (Recall Bias):

```text
[Mẫu 100-150 JD ngẫu nhiên]
            │
            ▼
    LLM Pre-Annotation
  (Gợi ý ban đầu có schema)
            │
            ▼
     Human Verification
            ├─► 1. ACCEPT : LLM trích xuất đúng, giữ nguyên.
            ├─► 2. REJECT : LLM bịa đặt / trích xuất rác, xóa bỏ.
            ├─► 3. MODIFY : Sửa lại ranh giới span hoặc type.
            └─► 4. ADD    : BỔ SUNG CÁC KỸ NĂNG LLM BỎ SÓT (Bắt buộc để đo Recall thật!).
```

---

## 6. Tiêu chuẩn đánh giá khớp Span (Span Matching Metrics)

Khi so sánh kết quả trích xuất của Model AI với tập nhãn vàng Gold Set:

1. **Strict Match (Khớp tuyệt đối)**:
   * `Type(pred) == Type(gold)` VÀ `Span(pred) == Span(gold)` (khớp chính xác từng ký tự).
   * Thường dùng để đánh giá `TECHNOLOGY`.
2. **Relaxed / Overlap Match (Khớp tương đối / Chồng lấn)**:
   * `Type(pred) == Type(gold)` VÀ `Intersection(Span(pred), Span(gold)) > 0`.
   * Thường áp dụng linh hoạt cho `ABILITY` vì ranh giới từ ngữ miêu tả hành động trong tiếng Việt có thể chênh lệch 1-2 từ liên từ.
