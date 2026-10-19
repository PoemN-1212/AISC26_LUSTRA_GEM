import sys
import io
import json
from sqlalchemy import create_engine, text
from qdrant_client import QdrantClient

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

engine = create_engine('postgresql+psycopg2://gem_admin:gem_secret_password@localhost:5432/gem_database')
with engine.connect() as conn:
    n_jds = conn.execute(text('SELECT count(1) FROM cleaned_job_postings')).scalar()
    n_projs = conn.execute(text('SELECT count(1) FROM cleaned_github_projects')).scalar()
    n_skills = conn.execute(text('SELECT count(1) FROM extracted_skills')).scalar()
    n_skills_acc = conn.execute(text("SELECT count(1) FROM extracted_skills WHERE verifier_status = 'ACCEPT'")).scalar()
    n_skills_rej = conn.execute(text("SELECT count(1) FROM extracted_skills WHERE verifier_status = 'REJECT'")).scalar()
    n_jds_extracted = conn.execute(text("SELECT count(DISTINCT source_id) FROM extracted_skills WHERE source_type = 'job'")).scalar()
    n_projs_extracted = conn.execute(text("SELECT count(DISTINCT source_id) FROM extracted_skills WHERE source_type = 'project'")).scalar()

print(f"=== POSTGRESQL STATUS ===")
print(f"Cleaned JDs: {n_jds}")
print(f"Cleaned Projects: {n_projs}")
print(f"Extracted Skills Total: {n_skills} (Accepted: {n_skills_acc}, Rejected: {n_skills_rej})")
print(f"JDs with extracted skills: {n_jds_extracted}/{n_jds} ({n_jds_extracted/n_jds*100:.1f}%)")
print(f"Projects with extracted skills: {n_projs_extracted}/{n_projs} ({n_projs_extracted/n_projs*100:.1f}%)")

print("\n=== QDRANT VECTOR DB STATUS ===")
try:
    qc = QdrantClient(url="http://localhost:6333", timeout=10.0)
    for col in ["market_jds", "student_projects"]:
        c_info = qc.get_collection(col)
        pts = c_info.points_count
        res, _ = qc.scroll(
            collection_name=col,
            limit=20,
            with_payload=True,
            with_vectors=False
        )
        enriched = sum(1 for p in res if p.payload and len(p.payload.get("skills", [])) > 0)
        print(f"Collection '{col}': {pts} vector points | Sample enriched with skills: {enriched}/{len(res)}")
except Exception as e:
    print(f"Qdrant check error: {e}")
