"""
Kịch bản tạo tập Golden Set chuẩn hóa (Pre-annotation & Guideline Alignment) cho GEM
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
Mô hình Teacher: Gemini Cloud (gemini-3.5-flash-lite) độc lập theo Annotation Guideline v1.0
"""

import os
import sys
import json
import time
import argparse
import pandas as pd
from typing import Dict, List, Any
from sqlalchemy import create_engine
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Thêm pipeline/src vào sys.path
pipeline_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline", "src"))
if pipeline_src not in sys.path:
    sys.path.insert(0, pipeline_src)

from gem_pipeline.extraction.extractor import SkillExtractor
from gem_pipeline.extraction.verifier import SkillExtractionVerifier

load_dotenv()


def get_db_uri() -> str:
    pg_user = os.getenv("POSTGRES_USER", "gem_admin")
    pg_pass = os.getenv("POSTGRES_PASSWORD", "gem_secret_password")
    pg_host = os.getenv("POSTGRES_HOST", "localhost")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_name = os.getenv("POSTGRES_DB", "gem_database")
    return f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_name}"


def load_checkpoint(checkpoint_path: str) -> Dict[str, Any]:
    if os.path.exists(checkpoint_path):
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"  ⚠ Không thể đọc checkpoint ({e}), bắt đầu mới.")
    return {"source_docs": [], "extracted_records": [], "processed_ids": []}


