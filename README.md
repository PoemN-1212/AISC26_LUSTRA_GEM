# 💎 GEM — Nền tảng AI định hướng & khớp nối năng lực Đồ án CNTT với xu hướng tuyển dụng

> **GEM** là nền tảng AI hỗ trợ sinh viên CNTT lựa chọn công nghệ và kỹ năng cho đồ án dựa trên dữ liệu tuyển dụng thực tế, đồng thời cung cấp góc nhìn về xu hướng công nghệ cho nhà trường.

<p align="center">
  <b>AISC 2026 · Data Driven Business · Team LUSTRA</b>
</p>

---

## 📖 Giới thiệu

Trong quá trình thực hiện đồ án CNTT, sinh viên thường phải tự quyết định nên sử dụng công nghệ, framework và kỹ năng nào. Tuy nhiên, việc lựa chọn này đôi khi dựa nhiều vào kinh nghiệm cá nhân hoặc xu hướng nhất thời, trong khi nhu cầu tuyển dụng trên thị trường liên tục thay đổi.

**GEM** giải quyết vấn đề này bằng cách thu thập dữ liệu tuyển dụng thực tế, phân tích các kỹ năng và công nghệ đang được doanh nghiệp yêu cầu, sau đó **khớp nối với thông tin đồ án của sinh viên** để đưa ra định hướng công nghệ phù hợp.

### 🎯 GEM hướng đến

- 📊 Phân tích xu hướng công nghệ từ dữ liệu tuyển dụng.
- 🧩 Khớp nối kỹ năng giữa **Đồ án CNTT ↔ Job Description**.
- 🤖 Ứng dụng AI/NLP để tự động nhận diện kỹ năng.
- 🛣️ Hỗ trợ xây dựng **Tech Roadmap** cho sinh viên.
- 🏫 Cung cấp **Dashboard xu hướng thị trường** cho nhà trường.

---

## 🏗️ Kiến trúc hệ thống

![Kiến trúc hệ thống GEM](Drafv1.png)

> `Drafv1.png` là bản kiến trúc hệ thống hiện tại và sẽ tiếp tục được cập nhật trong quá trình phát triển.

### 🔄 Luồng xử lý chính

```text
             JOB DESCRIPTION
                    │
                    │
                    ▼
              Thu thập dữ liệu
                    │
                    │
                    ├───────────────┐
                    │               │
                    ▼               ▼
             Auto Labeling     Student Project
                    │               │
                    └───────┬───────┘
                            ▼
                       PostgreSQL
                            │
                            ▼
                   Vector Embedding
                            │
                            ▼
                     Vector Database
                            │
                            ▼
                   Hybrid Scoring
                  ┌─────────┼─────────┐
                  │         │         │
               Cosine    Jaccard   Xu hướng
              Similarity Similarity thị trường
                  └─────────┼─────────┘
                            ▼
                  ┌─────────┴─────────┐
                  ▼                   ▼
             Tech Roadmap       Market Dashboard
                Student              School
```

---

## 🧩 Các thành phần chính

| Thành phần | Chức năng |
|---|---|
| **Apache Airflow** | Lập lịch và điều phối các pipeline dữ liệu |
| **BeautifulSoup** | Thu thập và phân tích dữ liệu từ trang web |
| **Auto Labeling** | Tự động nhận diện và kiểm tra kỹ năng |
| **PostgreSQL** | Lưu trữ dữ liệu và metadata |
| **Vector Embedding** | Chuyển đổi dữ liệu thành vector |
| **Vector Database** | Lưu trữ và tìm kiếm dữ liệu vector |
| **Hybrid Scoring** | Tính mức độ tương đồng và kết hợp xu hướng thị trường |
| **Dashboard** | Trực quan hóa xu hướng tuyển dụng |
| **Tech Roadmap** | Định hướng công nghệ cho sinh viên |
| **Docker** | Đóng gói và vận hành các dịch vụ |

---

## 📊 Dữ liệu

GEM tập trung vào hai nhóm dữ liệu chính:

### 1. Job Description

Dữ liệu tuyển dụng được thu thập từ các nền tảng tuyển dụng, trong đó tập trung vào:

