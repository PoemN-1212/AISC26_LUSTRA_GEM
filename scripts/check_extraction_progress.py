import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
load_dotenv()

def check():
    pg_user = os.getenv("POSTGRES_USER", "gem_admin")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "gem_secret_password")
    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_name = os.getenv("POSTGRES_DB", "gem_database")
    db_uri = f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_name}"

    engine = create_engine(db_uri)
    with engine.connect() as conn:
        total_jds = conn.execute(text("SELECT COUNT(*) FROM cleaned_job_postings WHERE char_count >= 100")).scalar()
        total_projs = conn.execute(text("SELECT COUNT(*) FROM cleaned_github_projects WHERE char_count >= 100")).scalar()
        
        # Check extracted_skills
        has_table = conn.execute(text("SELECT to_regclass('extracted_skills')")).scalar()
        if not has_table:
            print("Bảng extracted_skills chưa được tạo.")
            return

        total_extracted_skills = conn.execute(text("SELECT COUNT(*) FROM extracted_skills")).scalar()
        accepted_skills = conn.execute(text("SELECT COUNT(*) FROM extracted_skills WHERE verifier_status = 'ACCEPT'")).scalar()
        rejected_skills = conn.execute(text("SELECT COUNT(*) FROM extracted_skills WHERE verifier_status = 'REJECT'")).scalar()
        
        extracted_docs = conn.execute(text("SELECT DISTINCT doc_id FROM extracted_skills")).scalars().all()
        extracted_jds = [d for d in extracted_docs if d.startswith("JD_")]
        extracted_projs = [d for d in extracted_docs if d.startswith("GH_")]

    print("=" * 60)
    print("📊 BÁO CÁO TIẾN ĐỘ TRÍCH XUẤT HIỆN TẠI (POSTGRESQL)")
    print("=" * 60)
    print(f"Tổng JD hợp lệ (cleaned):           {total_jds}")
    print(f"  ➜ JD đã trích xuất:               {len(extracted_jds)} / {total_jds} ({len(extracted_jds)/total_jds*100:.1f}%)")
    print(f"  ➜ JD còn lại cần trích xuất:      {total_jds - len(extracted_jds)}")
    print("-" * 60)
    print(f"Tổng Project hợp lệ (cleaned):      {total_projs}")
    print(f"  ➜ Project đã trích xuất:          {len(extracted_projs)} / {total_projs} ({len(extracted_projs)/total_projs*100:.1f}%)")
    print(f"  ➜ Project còn lại cần trích xuất: {total_projs - len(extracted_projs)}")
    print("-" * 60)
    print(f"Tổng số Skills trong Database:      {total_extracted_skills}")
    print(f"  ➜ Chấp nhận (ACCEPT):             {accepted_skills} ({accepted_skills/max(1, total_extracted_skills)*100:.1f}%)")
    print(f"  ➜ Loại bỏ (REJECT):               {rejected_skills} ({rejected_skills/max(1, total_extracted_skills)*100:.1f}%)")
    print("=" * 60)

if __name__ == '__main__':
    check()
