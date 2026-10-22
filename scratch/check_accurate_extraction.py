import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

load_dotenv()
pg_user = os.getenv('POSTGRES_USER', 'gem_admin')
pg_pass = os.getenv('POSTGRES_PASSWORD', 'gem_secret_password')
pg_host = os.getenv('POSTGRES_HOST', 'localhost')
pg_port = os.getenv('POSTGRES_PORT', '5432')
pg_name = os.getenv('POSTGRES_DB', 'gem_database')
local_url = f'postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_name}'

cloud_url = os.getenv('CLOUD_DB_URL')
if cloud_url and cloud_url.startswith('postgresql://'):
    cloud_url = cloud_url.replace('postgresql://', 'postgresql+psycopg2://', 1)

def check_status(name, url):
    print(f"\n==================================================")
    print(f"📊 KIỂM TRA TRẠNG THÁI TRÍCH XUẤT: {name}")
    print(f"==================================================")
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            # 1. Total records in cleaned tables
            total_jds = conn.execute(text("SELECT COUNT(*) FROM cleaned_job_postings;")).scalar()
            valid_jds = conn.execute(text("SELECT COUNT(*) FROM cleaned_job_postings WHERE char_count >= 100;")).scalar()
            
            total_projs = conn.execute(text("SELECT COUNT(*) FROM cleaned_github_projects;")).scalar()
            valid_projs = conn.execute(text("SELECT COUNT(*) FROM cleaned_github_projects WHERE char_count >= 100;")).scalar()
            
            # 2. Existing doc_ids in extracted_skills
            extracted_doc_ids = set(conn.execute(text("SELECT DISTINCT doc_id FROM extracted_skills;")).scalars().all())
            
            # Check JDs extracted
            jd_ids = conn.execute(text("SELECT id FROM cleaned_job_postings WHERE char_count >= 100;")).scalars().all()
            jds_done = [jid for jid in jd_ids if f"JD_{jid}" in extracted_doc_ids]
            jds_pending = [jid for jid in jd_ids if f"JD_{jid}" not in extracted_doc_ids]
            
            # Check Projects extracted
            proj_ids = conn.execute(text("SELECT id FROM cleaned_github_projects WHERE char_count >= 100;")).scalars().all()
            projs_done = [pid for pid in proj_ids if f"GH_{pid}" in extracted_doc_ids]
            projs_pending = [pid for pid in proj_ids if f"GH_{pid}" not in extracted_doc_ids]
            
            # Total skills breakdown
            total_skills = conn.execute(text("SELECT COUNT(*) FROM extracted_skills;")).scalar()
            accept_skills = conn.execute(text("SELECT COUNT(*) FROM extracted_skills WHERE verifier_status = 'ACCEPT';")).scalar()
            reject_skills = conn.execute(text("SELECT COUNT(*) FROM extracted_skills WHERE verifier_status = 'REJECT';")).scalar()
            
            print(f"1. Tin tuyển dụng (Job Postings - JDs):")
            print(f"   • Tổng số JD trong DB: {total_jds}")
            print(f"   • Số JD hợp lệ (char_count >= 100): {valid_jds}")
            print(f"   • Số JD ĐÃ trích xuất: {len(jds_done)} / {valid_jds} ({len(jds_done)/valid_jds*100:.1f}%)")
            print(f"   • Số JD CÒN LẠI chưa trích xuất: {len(jds_pending)}")
            
            print(f"\n2. Đồ án sinh viên (GitHub Projects):")
            print(f"   • Tổng số Đồ án trong DB: {total_projs}")
            print(f"   • Số Đồ án hợp lệ (char_count >= 100): {valid_projs}")
            print(f"   • Số Đồ án ĐÃ trích xuất: {len(projs_done)} / {valid_projs} ({len(projs_done)/valid_projs*100:.1f}%)")
            print(f"   • Số Đồ án CÒN LẠI chưa trích xuất: {len(projs_pending)}")
            
            print(f"\n3. Thống kê Kỹ năng (Extracted Skills):")
            print(f"   • Tổng số kỹ năng đã trích xuất: {total_skills:,}")
            print(f"   • Kỹ năng được Verifier chấp thuận (ACCEPT): {accept_skills:,}")
            print(f"   • Kỹ năng bị Verifier loại bỏ (REJECT): {reject_skills:,}")
            
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra {name}: {e}")

check_status("LOCAL POSTGRESQL (Máy dev)", local_url)
if cloud_url:
    check_status("CLOUD NEON DB (Production/Sync)", cloud_url)