- Vị trí tuyển dụng.
- Mô tả công việc.
- Yêu cầu kỹ năng.
- Công nghệ và framework.
- Thông tin liên quan đến thị trường tuyển dụng.

### 2. Student Project

Thông tin đồ án của sinh viên được sử dụng để xác định:

- Chủ đề và lĩnh vực của đồ án.
- Công nghệ đang sử dụng.
- Kỹ năng hiện có.
- Các công nghệ/kỹ năng cần được bổ sung.

Dữ liệu sau khi thu thập sẽ được làm sạch, chuẩn hóa và đưa vào các bước xử lý tiếp theo.

---

## 🤖 AI & xử lý dữ liệu

Pipeline AI của GEM được xây dựng theo các bước chính:

```text
Dữ liệu thô
    │
    ▼
Làm sạch & chuẩn hóa
    │
    ▼
Auto Labeling
    │
    ▼
Deterministic Verification
    │
    ▼
Vector Embedding
    │
    ▼
Vector Database
    │
    ▼
Semantic Retrieval / Matching
```

### Auto Labeling

Hệ thống sử dụng mô hình AI để hỗ trợ trích xuất kỹ năng từ Job Description và dữ liệu đồ án.

Sau đó, kết quả được kiểm tra bằng cơ chế **Deterministic Verification** nhằm hạn chế các nhãn không chính xác.

### Vector Embedding

Thông tin về JD và đồ án được biểu diễn dưới dạng vector để phục vụ tìm kiếm và so sánh ngữ nghĩa.

### Vector Database

Các vector được lưu trữ trong cơ sở dữ liệu vector để hỗ trợ truy vấn và tìm kiếm các nội dung có mức độ tương đồng cao.

---

## 🎯 Cơ chế Matching & Scoring

GEM sử dụng cơ chế **Hybrid Scoring**, kết hợp nhiều yếu tố thay vì chỉ dựa vào một phép đo tương đồng.

```text
                 Hybrid Score
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
     Cosine         Jaccard      Market Trend
    Similarity      Similarity       Weight
        └─────────────┼─────────────┘
                      ▼
                Matching Result
```

### Các thành phần

**Cosine Similarity**

> Đánh giá mức độ tương đồng về mặt ngữ nghĩa giữa các vector.

**Jaccard Similarity**

> So sánh mức độ giao nhau giữa các tập kỹ năng/công nghệ.

**Market Trend**

> Bổ sung trọng số dựa trên xu hướng xuất hiện của công nghệ trong dữ liệu tuyển dụng.

> Các trọng số và công thức cuối cùng có thể tiếp tục được điều chỉnh trong quá trình thực nghiệm.

---

## 📈 Kết quả đầu ra

### 👨‍🎓 Dành cho sinh viên

GEM hướng đến việc cung cấp:

- Danh sách kỹ năng/công nghệ phù hợp với đồ án.
- Mức độ tương đồng giữa đồ án và nhu cầu tuyển dụng.
- Những kỹ năng đang có xu hướng được tuyển dụng.
- **Tech Roadmap** để định hướng bổ sung công nghệ/kỹ năng.

### 🏫 Dành cho nhà trường

Dashboard cung cấp góc nhìn tổng quan về:

- Xu hướng công nghệ trên thị trường.
- Các kỹ năng được doanh nghiệp yêu cầu.
- Mức độ phổ biến của từng công nghệ.
- Thông tin hỗ trợ định hướng đào tạo.

---

## 🛠️ Công nghệ sử dụng

| Nhóm | Công nghệ |
|---|---|
| **Ngôn ngữ** | Python |
| **Data Pipeline** | Apache Airflow |
| **Web Crawling** | BeautifulSoup, Requests |
| **AI / NLP** | LLM, Embedding Model |
| **Database** | PostgreSQL |
| **Vector Search** | Vector Database |
| **Container** | Docker, Docker Compose |
| **Database Client** | DBeaver |
| **Dashboard** | Đang phát triển |

---

## 📦 Công cụ cần cài đặt

Các thành viên có thể sử dụng danh sách dưới đây để chuẩn bị môi trường phát triển.

