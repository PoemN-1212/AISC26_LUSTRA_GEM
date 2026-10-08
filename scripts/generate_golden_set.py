"""
Kịch bản tạo bản nháp Golden Set (Pre-annotation Draft) cho GEM
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
Sử dụng SkillExtractor (Ưu tiên Qwen Local qua Ollama, fallback Gemini Cloud)
"""

import os
import json
import time
import argparse
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

from gem_pipeline.extraction.extractor import SkillExtractor

load_dotenv()

# 1. Cấu hình Database (Mặc định dùng Local DB nơi đã lưu dữ liệu cleaned)
def get_db_uri(use_cloud: bool = False):
    cloud_url = os.getenv("CLOUD_DB_URL")
    if use_cloud and cloud_url:
        return cloud_url.replace("postgresql://", "postgresql+psycopg2://")
    
    pg_user = os.getenv("POSTGRES_USER", "gem_admin")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "gem_secret_password")
    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_name = os.getenv("POSTGRES_DB", "gem_database")
    return f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_name}"

engine = create_engine(get_db_uri())


def build_golden_set_draft(jd_limit: int = 30, project_limit: int = 10, delay_sec: float = 1.0):
    """
    Lấy mẫu từ cleaned_job_postings và cleaned_github_projects,
    chạy LLM pre-annotation và xuất file Excel Golden Set Draft với cấu trúc nghiệm thu.
    """
    print("=" * 70)
    print("🚀 BẮT ĐẦU TẠO BẢN NHÁP GOLDEN SET (PRE-ANNOTATION DRAFT)")
    print(f"📊 Cấu hình mẫu: {jd_limit} JDs tuyển dụng | {project_limit} Đồ án sinh viên")
    print("=" * 70)

    extractor = SkillExtractor()
    backend_info = f"Ollama Local ({extractor.ollama_model})" if extractor._is_ollama_available() else "Gemini Cloud API"
    print(f"🤖 LLM Engine đang sử dụng: {backend_info}\n")

    # 1. Lấy mẫu từ cleaned_job_postings
    print("[1/3] Đang lấy mẫu từ cleaned_job_postings...")
    jd_query = f"""
        SELECT id, raw_job_id, title, company, content_clean
        FROM cleaned_job_postings
        WHERE char_count >= 200
        ORDER BY RANDOM()
        LIMIT {jd_limit};
    """
    try:
        df_jds = pd.read_sql(jd_query, engine)
        print(f"✅ Đã chọn ngẫu nhiên {len(df_jds)} JD tuyển dụng.")
    except Exception as e:
        print(f"❌ Lỗi đọc cleaned_job_postings: {e}")
        df_jds = pd.DataFrame()

    # 2. Lấy mẫu từ cleaned_github_projects
    print("\n[2/3] Đang lấy mẫu từ cleaned_github_projects...")
    proj_query = f"""
        SELECT id, raw_project_id, repo_name, author, combined_clean_text
        FROM cleaned_github_projects
        WHERE char_count >= 150
        ORDER BY RANDOM()
        LIMIT {project_limit};
    """
    try:
        df_props = pd.read_sql(proj_query, engine)
        print(f"✅ Đã chọn ngẫu nhiên {len(df_props)} đồ án GitHub.")
    except Exception as e:
        print(f"❌ Lỗi đọc cleaned_github_projects: {e}")
        df_props = pd.DataFrame()

    # 3. Chạy trích xuất candidate skills
    source_docs = []
    extracted_records = []

    # Xử lý JDs
    if not df_jds.empty:
        print(f"\n[3/3] Đang chạy trích xuất {len(df_jds)} JD tuyển dụng...")
        for idx, row in df_jds.iterrows():
            doc_id = f"JD_{row['id']}"
            title = row.get("title", "")
            content = row.get("content_clean", "")
            print(f"  [{idx + 1}/{len(df_jds)}] JD: {title[:45]}...", flush=True)

            source_docs.append({
                "doc_id": doc_id,
                "doc_type": "JOB_POSTING",
                "title": title,
                "author_or_company": row.get("company", ""),
                "char_count": len(content),
                "content_clean": content,
                "missing_skills_added": ""
            })

            skills = extractor.extract_baseline(content)
            for s in skills:
                if isinstance(s, dict) and s.get("evidence"):
                    extracted_records.append({
                        "doc_id": doc_id,
                        "doc_type": "JOB_POSTING",
                        "title": title,
                        "evidence": s.get("evidence", "").strip(),
                        "skill": s.get("skill", "").strip(),
                        "type": s.get("type", "TECHNOLOGY").upper(),
                        "context": s.get("context", "required"),
                        "human_verify": "",             # ACCEPT / REJECT / MODIFY
                        "human_corrected_skill": "",     # Điền nếu cần sửa tên
                        "human_corrected_type": "",      # Điền nếu cần sửa type
                        "note": ""                       # Ghi chú lý do nếu reject
                    })
            time.sleep(delay_sec)

    # Xử lý GitHub projects
    if not df_props.empty:
        print(f"\nĐang chạy trích xuất {len(df_props)} Đồ án GitHub...", flush=True)
        for idx, row in df_props.iterrows():
            doc_id = f"GH_{row['id']}"
            repo = row.get("repo_name", "")
            content = row.get("combined_clean_text", "")
            print(f"  [{idx + 1}/{len(df_props)}] Project: {repo[:45]}...", flush=True)

            source_docs.append({
                "doc_id": doc_id,
                "doc_type": "GITHUB_PROJECT",
                "title": repo,
                "author_or_company": row.get("author", ""),
                "char_count": len(content),
                "content_clean": content,
                "missing_skills_added": ""
            })

            skills = extractor.extract_baseline(content)
            for s in skills:
                if isinstance(s, dict) and s.get("evidence"):
                    extracted_records.append({
                        "doc_id": doc_id,
                        "doc_type": "GITHUB_PROJECT",
                        "title": repo,
                        "evidence": s.get("evidence", "").strip(),
                        "skill": s.get("skill", "").strip(),
                        "type": s.get("type", "TECHNOLOGY").upper(),
                        "context": s.get("context", "required"),
                        "human_verify": "",
                        "human_corrected_skill": "",
                        "human_corrected_type": "",
                        "note": ""
                    })
            time.sleep(delay_sec)

    # 4. Xuất file Excel đa sheet
    output_dir = os.path.join("data", "gold", "annotations")
    os.makedirs(output_dir, exist_ok=True)
    excel_path = os.path.join(output_dir, "GEM_Golden_Set_Draft.xlsx")

    guideline_sheet_data = pd.DataFrame([
        {"Quy tắc": "Nhãn TECHNOLOGY", "Chi tiết": "Ngôn ngữ, Framework, DB, Cloud, Tool DevOps, Protocol, API. Ví dụ: Python, React, PostgreSQL, Docker."},
        {"Quy tắc": "Nhãn ABILITY", "Chi tiết": "Hành động kỹ thuật: [Động từ] + [Đối tượng]. Ví dụ: phát triển REST API, thiết kế CSDL, viết unit test."},
        {"Quy tắc": "Minimal Meaningful Span", "Chi tiết": "Tuyệt đối bỏ từ đệm (thành thạo, có kinh nghiệm, hiểu biết, proficient in...). Giữ ranh giới lõi."},
        {"Quy tắc": "Evidence Preservation", "Chi tiết": "Evidence phải là chuỗi con 100% trong văn bản gốc. Chuẩn hóa tên vào cột skill."},
        {"Quy tắc": "Negative Rules", "Chi tiết": "KHÔNG gán: Job Title (Backend Dev), Tên cty (FPT), Phúc lợi (BHXH, ăn trưa), Soft skills chung chung."},
        {"Quy tắc": "Cột human_verify", "Chi tiết": "ACCEPT = Đồng ý | REJECT = Bỏ (do ảo giác, từ thừa, chức danh) | MODIFY = Đúng nhưng cần sửa type/tên."}
    ])

    df_skills = pd.DataFrame(extracted_records)
    df_sources = pd.DataFrame(source_docs)

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df_skills.to_excel(writer, sheet_name="Skills_To_Verify", index=False)
        df_sources.to_excel(writer, sheet_name="Source_Documents", index=False)
        guideline_sheet_data.to_excel(writer, sheet_name="Guideline_Summary", index=False)

    print("\n" + "=" * 70)
    print(f"🎉 XUẤT FILE HOÀN TẤT: {excel_path}")
    print(f"📌 Tổng số văn bản nguồn: {len(df_sources)} tài liệu")
    print(f"📌 Tổng số candidate skills trích xuất: {len(df_skills)} kỹ năng")
    print("👉 Người thẩm định mở file Excel, đọc văn bản ở sheet 'Source_Documents' và duyệt ở sheet 'Skills_To_Verify'.")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tạo bản nháp Golden Set cho GEM")
    parser.add_argument("--jds", type=int, default=15, help="Số lượng JD lấy mẫu (mặc định: 15)")
    parser.add_argument("--projs", type=int, default=5, help="Số lượng Project lấy mẫu (mặc định: 5)")
    parser.add_argument("--delay", type=float, default=0.5, help="Thời gian chờ giữa các request (giây)")
    args = parser.parse_args()

    build_golden_set_draft(jd_limit=args.jds, project_limit=args.projs, delay_sec=args.delay)