import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
pg_user = os.getenv('POSTGRES_USER', 'gem_admin')
pg_pass = os.getenv('POSTGRES_PASSWORD', 'gem_secret_password')
pg_host = os.getenv('POSTGRES_HOST', 'localhost')
pg_port = os.getenv('POSTGRES_PORT', '5432')
pg_name = os.getenv('POSTGRES_DB', 'gem_database')
local_url = f'postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_name}'

engine = create_engine(local_url)
with engine.connect() as conn:
    print("=== KIỂM TRA CHI TIẾT TRÍCH XUẤT LOCAL POSTGRES ===")
    
    # 1. JDs
    total_jds = conn.execute(text("SELECT COUNT(*) FROM cleaned_job_postings;")).scalar()
    jds_extracted = conn.execute(text("SELECT COUNT(DISTINCT doc_id) FROM extracted_skills WHERE source_type = 'job';")).scalar()
    print(f"1. Tin tuyển dụng (JDs):")
    print(f"   - Tổng số JD đã làm sạch: {total_jds}")
    print(f"   - Số JD ĐÃ trích xuất ra kỹ năng: {jds_extracted} ({jds_extracted/total_jds*100:.2f}%)")
    
    # Check if there are JDs without skills in extracted_skills
    unextracted_jds = conn.execute(text("""
        SELECT COUNT(*) 
        FROM cleaned_job_postings j
        WHERE CAST(j.id AS VARCHAR) NOT IN (
            SELECT DISTINCT doc_id FROM extracted_skills WHERE source_type = 'job'
        );
    """)).scalar()
    print(f"   - Số JD chưa có bản ghi trong extracted_skills: {unextracted_jds}")
    
    # 2. Projects
    total_projs = conn.execute(text("SELECT COUNT(*) FROM cleaned_github_projects;")).scalar()
    projs_extracted = conn.execute(text("SELECT COUNT(DISTINCT doc_id) FROM extracted_skills WHERE source_type = 'project';")).scalar()
    print(f"\n2. Đồ án / Repositories (Projects):")
    print(f"   - Tổng số Project trong cleaned_github_projects: {total_projs}")
    print(f"   - Số Project ĐÃ trích xuất ra kỹ năng: {projs_extracted}")
    
    # Check unextracted projects
    unextracted_projs = conn.execute(text("""
        SELECT COUNT(*) 
        FROM cleaned_github_projects p
        WHERE CAST(p.id AS VARCHAR) NOT IN (
            SELECT DISTINCT doc_id FROM extracted_skills WHERE source_type = 'project'
        );
    """)).scalar()
    print(f"   - Số Project trong cleaned_github_projects chưa có kỹ năng: {unextracted_projs}")
    
    # Check doc_ids in extracted_skills for projects
    sample_proj_docs = conn.execute(text("SELECT DISTINCT doc_id FROM extracted_skills WHERE source_type = 'project' LIMIT 10;")).fetchall()
    print(f"   - Mẫu doc_id của project trong extracted_skills: {[r[0] for r in sample_proj_docs]}")
    
    # Check verifier status
    print(f"\n3. Phân bố trạng thái Verifier:")
    status_counts = conn.execute(text("SELECT verifier_status, COUNT(*) FROM extracted_skills GROUP BY verifier_status;")).fetchall()
    for status, cnt in status_counts:
        print(f"   - {status}: {cnt}")
