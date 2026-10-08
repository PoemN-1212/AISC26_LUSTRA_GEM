import os
import psycopg2
from dotenv import load_dotenv
from gem_pipeline.cleaning.job_cleaner import clean_job_record
from gem_pipeline.cleaning.project_cleaner import clean_project_record

load_dotenv()

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_USER = os.getenv("POSTGRES_USER", "gem_admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "gem_secret_password")
DB_NAME = os.getenv("POSTGRES_DB", "gem_database")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )


def init_cleaned_tables(conn):
    cur = conn.cursor()
    # 1. Bảng lưu JD đã làm sạch
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
            cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # 2. Bảng lưu Đồ án đã làm sạch
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cleaned_github_projects (
            id SERIAL PRIMARY KEY,
            raw_project_id INT UNIQUE REFERENCES raw_github_projects(id) ON DELETE CASCADE,
            repo_name VARCHAR,
            author VARCHAR,
            language VARCHAR,
            combined_clean_text TEXT NOT NULL,
            content_hash VARCHAR(64),
            char_count INT,
            cleaned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()


def process_clean_jobs(conn, limit=None):
    cur = conn.cursor()
    query = "SELECT id, title, company, salary_min, salary_max, full_content FROM raw_job_postings"
    if limit:
        query += f" LIMIT {limit}"
    cur.execute(query)
    rows = cur.fetchall()

    saved_count = 0
    total_raw_len = 0
    total_clean_len = 0

    insert_sql = """
        INSERT INTO cleaned_job_postings 
        (raw_job_id, title, company, salary_min, salary_max, content_clean, content_hash, char_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (raw_job_id) DO UPDATE 
        SET content_clean = EXCLUDED.content_clean,
            content_hash = EXCLUDED.content_hash,
            char_count = EXCLUDED.char_count,
            cleaned_at = CURRENT_TIMESTAMP;
    """

    for row in rows:
        raw_dict = {
            "id": row[0],
            "title": row[1],
            "company": row[2],
            "salary_min": row[3],
            "salary_max": row[4],
            "full_content": row[5]
        }
        cleaned = clean_job_record(raw_dict)
        total_raw_len += cleaned["content_raw_length"]
        total_clean_len += cleaned["content_clean_length"]

        cur.execute(insert_sql, (
            cleaned["job_id"],
            cleaned["title"],
            cleaned["company"],
            cleaned["salary_min"],
            cleaned["salary_max"],
            cleaned["content_clean"],
            cleaned["content_hash"],
            cleaned["content_clean_length"]
        ))
        saved_count += 1

    conn.commit()
    cur.close()

    reduction = ((total_raw_len - total_clean_len) / total_raw_len * 100) if total_raw_len > 0 else 0
    return saved_count, total_raw_len, total_clean_len, reduction


def process_clean_projects(conn, limit=None):
    cur = conn.cursor()
    query = "SELECT id, repo_name, author, description, readme_content, language FROM raw_github_projects"
    if limit:
        query += f" LIMIT {limit}"
    cur.execute(query)
    rows = cur.fetchall()

    saved_count = 0
    total_raw_len = 0
    total_clean_len = 0

    insert_sql = """
        INSERT INTO cleaned_github_projects 
        (raw_project_id, repo_name, author, language, combined_clean_text, content_hash, char_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (raw_project_id) DO UPDATE 
        SET combined_clean_text = EXCLUDED.combined_clean_text,
            content_hash = EXCLUDED.content_hash,
            char_count = EXCLUDED.char_count,
            cleaned_at = CURRENT_TIMESTAMP;
    """

    for row in rows:
        raw_dict = {
            "id": row[0],
            "repo_name": row[1],
            "author": row[2],
            "description": row[3],
            "readme_content": row[4],
            "language": row[5]
        }
        cleaned = clean_project_record(raw_dict)
        total_raw_len += cleaned["readme_raw_length"]
        total_clean_len += cleaned["combined_clean_length"]

        cur.execute(insert_sql, (
            cleaned["project_id"],
            cleaned["repo_name"],
            cleaned["author"],
            cleaned["language"],
            cleaned["combined_clean_text"],
            cleaned["content_hash"],
            cleaned["combined_clean_length"]
        ))
        saved_count += 1

    conn.commit()
    cur.close()

    reduction = ((total_raw_len - total_clean_len) / total_raw_len * 100) if total_raw_len > 0 else 0
    return saved_count, total_raw_len, total_clean_len, reduction


def main():
    print("=" * 60)
    print("💎 GEM PIPELINE: BẮT ĐẦU QUÁ TRÌNH LÀM SẠCH DỮ LIỆU (STAGE 1)")
    print("=" * 60)

    conn = get_connection()
    init_cleaned_tables(conn)
    print("✅ Đã khởi tạo 2 bảng lưu trữ: 'cleaned_job_postings' và 'cleaned_github_projects'.")

    # 1. Làm sạch Job Postings
    print("\n[1/2] Đang làm sạch dữ liệu tin tuyển dụng TopCV...")
    job_count, j_raw, j_clean, j_red = process_clean_jobs(conn)
    print(f"  -> Đã làm sạch thành công: {job_count} JD.")
    print(f"  -> Tổng dung lượng ký tự: {j_raw:,} -> {j_clean:,} chars (Giảm nhiễu: {j_red:.1f}%).")

    # 2. Làm sạch GitHub Projects
    print("\n[2/2] Đang làm sạch dữ liệu đồ án sinh viên GitHub...")
    gh_count, g_raw, g_clean, g_red = process_clean_projects(conn)
    print(f"  -> Đã làm sạch thành công: {gh_count} đồ án.")
    print(f"  -> Tổng dung lượng ký tự: {g_raw:,} -> {g_clean:,} chars (Giảm nhiễu: {g_red:.1f}%).")

    conn.close()
    print("\n🎉 HOÀN TẤT GIAI ĐOẠN LÀM SẠCH!")
    print("Bây giờ bạn có thể mở DBeaver và xem 2 bảng mới sạch đẹp!")


if __name__ == "__main__":
    main()
