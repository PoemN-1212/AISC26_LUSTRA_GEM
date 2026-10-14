"""
GEM Data Cleaning & Normalization Pipeline (Stage 1)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Chức năng:
1. Làm sạch dữ liệu Job Descriptions (TopCV) và Đồ án sinh viên (GitHub).
2. Chuẩn hóa & bảo toàn toàn diện các thuộc tính thời gian (posted_date, posted_year, posted_month, location, created_at, updated_at, pushed_at).
3. Lưu trữ & Đồng bộ hóa 3 tầng (Triple-Tier Persistence):
   - Tầng 1: CSDL cục bộ (Local PostgreSQL - Docker/localhost)
   - Tầng 2: CSDL đám mây (Cloud PostgreSQL - Neon)
   - Tầng 3: File JSONL tại data/processed/jobs/ và data/processed/projects/
"""

import os
import sys
import json
from datetime import datetime, date
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Thêm pipeline/src vào sys.path
pipeline_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline", "src"))
if pipeline_src not in sys.path:
    sys.path.insert(0, pipeline_src)

from gem_pipeline.cleaning.job_cleaner import clean_job_record
from gem_pipeline.cleaning.project_cleaner import clean_project_record

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_USER = os.getenv("POSTGRES_USER", "gem_admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "gem_secret_password")
DB_NAME = os.getenv("POSTGRES_DB", "gem_database")

CLOUD_DB_URL = os.getenv("CLOUD_DB_URL")


def get_local_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME,
        connect_timeout=10
    )


def get_cloud_connection():
    if CLOUD_DB_URL:
        try:
            return psycopg2.connect(CLOUD_DB_URL, connect_timeout=15)
        except Exception as e:
            print(f"⚠️ Cảnh báo: Không thể kết nối Cloud DB ({e})")
    return None


def get_data_dir() -> str:
    possible_paths = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")),
        "/opt/airflow/data",
        "data"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(default_path, exist_ok=True)
    return default_path


def init_cleaned_tables(conn):
    """Khởi tạo cấu trúc bảng sạch với đầy đủ các cột thời gian và chỉ mục."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cleaned_job_postings (
            id SERIAL PRIMARY KEY,
            raw_job_id INT UNIQUE REFERENCES raw_job_postings(id) ON DELETE CASCADE,
            title VARCHAR,
            company VARCHAR,
            salary_min NUMERIC,
            salary_max NUMERIC,
            content_clean TEXT NOT NULL,
            content_hash VARCHAR(64),
            char_count INT,
            posted_date DATE,
            posted_year INT,
            posted_month INT,
            location VARCHAR,
            cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS cleaned_github_projects (
            id SERIAL PRIMARY KEY,
            raw_project_id INT UNIQUE REFERENCES raw_github_projects(id) ON DELETE CASCADE,
            repo_name VARCHAR,
            author VARCHAR,
            language VARCHAR,
            combined_clean_text TEXT NOT NULL,
            content_hash VARCHAR(64),
            char_count INT,
            created_at VARCHAR,
            updated_at VARCHAR,
            pushed_at VARCHAR,
            cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_cleaned_job_posted_date ON cleaned_job_postings(posted_date);
        CREATE INDEX IF NOT EXISTS idx_cleaned_job_year_month ON cleaned_job_postings(posted_year, posted_month);
    """)
    conn.commit()
    cur.close()


def parse_date(raw_date):
    if not raw_date:
        return None
    if isinstance(raw_date, (date, datetime)):
        return raw_date
    if isinstance(raw_date, str):
        try:
            return datetime.strptime(raw_date[:10], "%Y-%m-%d").date()
        except Exception:
            return None
    return None


