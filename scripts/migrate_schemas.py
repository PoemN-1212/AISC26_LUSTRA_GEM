"""
GEM Database Migration Script: Bổ sung các thuộc tính thời gian (Temporal Attributes)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
Đồng bộ Schema cho cả Local PostgreSQL và Neon Cloud PostgreSQL.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

MIGRATION_SQL = """
-- 1. raw_job_postings
ALTER TABLE raw_job_postings ADD COLUMN IF NOT EXISTS posted_date DATE;
ALTER TABLE raw_job_postings ADD COLUMN IF NOT EXISTS valid_through DATE;
ALTER TABLE raw_job_postings ADD COLUMN IF NOT EXISTS location VARCHAR;
ALTER TABLE raw_job_postings ADD COLUMN IF NOT EXISTS employment_type VARCHAR;

-- 2. cleaned_job_postings
ALTER TABLE cleaned_job_postings ADD COLUMN IF NOT EXISTS posted_date DATE;
ALTER TABLE cleaned_job_postings ADD COLUMN IF NOT EXISTS posted_year INT;
ALTER TABLE cleaned_job_postings ADD COLUMN IF NOT EXISTS posted_month INT;
ALTER TABLE cleaned_job_postings ADD COLUMN IF NOT EXISTS location VARCHAR;

-- 3. raw_github_projects
ALTER TABLE raw_github_projects ADD COLUMN IF NOT EXISTS updated_at VARCHAR;
ALTER TABLE raw_github_projects ADD COLUMN IF NOT EXISTS pushed_at VARCHAR;

-- 4. cleaned_github_projects
ALTER TABLE cleaned_github_projects ADD COLUMN IF NOT EXISTS created_at VARCHAR;
ALTER TABLE cleaned_github_projects ADD COLUMN IF NOT EXISTS updated_at VARCHAR;
ALTER TABLE cleaned_github_projects ADD COLUMN IF NOT EXISTS pushed_at VARCHAR;

-- 5. extracted_skills
ALTER TABLE extracted_skills ADD COLUMN IF NOT EXISTS posted_date DATE;
ALTER TABLE extracted_skills ADD COLUMN IF NOT EXISTS posted_year INT;
ALTER TABLE extracted_skills ADD COLUMN IF NOT EXISTS posted_month INT;

-- Đánh index cho thời gian để tối ưu truy vấn xu hướng (Trend Queries)
CREATE INDEX IF NOT EXISTS idx_cleaned_job_posted_date ON cleaned_job_postings(posted_date);
CREATE INDEX IF NOT EXISTS idx_extracted_skills_posted_date ON extracted_skills(posted_date);
CREATE INDEX IF NOT EXISTS idx_extracted_skills_year_month ON extracted_skills(posted_year, posted_month);
"""

def migrate():
    # 1. Local Database
    print("[1/2] Đang cập nhật Local PostgreSQL...")
    try:
        conn_local = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            user=os.getenv("POSTGRES_USER", "gem_admin"),
            password=os.getenv("POSTGRES_PASSWORD", "gem_secret_password"),
            dbname=os.getenv("POSTGRES_DB", "gem_database")
        )
        with conn_local.cursor() as cur:
            cur.execute(MIGRATION_SQL)
        conn_local.commit()
        conn_local.close()
        print("  -> Thành công: Local DB đã được bổ sung các thuộc tính thời gian!")
    except Exception as e:
        print(f"  -> Lỗi cập nhật Local DB: {e}")

    # 2. Cloud Database (Neon)
    cloud_url = os.getenv("CLOUD_DB_URL")
    if cloud_url:
        print("\n[2/2] Đang cập nhật Neon Cloud PostgreSQL...")
        try:
            conn_cloud = psycopg2.connect(cloud_url)
            with conn_cloud.cursor() as cur:
                # Đảm bảo các bảng cơ bản tồn tại trên Cloud
                cur.execute("""
                CREATE TABLE IF NOT EXISTS raw_job_postings (
                    id SERIAL PRIMARY KEY,
                    url VARCHAR UNIQUE NOT NULL,
                    title VARCHAR,
                    company VARCHAR,
                    salary_min NUMERIC,
                    salary_max NUMERIC,
                    full_content TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS raw_github_projects (
                    id SERIAL PRIMARY KEY,
                    repo_url VARCHAR UNIQUE NOT NULL,
                    repo_name VARCHAR,
                    author VARCHAR,
                    description TEXT,
                    readme_content TEXT,
                    language VARCHAR,
                    stars INT,
                    created_at VARCHAR,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS cleaned_job_postings (
                    id SERIAL PRIMARY KEY,
                    raw_job_id INT UNIQUE,
                    title VARCHAR,
                    company VARCHAR,
                    salary_min NUMERIC,
                    salary_max NUMERIC,
                    content_clean TEXT NOT NULL,
                    content_hash VARCHAR(64),
                    char_count INT,
                    cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS cleaned_github_projects (
                    id SERIAL PRIMARY KEY,
                    raw_project_id INT UNIQUE,
                    repo_name VARCHAR,
                    author VARCHAR,
                    language VARCHAR,
                    combined_clean_text TEXT NOT NULL,
                    content_hash VARCHAR(64),
                    char_count INT,
                    cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS extracted_skills (
                    id SERIAL PRIMARY KEY,
                    source_type VARCHAR(20) NOT NULL,
                    source_id VARCHAR(50) NOT NULL,
                    doc_id VARCHAR(50) NOT NULL,
                    title TEXT,
                    evidence TEXT NOT NULL,
                    skill TEXT NOT NULL,
                    type VARCHAR(20) NOT NULL,
                    context VARCHAR(20) DEFAULT 'required',
                    start_char INTEGER,
                    end_char INTEGER,
                    verifier_status VARCHAR(20) NOT NULL,
                    rejection_reason TEXT,
                    model_name VARCHAR(50) DEFAULT 'qwen2.5:7b',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cur.execute(MIGRATION_SQL)
            conn_cloud.commit()
            conn_cloud.close()
            print("  -> Thành công: Neon Cloud DB đã được đồng bộ toàn diện!")
        except Exception as e:
            print(f"  -> Lỗi cập nhật Cloud DB: {e}")
    else:
        print("\n[2/2] Bỏ qua Cloud DB vì chưa cấu hình CLOUD_DB_URL.")


if __name__ == "__main__":
    migrate()
