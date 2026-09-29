# 🚀 Dự Án GEM: Nền Tảng AI Định Hướng & Khớp Nối Năng Lực Đồ Án CNTT

## 📌 1. Giới thiệu Dự Án
**GEM (An AI Platform for Orienting and Matching IT Capstone Projects with Recruitment Trends)** là dự án tham gia cuộc thi *Advanced Information Systems Contest 2026* do đội thi LUSTRA thuộc Khoa Hệ thống Thông tin (UIT) thực hiện.

**Bài toán:** Sinh viên CNTT thường gặp khó khăn trong việc chọn công nghệ cho đồ án, dẫn đến tình trạng hệ thống xây dựng xong bị lỗi thời, tạo ra "Độ chêch lệch kỹ năng" (Skill Gap) lớn so với yêu cầu của thị trường lao động.

**Mục tiêu GEM:** 
Thay vì chỉ khớp nối CV khi sinh viên đã ra trường, GEM ứng dụng tư duy **Shift-Left** bằng cách can thiệp sớm vào giai đoạn thai nghén ý tưởng đồ án. Nền tảng sử dụng Kiến trúc RAG (Retrieval-Augmented Generation) để đối chiếu "Điểm thực chiến" của ý tưởng đồ án với hàng chục ngàn tin tuyển dụng (Job Descriptions) thời gian thực, từ đó xuất ra báo cáo định hướng công nghệ cá nhân hóa.

---

## 👥 2. Đội thi LUSTRA
*Sinh viên Khoa Hệ thống Thông tin - Trường Đại học Công nghệ Thông tin (UIT)*
- **Lê Vĩnh Thái** - 23521417 (Trưởng nhóm / Data Engineer)
- **Nguyễn Văn Mạnh Huy** - 23520641
- **Trần Nhụy Tam Tử Phục** - 24521400
- **Phạm Nhật Khoa** - 23520753

---

## 🏗️ 3. Phân Hệ Đang Triển Khai: Data Ingestion Pipeline
Kho lưu trữ (Repository) này chứa mã nguồn của **Giai đoạn 1: Thu thập và Tiền xử lý dữ liệu thô (Data Ingestion)**. 
Hệ thống sử dụng Python và Apache Airflow để cào tự động 10.000+ tin tuyển dụng IT từ TopCV, vượt rào chống bot qua FlareSolverr và lưu trữ tập trung trên hệ thống Neon.tech Cloud PostgreSQL.

### Kiến Trúc Data Pipeline
- **Apache Airflow:** Lập lịch và điều phối (Orchestration).
- **Python (BeautifulSoup, Requests):** Bóc tách văn bản phi cấu trúc áp dụng cơ chế Chunking tối ưu RAM.
- **FlareSolverr:** Proxy Server vượt tường lửa Cloudflare Captcha.
- **Neon.tech:** Cloud Database lưu trữ JDs chia sẻ cho toàn bộ Data Analyst/AI Engineer trong nhóm.
- **Docker Compose:** Đóng gói môi trường đồng nhất.

---

## ⚙️ 4. Hướng dẫn Cài đặt Môi trường & Khởi chạy Pipeline

### Yêu cầu tiên quyết (Prerequisites)
1. Cài đặt **Git**, **Docker Desktop**, và phần mềm quản trị CSDL **DBeaver**.
2. *(Máy Windows)* Bật WSL2 và tạo file `%USERPROFILE%\.wslconfig` để cấp đủ RAM:
   ```ini
   [wsl2]
   memory=8GB
   swap=4GB
   ```
Các bước khởi động

**Bước 1**: Clone Code

```Bash
git clone https://github.com/PoemN-1212/AISC26_LUSTRA_GEM.git
cd gem-data-ingestion
```
**Bước 2**: Cấu hình Biến môi trường (.env)
Tạo file .env ở thư mục gốc và dán thông tin (Liên hệ Trưởng nhóm Lê Vĩnh Thái để nhận Password Cloud DB):

```Ini, TOML
# Cấu hình Metadata Airflow (Local)
POSTGRES_USER=gem_admin
POSTGRES_PASSWORD=gem_secret_password
POSTGRES_DB=gem_database
POSTGRES_PORT=5432

# Kết nối Cloud Database (Neon.tech)
CLOUD_DB_URL=postgresql://neondb_owner:[PASSWORD_Ở_ĐÂY]@ep-red-salad-b3mi20mi-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
```
**Bước 3**: Chạy Hệ Thống

```Bash
docker-compose --env-file .env up -d
```

Chờ khoảng 2 phút để container khởi tạo mạng.

**Bước 4**: Kích hoạt Thu Thập (Airflow)
Truy cập http://localhost:8080, tìm DAG gem_topcv_daily_crawler, gạt công tắc Unpause và bấm Trigger DAG.

## 🗄️ 5. Hướng dẫn Lấy Dữ Liệu (Dành cho AI Team)
Các thành viên phụ trách xây dựng Bộ kiểm duyệt tất định (Deterministic Verifier) và Mô hình Không gian Vector (Qdrant) không cần chạy Airflow. Chỉ cần kết nối thẳng vào Cloud DB để lấy Data JDs sạch.

Mở DBeaver -> Tạo kết nối PostgreSQL mới.

Nhập các thông số:

Host: ep-red-salad-b3mi20mi-pooler.c-4.ap-southeast-1.aws.neon.tech

Database: neondb

Username: neondb_owner

Password: Liên hệ Trưởng nhóm.

⚠️ Chuyển sang tab SSL, mục SSL mode chọn require.

Truy vấn hoặc Export bảng: neondb > Schemas > public > Tables > raw_job_postings.

## 🎯 6. Giai Đoạn Tiếp Theo (Roadmap)
Dữ liệu JDs thu thập từ Pipeline này sẽ được chuyển sang các phân hệ sau của dự án:

Auto-labeling Framework: Đưa qua LLM để định dạng nhãn đóng khung (Span Anchoring).

Vectorization: Nhúng đa ngữ bằng BGE-M3 và lưu trữ lên Qdrant DB.

Web Application: Tích hợp thuật toán tính điểm thực chiến (Cosine Distance & Jaccard) trên nền tảng Web cho sinh viên trải nghiệm.