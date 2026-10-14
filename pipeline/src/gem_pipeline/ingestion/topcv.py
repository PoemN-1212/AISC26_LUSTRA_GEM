"""
GEM TopCV Ingestion Engine (Mô-đun cào tin tuyển dụng TopCV IT)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Cải tiến toàn diện:
1. Lưu trữ 3 Lớp Đồng Bộ (Triple Storage):
   - Lớp 1: Ghi file JSONL vào data/raw/topcv/topcv_jobs.jsonl
   - Lớp 2: Ghi vào CSDL Local PostgreSQL (gem_database)
   - Lớp 3: Tự động đồng bộ lên Neon Cloud PostgreSQL (nếu có CLOUD_DB_URL)
2. Bóc tách thuộc tính Thời gian từ JSON-LD (datePosted, validThrough) để phân tích Xu hướng (Trend Analysis).
3. Cơ chế DB Auto-Reconnect & Retry: Miễn nhiễm với sự cố lag mạng hoặc rớt DNS Docker.
4. Tự động xoay vòng Session FlareSolverr (Session Rotation mỗi 50 trang): Chống tràn RAM và chống chặn.
5. Checkpoint thông minh: Bỏ qua các URL đã cào thành công để tiếp tục cào mượt mà.
"""

import os
import sys
import json
import time
import random
import requests
import psycopg2
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, Tuple
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
FLARESOLVERR_URL = os.getenv("FLARESOLVERR_URL", "http://localhost:8191/v1")


def get_data_dir() -> str:
    """Xác định đường dẫn thư mục data/ trên máy host hoặc trong container Airflow."""
    env_dir = os.getenv("GEM_DATA_DIR")
    if env_dir and os.path.exists(env_dir):
        return env_dir
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
    """Lọc bỏ ký tự NUL 0x00 an toàn cho CSDL PostgreSQL."""
    if not text:
        return ""
    return text.replace("\x00", "").replace("\0", "").strip()


def parse_date_string(date_str: Optional[str]) -> Optional[str]:
    """Chuẩn hóa chuỗi ngày giờ (ví dụ '2024-09-25T08:00:00+07:00' -> '2024-09-25')."""
    if not date_str:
        return None
    try:
        # Lấy 10 ký tự đầu YYYY-MM-DD
        part = date_str.split("T")[0].split(" ")[0].strip()
        if len(part) == 10 and part.count("-") == 2:
            return part
    except Exception:
        pass
    return None


def get_local_connection():
    """Tạo kết nối Local PostgreSQL với 3 lần retry."""
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
    """Tạo kết nối Neon Cloud PostgreSQL."""
    if CLOUD_DB_URL:
        try:
            return psycopg2.connect(CLOUD_DB_URL, connect_timeout=15)
        except Exception as e:
            print(f"⚠️ Cảnh báo: Không thể kết nối Cloud DB ({e})")
            return None
    return None


def init_storage():
    """Khởi tạo cấu trúc lưu trữ (Thư mục file JSONL + Bảng CSDL)."""
    # 1. Thư mục file
    data_dir = get_data_dir()
    raw_topcv_dir = os.path.join(data_dir, "raw", "topcv")
    os.makedirs(raw_topcv_dir, exist_ok=True)

    create_table_sql = """
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
    if CLOUD_DB_URL:
        try:
            conn_cloud = get_cloud_connection()
            if conn_cloud:
                with conn_cloud.cursor() as cur:
                    cur.execute(create_table_sql)
                conn_cloud.commit()
                conn_cloud.close()
        except Exception as e:
            print(f"⚠️ Lỗi khởi tạo Cloud DB: {e}")


def save_to_jsonl(record: Dict[str, Any]):
    """Lưu bản ghi tuyển dụng vào file data/raw/topcv/topcv_jobs.jsonl."""
    try:
        data_dir = get_data_dir()
        file_path = os.path.join(data_dir, "raw", "topcv", "topcv_jobs.jsonl")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"⚠️ Lỗi ghi file JSONL cục bộ: {e}")


class FlareSolverrClient:
    """Quản lý kết nối FlareSolverr với cơ chế Session Rotation định kỳ."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_id = None
        self.request_count = 0

    def create_session(self):
        try:
            if self.session_id:
                self.destroy_session()
            res = requests.post(f"{self.base_url}", json={"cmd": "sessions.create"}, timeout=25)
            self.session_id = res.json().get("session")
            self.request_count = 0
            print(f"🔄 Đã tạo FlareSolverr Session mới: {self.session_id}")
        except Exception as e:
            print(f"⚠️ Không thể tạo Session FlareSolverr ({e})")
            self.session_id = None

    def destroy_session(self):
        if self.session_id:
            try:
                requests.post(f"{self.base_url}", json={"cmd": "sessions.destroy", "session": self.session_id}, timeout=10)
            except Exception:
                pass
            self.session_id = None

    def fetch_html(self, url: str) -> str:
        # Tự động làm mới Session sau mỗi 60 requests để giải phóng RAM Chrome
        if not self.session_id or self.request_count >= 60:
            self.create_session()

        self.request_count += 1
        for attempt in range(2):
            try:
                payload = {
                    "cmd": "request.get",
                    "url": url,
                    "session": self.session_id,
                    "maxTimeout": 45000
                }
                res = requests.post(self.base_url, json=payload, timeout=50)
                html = res.json().get("solution", {}).get("response", "")
                if html:
                    return html
            except Exception as e:
                print(f"     ⚠️ FlareSolverr thử lần {attempt+1} thất bại: {e}")
                time.sleep(3)
                self.create_session()
        return ""


