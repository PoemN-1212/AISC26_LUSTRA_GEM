import os
import json
import time
import random
import requests
import psycopg2
from bs4 import BeautifulSoup

DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_USER = os.getenv("POSTGRES_USER", "gem_admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "gem_secret_password")
DB_NAME = os.getenv("POSTGRES_DB", "gem_database")
FLARESOLVERR_URL = os.getenv("FLARESOLVERR_URL", "http://flaresolverr:8191/v1")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME,
    )


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
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
    """)
    conn.commit()
    cursor.close()
    conn.close()


def run_bulk_crawler():
    init_db()
    print("Khởi động hệ thống thu thập (Lọc 100% IT theo danh mục cr257, max 70 pages)...")

    # KHỞI TẠO SESSION
    session_res = requests.post(FLARESOLVERR_URL, json={"cmd": "sessions.create"}, timeout=30)
    session_id = session_res.json().get("session")
    if not session_id:
        print("Không thể tạo Session với FlareSolverr!")
        return

    def fetch_html(url):
        try:
            payload = {"cmd": "request.get", "url": url, "session": session_id, "maxTimeout": 60000}
            res = requests.post(FLARESOLVERR_URL, json=payload, timeout=70)
            return res.json().get("solution", {}).get("response", "")
        except Exception as e:
            print(f"Lỗi FlareSolverr: {e}")
            return ""

    # 1. QUÉT DANH SÁCH TỪ URL TỔNG HỢP IT CỦA USER
    target_categories = [
        "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?type_keyword=1&disable_auto_detect_type_keyword=1&sba=1&category_family=r257&saturday_status=0"
    ]

    job_urls = []
    max_pages_per_category = 70

    for base_url in target_categories:
        print(f"\n--- Đang quét danh mục tổng hợp IT (Dự kiến ~2600+ tin) ---")
        for page_num in range(1, max_pages_per_category + 1):
            url_to_fetch = f"{base_url}&page={page_num}"
            print(f"Quét trang {page_num}...")

            html = fetch_html(url_to_fetch)
            soup = BeautifulSoup(html, "html.parser")

            if "Just a moment..." in soup.text:
                print(f"Trang {page_num} kẹt Captcha, thử bỏ qua...")
                time.sleep(5)
                continue

            links = soup.find_all('a', href=True)
            valid_links_found = 0

            for a in links:
                href = a['href']
                if "/viec-lam/" in href and href.startswith("https://www.topcv.vn/"):
                    clean_url = href.split('?')[0]
                    if clean_url not in job_urls:
                        job_urls.append(clean_url)
                        valid_links_found += 1

            if valid_links_found == 0:
                print(f"Trang {page_num} không có tin mới. Đã vét sạch danh mục!")
                break

            time.sleep(random.uniform(1.5, 3.5))

    print(f"\nTìm thấy tổng cộng {len(job_urls)} URL tin IT. Bắt đầu bóc tách...")

    # 2. BÓC TÁCH CHI TIẾT
    conn = get_db_connection()
    cursor = conn.cursor()
    success_count = 0

    for idx, url in enumerate(job_urls):
        print(f"[{idx+1}/{len(job_urls)}] Đang mở: {url}")

        if idx > 0 and idx % 100 == 0:
            print("Đã xử lý 100 tin. Hệ thống nghỉ ngơi 30s để làm mát...")
            time.sleep(30)

        html = fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        script_tag = soup.find("script", type="application/ld+json")
        if script_tag:
            try:
                data = json.loads(script_tag.string)
                description_html = data.get("description", "")
                clean_description = BeautifulSoup(description_html, "html.parser").get_text(separator="\n", strip=True)

                base_salary = data.get("baseSalary")
                if isinstance(base_salary, dict):
                    salary_val = base_salary.get("value")
                    if isinstance(salary_val, dict):
                        salary_min = salary_val.get("minValue", 0) or 0
                        salary_max = salary_val.get("maxValue", 0) or 0
                    elif isinstance(salary_val, (int, float)):
                        salary_min = salary_val
                        salary_max = salary_val
                    else:
                        salary_min = 0
                        salary_max = 0
                else:
                    salary_min = 0
                    salary_max = 0

                cursor.execute("""
                    INSERT INTO raw_job_postings (url, title, company, salary_min, salary_max, full_content)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO NOTHING;
                """, (
                    url,
                    data.get("title", ""),
                    data.get("hiringOrganization", {}).get("name", "") if isinstance(data.get("hiringOrganization"), dict) else "",
                    salary_min,
                    salary_max,
                    clean_description
                ))

                if cursor.rowcount > 0:
                    success_count += 1
                    print(f"  -> Lưu MỚI thành công: {data.get('title', '')[:50]}...")
                else:
                    print(f"  -> Đã tồn tại")
                conn.commit()
            except Exception as e:
                print(f"  -> Lỗi phân tích JSON: {e}")
        else:
            print("  -> Không tìm thấy dữ liệu hoặc bị chặn.")

        time.sleep(random.uniform(2.5, 4.5))

    cursor.close()
    conn.close()
    try:
        requests.post(FLARESOLVERR_URL, json={"cmd": "sessions.destroy", "session": session_id}, timeout=10)
    except Exception:
        pass
    print(f"Hoàn thành! Đã lưu mới {success_count} công việc IT thuần túy vào kho dữ liệu.")


if __name__ == "__main__":
    run_bulk_crawler()