def save_checkpoint(checkpoint_path: str, data: Dict[str, Any]):
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
    with open(checkpoint_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def build_golden_set(
    jd_limit: int = 200,
    project_limit: int = 20,
    model_name: str = "gemini-3.5-flash-lite",
    backend: str = "gemini",
    delay_sec: float = 0.5,
    resume: bool = True,
    output_prefix: str = "GEM_Golden_Set_200JDs"
):
    print("=" * 80)
    print("🚀 BẮT ĐẦU TẠO TẬP NHÃN VÀNG ĐỘC LẬP (INDEPENDENT GOLDEN SET GENERATOR)")
    print(f"📊 Mục tiêu: {jd_limit} JDs tuyển dụng (~10% dataset) | {project_limit} Đồ án sinh viên")
    print(f"🤖 Teacher LLM Engine: {model_name} (Backend: {backend})")
    print("=" * 80)

    engine = create_engine(get_db_uri())
    extractor = SkillExtractor(backend=backend, gemini_models=[model_name, "gemini-3.8-flash", "gemini-flash-latest"])
    verifier = SkillExtractionVerifier()

    output_dir = os.path.join("data", "gold", "annotations")
    os.makedirs(output_dir, exist_ok=True)
    checkpoint_file = os.path.join(output_dir, f"{output_prefix.lower()}_checkpoint.json")
    excel_output = os.path.join(output_dir, f"{output_prefix}.xlsx")

    ckpt = load_checkpoint(checkpoint_file) if resume else {"source_docs": [], "extracted_records": [], "processed_ids": []}
    source_docs = ckpt["source_docs"]
    extracted_records = ckpt["extracted_records"]
    processed_ids = set(ckpt["processed_ids"])

    print(f"🔄 Checkpoint: Đã xử lý {len(processed_ids)} tài liệu trước đó.")

    # 1. Lấy mẫu phân tầng từ cleaned_job_postings
    print("\n[1/3] Đang tải danh sách cleaned_job_postings từ PostgreSQL...")
    jd_query = f"""
        SELECT id, raw_job_id, title, company, content_clean
        FROM cleaned_job_postings
        WHERE char_count >= 250
        ORDER BY id ASC
        LIMIT {jd_limit};
    """
    df_jds = pd.read_sql(jd_query, engine)
    print(f"✅ Đã chọn {len(df_jds)} JD tuyển dụng.")

    # 2. Lấy mẫu từ cleaned_github_projects
    print("\n[2/3] Đang tải danh sách cleaned_github_projects từ PostgreSQL...")
    proj_query = f"""
        SELECT id, raw_project_id, repo_name, author, combined_clean_text
        FROM cleaned_github_projects
        WHERE char_count >= 150
        ORDER BY id ASC
        LIMIT {project_limit};
    """
    df_projs = pd.read_sql(proj_query, engine)
    print(f"✅ Đã chọn {len(df_projs)} đồ án GitHub.")

    # 3. Trích xuất và Thẩm định theo Guideline
    total_docs = len(df_jds) + len(df_projs)
    current_count = len(processed_ids)

    # 3.1 Xử lý JDs
    for idx, row in df_jds.iterrows():
        doc_id = f"JD_{row['id']}"
        if doc_id in processed_ids:
            continue

        current_count += 1
        title = row.get("title", "")
        content = (row.get("content_clean") or "").strip()
        if len(content) > 3500:
            content = content[:3500]
        print(f"\n[{current_count}/{total_docs}] Đang xử lý {doc_id}: {title[:50]}... ({len(content)} ký tự)", flush=True)

        t0 = time.time()
        # Gọi Teacher Prompt chuẩn Guideline
        raw_candidates = extractor.extract_baseline(content, prompt_type="guideline")
        t_el = time.time() - t0

        verified_results = verifier.verify_document_skills(raw_candidates, content)
        accepted_count = sum(1 for v in verified_results if v.is_valid)
        print(f"  ⏱ Thời gian: {t_el:.1f}s | Trích xuất: {len(raw_candidates)} | Hợp lệ (ACCEPT): {accepted_count} | Loại (REJECT): {len(verified_results) - accepted_count}")

        source_docs.append({
            "doc_id": doc_id,
            "doc_type": "JOB_POSTING",
            "title": title,
            "author_or_company": row.get("company", ""),
            "char_count": len(content),
            "content_clean": content,
            "missing_skills_added": ""
        })

        for v in verified_results:
            extracted_records.append({
                "doc_id": doc_id,
                "doc_type": "JOB_POSTING",
                "title": title,
                "evidence": v.evidence,
                "skill": v.skill,
                "type": v.type,
                "context": v.context,
                "start_char": v.start_char if v.start_char is not None else "",
                "end_char": v.end_char if v.end_char is not None else "",
                "human_verify": "ACCEPT" if v.is_valid else "REJECT",
                "human_corrected_skill": "",
                "human_corrected_type": "",
                "note": "Auto-verified: " + (", ".join(v.issues) if v.issues else "Passed 5-layer verifier") if v.is_valid else f"Auto-rejected: {v.rejection_reason}"
            })

        processed_ids.add(doc_id)
        ckpt = {
            "source_docs": source_docs,
            "extracted_records": extracted_records,
            "processed_ids": list(processed_ids)
        }
        save_checkpoint(checkpoint_file, ckpt)
        time.sleep(delay_sec)

    # 3.2 Xử lý Projects
    for idx, row in df_projs.iterrows():
        doc_id = f"GH_{row['id']}"
        if doc_id in processed_ids:
            continue

        current_count += 1
        repo = row.get("repo_name", "")
        content = (row.get("combined_clean_text") or "").strip()
        if len(content) > 3500:
            content = content[:3500]
        print(f"\n[{current_count}/{total_docs}] Đang xử lý {doc_id}: {repo[:50]}... ({len(content)} ký tự)", flush=True)

        t0 = time.time()
        raw_candidates = extractor.extract_baseline(content, prompt_type="guideline")
        t_el = time.time() - t0

        verified_results = verifier.verify_document_skills(raw_candidates, content)
        accepted_count = sum(1 for v in verified_results if v.is_valid)
        print(f"  ⏱ Thời gian: {t_el:.1f}s | Trích xuất: {len(raw_candidates)} | Hợp lệ (ACCEPT): {accepted_count} | Loại (REJECT): {len(verified_results) - accepted_count}")

        source_docs.append({
            "doc_id": doc_id,
            "doc_type": "GITHUB_PROJECT",
            "title": repo,
            "author_or_company": row.get("author", ""),
            "char_count": len(content),
            "content_clean": content,
            "missing_skills_added": ""
        })

        for v in verified_results:
            extracted_records.append({
                "doc_id": doc_id,
                "doc_type": "GITHUB_PROJECT",
                "title": repo,
                "evidence": v.evidence,
                "skill": v.skill,
                "type": v.type,
                "context": v.context,
                "start_char": v.start_char if v.start_char is not None else "",
                "end_char": v.end_char if v.end_char is not None else "",
                "human_verify": "ACCEPT" if v.is_valid else "REJECT",
                "human_corrected_skill": "",
                "human_corrected_type": "",
                "note": "Auto-verified: " + (", ".join(v.issues) if v.issues else "Passed 5-layer verifier") if v.is_valid else f"Auto-rejected: {v.rejection_reason}"
            })

        processed_ids.add(doc_id)
        ckpt = {
            "source_docs": source_docs,
            "extracted_records": extracted_records,
            "processed_ids": list(processed_ids)
        }
        save_checkpoint(checkpoint_file, ckpt)
        time.sleep(delay_sec)

    # 4. Xuất file Excel Golden Set
    print("\n[4/4] Đang tổng hợp và xuất file Excel...")
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

    target_excel = excel_output
    try:
        with pd.ExcelWriter(target_excel, engine="openpyxl") as writer:
            df_skills.to_excel(writer, sheet_name="Skills_To_Verify", index=False)
            df_sources.to_excel(writer, sheet_name="Source_Documents", index=False)
            guideline_sheet_data.to_excel(writer, sheet_name="Guideline_Summary", index=False)
    except PermissionError:
        print(f"\n  ⚠ Cảnh báo: File '{excel_output}' đang được mở bởi ứng dụng khác.")
        target_excel = excel_output.replace(".xlsx", "_latest.xlsx")
        print(f"  📁 Tự động xuất ra file thay thế: {target_excel}")
        with pd.ExcelWriter(target_excel, engine="openpyxl") as writer:
            df_skills.to_excel(writer, sheet_name="Skills_To_Verify", index=False)
            df_sources.to_excel(writer, sheet_name="Source_Documents", index=False)
            guideline_sheet_data.to_excel(writer, sheet_name="Guideline_Summary", index=False)

    print("\n" + "=" * 80)
    print(f"🎉 XUẤT TẬP NHÃN VÀNG THÀNH CÔNG: {target_excel}")
    print(f"📌 Tổng số văn bản nguồn: {len(df_sources)} tài liệu ({len(df_jds)} JD, {len(df_projs)} Projects)")
    print(f"📌 Tổng số bản ghi kỹ năng: {len(df_skills)} kỹ năng")
    acc_count = len(df_skills[df_skills["human_verify"] == "ACCEPT"])
    rej_count = len(df_skills[df_skills["human_verify"] == "REJECT"])
    print(f"  ✅ Đạt chuẩn Guideline (ACCEPT): {acc_count} ({acc_count/max(len(df_skills),1)*100:.1f}%)")
    print(f"  ❌ Bị lọc bởi 5-Layer Verifier (REJECT): {rej_count} ({rej_count/max(len(df_skills),1)*100:.1f}%)")
    print("=" * 80)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tạo tập Golden Set chuẩn hóa cho GEM")
    parser.add_argument("--jds", type=int, default=200, help="Số lượng JD lấy mẫu (mặc định: 200)")
    parser.add_argument("--projs", type=int, default=80, help="Số lượng Project lấy mẫu (mặc định: 80)")
    parser.add_argument("--model", type=str, default="gemini-3.5-flash-lite", help="Tên model LLM (mặc định: gemini-3.5-flash-lite)")
    parser.add_argument("--backend", type=str, default="gemini", help="Backend (gemini / ollama)")
    parser.add_argument("--delay", type=float, default=0.3, help="Thời gian chờ giữa các request (giây)")
    parser.add_argument("--no-resume", action="store_true", help="Không dùng checkpoint cũ, tạo lại từ đầu")
    parser.add_argument("--output-prefix", type=str, default="GEM_Golden_Set_280Docs", help="Tiền tố file xuất")
    args = parser.parse_args()

    build_golden_set(
        jd_limit=args.jds,
        project_limit=args.projs,
        model_name=args.model,
        backend=args.backend,
        delay_sec=args.delay,
        resume=not args.no_resume,
        output_prefix=args.output_prefix
    )