def process_clean_jobs(conn_local, conn_cloud=None, limit=None):
    """Làm sạch toàn bộ tin tuyển dụng TopCV và đồng bộ 3 tầng."""
    cur = conn_local.cursor()
    query = """
        SELECT id, url, title, company, salary_min, salary_max, full_content, posted_date, location 
        FROM raw_job_postings
        ORDER BY id;
    """
    if limit:
        query += f" LIMIT {limit}"
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()

    total_raw_len = 0
    total_clean_len = 0
    local_batch = []
    jsonl_records = []
    job_clean_map = {}  # url -> clean data (dùng để sync sang Cloud DB)

    for row in rows:
        job_id = row[0]
        url = row[1]
        title = row[2]
        company = row[3]
        sal_min = row[4]
        sal_max = row[5]
        content = row[6]
        raw_posted_date = parse_date(row[7])
        location = row[8] or ""

        raw_dict = {
            "id": job_id,
            "title": title,
            "company": company,
            "salary_min": sal_min,
            "salary_max": sal_max,
            "full_content": content
        }
        cleaned = clean_job_record(raw_dict)
        total_raw_len += cleaned["content_raw_length"]
        total_clean_len += cleaned["content_clean_length"]

        posted_year = raw_posted_date.year if raw_posted_date else None
        posted_month = raw_posted_date.month if raw_posted_date else None

        record_tuple = (
            cleaned["job_id"],
            cleaned["title"],
            cleaned["company"],
            cleaned["salary_min"],
            cleaned["salary_max"],
            cleaned["content_clean"],
            cleaned["content_hash"],
            cleaned["content_clean_length"],
            raw_posted_date,
            posted_year,
            posted_month,
            location
        )
        local_batch.append(record_tuple)

        job_clean_map[url] = {
            "title": cleaned["title"],
            "company": cleaned["company"],
            "salary_min": cleaned["salary_min"],
            "salary_max": cleaned["salary_max"],
            "content_clean": cleaned["content_clean"],
            "content_hash": cleaned["content_hash"],
            "char_count": cleaned["content_clean_length"],
            "posted_date": raw_posted_date,
            "posted_year": posted_year,
            "posted_month": posted_month,
            "location": location
        }

        jsonl_records.append({
            "raw_job_id": cleaned["job_id"],
            "url": url,
            "title": cleaned["title"],
            "company": cleaned["company"],
            "salary_min": float(cleaned["salary_min"]) if cleaned["salary_min"] is not None else 0,
            "salary_max": float(cleaned["salary_max"]) if cleaned["salary_max"] is not None else 0,
            "content_clean": cleaned["content_clean"],
            "content_hash": cleaned["content_hash"],
            "char_count": cleaned["content_clean_length"],
            "posted_date": str(raw_posted_date) if raw_posted_date else None,
            "posted_year": posted_year,
            "posted_month": posted_month,
            "location": location
        })

    # 1. NẠP VÀO LOCAL POSTGRESQL (Tầng 1)
    insert_sql = """
        INSERT INTO cleaned_job_postings 
        (raw_job_id, title, company, salary_min, salary_max, content_clean, content_hash, char_count, 
         posted_date, posted_year, posted_month, location)
        VALUES %s
        ON CONFLICT (raw_job_id) DO UPDATE 
        SET content_clean = EXCLUDED.content_clean,
            content_hash = EXCLUDED.content_hash,
            char_count = EXCLUDED.char_count,
            posted_date = EXCLUDED.posted_date,
            posted_year = EXCLUDED.posted_year,
            posted_month = EXCLUDED.posted_month,
            location = EXCLUDED.location,
            cleaned_at = CURRENT_TIMESTAMP;
    """
    cur_loc = conn_local.cursor()
    batch_size = 500
    for i in range(0, len(local_batch), batch_size):
        chunk = local_batch[i:i + batch_size]
        execute_values(cur_loc, insert_sql, chunk)
    conn_local.commit()
    cur_loc.close()
    print(f"  ✅ Đã lưu {len(local_batch):,} tin vào Local DB (cleaned_job_postings).")

    # 2. XUẤT RA FILE JSONL CỤC BỘ (Tầng 2)
    data_dir = get_data_dir()
    out_dir = os.path.join(data_dir, "processed", "jobs")
    os.makedirs(out_dir, exist_ok=True)
    out_jsonl = os.path.join(out_dir, "cleaned_jobs.jsonl")
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for r in jsonl_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  📁 Đã xuất dữ liệu ra file: {out_jsonl}")

    # 3. ĐỒNG BỘ SANG CLOUD POSTGRESQL (Tầng 3)
    if conn_cloud:
        print("  🌐 Đang đồng bộ hóa sang Cloud DB (Neon)...")
        try:
            cur_cld = conn_cloud.cursor()
            # Lấy bản đồ URL -> ID trên Cloud để khớp chính xác raw_job_id
            cur_cld.execute("SELECT url, id FROM raw_job_postings;")
            cloud_url_map = {r[0]: r[1] for r in cur_cld.fetchall()}

            cloud_batch = []
            for url, data in job_clean_map.items():
                if url in cloud_url_map:
                    cloud_job_id = cloud_url_map[url]
                    cloud_batch.append((
                        cloud_job_id,
                        data["title"],
                        data["company"],
                        data["salary_min"],
                        data["salary_max"],
                        data["content_clean"],
                        data["content_hash"],
                        data["char_count"],
                        data["posted_date"],
                        data["posted_year"],
                        data["posted_month"],
                        data["location"]
                    ))

            for i in range(0, len(cloud_batch), batch_size):
                chunk = cloud_batch[i:i + batch_size]
                execute_values(cur_cld, insert_sql, chunk)
            conn_cloud.commit()
            cur_cld.close()
            print(f"  ☁️ Đã đồng bộ thành công {len(cloud_batch):,} tin lên Cloud DB (Neon).")
        except Exception as e:
            print(f"  ⚠️ Lỗi đồng bộ Cloud DB: {e}")
            conn_cloud.rollback()

    reduction = ((total_raw_len - total_clean_len) / total_raw_len * 100) if total_raw_len > 0 else 0
    return len(rows), total_raw_len, total_clean_len, reduction


