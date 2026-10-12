# 🚀 GEM Backend API Services

Hệ thống REST API cho Nền tảng Cố vấn Ý tưởng Đồ án & Định hướng Nghề nghiệp IT (GEM - AISC 2026).

---

## 📌 Các Endpoints Chính

### 1. Nhóm Cố vấn & Đồng hành (Consultation & Co-Pilot)
* `POST /api/consultation/analyze-idea`:
  - **Mô tả:** Phân tích ý tưởng thô từ ngôn ngữ tự nhiên.
  - **Đầu ra:** Miền bài toán (domain), các chức năng cần có (features), và 2–3 hướng nghề nghiệp tiềm năng.
* `POST /api/consultation/blueprint`:
  - **Mô tả:** Sinh Blueprint Kiến trúc Công nghệ 3 Lớp (Core Stack, Career Boosters từ TopCV, Personal Extension e.g. AI/Data).
  - **Đầu ra:** Đề xuất công nghệ, bằng chứng thị trường, đồ án tham khảo từ Qdrant, và lộ trình Sprint theo tháng.
* `POST /api/consultation/chat`:
  - **Mô tả:** Endpoint hội thoại đa lượt (Stateful Co-Pilot).
  - **Tham số:** `session_id`, `message`.
  - **Tính năng:** Tự động duy trì trạng thái ngữ cảnh qua các lượt chat (đổi target role, điều chỉnh thời gian, ưu tiên tech stack).

### 2. Nhóm Thị trường Lao động (Market Intelligence)
* `GET /api/market/roles`:
  - **Mô tả:** Lấy danh sách thống kê phân bổ theo 12 Lĩnh vực lớn (Domains) và các Vị trí chuyên môn (Specific Roles) từ 700+ JD TopCV.
* `GET /api/market/role-profile/{role_name}`:
  - **Mô tả:** Trả về Hồ sơ Kỹ năng của một vị trí cụ thể (tách biệt Core Must-Have vs Differentiating Boosters).

---

## 🛠️ Hướng dẫn Chạy Backend

```bash
# Kích hoạt môi trường ảo
.\.venv\Scripts\Activate.ps1

# Khởi chạy server FastAPI với Uvicorn
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Tài liệu tương tác Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
