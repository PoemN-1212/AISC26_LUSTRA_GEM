import os
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, "pipeline/src")
from dotenv import load_dotenv
load_dotenv()

from gem_pipeline.market.role_profiler import RoleSkillProfiler
from gem_pipeline.vector_store.qdrant_service import QdrantVectorService

profiler = RoleSkillProfiler()
qdrant = QdrantVectorService()

print("="*75)
print("1. THỐNG KÊ TOÀN DIỆN VỀ SỐ LƯỢNG JD THEO ROLE PROFILER TRONG DATABASE")
print("="*75)

summary_data = profiler.get_all_role_summaries()
total_jds = summary_data.get("total_jds", 0)
print(f"Tổng số JDs đã làm sạch trong cleaned_job_postings: {total_jds:,} JDs\n")

print(f"{'Lĩnh vực (Domain)':<28} | {'Vị trí (Specific Role)':<32} | {'Số JDs':<10} | {'Tỷ trọng'}")
print("-" * 85)
for r in summary_data.get("roles", []):
    print(f"{r['domain']:<28} | {r['specific_role']:<32} | {r['jd_count']:<10} | {r['share_pct']}%")

print("\n" + "="*75)
print("2. KIỂM TRA SỐ LƯỢNG VECTOR TRONG QDRANT (KHO TÌM KIẾM NGỮ NGHĨA)")
print("="*75)
try:
    info_jobs = qdrant.client.get_collection(qdrant.COLLECTION_JDS)
    print(f"• Collection '{qdrant.COLLECTION_JDS}': {info_jobs.points_count:,} điểm vector (JDs)")
except Exception as e:
    print(f"Lỗi Qdrant jobs: {e}")

try:
    info_projs = qdrant.client.get_collection(qdrant.COLLECTION_PROJECTS)
    print(f"• Collection '{qdrant.COLLECTION_PROJECTS}': {info_projs.points_count:,} điểm vector (Đồ án GitHub)")
except Exception as e:
    print(f"Lỗi Qdrant projects: {e}")

print("\n" + "="*75)
print("3. CHI TIẾT SỐ LƯỢNG JD ĐỐI CHIẾU THỰC TẾ THEO CÁC VAI TRÒ CHÍNH")
print("="*75)
sample_roles = [
    "Backend Developer", 
    "Frontend Developer", 
    "Fullstack Developer", 
    "Data Engineer", 
    "AI / Machine Learning Engineer", 
    "DevOps Engineer",
    "Mobile Developer",
    "QA / QC / Software Tester",
    "Data Analyst",
    "Security / Cyber Security"
]

for r in sample_roles:
    p = profiler.get_role_skill_profile(r, top_k=15)
    core_count = len(p.get("core_skills", []))
    boost_count = len(p.get("boost_skills", []))
    ability_count = len(p.get("abilities", []))
    print(f"• {r:<30}: {p.get('total_jds', 0):>4} JDs đối chiếu | {core_count:>2} Core skills | {boost_count:>2} Boosters | {ability_count:>2} Abilities")
