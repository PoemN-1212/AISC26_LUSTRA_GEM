"""
GEM Database Seeder & Data Bootstrapper
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Mục đích:
Cho phép bất kỳ thành viên nào trong nhóm (hoặc giám khảo) khi clone dự án về
có thể khởi tạo toàn bộ CSDL cục bộ (PostgreSQL Local) và dữ liệu trong thư mục data/
ngay lập tức trong 30-45 giây mà KHÔNG CẦN phải cào lại dữ liệu từ đầu!

Cách sử dụng:
1. Khôi phục từ Cloud Database (Neon PostgreSQL - Khuyên dùng):
   python scripts/seed_database.py --source cloud

2. Khôi phục từ các file dữ liệu cục bộ (.jsonl trong thư mục data/):
   python scripts/seed_database.py --source file
"""

import os
import sys
import json
import argparse
import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

LOCAL_DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
LOCAL_DB_PORT = os.getenv("POSTGRES_PORT", "5432")
LOCAL_DB_USER = os.getenv("POSTGRES_USER", "gem_admin")
LOCAL_DB_PASS = os.getenv("POSTGRES_PASSWORD", "gem_secret_password")
LOCAL_DB_NAME = os.getenv("POSTGRES_DB", "gem_database")

CLOUD_DB_URL = os.getenv("CLOUD_DB_URL")


def get_local_connection():
    return psycopg2.connect(
        host=LOCAL_DB_HOST,
        port=LOCAL_DB_PORT,
        user=LOCAL_DB_USER,
        password=LOCAL_DB_PASS,
        dbname=LOCAL_DB_NAME,
        connect_timeout=10
    )


def get_cloud_connection():
    if not CLOUD_DB_URL:
        print("❌ LỖI: Biến môi trường CLOUD_DB_URL chưa được cấu hình trong file .env!")
        return None
    import time
    for attempt in range(1, 4):
        try:
            return psycopg2.connect(CLOUD_DB_URL, connect_timeout=45)
        except Exception as e:
            if attempt < 3:
                print(f"  ⏳ Neon DB đang khởi động từ trạng thái ngủ (lần thử {attempt}/3)... Đang thử lại sau 3s...")
                time.sleep(3)
            else:
                print(f"❌ Không thể kết nối Cloud DB sau 3 lần thử: {e}")
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


