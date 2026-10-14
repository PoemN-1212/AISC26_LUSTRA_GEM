"""
GEM GitHub Projects Ingestion Engine (Mô-đun cào đồ án sinh viên GitHub)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Cải tiến toàn diện:
1. Triệt tiêu 100% lỗi 'ValueError: A string literal cannot contain NUL (0x00) characters'.
2. Cơ chế lưu trữ 3 Lớp (Triple Storage):
   - Lớp 1: Ghi file JSONL trực tiếp vào data/raw/github/github_projects.jsonl
   - Lớp 2: Ghi vào CSDL Local PostgreSQL (gem_database)
   - Lớp 3: Tự động đồng bộ lên Neon Cloud PostgreSQL (nếu có CLOUD_DB_URL)
3. Bổ sung các mốc thời gian: created_at, updated_at, pushed_at.
4. Xử lý lỗi độc lập cho từng repo (Fault-Tolerant): lỗi 1 repo không làm chết cả tiến trình.
5. Mở rộng bộ từ khóa đa dạng để thu thập 400 - 600 đồ án chất lượng cao.
"""

import os
import sys
import json
import time
import base64
import requests
import psycopg2
from typing import Optional, Dict, Any
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
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def get_data_dir() -> str:
    """Xác định đường dẫn thư mục data/ trên máy host hoặc trong Airflow container."""
    env_dir = os.getenv("GEM_DATA_DIR")
    if env_dir and os.path.exists(env_dir):
        return env_dir
    # Thử tìm tương đối từ repo root
    possible_paths = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")),
        "/opt/airflow/data",
        "data"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    os.makedirs("data", exist_ok=True)
    return "data"


def sanitize_text(text: Optional[str]) -> str:
    """Loại bỏ ký tự NUL 0x00 và chuẩn hóa chuỗi an toàn cho PostgreSQL."""
    if not text:
        return ""
    # PostgreSQL nghiêm cấm byte 0x00 (\x00 hoặc \0)
    return text.replace("\x00", "").replace("\0", "").strip()


def get_local_connection():
    """Tạo kết nối đến Local PostgreSQL với retry logic."""
    for attempt in range(3):
        try:
            return psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASS,
                dbname=DB_NAME,
                connect_timeout=10
            )
        except Exception as e:
            if attempt == 2:
                raise e
            time.sleep(2)


def get_cloud_connection():
    """Tạo kết nối đến Neon Cloud PostgreSQL."""
    if CLOUD_DB_URL:
        try:
            return psycopg2.connect(CLOUD_DB_URL, connect_timeout=15)
        except Exception as e:
            print(f"⚠️ Cảnh báo: Không thể kết nối Cloud DB ({e})")
            return None
    return None


