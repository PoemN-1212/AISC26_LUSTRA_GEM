import os
import time
import requests
import psycopg2
import base64

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_USER = os.getenv("POSTGRES_USER", "gem_admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "gem_secret_password")
DB_NAME = os.getenv("POSTGRES_DB", "gem_database")

CLOUD_DB_URL = os.getenv("CLOUD_DB_URL")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def get_local_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME
    )


def get_cloud_connection():
    if CLOUD_DB_URL:
        try:
            return psycopg2.connect(CLOUD_DB_URL)
        except Exception as e:
            print(f"Cảnh báo: Không thể kết nối Cloud DB ({e})")
            return None
    return None


def init_dbs():
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
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """
    # Khởi tạo bảng ở Local
    conn_local = get_local_connection()
    cursor_local = conn_local.cursor()
    cursor_local.execute(create_table_sql)
    conn_local.commit()
    conn_local.close()

    # Khởi tạo bảng ở Cloud (nếu có)
    conn_cloud = get_cloud_connection()
    if conn_cloud:
        cursor_cloud = conn_cloud.cursor()
        cursor_cloud.execute(create_table_sql)
        conn_cloud.commit()
        conn_cloud.close()


def fetch_github_projects():
    if not GITHUB_TOKEN:
        print("LỖI: Chưa cấu hình GITHUB_TOKEN trong file .env!")
        return

    init_dbs()

    conn_local = get_local_connection()
    cursor_local = conn_local.cursor()

    conn_cloud = get_cloud_connection()
    cursor_cloud = conn_cloud.cursor() if conn_cloud else None

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    queries = [
        '"đồ án tốt nghiệp" in:readme,description',
        '"capstone project" in:readme,description',
        '"khóa luận tốt nghiệp" in:readme,description'
    ]

    total_saved = 0

    for query in queries:
        print(f"\n--- Đang tìm kiếm từ khóa: {query} ---")
        for page in range(1, 6):
            search_url = f"https://api.github.com/search/repositories?q={query}&sort=updated&order=desc&per_page=30&page={page}"
            res = requests.get(search_url, headers=headers)

            if res.status_code != 200:
                print(f"Lỗi API hoặc hết Rate Limit: {res.text}")
                time.sleep(10)
                continue

            items = res.json().get("items", [])
            if not items:
                break

            for repo in items:
                repo_name = repo.get("full_name")
                repo_url = repo.get("html_url")

                # Kiểm tra trùng lặp trên Local để tiết kiệm Request
                cursor_local.execute("SELECT 1 FROM raw_github_projects WHERE repo_url = %s", (repo_url,))
                if cursor_local.fetchone():
                    continue

                print(f"  -> Đang bóc tách: {repo_name}")

                readme_url = f"https://api.github.com/repos/{repo_name}/readme"
                readme_res = requests.get(readme_url, headers=headers)
                readme_content = ""

                if readme_res.status_code == 200:
                    readme_data = readme_res.json()
                    if "content" in readme_data:
                        try:
                            readme_content = base64.b64decode(readme_data["content"]).decode('utf-8', errors='ignore')
                        except Exception as e:
                            print(f"Lỗi giải mã README: {e}")

                insert_sql = """
                    INSERT INTO raw_github_projects 
                    (repo_url, repo_name, author, description, readme_content, language, stars, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (repo_url) DO NOTHING;
                """
                data_tuple = (
                    repo_url, repo.get("name"), repo.get("owner", {}).get("login"),
                    repo.get("description", ""), readme_content, repo.get("language"),
                    repo.get("stargazers_count"), repo.get("created_at")
                )

                # Lưu vào Local DB
                cursor_local.execute(insert_sql, data_tuple)
                conn_local.commit()

                # Lưu vào Cloud DB (nếu có cấu hình)
                if cursor_cloud:
                    try:
                        cursor_cloud.execute(insert_sql, data_tuple)
                        conn_cloud.commit()
                    except Exception as err:
                        print(f"Lỗi ghi Cloud DB: {err}")

                total_saved += 1
                time.sleep(1)

    cursor_local.close()
    conn_local.close()
    if conn_cloud:
        cursor_cloud.close()
        conn_cloud.close()

    print(f"\n✅ HOÀN THÀNH! Đã lưu {total_saved} đồ án.")


if __name__ == "__main__":
    fetch_github_projects()