def init_local_schema(conn):
    """Đảm bảo tất cả 5 bảng dữ liệu tồn tại với đầy đủ cột thời gian."""
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_job_postings (
            id SERIAL PRIMARY KEY,
            url VARCHAR UNIQUE NOT NULL,
            title VARCHAR,
            company VARCHAR,
            salary_min NUMERIC,
            salary_max NUMERIC,
            full_content TEXT,
            posted_date DATE,
            valid_through DATE,
            location VARCHAR,
            employment_type VARCHAR,
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
            stars INT DEFAULT 0,
            created_at VARCHAR,
            updated_at VARCHAR,
            pushed_at VARCHAR,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

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

        CREATE TABLE IF NOT EXISTS extracted_skills (
            id SERIAL PRIMARY KEY,
            source_type VARCHAR,
            source_id INT,
            doc_id VARCHAR,
            title VARCHAR,
            evidence TEXT,
            skill VARCHAR,
            type VARCHAR,
            context TEXT,
            start_char INT,
            end_char INT,
            verifier_status VARCHAR,
            rejection_reason TEXT,
            model_name VARCHAR,
            posted_date DATE,
            posted_year INT,
            posted_month INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_skills_source ON extracted_skills(source_type, source_id);
        CREATE INDEX IF NOT EXISTS idx_skills_name ON extracted_skills(skill);
        CREATE INDEX IF NOT EXISTS idx_skills_year_month ON extracted_skills(posted_year, posted_month);

        DO $$
        BEGIN
            ALTER TABLE extracted_skills ALTER COLUMN evidence DROP NOT NULL;
            ALTER TABLE extracted_skills ALTER COLUMN skill DROP NOT NULL;
            ALTER TABLE extracted_skills ALTER COLUMN type DROP NOT NULL;
            ALTER TABLE extracted_skills ALTER COLUMN verifier_status DROP NOT NULL;
        EXCEPTION WHEN OTHERS THEN
            NULL;
        END $$;
    """)
    conn.commit()
    cur.close()


def reset_local_tables(conn):
    """Xóa sạch dữ liệu cũ và reset sequence theo thứ tự khóa ngoại để nạp mới đồng bộ."""
    cur = conn.cursor()
    try:
        cur.execute("""
            TRUNCATE TABLE extracted_skills, cleaned_job_postings, cleaned_github_projects, raw_job_postings, raw_github_projects RESTART IDENTITY CASCADE;
        """)
        conn.commit()
        print("  🧹 Đã làm sạch các bảng dữ liệu cũ trên Local PostgreSQL.", flush=True)
    except Exception as e:
        conn.rollback()
        print(f"  ℹ️ Bảng chưa tồn tại hoặc không cần truncate: {e}", flush=True)
    finally:
        cur.close()


def seed_from_cloud(reset: bool = True):
    """Kéo dữ liệu trực tiếp từ Neon Cloud PostgreSQL về Local PostgreSQL."""
    print("🌐 Bắt đầu kết nối Neon Cloud PostgreSQL...", flush=True)
    conn_cloud = get_cloud_connection()
    if not conn_cloud:
        return

    print("🐘 Kết nối Local PostgreSQL (Docker/Localhost)...", flush=True)
    try:
        conn_local = get_local_connection()
    except Exception as e:
        print(f"❌ Không thể kết nối Local PostgreSQL: {e}", flush=True)
        print("💡 Hãy chắc chắn bạn đã chạy: docker compose -f infra/docker-compose.yml up -d gem_postgres", flush=True)
        conn_cloud.close()
        return

    init_local_schema(conn_local)
    if reset:
        reset_local_tables(conn_local)

    data_dir = get_data_dir()
    os.makedirs(os.path.join(data_dir, "raw", "topcv"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "raw", "github"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "processed", "jobs"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "processed", "projects"), exist_ok=True)
    os.makedirs(os.path.join(data_dir, "processed", "skills"), exist_ok=True)

    tables_config = [
        {
            "name": "raw_job_postings",
            "select_cols": "id, url, title, company, salary_min, salary_max, full_content, posted_date, valid_through, location, employment_type, scraped_at",
            "insert_cols": "(id, url, title, company, salary_min, salary_max, full_content, posted_date, valid_through, location, employment_type, scraped_at)",
            "query": "SELECT id, url, title, company, salary_min, salary_max, full_content, posted_date, valid_through, location, employment_type, scraped_at FROM raw_job_postings ORDER BY id;",
            "conflict_clause": "ON CONFLICT (id) DO NOTHING",
            "jsonl_path": os.path.join(data_dir, "raw", "topcv", "topcv_jobs.jsonl")
        },
        {
            "name": "raw_github_projects",
            "select_cols": "id, repo_url, repo_name, author, description, readme_content, language, stars, created_at, updated_at, pushed_at, scraped_at",
            "insert_cols": "(id, repo_url, repo_name, author, description, readme_content, language, stars, created_at, updated_at, pushed_at, scraped_at)",
            "query": "SELECT id, repo_url, repo_name, author, description, readme_content, language, stars, created_at, updated_at, pushed_at, scraped_at FROM raw_github_projects ORDER BY id;",
            "conflict_clause": "ON CONFLICT (id) DO NOTHING",
            "jsonl_path": os.path.join(data_dir, "raw", "github", "github_projects.jsonl")
        },
        {
            "name": "cleaned_job_postings",
            "select_cols": "id, raw_job_id, title, company, salary_min, salary_max, content_clean, content_hash, char_count, posted_date, posted_year, posted_month, location, cleaned_at",
            "insert_cols": "(id, raw_job_id, title, company, salary_min, salary_max, content_clean, content_hash, char_count, posted_date, posted_year, posted_month, location, cleaned_at)",
            "query": """
                SELECT id, raw_job_id, title, company, salary_min, salary_max, content_clean, content_hash, char_count, posted_date, posted_year, posted_month, location, cleaned_at 
                FROM cleaned_job_postings 
                WHERE raw_job_id IN (SELECT id FROM raw_job_postings)
                ORDER BY id;
            """,
            "conflict_clause": "ON CONFLICT (id) DO NOTHING",
            "jsonl_path": os.path.join(data_dir, "processed", "jobs", "cleaned_jobs.jsonl")
        },
        {
            "name": "cleaned_github_projects",
            "select_cols": "id, raw_project_id, repo_name, author, language, combined_clean_text, content_hash, char_count, created_at, updated_at, pushed_at, cleaned_at",
            "insert_cols": "(id, raw_project_id, repo_name, author, language, combined_clean_text, content_hash, char_count, created_at, updated_at, pushed_at, cleaned_at)",
            "query": """
                SELECT id, raw_project_id, repo_name, author, language, combined_clean_text, content_hash, char_count, created_at, updated_at, pushed_at, cleaned_at 
                FROM cleaned_github_projects 
                WHERE raw_project_id IN (SELECT id FROM raw_github_projects)
                ORDER BY id;
            """,
            "conflict_clause": "ON CONFLICT (id) DO NOTHING",
            "jsonl_path": os.path.join(data_dir, "processed", "projects", "cleaned_projects.jsonl")
        },
        {
            "name": "extracted_skills",
            "select_cols": "id, source_type, source_id, doc_id, title, evidence, skill, type, context, start_char, end_char, verifier_status, rejection_reason, model_name, posted_date, posted_year, posted_month, created_at",
            "insert_cols": "(id, source_type, source_id, doc_id, title, evidence, skill, type, context, start_char, end_char, verifier_status, rejection_reason, model_name, posted_date, posted_year, posted_month, created_at)",
            "query": "SELECT id, source_type, source_id, doc_id, title, evidence, skill, type, context, start_char, end_char, verifier_status, rejection_reason, model_name, posted_date, posted_year, posted_month, created_at FROM extracted_skills ORDER BY id;",
            "conflict_clause": "ON CONFLICT (id) DO NOTHING",
            "jsonl_path": os.path.join(data_dir, "processed", "skills", "extracted_skills.jsonl")
        }
    ]

    print("\n📦 Đang kéo dữ liệu từ Cloud và nạp vào Local DB...", flush=True)
    cur_cloud = conn_cloud.cursor()
    cur_local = conn_local.cursor()

    for idx, cfg in enumerate(tables_config, 1):
        tbl = cfg["name"]
        print(f"\n--- [{idx}/5] Đồng bộ bảng `{tbl}` ---", flush=True)
        try:
            cur_cloud.execute(cfg["query"])
            rows = cur_cloud.fetchall()
            print(f"  -> Lấy được {len(rows):,} bản ghi từ Cloud.", flush=True)
        except Exception as e:
            print(f"  ⚠️ Lỗi đọc từ Cloud ({tbl}): {e}", flush=True)
            conn_cloud.rollback()
            continue

        if not rows:
            print(f"  ℹ️ Bảng `{tbl}` trên Cloud đang trống, bỏ qua.", flush=True)
            continue

        # Khử trùng lặp ID (nếu có trên Cloud) trước khi nạp để bảo đảm an toàn 100%
        seen_ids = set()
        dedup_rows = []
        for r in rows:
            row_id = r[0]
            if row_id not in seen_ids:
                seen_ids.add(row_id)
                dedup_rows.append(r)
        if len(dedup_rows) < len(rows):
            print(f"  ✨ Đã lọc bỏ {len(rows) - len(dedup_rows)} bản ghi trùng ID, còn lại {len(dedup_rows):,} bản ghi chuẩn.", flush=True)
        rows = dedup_rows

        # Nạp vào Local DB theo batch
        batch_size = 500
        sql = f"""
            INSERT INTO {tbl} {cfg['insert_cols']}
            VALUES %s
            {cfg['conflict_clause']}
        """
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            execute_values(cur_local, sql, batch)
        conn_local.commit()
        print(f"  ✅ Đã nạp thành công {len(rows):,} bản ghi vào Local PostgreSQL.", flush=True)

        # Cập nhật lại Sequence ID để tránh lỗi trùng ID khi người dùng insert mới
        try:
            cur_local.execute(f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), COALESCE(MAX(id), 1)) FROM {tbl};")
            conn_local.commit()
        except Exception:
            pass

        # Xuất ra file JSONL trong thư mục data/
        cols = [c.strip() for c in cfg["select_cols"].split(",")]
        try:
            with open(cfg["jsonl_path"], "w", encoding="utf-8") as f:
                for r in rows:
                    row_dict = {}
                    for col_name, val in zip(cols, r):
                        row_dict[col_name] = str(val) if val is not None else None
                    f.write(json.dumps(row_dict, ensure_ascii=False) + "\n")
            print(f"  📁 Đã xuất dữ liệu ra file: {cfg['jsonl_path']}", flush=True)
        except Exception as e:
            print(f"  ⚠️ Lỗi xuất JSONL: {e}", flush=True)

    cur_cloud.close()
    cur_local.close()
    conn_cloud.close()
    conn_local.close()

    print("\n🎉 HOÀN TẤT SEEDING TỪ CLOUD! Cơ sở dữ liệu và thư mục data/ của bạn đã sẵn sàng 100%!", flush=True)


def seed_from_file(reset: bool = True):
    """Khởi tạo Local DB từ các file JSONL trong thư mục data/."""
    data_dir = get_data_dir()
    print(f"📁 Bắt đầu nạp dữ liệu từ thư mục cục bộ: {data_dir}", flush=True)

    try:
        conn = get_local_connection()
    except Exception as e:
        print(f"❌ Không thể kết nối Local PostgreSQL: {e}", flush=True)
        print("💡 Hãy chắc chắn bạn đã chạy: docker compose -f infra/docker-compose.yml up -d gem_postgres", flush=True)
        return

    init_local_schema(conn)
    if reset:
        reset_local_tables(conn)

    cur = conn.cursor()

    files_config = [
        {
            "name": "raw_job_postings",
            "path": os.path.join(data_dir, "raw", "topcv", "topcv_jobs.jsonl"),
            "cols": ["id", "url", "title", "company", "salary_min", "salary_max", "full_content", "posted_date", "valid_through", "location", "employment_type", "scraped_at"],
            "conflict_col": "id"
        },
        {
            "name": "raw_github_projects",
            "path": os.path.join(data_dir, "raw", "github", "github_projects.jsonl"),
            "cols": ["id", "repo_url", "repo_name", "author", "description", "readme_content", "language", "stars", "created_at", "updated_at", "pushed_at", "scraped_at"],
            "conflict_col": "id"
        },
        {
            "name": "cleaned_job_postings",
            "path": os.path.join(data_dir, "processed", "jobs", "cleaned_jobs.jsonl"),
            "cols": ["id", "raw_job_id", "title", "company", "salary_min", "salary_max", "content_clean", "content_hash", "char_count", "posted_date", "posted_year", "posted_month", "location", "cleaned_at"],
            "conflict_col": "id",
            "fk_check": ("raw_job_id", "raw_job_postings")
        },
        {
            "name": "cleaned_github_projects",
            "path": os.path.join(data_dir, "processed", "projects", "cleaned_projects.jsonl"),
            "cols": ["id", "raw_project_id", "repo_name", "author", "language", "combined_clean_text", "content_hash", "char_count", "created_at", "updated_at", "pushed_at", "cleaned_at"],
            "conflict_col": "id",
            "fk_check": ("raw_project_id", "raw_github_projects")
        },
        {
            "name": "extracted_skills",
            "path": os.path.join(data_dir, "processed", "skills", "extracted_skills.jsonl"),
            "cols": ["id", "source_type", "source_id", "doc_id", "title", "evidence", "skill", "type", "context", "start_char", "end_char", "verifier_status", "rejection_reason", "model_name", "posted_date", "posted_year", "posted_month", "created_at"],
            "conflict_col": "id"
        }
    ]

    for cfg in files_config:
        tbl = cfg["name"]
        file_path = cfg["path"]
        if not os.path.exists(file_path):
            print(f"ℹ️ File {file_path} không tồn tại, bỏ qua bảng `{tbl}`.", flush=True)
            continue

        print(f"\n--- Đang nạp bảng `{tbl}` từ file {os.path.basename(file_path)} ---", flush=True)
        records = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        records.append(json.loads(line))
                    except Exception:
                        pass

        if not records:
            print(f"  ℹ️ File trống, bỏ qua.", flush=True)
            continue

        # Nếu có FK check, chỉ giữ các bản ghi có FK tồn tại
        if "fk_check" in cfg:
            fk_col, ref_table = cfg["fk_check"]
            cur.execute(f"SELECT id FROM {ref_table};")
            valid_ids = set(r[0] for r in cur.fetchall())
            valid_records = []
            for r in records:
                val = r.get(fk_col)
                if val is not None:
                    try:
                        if int(val) in valid_ids:
                            valid_records.append(r)
                    except Exception:
                        pass
            records = valid_records

        cols_str = ", ".join(cfg["cols"])
        insert_sql = f"""
            INSERT INTO {tbl} ({cols_str})
            VALUES %s
            ON CONFLICT ({cfg['conflict_col']}) DO NOTHING;
        """

        # Chuyển đổi bản ghi thành tuple
        rows_to_insert = []
        for r in records:
            row_vals = []
            for col in cfg["cols"]:
                val = r.get(col)
                if val == "None" or val == "":
                    val = None
                row_vals.append(val)
            rows_to_insert.append(tuple(row_vals))

        batch_size = 500
        for i in range(0, len(rows_to_insert), batch_size):
            batch = rows_to_insert[i:i + batch_size]
            execute_values(cur, insert_sql, batch)
        conn.commit()
        print(f"  ✅ Đã nạp thành công {len(rows_to_insert):,} bản ghi vào bảng `{tbl}`.", flush=True)

        try:
            cur.execute(f"SELECT setval(pg_get_serial_sequence('{tbl}', 'id'), COALESCE(MAX(id), 1)) FROM {tbl};")
            conn.commit()
        except Exception:
            pass

    cur.close()
    conn.close()
    print("\n🎉 HOÀN TẤT NẠP DỮ LIỆU TỪ FILE! Local PostgreSQL đã sẵn sàng hoạt động 100%!", flush=True)


def seed_qdrant():
    """Tự động kiểm tra Qdrant và lập chỉ mục Vector cho 100% JD và Đồ án."""
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    print(f"\n🧠 [Qdrant Vector Store] Kiểm tra kết nối tới {qdrant_url}...", flush=True)
    try:
        r = requests.get(f"{qdrant_url}/collections", timeout=3)
        if r.status_code != 200:
            print("  ⚠️ Qdrant phản hồi không thành công, bỏ qua bước vector hóa.", flush=True)
            return
    except Exception:
        print("  ℹ️ Qdrant chưa được khởi động (bạn có thể chạy: docker compose -f infra/docker-compose.yml up -d gem_qdrant). Bỏ qua vector hóa.", flush=True)
        return

    # 1. ƯU TIÊN KHÔI PHỤC SIÊU TỐC TỪ SNAPSHOT NẾU CÓ (Chỉ mất 2-3 giây, không cần Ollama/GPU)
    data_dir = get_data_dir()
    snapshots_dir = os.path.join(data_dir, "qdrant_snapshots")
    market_snap = os.path.join(snapshots_dir, "market_jds.snapshot")
    proj_snap = os.path.join(snapshots_dir, "student_projects.snapshot")

    if os.path.exists(market_snap) and os.path.exists(proj_snap):
        print("  ⚡ Tìm thấy file Vector Snapshots trong data/qdrant_snapshots/! Khôi phục tức thì trong vài giây...", flush=True)
        try:
            with open(market_snap, "rb") as f1:
                r1 = requests.post(
                    f"{qdrant_url}/collections/market_jds/snapshots/upload?priority=snapshot",
                    files={"snapshot": ("market_jds.snapshot", f1, "application/octet-stream")},
                    timeout=60
                )
            with open(proj_snap, "rb") as f2:
                r2 = requests.post(
                    f"{qdrant_url}/collections/student_projects/snapshots/upload?priority=snapshot",
                    files={"snapshot": ("student_projects.snapshot", f2, "application/octet-stream")},
                    timeout=60
                )
            if r1.status_code == 200 and r2.status_code == 200:
                print("  🎉 KHÔI PHỤC VECTOR QDRANT THÀNH CÔNG TỪ SNAPSHOT! (Không cần chạy Embedding Ollama)", flush=True)
                return
            else:
                print(f"  ⚠️ Phản hồi upload snapshot: {r1.status_code}, {r2.status_code}. Chuyển sang fallback...", flush=True)
        except Exception as e:
            print(f"  ⚠️ Khôi phục snapshot thất bại ({e}), chuyển sang fallback...", flush=True)

    # 2. FALLBACK: Chạy Vector hóa tuần tự qua BGE-M3 (nếu không có snapshot)
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline", "src")))
    try:
        from gem_pipeline.vector_store.qdrant_service import QdrantVectorService
        svc = QdrantVectorService(qdrant_url=qdrant_url)
        print("  ⚡ Đang vector hóa và nạp tin tuyển dụng (market_jds)...", flush=True)
        cnt_jds = svc.index_all_jds()
        print(f"  ✅ Đã nạp {cnt_jds:,} vector JD vào Qdrant.", flush=True)

        print("  ⚡ Đang vector hóa và nạp đồ án sinh viên (student_projects)...", flush=True)
        cnt_projs = svc.index_all_projects()
        print(f"  ✅ Đã nạp {cnt_projs:,} vector đồ án vào Qdrant.", flush=True)
        print("🎉 HOÀN TẤT ĐỒNG BỘ VECTOR QDRANT! Cả PostgreSQL và Qdrant đã sẵn sàng 100%!", flush=True)
    except Exception as e:
        print(f"  ⚠️ Lỗi khi nạp dữ liệu vào Qdrant: {e}", flush=True)


def main():
    parser = argparse.ArgumentParser(description="GEM Database Bootstrapper")
    parser.add_argument("--source", choices=["cloud", "file"], default="cloud",
                        help="Nguồn nạp dữ liệu: 'cloud' (từ Neon Cloud DB) hoặc 'file' (từ file JSONL)")
    parser.add_argument("--reset", action="store_true", default=True,
                        help="Làm sạch dữ liệu cũ trước khi nạp để tránh trùng lặp/xung đột ID (Mặc định: True)")
    parser.add_argument("--no-reset", dest="reset", action="store_false",
                        help="Không xóa dữ liệu cũ, chỉ chèn bổ sung")
    parser.add_argument("--skip-qdrant", action="store_true", default=False,
                        help="Bỏ qua bước nạp vector vào Qdrant (mặc định sẽ tự động nạp)")
    args = parser.parse_args()

    if args.source == "cloud":
        seed_from_cloud(reset=args.reset)
    else:
        seed_from_file(reset=args.reset)

    if not args.skip_qdrant:
        seed_qdrant()


if __name__ == "__main__":
    main()