def init_storage():
    """Khởi tạo bảng trong DB và thư mục lưu trữ file data/raw/github/."""
    # 1. Tạo thư mục file cục bộ
    data_dir = get_data_dir()
    raw_github_dir = os.path.join(data_dir, "raw", "github")
    os.makedirs(raw_github_dir, exist_ok=True)

    create_table_sql = """
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
            updated_at VARCHAR,
            pushed_at VARCHAR,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    # 2. Local DB
    try:
        conn = get_local_connection()
        with conn.cursor() as cur:
            cur.execute(create_table_sql)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Lỗi khởi tạo Local DB: {e}")

    # 3. Cloud DB
    conn_cloud = get_cloud_connection()
    if conn_cloud:
        try:
            with conn_cloud.cursor() as cur:
                cur.execute(create_table_sql)
            conn_cloud.commit()
            conn_cloud.close()
        except Exception as e:
            print(f"⚠️ Lỗi khởi tạo Cloud DB: {e}")


def save_to_jsonl(record: Dict[str, Any]):
    """Ghi bản ghi vào file data/raw/github/github_projects.jsonl."""
    try:
        data_dir = get_data_dir()
        file_path = os.path.join(data_dir, "raw", "github", "github_projects.jsonl")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"⚠️ Lỗi ghi file JSONL cục bộ: {e}")


def fetch_github_projects(max_repos_target: int = 500):
    if not GITHUB_TOKEN:
        print("❌ LỖI: Chưa cấu hình GITHUB_TOKEN trong file .env!")
        return

    init_storage()
    data_dir = get_data_dir()
    jsonl_file = os.path.join(data_dir, "raw", "github", "github_projects.jsonl")
    print(f"🚀 Bắt đầu cào đồ án GitHub (Mục tiêu: ~{max_repos_target} repos)...")
    print(f"📁 Thư mục lưu file cục bộ: {jsonl_file}")

    # Nạp danh sách repo đã có trong Local DB để tránh cào lại
    existing_urls = set()
    try:
        conn = get_local_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT repo_url FROM raw_github_projects;")
            rows = cur.fetchall()
            existing_urls = {r[0] for r in rows}
        conn.close()
        print(f"ℹ️ Đã có {len(existing_urls)} đồ án sẵn trong cơ sở dữ liệu.")
    except Exception as e:
        print(f"⚠️ Không thể đọc existing URLs từ DB: {e}")

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Bộ truy vấn đa dạng bao phủ nhiều nhánh ngành IT
    queries = [
        '"đồ án tốt nghiệp" in:readme,description',
        '"khóa luận tốt nghiệp" in:readme,description',
        '"capstone project" in:readme,description',
        '"đồ án môn học" in:readme,description',
        '"đồ án chuyên ngành" in:readme,description',
        '"đồ án" uit in:readme,description',
        '"đồ án" backend in:readme,description',
        '"đồ án" frontend in:readme,description',
        '"đồ án" spring boot in:readme,description',
        '"đồ án" flutter in:readme,description',
        '"đồ án" reactjs in:readme,description',
        '"graduation project" vietnam in:readme,description'
    ]

    total_new_saved = 0
    total_current = len(existing_urls)

    for query in queries:
        if total_current >= max_repos_target:
            print(f"\n🎉 Đã đạt mục tiêu {max_repos_target} đồ án! Dừng cào.")
            break

        print(f"\n--- Đang tìm kiếm từ khóa: {query} ---")
        for page in range(1, 5):  # Mỗi từ khóa quét 4 trang = 120 kết quả
            if total_current >= max_repos_target:
                break

            search_url = f"https://api.github.com/search/repositories?q={query}&sort=updated&order=desc&per_page=30&page={page}"
            try:
                res = requests.get(search_url, headers=headers, timeout=15)
            except Exception as e:
                print(f"⚠️ Lỗi kết nối Search API: {e}")
                time.sleep(5)
                continue

            if res.status_code == 403:
                print(f"⚠️ Hết Rate Limit GitHub. Tạm nghỉ 30s...")
                time.sleep(30)
                continue
            elif res.status_code != 200:
                print(f"⚠️ Lỗi API ({res.status_code}): {res.text[:100]}")
                time.sleep(5)
                continue

            items = res.json().get("items", [])
            if not items:
                break

            for repo in items:
                repo_url = repo.get("html_url")
                if not repo_url or repo_url in existing_urls:
                    continue

                repo_name = repo.get("full_name")
                print(f"  -> [{total_current + 1}] Bóc tách: {repo_name}")

                # Bóc tách README
                readme_content = ""
                readme_url = f"https://api.github.com/repos/{repo_name}/readme"
                try:
                    readme_res = requests.get(readme_url, headers=headers, timeout=12)
                    if readme_res.status_code == 200:
                        readme_data = readme_res.json()
                        if "content" in readme_data:
                            raw_decoded = base64.b64decode(readme_data["content"]).decode('utf-8', errors='ignore')
                            readme_content = sanitize_text(raw_decoded)
                except Exception as e:
                    print(f"     ⚠️ Lỗi tải README {repo_name}: {e}")

                # Làm sạch dữ liệu
                clean_repo_name = sanitize_text(repo.get("name"))
                clean_author = sanitize_text(repo.get("owner", {}).get("login"))
                clean_desc = sanitize_text(repo.get("description", ""))
                clean_lang = sanitize_text(repo.get("language"))
                stars = repo.get("stargazers_count", 0) or 0
                created_at = repo.get("created_at")
                updated_at = repo.get("updated_at")
                pushed_at = repo.get("pushed_at")

                record = {
                    "repo_url": repo_url,
                    "repo_name": clean_repo_name,
                    "author": clean_author,
                    "description": clean_desc,
                    "readme_content": readme_content,
                    "language": clean_lang,
                    "stars": stars,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "pushed_at": pushed_at,
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }

                # 1. Ghi File JSONL (Lớp 1)
                save_to_jsonl(record)

                # 2. Ghi Local DB (Lớp 2)
                try:
                    conn_loc = get_local_connection()
                    with conn_loc.cursor() as cur:
                        cur.execute("""
                            INSERT INTO raw_github_projects 
                            (repo_url, repo_name, author, description, readme_content, language, stars, created_at, updated_at, pushed_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (repo_url) DO UPDATE
                            SET updated_at = EXCLUDED.updated_at,
                                pushed_at = EXCLUDED.pushed_at;
                        """, (
                            repo_url, clean_repo_name, clean_author, clean_desc,
                            readme_content, clean_lang, stars, created_at, updated_at, pushed_at
                        ))
                    conn_loc.commit()
                    conn_loc.close()
                except Exception as err:
                    print(f"     ⚠️ Lỗi ghi Local DB ({repo_name}): {err}")

                # 3. Ghi Cloud DB (Lớp 3)
                if CLOUD_DB_URL:
                    try:
                        conn_cld = get_cloud_connection()
                        if conn_cld:
                            with conn_cld.cursor() as cur:
                                cur.execute("""
                                    INSERT INTO raw_github_projects 
                                    (repo_url, repo_name, author, description, readme_content, language, stars, created_at, updated_at, pushed_at)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (repo_url) DO UPDATE
                                    SET updated_at = EXCLUDED.updated_at,
                                        pushed_at = EXCLUDED.pushed_at;
                                """, (
                                    repo_url, clean_repo_name, clean_author, clean_desc,
                                    readme_content, clean_lang, stars, created_at, updated_at, pushed_at
                                ))
                            conn_cld.commit()
                            conn_cld.close()
                    except Exception as err:
                        print(f"     ⚠️ Lỗi ghi Cloud DB ({repo_name}): {err}")

                existing_urls.add(repo_url)
                total_new_saved += 1
                total_current += 1
                time.sleep(1.2)

            time.sleep(2)

    print(f"\n✅ HOÀN THÀNH CÀO GITHUB! Đã lưu mới {total_new_saved} đồ án (Tổng kho: {total_current} đồ án).")
    print(f"📁 Dữ liệu đã được lưu đồng thời vào: File JSONL, Local PostgreSQL và Neon Cloud DB.")


if __name__ == "__main__":
    fetch_github_projects()