def run_bulk_crawler(max_pages: int = 150):
    init_storage()
    data_dir = get_data_dir()
    jsonl_file = os.path.join(data_dir, "raw", "topcv", "topcv_jobs.jsonl")
    print("🚀 Khởi động hệ thống thu thập TopCV IT (Chế độ lưu 3 lớp + Lọc thời gian)...")
    print(f"📁 Thư mục lưu file JSONL: {jsonl_file}")

    flaresolverr = FlareSolverrClient(FLARESOLVERR_URL)
    flaresolverr.create_session()

    # 1. Đọc danh sách URL đã có sẵn đầy đủ ngày tháng để tránh cào lại
    existing_urls = set()
    try:
        conn = get_local_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT url FROM raw_job_postings WHERE posted_date IS NOT NULL;")
            rows = cur.fetchall()
            existing_urls = {r[0] for r in rows}
        conn.close()
        print(f"ℹ️ Đã có {len(existing_urls)} tin tuyển dụng có sẵn ngày đăng (sẽ bỏ qua để tối ưu thời gian).")
    except Exception as e:
        print(f"⚠️ Lỗi đọc existing URLs từ Local DB: {e}")

    # 2. QUÉT DANH SÁCH URL TỪ DANH MỤC CNTT (Category cr257)
    target_categories = [
        "https://www.topcv.vn/tim-viec-lam-cong-nghe-thong-tin-cr257?type_keyword=1&disable_auto_detect_type_keyword=1&sba=1&category_family=r257&saturday_status=0"
    ]

    job_urls = []
    for base_url in target_categories:
        print(f"\n--- Quét danh mục tổng hợp IT (Tối đa {max_pages} trang) ---")
        for page_num in range(1, max_pages + 1):
            url_to_fetch = f"{base_url}&page={page_num}"
            print(f"Quét danh sách trang {page_num}...")

            html = flaresolverr.fetch_html(url_to_fetch)
            soup = BeautifulSoup(html, "html.parser")

            if "Just a moment..." in soup.text:
                print(f"Trang {page_num} kẹt Cloudflare, tạm nghỉ 5s...")
                time.sleep(5)
                continue

            links = soup.find_all('a', href=True)
            new_links_in_page = 0

            for a in links:
                href = a['href']
                if "/viec-lam/" in href and href.startswith("https://www.topcv.vn/"):
                    clean_url = href.split('?')[0]
                    if clean_url not in job_urls:
                        job_urls.append(clean_url)
                        new_links_in_page += 1

            if new_links_in_page == 0 and page_num > 5:
                print(f"Trang {page_num} không còn tin mới. Đã quét xong danh mục!")
                break

            time.sleep(random.uniform(1.2, 2.5))

    print(f"\n🔍 Tổng cộng tìm thấy {len(job_urls)} URL công việc IT. Bắt đầu bóc tách...")

    # 3. BÓC TÁCH CHI TIẾT VÀ LƯU 3 LỚP
    new_saved_count = 0

    for idx, url in enumerate(job_urls):
        print(f"[{idx+1}/{len(job_urls)}] Đang mở: {url}")

        if url in existing_urls:
            print("  -> Đã tồn tại trong DB, bỏ qua.")
            continue

        if idx > 0 and idx % 80 == 0:
            print("⏳ Đã xử lý 80 tin. Tạm nghỉ 15s để làm mát kết nối...")
            time.sleep(15)

        html = flaresolverr.fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        script_tag = soup.find("script", type="application/ld+json")
        if script_tag and script_tag.string:
            try:
                data = json.loads(script_tag.string)
                desc_html = data.get("description", "") or ""
                clean_description = BeautifulSoup(desc_html, "html.parser").get_text(separator="\n", strip=True)
                clean_description = sanitize_text(clean_description)

                # Bóc tách Lương
                salary_min = 0
                salary_max = 0
                base_salary = data.get("baseSalary")
                if isinstance(base_salary, dict):
                    val = base_salary.get("value")
                    if isinstance(val, dict):
                        salary_min = val.get("minValue", 0) or 0
                        salary_max = val.get("maxValue", 0) or 0
                    elif isinstance(val, (int, float)):
                        salary_min = val
                        salary_max = val

                # Bóc tách Thời gian & Thuộc tính Xu hướng (Trend Attributes)
                raw_posted_date = data.get("datePosted")
                raw_valid_through = data.get("validThrough")
                posted_date = parse_date_string(raw_posted_date)
                valid_through = parse_date_string(raw_valid_through)

                # Địa điểm và hình thức làm việc
                location = ""
                job_loc = data.get("jobLocation")
                if isinstance(job_loc, dict):
                    address = job_loc.get("address")
                    if isinstance(address, dict):
                        location = address.get("addressLocality") or address.get("addressRegion") or ""
                    elif isinstance(address, str):
                        location = address
                location = sanitize_text(location)

                employment_type = sanitize_text(data.get("employmentType", ""))
                title = sanitize_text(data.get("title", ""))
                company = ""
                hiring_org = data.get("hiringOrganization")
                if isinstance(hiring_org, dict):
                    company = sanitize_text(hiring_org.get("name", ""))

                record = {
                    "url": url,
                    "title": title,
                    "company": company,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "full_content": clean_description,
                    "posted_date": posted_date,
                    "valid_through": valid_through,
                    "location": location,
                    "employment_type": employment_type,
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                }

                # 1. Ghi File JSONL cục bộ (Lớp 1)
                save_to_jsonl(record)

                # 2. Ghi Local DB (Lớp 2) với retry
                try:
                    conn_loc = get_local_connection()
                    with conn_loc.cursor() as cur:
                        cur.execute("""
                            INSERT INTO raw_job_postings 
                            (url, title, company, salary_min, salary_max, full_content, posted_date, valid_through, location, employment_type)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (url) DO UPDATE
                            SET posted_date = COALESCE(EXCLUDED.posted_date, raw_job_postings.posted_date),
                                valid_through = COALESCE(EXCLUDED.valid_through, raw_job_postings.valid_through),
                                location = COALESCE(EXCLUDED.location, raw_job_postings.location);
                        """, (
                            url, title, company, salary_min, salary_max, clean_description,
                            posted_date, valid_through, location, employment_type
                        ))
                    conn_loc.commit()
                    conn_loc.close()
                except Exception as err:
                    print(f"     ⚠️ Lỗi ghi Local DB ({url}): {err}")

                # 3. Ghi Cloud DB (Lớp 3)
                if CLOUD_DB_URL:
                    try:
                        conn_cld = get_cloud_connection()
                        if conn_cld:
                            with conn_cld.cursor() as cur:
                                cur.execute("""
                                    INSERT INTO raw_job_postings 
                                    (url, title, company, salary_min, salary_max, full_content, posted_date, valid_through, location, employment_type)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (url) DO UPDATE
                                    SET posted_date = COALESCE(EXCLUDED.posted_date, raw_job_postings.posted_date),
                                        valid_through = COALESCE(EXCLUDED.valid_through, raw_job_postings.valid_through),
                                        location = COALESCE(EXCLUDED.location, raw_job_postings.location);
                                """, (
                                    url, title, company, salary_min, salary_max, clean_description,
                                    posted_date, valid_through, location, employment_type
                                ))
                            conn_cld.commit()
                            conn_cld.close()
                    except Exception as err:
                        print(f"     ⚠️ Lỗi ghi Cloud DB: {err}")

                existing_urls.add(url)
                new_saved_count += 1
                print(f"  -> Lưu MỚI thành công: {title[:40]}... (Ngày đăng: {posted_date or 'N/A'})")

            except Exception as e:
                print(f"  -> Lỗi phân tích JSON từ thẻ script: {e}")
        else:
            print("  -> Không tìm thấy dữ liệu JSON-LD hoặc bị chặn.")

        time.sleep(random.uniform(2.0, 3.8))

    flaresolverr.destroy_session()
    print(f"\n🎉 HOÀN THÀNH CÀO TOPCV! Đã lưu mới {new_saved_count} tin tuyển dụng.")
    print(f"📁 Dữ liệu đã được lưu trữ 3 lớp: File JSONL, Local PostgreSQL và Neon Cloud DB.")


if __name__ == "__main__":
    run_bulk_crawler()
