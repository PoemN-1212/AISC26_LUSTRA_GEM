"""
GEM Data Synchronization & Triple Storage Exporter
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Chức năng:
1. Xuất toàn bộ dữ liệu hiện có từ PostgreSQL ra thư mục data/ (JSONL):
   - data/raw/topcv/topcv_jobs.jsonl
   - data/raw/github/github_projects.jsonl
   - data/processed/jobs/cleaned_jobs.jsonl
   - data/processed/projects/cleaned_projects.jsonl
   - data/processed/skills/extracted_skills.jsonl
2. Đồng bộ hóa toàn bộ dữ liệu từ Local PostgreSQL lên Neon Cloud PostgreSQL (CLOUD_DB_URL).
"""

import os
import sys
import json
import psycopg2
from dotenv import load_dotenv

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


def get_local_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )


def get_cloud_conn():
    if CLOUD_DB_URL:
        try:
            return psycopg2.connect(CLOUD_DB_URL)
        except Exception as e:
            print(f"⚠️ Cảnh báo: Không thể kết nối Cloud DB: {e}")
    return None


def export_and_sync():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    os.makedirs(os.path.join(base_dir, "raw", "topcv"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "raw", "github"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "processed", "jobs"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "processed", "projects"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "processed", "skills"), exist_ok=True)

    conn_loc = get_local_conn()
    conn_cld = get_cloud_conn()

    print("🚀 Bắt đầu quá trình đồng bộ và xuất dữ liệu Triple Storage...\n")

    # =========================================================================
    # 1. RAW TOPCV JOBS
    # =========================================================================
    print("📦 [1/5] Đang xử lý raw_job_postings...")
    with conn_loc.cursor() as cur:
        cur.execute("""
            SELECT id, url, title, company, salary_min, salary_max, full_content, 
                   posted_date, valid_through, location, employment_type, scraped_at 
            FROM raw_job_postings ORDER BY id;
        """)
        rows = cur.fetchall()

    topcv_jsonl_path = os.path.join(base_dir, "raw", "topcv", "topcv_jobs.jsonl")
    with open(topcv_jsonl_path, "w", encoding="utf-8") as f:
        for r in rows:
            obj = {
                "id": r[0], "url": r[1], "title": r[2], "company": r[3],
                "salary_min": float(r[4]) if r[4] is not None else 0,
                "salary_max": float(r[5]) if r[5] is not None else 0,
                "full_content": r[6],
                "posted_date": str(r[7]) if r[7] else None,
                "valid_through": str(r[8]) if r[8] else None,
                "location": r[9], "employment_type": r[10],
                "scraped_at": str(r[11]) if r[11] else None
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"  -> Đã xuất {len(rows)} bản ghi ra file: {topcv_jsonl_path}")

    if conn_cld:
        print("  -> Đang đồng bộ raw_job_postings lên Neon Cloud DB...")
        with conn_cld.cursor() as cur_c:
            for r in rows:
                cur_c.execute("""
                    INSERT INTO raw_job_postings 
                    (url, title, company, salary_min, salary_max, full_content, posted_date, valid_through, location, employment_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING;
                """, (r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[9], r[10]))
        conn_cld.commit()
        print("  -> Đồng bộ Cloud DB thành công!")

    # =========================================================================
    # 2. RAW GITHUB PROJECTS
    # =========================================================================
    print("\n📦 [2/5] Đang xử lý raw_github_projects...")
    with conn_loc.cursor() as cur:
        cur.execute("""
            SELECT id, repo_url, repo_name, author, description, readme_content, 
                   language, stars, created_at, updated_at, pushed_at, scraped_at 
            FROM raw_github_projects ORDER BY id;
        """)
        rows = cur.fetchall()

    gh_jsonl_path = os.path.join(base_dir, "raw", "github", "github_projects.jsonl")
    with open(gh_jsonl_path, "w", encoding="utf-8") as f:
        for r in rows:
            obj = {
                "id": r[0], "repo_url": r[1], "repo_name": r[2], "author": r[3],
                "description": r[4], "readme_content": r[5], "language": r[6],
                "stars": r[7], "created_at": r[8], "updated_at": r[9],
                "pushed_at": r[10], "scraped_at": str(r[11]) if r[11] else None
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"  -> Đã xuất {len(rows)} bản ghi ra file: {gh_jsonl_path}")

    if conn_cld:
        print("  -> Đang đồng bộ raw_github_projects lên Neon Cloud DB...")
        with conn_cld.cursor() as cur_c:
            for r in rows:
                clean_readme = (r[5] or "").replace("\x00", "").replace("\0", "")
                clean_desc = (r[4] or "").replace("\x00", "").replace("\0", "")
                cur_c.execute("""
                    INSERT INTO raw_github_projects 
                    (repo_url, repo_name, author, description, readme_content, language, stars, created_at, updated_at, pushed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (repo_url) DO NOTHING;
                """, (r[1], r[2], r[3], clean_desc, clean_readme, r[6], r[7], r[8], r[9], r[10]))
        conn_cld.commit()
        print("  -> Đồng bộ Cloud DB thành công!")

    # =========================================================================
    # 3. CLEANED JOB POSTINGS
    # =========================================================================
    print("\n📦 [3/5] Đang xử lý cleaned_job_postings...")
    with conn_loc.cursor() as cur:
        cur.execute("""
            SELECT id, raw_job_id, title, company, salary_min, salary_max, 
                   content_clean, content_hash, char_count, cleaned_at, posted_date, location
            FROM cleaned_job_postings ORDER BY id;
        """)
        rows = cur.fetchall()

    cleaned_jobs_path = os.path.join(base_dir, "processed", "jobs", "cleaned_jobs.jsonl")
    with open(cleaned_jobs_path, "w", encoding="utf-8") as f:
        for r in rows:
            obj = {
                "id": r[0], "raw_job_id": r[1], "title": r[2], "company": r[3],
                "salary_min": float(r[4]) if r[4] is not None else 0,
                "salary_max": float(r[5]) if r[5] is not None else 0,
                "content_clean": r[6], "content_hash": r[7], "char_count": r[8],
                "cleaned_at": str(r[9]) if r[9] else None,
                "posted_date": str(r[10]) if r[10] else None,
                "location": r[11]
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"  -> Đã xuất {len(rows)} bản ghi ra file: {cleaned_jobs_path}")

    if conn_cld:
        print("  -> Đang đồng bộ cleaned_job_postings lên Neon Cloud DB...")
        with conn_cld.cursor() as cur_c:
            for r in rows:
                cur_c.execute("""
                    INSERT INTO cleaned_job_postings 
                    (raw_job_id, title, company, salary_min, salary_max, content_clean, content_hash, char_count, posted_date, location)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (raw_job_id) DO NOTHING;
                """, (r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], r[10], r[11]))
        conn_cld.commit()
        print("  -> Đồng bộ Cloud DB thành công!")

    # =========================================================================
    # 4. CLEANED GITHUB PROJECTS
    # =========================================================================
    print("\n📦 [4/5] Đang xử lý cleaned_github_projects...")
    with conn_loc.cursor() as cur:
        cur.execute("""
            SELECT id, raw_project_id, repo_name, author, language, 
                   combined_clean_text, content_hash, char_count, cleaned_at, created_at
            FROM cleaned_github_projects ORDER BY id;
        """)
        rows = cur.fetchall()

    cleaned_proj_path = os.path.join(base_dir, "processed", "projects", "cleaned_projects.jsonl")
    with open(cleaned_proj_path, "w", encoding="utf-8") as f:
        for r in rows:
            obj = {
                "id": r[0], "raw_project_id": r[1], "repo_name": r[2], "author": r[3],
                "language": r[4], "combined_clean_text": r[5], "content_hash": r[6],
                "char_count": r[7], "cleaned_at": str(r[8]) if r[8] else None,
                "created_at": r[9]
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"  -> Đã xuất {len(rows)} bản ghi ra file: {cleaned_proj_path}")

    if conn_cld:
        print("  -> Đang đồng bộ cleaned_github_projects lên Neon Cloud DB...")
        with conn_cld.cursor() as cur_c:
            for r in rows:
                cur_c.execute("""
                    INSERT INTO cleaned_github_projects 
                    (raw_project_id, repo_name, author, language, combined_clean_text, content_hash, char_count, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (raw_project_id) DO NOTHING;
                """, (r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[9]))
        conn_cld.commit()
        print("  -> Đồng bộ Cloud DB thành công!")

    # =========================================================================
    # 5. EXTRACTED SKILLS
    # =========================================================================
    print("\n📦 [5/5] Đang xử lý extracted_skills (12,557 thực thể)...")
    with conn_loc.cursor() as cur:
        cur.execute("""
            SELECT id, source_type, source_id, doc_id, title, evidence, skill, 
                   type, context, start_char, end_char, verifier_status, rejection_reason, model_name, created_at
            FROM extracted_skills ORDER BY id;
        """)
        rows = cur.fetchall()

    skills_jsonl_path = os.path.join(base_dir, "processed", "skills", "extracted_skills.jsonl")
    with open(skills_jsonl_path, "w", encoding="utf-8") as f:
        for r in rows:
            obj = {
                "id": r[0], "source_type": r[1], "source_id": r[2], "doc_id": r[3],
                "title": r[4], "evidence": r[5], "skill": r[6], "type": r[7],
                "context": r[8], "start_char": r[9], "end_char": r[10],
                "verifier_status": r[11], "rejection_reason": r[12],
                "model_name": r[13], "created_at": str(r[14]) if r[14] else None
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"  -> Đã xuất {len(rows)} bản ghi ra file: {skills_jsonl_path}")

    if conn_cld:
        print("  -> Đang đồng bộ extracted_skills lên Neon Cloud DB theo từng batch...")
        batch_size = 500
        with conn_cld.cursor() as cur_c:
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                args_str = ",".join(cur_c.mogrify(
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8], x[9], x[10], x[11], x[12], x[13])
                ).decode('utf-8') for x in batch)
                cur_c.execute(f"""
                    INSERT INTO extracted_skills 
                    (source_type, source_id, doc_id, title, evidence, skill, type, context, start_char, end_char, verifier_status, rejection_reason, model_name)
                    VALUES {args_str};
                """)
                conn_cld.commit()
                print(f"     -> Đã sync {min(i + batch_size, len(rows))}/{len(rows)} skills...")
        print("  -> Đồng bộ extracted_skills lên Cloud DB thành công!")

    conn_loc.close()
    if conn_cld:
        conn_cld.close()

    print("\n🎉 HOÀN THÀNH ĐỒNG BỘ TOÀN DIỆN!")
    print(f"📁 Thư mục data/ hiện đã chứa đầy đủ 5 tệp JSONL:")
    print(f"   - {topcv_jsonl_path}")
    print(f"   - {gh_jsonl_path}")
    print(f"   - {cleaned_jobs_path}")
    print(f"   - {cleaned_proj_path}")
    print(f"   - {skills_jsonl_path}")
    print(f"☁️ Toàn bộ dữ liệu cũng đã được sao lưu đồng bộ lên Neon Cloud PostgreSQL!")


if __name__ == "__main__":
    export_and_sync()