def process_clean_projects(conn_local, conn_cloud=None, limit=None):
    """Làm sạch toàn bộ đồ án sinh viên GitHub và đồng bộ 3 tầng."""
    cur = conn_local.cursor()
    query = """
        SELECT id, repo_url, repo_name, author, description, readme_content, language, 
               created_at, updated_at, pushed_at 
        FROM raw_github_projects
        ORDER BY id;
    """
    if limit:
        query += f" LIMIT {limit}"
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()

    total_raw_len = 0
    total_clean_len = 0
    local_batch = []
    jsonl_records = []
    proj_clean_map = {}

    for row in rows:
        proj_id = row[0]
        repo_url = row[1]
        repo_name = row[2]
        author = row[3]
        desc = row[4]
        readme = row[5]
        language = row[6]
        created_at = row[7]
        updated_at = row[8]
        pushed_at = row[9]

        raw_dict = {
            "id": proj_id,
            "repo_name": repo_name,
            "author": author,
            "description": desc,
            "readme_content": readme,
            "language": language
        }
        cleaned = clean_project_record(raw_dict)
        total_raw_len += cleaned["readme_raw_length"]
        total_clean_len += cleaned["combined_clean_length"]

        record_tuple = (
            cleaned["project_id"],
            cleaned["repo_name"],
            cleaned["author"],
            cleaned["language"],
            cleaned["combined_clean_text"],
            cleaned["content_hash"],
            cleaned["combined_clean_length"],
            created_at,
            updated_at,
            pushed_at
        )
        local_batch.append(record_tuple)

        proj_clean_map[repo_url] = {
            "repo_name": cleaned["repo_name"],
            "author": cleaned["author"],
            "language": cleaned["language"],
            "combined_clean_text": cleaned["combined_clean_text"],
            "content_hash": cleaned["content_hash"],
            "char_count": cleaned["combined_clean_length"],
            "created_at": created_at,
            "updated_at": updated_at,
            "pushed_at": pushed_at
        }

        jsonl_records.append({
            "raw_project_id": cleaned["project_id"],
            "repo_url": repo_url,
            "repo_name": cleaned["repo_name"],
            "author": cleaned["author"],
            "language": cleaned["language"],
            "combined_clean_text": cleaned["combined_clean_text"],
            "content_hash": cleaned["content_hash"],
            "char_count": cleaned["combined_clean_length"],
            "created_at": created_at,
            "updated_at": updated_at,
            "pushed_at": pushed_at
        })

    # 1. NẠP VÀO LOCAL POSTGRESQL (Tầng 1)
    insert_sql = """
        INSERT INTO cleaned_github_projects 
        (raw_project_id, repo_name, author, language, combined_clean_text, content_hash, char_count, 
         created_at, updated_at, pushed_at)
        VALUES %s
        ON CONFLICT (raw_project_id) DO UPDATE 
        SET combined_clean_text = EXCLUDED.combined_clean_text,
            content_hash = EXCLUDED.content_hash,
            char_count = EXCLUDED.char_count,
            created_at = EXCLUDED.created_at,
            updated_at = EXCLUDED.updated_at,
            pushed_at = EXCLUDED.pushed_at,
            cleaned_at = CURRENT_TIMESTAMP;
    """
    cur_loc = conn_local.cursor()
    batch_size = 500
    for i in range(0, len(local_batch), batch_size):
        chunk = local_batch[i:i + batch_size]
        execute_values(cur_loc, insert_sql, chunk)
    conn_local.commit()
    cur_loc.close()
    print(f"  ✅ Đã lưu {len(local_batch):,} đồ án vào Local DB (cleaned_github_projects).")

    # 2. XUẤT RA FILE JSONL CỤC BỘ (Tầng 2)
    data_dir = get_data_dir()
    out_dir = os.path.join(data_dir, "processed", "projects")
    os.makedirs(out_dir, exist_ok=True)
    out_jsonl = os.path.join(out_dir, "cleaned_projects.jsonl")
    with open(out_jsonl, "w", encoding="utf-8") as f:
        for r in jsonl_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"  📁 Đã xuất dữ liệu ra file: {out_jsonl}")

    # 3. ĐỒNG BỘ SANG CLOUD POSTGRESQL (Tầng 3)
    if conn_cloud:
        print("  🌐 Đang đồng bộ hóa sang Cloud DB (Neon)...")
        try:
            cur_cld = conn_cloud.cursor()
            cur_cld.execute("SELECT repo_url, id FROM raw_github_projects;")
            cloud_repo_map = {r[0]: r[1] for r in cur_cld.fetchall()}

            cloud_batch = []
            for repo_url, data in proj_clean_map.items():
                if repo_url in cloud_repo_map:
                    cloud_proj_id = cloud_repo_map[repo_url]
                    cloud_batch.append((
                        cloud_proj_id,
                        data["repo_name"],
                        data["author"],
                        data["language"],
                        data["combined_clean_text"],
                        data["content_hash"],
                        data["char_count"],
                        data["created_at"],
                        data["updated_at"],
                        data["pushed_at"]
                    ))

            for i in range(0, len(cloud_batch), batch_size):
                chunk = cloud_batch[i:i + batch_size]
                execute_values(cur_cld, insert_sql, chunk)
            conn_cloud.commit()
            cur_cld.close()
            print(f"  ☁️ Đã đồng bộ thành công {len(cloud_batch):,} đồ án lên Cloud DB (Neon).")
        except Exception as e:
            print(f"  ⚠️ Lỗi đồng bộ Cloud DB: {e}")
            conn_cloud.rollback()

    reduction = ((total_raw_len - total_clean_len) / total_raw_len * 100) if total_raw_len > 0 else 0
    return len(rows), total_raw_len, total_clean_len, reduction