| Công cụ | Mục đích | Tải xuống |
|---|---|---|
| **Git** | Quản lý mã nguồn | [Git](https://git-scm.com/downloads) |
| **Docker Desktop** | Chạy các container | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| **Python** | Phát triển Data Pipeline | [Python](https://www.python.org/downloads/) |
| **DBeaver** | Quản lý PostgreSQL | [DBeaver](https://dbeaver.io/download/) |
| **Visual Studio Code** | Lập trình và chỉnh sửa mã nguồn | [VS Code](https://code.visualstudio.com/download) |
| **WSL2** | Môi trường Linux trên Windows | [WSL2](https://learn.microsoft.com/windows/wsl/install) |

> **Lưu ý:** Phiên bản cụ thể của từng công cụ sẽ được thống nhất theo môi trường triển khai của nhóm.

---

## ⚙️ Cài đặt & chạy dự án

### 1. Clone repository

```bash
git clone https://github.com/PoemN-1212/AISC26_LUSTRA_GEM.git
cd AISC26_LUSTRA_GEM
```

### 2. Thiết lập môi trường ảo (Virtual Environment)
Việc này giúp IDE nhận diện đúng thư viện, hỗ trợ code và tránh báo lỗi (chạy ở thư mục gốc AISC26_LUSTRA_GEM).

```bash
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt môi trường (Dành cho Windows PowerShell)
.\.venv\Scripts\Activate.ps1
# Lưu ý: Nếu báo lỗi đỏ, chạy lệnh này trước để cấp quyền: Set-ExecutionPolicy Unrestricted -Scope CurrentUser

# Cài đặt các thư viện cơ bản
pip install requests bs4 psycopg2-binary apache-airflow
```


### 3. Tạo file môi trường

Tạo file `.env` dựa trên cấu hình mẫu:

```bash
cp .env.example .env
```

Sau đó cấu hình các thông tin cần thiết như:

```env
# POSTGRESQL CONFIG
POSTGRES_USER=gem_admin
POSTGRES_PASSWORD=gem_secret_password
POSTGRES_DB=gem_database
POSTGRES_PORT=5432

# QDRANT CONFIG
QDRANT_PORT=6333

# KẾT NỐI CLOUD (Nhận Password từ Trưởng nhóm)
CLOUD_DB_URL=postgresql://neondb_owner:[PASSWORD]@ep-red-salad-b3mi20mi-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?sslmode=require
GITHUB_TOKEN=ghp_...
```

> ⚠️ **Không commit mật khẩu, API Key hoặc thông tin kết nối cơ sở dữ liệu thật lên GitHub.**

### 4. Khởi động hệ thống

```bash
# Di chuyển vào thư mục chứa file docker-compose.yml
cd infra

# Khởi động toàn bộ container lên (Lấy biến môi trường từ thư mục cha)
docker-compose --env-file ../.env up -d

# --- CÁC BƯỚC DƯỚI ĐÂY CHỈ CẦN CHẠY TRONG LẦN ĐẦU TIÊN CÀI ĐẶT ---

# Khởi tạo Metadata Database cho Airflow
docker exec -it gem_airflow_webserver airflow db init

# Tạo tài khoản đăng nhập giao diện Airflow (có thể thay đổi dựa theo bạn muốn)
docker exec -it gem_airflow_webserver airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
```

Kiểm tra các container:

```bash
docker compose ps
```

### 5. Truy cập hệ thống

Sau khi hệ thống khởi động:

```text
http://localhost:8080
```

Tại Airflow, các DAG có thể được theo dõi và thực thi theo lịch đã cấu hình.

---

## 🗄️ Lưu trữ dữ liệu

Kiến trúc hiện tại sử dụng PostgreSQL làm nơi lưu trữ dữ liệu có cấu trúc và metadata.

Luồng tổng quát:

```text
Crawler
   │
   ▼
Raw Job Data
   │
   ▼
Cleaning / Processing
   │
   ▼
Auto Labeling
   │
   ▼
PostgreSQL
   │
   ├──────────────► Metadata / JSON
   │
   └──────────────► Vector Embedding
                            │
                            ▼
                     Vector Database
```

Hệ thống cũng có cơ chế **Data Retiring / TTL Cleanup** để xử lý dữ liệu cũ theo chu kỳ.

---

## 🧹 Data Retiring

Dữ liệu tuyển dụng có tính chất thay đổi theo thời gian. Vì vậy, GEM có cơ chế quản lý vòng đời dữ liệu:

```text
Dữ liệu mới
    │
    ▼
Lưu trữ
    │
    ▼
Theo dõi thời gian
    │
    ▼
TTL / Retiring
    │
    ▼
Dọn dẹp dữ liệu cũ
```

Việc này giúp hạn chế dữ liệu lỗi thời ảnh hưởng đến việc phân tích xu hướng thị trường.

---

## 📂 Cấu trúc Repository

```text
AISC26_LUSTRA_GEM/
│
├── dags/                 # Airflow DAGs
├── crawler/              # Thu thập dữ liệu
├── processing/           # Làm sạch & xử lý dữ liệu
├── labeling/             # Auto Labeling
├── embedding/            # Vector Embedding
├── scoring/              # Matching & Scoring
├── dashboard/            # Dashboard
├── docker/               # Docker configuration
│
├── Drafv1.png            # Kiến trúc hệ thống hiện tại
├── .env.example          # Mẫu biến môi trường
├── docker-compose.yml     # Docker Compose
└── README.md             # Tài liệu dự án
```

> Cấu trúc thư mục có thể thay đổi khi các module tiếp tục được phát triển.

---

## 🗺️ Tiến độ phát triển

| Hạng mục | Trạng thái |
|---|---|
| Thu thập dữ liệu tuyển dụng | 🟢 Đang phát triển |
| Làm sạch & xử lý dữ liệu | 🟢 Đang phát triển |
| Auto Labeling | 🟡 Đang hoàn thiện |
| Vector Embedding | 🟡 Đang phát triển |
| Vector Database | 🟡 Đang phát triển |
| Hybrid Matching | 🟡 Đang phát triển |
| Tech Roadmap | ⚪ Đang lên kế hoạch |
| Market Trend Dashboard | ⚪ Đang lên kế hoạch |

> Trạng thái sẽ được cập nhật theo tiến độ thực tế của nhóm.

---

## 👥 Đội ngũ LUSTRA

**Cuộc thi Advanced Information Systems Contest 2026 — AISC 2026**

| Thành viên | MSSV | Vai trò |
|---|---:|---|
| **Lê Vĩnh Thái** | 23521417 | Team Lead / Data Engineer |
| **Nguyễn Văn Mạnh Huy** | 23520641 | — |
| **Trần Nhụy Tam Tử Phục** | 24521400 | — |
| **Phạm Nhật Khoa** | 23520753 | — |

**Đơn vị:** Trường Đại học Công nghệ Thông tin — ĐHQG-HCM (UIT)  
**Khoa:** Hệ thống Thông tin  
**Chủ đề:** Data Driven Business

---

## 🏆 Về dự án

**GEM** được phát triển trong khuôn khổ **AISC 2026**, với định hướng xây dựng một nền tảng dữ liệu và AI giúp kết nối:

```text
Đồ án sinh viên
       ↕
      GEM
       ↕
Thị trường tuyển dụng
```

Mục tiêu cuối cùng là biến dữ liệu tuyển dụng thành những thông tin có thể sử dụng trực tiếp để hỗ trợ sinh viên **định hướng công nghệ, phát triển kỹ năng và xây dựng đồ án có tính thị trường cao hơn**.

---

## 🚧 Trạng thái dự án

> **GEM đang trong quá trình phát triển.**

Kiến trúc `Drafv1.png` hiện là bản mô tả tổng thể của hệ thống. Các thành phần, công nghệ và luồng xử lý sẽ tiếp tục được nhóm cập nhật khi triển khai thực tế.

---

<p align="center">
  <b>💎 GEM × LUSTRA</b><br>
  <i>Kết nối Đồ án CNTT với nhu cầu của thị trường tuyển dụng.</i>
</p>
