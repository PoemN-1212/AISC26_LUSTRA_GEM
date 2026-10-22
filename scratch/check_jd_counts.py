import os
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import create_engine, text

cloud_url = os.getenv('CLOUD_DB_URL')
if cloud_url and cloud_url.startswith("postgresql://"):
    cloud_url = cloud_url.replace("postgresql://", "postgresql+psycopg2://", 1)

db_url = cloud_url or f"postgresql+psycopg2://{os.getenv('POSTGRES_USER','gem_admin')}:{os.getenv('POSTGRES_PASSWORD','gem_secret_password')}@localhost:{os.getenv('POSTGRES_PORT','5432')}/{os.getenv('POSTGRES_DB','gem_database')}"
engine = create_engine(db_url)

print("="*60)
print("BÁO CÁO THỐNG KÊ CHI TIẾT DỮ LIỆU JD & KỸ NĂNG HỆ THỐNG GEM")
print("="*60)

with engine.connect() as conn:
    # 1. Tổng JD
    raw_jds = conn.execute(text("SELECT COUNT(*) FROM raw_job_postings;")).scalar()
    clean_jds = conn.execute(text("SELECT COUNT(*) FROM cleaned_job_postings;")).scalar()
    clean_projs = conn.execute(text("SELECT COUNT(*) FROM cleaned_github_projects;")).scalar()
    print(f"\n1. Dữ liệu tin tuyển dụng (Job Postings):")
    print(f"   - Tổng JD thu thập thô (raw_job_postings): {raw_jds:,} JDs")
    print(f"   - Tổng JD đã làm sạch & chuẩn hóa (cleaned_job_postings): {clean_jds:,} JDs")
    print(f"   - Tổng Đồ án sinh viên đã làm sạch (cleaned_github_projects): {clean_projs:,} dự án")

    # 2. extracted_skills
    total_skills = conn.execute(text("SELECT COUNT(*) FROM extracted_skills;")).scalar()
    accepted_skills = conn.execute(text("SELECT COUNT(*) FROM extracted_skills WHERE verifier_status = 'ACCEPT';")).scalar()
    job_skills = conn.execute(text("SELECT COUNT(*) FROM extracted_skills WHERE source_type = 'job';")).scalar()
    proj_skills = conn.execute(text("SELECT COUNT(*) FROM extracted_skills WHERE source_type = 'project';")).scalar()
    distinct_jobs_extracted = conn.execute(text("SELECT COUNT(DISTINCT source_id) FROM extracted_skills WHERE source_type = 'job';")).scalar()
    distinct_projs_extracted = conn.execute(text("SELECT COUNT(DISTINCT source_id) FROM extracted_skills WHERE source_type = 'project';")).scalar()

    print(f"\n2. Kỹ năng đã trích xuất thực tế (extracted_skills):")
    print(f"   - Tổng số kỹ năng đã trích xuất: {total_skills:,} bản ghi")
    print(f"   - Kỹ năng được Verifier chấp thuận (ACCEPT): {accepted_skills:,} bản ghi")
    print(f"   - Kỹ năng trích xuất từ JDs: {job_skills:,} bản ghi")
    print(f"   - Kỹ năng trích xuất từ Projects: {proj_skills:,} bản ghi")
    print(f"   - Số lượng JDs THỰC TẾ ĐÃ TRÍCH XUẤT KỸ NĂNG: {distinct_jobs_extracted:,} / {clean_jds:,} JDs ({distinct_jobs_extracted/clean_jds*100:.1f}%)")
    print(f"   - Số lượng Projects THỰC TẾ ĐÃ TRÍCH XUẤT KỸ NĂNG: {distinct_projs_extracted:,} / {clean_projs:,} Projects ({distinct_projs_extracted/clean_projs*100:.1f}%)")

    # 3. Phân rã theo vai trò nghề nghiệp
    print(f"\n3. Phân rã theo Vị trí công việc (Role Breakdown) trong cleaned_job_postings:")
    role_sql = text("""
        SELECT 
            j.role,
            COUNT(DISTINCT j.id) as total_jds,
            COUNT(DISTINCT CASE WHEN s.id IS NOT NULL THEN j.id END) as extracted_jds,
            COUNT(s.id) as total_skills,
            COUNT(CASE WHEN s.verifier_status = 'ACCEPT' THEN s.id END) as accepted_skills
        FROM cleaned_job_postings j
        LEFT JOIN extracted_skills s ON s.source_type = 'job' AND s.source_id = CAST(j.id AS VARCHAR)
        GROUP BY j.role
        ORDER BY total_jds DESC;
    """)
    rows = conn.execute(role_sql).fetchall()
    print(f"   {'Vị trí (Role)':<28} | {'Tổng JDs':<10} | {'Đã trích xuất':<14} | {'Tổng Kỹ Năng':<14} | {'Skills ACCEPT':<14}")
    print("   " + "-"*90)
    for r in rows:
        role_name = r[0] or "Chưa phân loại"
        print(f"   {role_name:<28} | {r[1]:<10} | {r[2]:<14} | {r[3]:<14} | {r[4]:<14}")