def main():
    print("=" * 65)
    print("💎 GEM PIPELINE: BẮT ĐẦU LÀM SẠCH VÀ ĐỒNG BỘ 3 TẦNG (STAGE 1)")
    print("=" * 65)

    conn_local = get_local_connection()
    conn_cloud = get_cloud_connection()

    init_cleaned_tables(conn_local)
    if conn_cloud:
        init_cleaned_tables(conn_cloud)
        print("🌐 Đã kết nối và khởi tạo bảng sạch trên Neon Cloud DB.")
    print("🐘 Đã kết nối và khởi tạo bảng sạch trên Local PostgreSQL.")

    # 1. Làm sạch Job Postings (TopCV)
    print("\n[1/2] Đang làm sạch dữ liệu tin tuyển dụng TopCV...")
    job_count, j_raw, j_clean, j_red = process_clean_jobs(conn_local, conn_cloud)
    print(f"  -> Hoàn tất xử lý: {job_count:,} JD.")
    print(f"  -> Dung lượng ký tự: {j_raw:,} -> {j_clean:,} chars (Giảm nhiễu văn bản: {j_red:.1f}%).")

    # 2. Làm sạch GitHub Projects
    print("\n[2/2] Đang làm sạch dữ liệu đồ án sinh viên GitHub...")
    gh_count, g_raw, g_clean, g_red = process_clean_projects(conn_local, conn_cloud)
    print(f"  -> Hoàn tất xử lý: {gh_count:,} đồ án.")
    print(f"  -> Dung lượng ký tự: {g_raw:,} -> {g_clean:,} chars (Giảm nhiễu văn bản: {g_red:.1f}%).")

    conn_local.close()
    if conn_cloud:
        conn_cloud.close()

    print("\n" + "=" * 65)
    print("🎉 HOÀN THÀNH XUẤT SẮC GIAI ĐOẠN LÀM SẠCH (STAGE 1)!")
    print("✅ Đã lưu trữ và đồng bộ hóa thành công 100% vào cả 3 tầng:")
    print("   1. Local PostgreSQL (bảng cleaned_job_postings, cleaned_github_projects)")
    print("   2. Neon Cloud PostgreSQL (bảng cleaned_job_postings, cleaned_github_projects)")
    print("   3. File JSONL cục bộ tại data/processed/jobs/ và data/processed/projects/")
    print("=" * 65)


if __name__ == "__main__":
    main()
