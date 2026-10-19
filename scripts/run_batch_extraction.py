"""
Kịch bản trích xuất kỹ năng hàng loạt (Full Corpus Batch Extraction)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Trích xuất toàn bộ kho dữ liệu:
- 700 cleaned_job_postings
- 292 cleaned_github_projects
Lưu trữ trực tiếp vào bảng 'extracted_skills' trong PostgreSQL.
Hỗ trợ tái sử dụng 120 tài liệu đã có trong Golden Set để tiết kiệm thời gian.
"""

import os
import sys
import json
import time
import argparse
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Đảm bảo Windows console UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Thêm pipeline/src vào sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pipeline", "src"))

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


def init_extracted_skills_table(engine):
    """Khởi tạo bảng extracted_skills trong PostgreSQL nếu chưa tồn tại."""
    ddl = """
    CREATE TABLE IF NOT EXISTS extracted_skills (
        id SERIAL PRIMARY KEY,
        source_type VARCHAR(20) NOT NULL,      -- 'job' hoặc 'project'
        source_id VARCHAR(50) NOT NULL,        -- id gốc từ bảng cleaned
        doc_id VARCHAR(50) NOT NULL,           -- JD_123 hoặc GH_45
        title TEXT,
        evidence TEXT NOT NULL,
        skill TEXT NOT NULL,
        type VARCHAR(20) NOT NULL,             -- 'TECHNOLOGY' hoặc 'ABILITY'
        context VARCHAR(20) DEFAULT 'required',
        start_char INTEGER,
        end_char INTEGER,
        verifier_status VARCHAR(20) NOT NULL,  -- 'ACCEPT' hoặc 'REJECT'
        rejection_reason TEXT,
        model_name VARCHAR(50) DEFAULT 'qwen2.5:7b',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_extracted_skills_doc_id ON extracted_skills(doc_id);
    CREATE INDEX IF NOT EXISTS idx_extracted_skills_type ON extracted_skills(type);
    CREATE INDEX IF NOT EXISTS idx_extracted_skills_status ON extracted_skills(verifier_status);
    CREATE INDEX IF NOT EXISTS idx_extracted_skills_skill ON extracted_skills(skill);
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))
    print("✅ Đã khởi tạo bảng 'extracted_skills' và các chỉ mục trong PostgreSQL.")


def preload_golden_set_skills(engine, excel_path: str = "data/gold/annotations/GEM_Golden_Set_280Docs.xlsx") -> set:
    """Nạp sẵn các kỹ năng đã trích xuất từ tệp Golden Set để bỏ qua các tài liệu đã làm."""
    if not os.path.exists(excel_path):
        for alt in ["data/gold/annotations/GEM_Golden_Set_280Docs.xlsx", "data/gold/annotations/GEM_Golden_Set_200JDs.xlsx", "data/gold/annotations/GEM_Golden_Set_100JDs.xlsx"]:
            if os.path.exists(alt):
                excel_path = alt
                break
    if not os.path.exists(excel_path):
        return set()

    print(f"📦 Đang nạp trước dữ liệu từ tệp Golden Set: {excel_path}...")
    df_skills = pd.read_excel(excel_path, sheet_name="Skills_To_Verify")
    
    # Kiểm tra xem những doc_id nào đã có trong extracted_skills
    with engine.connect() as conn:
        existing_docs = set(conn.execute(text("SELECT DISTINCT doc_id FROM extracted_skills")).scalars().all())

    records_to_insert = []
    processed_doc_ids = set()

    for _, row in df_skills.iterrows():
        doc_id = str(row["doc_id"])
        processed_doc_ids.add(doc_id)
        if doc_id in existing_docs:
            continue

        raw_skill = str(row["skill"]).strip() if pd.notna(row.get("skill")) else ""
        raw_type = str(row["type"]).strip().upper() if pd.notna(row.get("type")) else "TECHNOLOGY"
        evidence = str(row["evidence"]).strip() if pd.notna(row.get("evidence")) else raw_skill
        v_status = str(row.get("human_verify", "ACCEPT")).strip().upper()
        
        s_type = "job" if doc_id.startswith("JD_") else "project"
        s_id = doc_id.replace("JD_", "").replace("GH_", "")

        records_to_insert.append({
            "source_type": s_type,
            "source_id": s_id,
            "doc_id": doc_id,
            "title": str(row.get("title", "")),
            "evidence": evidence,
            "skill": raw_skill,
            "type": raw_type,
            "context": str(row.get("context", "required")),
            "start_char": int(row["start_char"]) if pd.notna(row.get("start_char")) and str(row.get("start_char")).isdigit() else None,
            "end_char": int(row["end_char"]) if pd.notna(row.get("end_char")) and str(row.get("end_char")).isdigit() else None,
            "verifier_status": v_status,
            "rejection_reason": str(row.get("note", "")) if v_status == "REJECT" else None,
            "model_name": "qwen2.5:7b"
        })

    if records_to_insert:
        df_insert = pd.DataFrame(records_to_insert)
        df_insert.to_sql("extracted_skills", engine, if_exists="append", index=False)
        print(f"🎉 Đã nạp thành công {len(records_to_insert)} bản ghi kỹ năng của {len(processed_doc_ids)} tài liệu Golden Set vào Database!")
    else:
        print(f"ℹ️ {len(processed_doc_ids)} tài liệu Golden Set đã tồn tại trong database, bỏ qua nạp trùng.")

    return processed_doc_ids


def run_full_extraction(
    model_name: str = "qwen2.5:7b",
    backend: str = "ollama",
    batch_size: int = 10,
    delay_sec: float = 0.2
):
    print("=" * 80)
    print("🚀 BẮT ĐẦU TRÍCH XUẤT TOÀN BỘ KHO DỮ LIỆU GEM (FULL CORPUS EXTRACTION)")
    print(f"🤖 Mô hình: {model_name} (Backend: {backend})")
    print("=" * 80)

    engine = create_engine(get_db_uri())
    init_extracted_skills_table(engine)

    # 1. Nạp trước 120 tài liệu đã có
    preloaded_docs = preload_golden_set_skills(engine)

    # Lấy danh sách doc_id đã có trong database
    with engine.connect() as conn:
        already_extracted = set(conn.execute(text("SELECT DISTINCT doc_id FROM extracted_skills")).scalars().all())

    extractor = SkillExtractor(backend=backend, ollama_model=model_name)
    verifier = SkillExtractionVerifier()

    # 2. Tải toàn bộ JDs cần trích xuất
    df_jds = pd.read_sql("""
        SELECT id, raw_job_id, title, company, content_clean
        FROM cleaned_job_postings
        WHERE char_count >= 100
        ORDER BY id ASC;
    """, engine)

    # 3. Tải toàn bộ Projects cần trích xuất
    df_projs = pd.read_sql("""
        SELECT id, raw_project_id, repo_name, author, combined_clean_text
        FROM cleaned_github_projects
        WHERE char_count >= 100
        ORDER BY id ASC;
    """, engine)

    pending_jds = [row for _, row in df_jds.iterrows() if f"JD_{row['id']}" not in already_extracted]
    pending_projs = [row for _, row in df_projs.iterrows() if f"GH_{row['id']}" not in already_extracted]

    total_pending = len(pending_jds) + len(pending_projs)
    print(f"\n📊 Tổng quan dữ liệu:")
    print(f"  - JD Tuyển dụng: Tổng {len(df_jds)} | Đã có: {len(df_jds) - len(pending_jds)} | Cần xử lý: {len(pending_jds)}")
    print(f"  - Đồ án GitHub: Tổng {len(df_projs)} | Đã có: {len(df_projs) - len(pending_projs)} | Cần xử lý: {len(pending_projs)}")
    print(f"  - Tổng số tài liệu cần trích xuất mới: {total_pending}")

    if total_pending == 0:
        print("\n🎉 Toàn bộ dữ liệu đã được trích xuất đầy đủ trong database!")
        return

    processed_count = 0
    buffer_records = []

    def flush_buffer(records):
        if not records:
            return
        df_buf = pd.DataFrame(records)
        if "context" in df_buf.columns:
            df_buf["context"] = df_buf["context"].astype(str).str.slice(0, 250)
        if "type" in df_buf.columns:
            df_buf["type"] = df_buf["type"].astype(str).str.slice(0, 95)
        if "source_type" in df_buf.columns:
            df_buf["source_type"] = df_buf["source_type"].astype(str).str.slice(0, 45)
        if "verifier_status" in df_buf.columns:
            df_buf["verifier_status"] = df_buf["verifier_status"].astype(str).str.slice(0, 45)
        df_buf.to_sql("extracted_skills", engine, if_exists="append", index=False)
        records.clear()

    # Xử lý JDs
    for row in pending_jds:
        doc_id = f"JD_{row['id']}"
        title = row.get("title", "")
        content = (row.get("content_clean") or "").strip()
        if len(content) > 3500:
            content = content[:3500]

        processed_count += 1
        print(f"\n[{processed_count}/{total_pending}] Đang xử lý {doc_id}: {title[:40]}... ({len(content)} ký tự)", flush=True)

        t0 = time.time()
        raw_candidates = extractor.extract_baseline(content, prompt_type="student")
        t_el = time.time() - t0

        verified_results = verifier.verify_document_skills(raw_candidates, content)
        acc_cnt = sum(1 for v in verified_results if v.is_valid)
        rej_cnt = len(verified_results) - acc_cnt

        print(f"  ⏱ {t_el:.1f}s | Trích xuất: {len(raw_candidates)} | ACCEPT: {acc_cnt} | REJECT: {rej_cnt}", flush=True)

        for v in verified_results:
            buffer_records.append({
                "source_type": "job",
                "source_id": str(row["id"]),
                "doc_id": doc_id,
                "title": title,
                "evidence": v.evidence,
                "skill": v.skill,
                "type": v.type,
                "context": v.context,
                "start_char": v.start_char,
                "end_char": v.end_char,
                "verifier_status": "ACCEPT" if v.is_valid else "REJECT",
                "rejection_reason": v.rejection_reason if not v.is_valid else None,
                "model_name": model_name
            })

        if len(buffer_records) >= 20:
            flush_buffer(buffer_records)

        time.sleep(delay_sec)

    # Xử lý Projects
    for row in pending_projs:
        doc_id = f"GH_{row['id']}"
        repo = row.get("repo_name", "")
        content = (row.get("combined_clean_text") or "").strip()
        if len(content) > 3500:
            content = content[:3500]

        processed_count += 1
        print(f"\n[{processed_count}/{total_pending}] Đang xử lý {doc_id}: {repo[:40]}... ({len(content)} ký tự)", flush=True)

        t0 = time.time()
        raw_candidates = extractor.extract_baseline(content, prompt_type="student")
        t_el = time.time() - t0

        verified_results = verifier.verify_document_skills(raw_candidates, content)
        acc_cnt = sum(1 for v in verified_results if v.is_valid)
        rej_cnt = len(verified_results) - acc_cnt

        print(f"  ⏱ {t_el:.1f}s | Trích xuất: {len(raw_candidates)} | ACCEPT: {acc_cnt} | REJECT: {rej_cnt}", flush=True)

        for v in verified_results:
            buffer_records.append({
                "source_type": "project",
                "source_id": str(row["id"]),
                "doc_id": doc_id,
                "title": repo,
                "evidence": v.evidence,
                "skill": v.skill,
                "type": v.type,
                "context": v.context,
                "start_char": v.start_char,
                "end_char": v.end_char,
                "verifier_status": "ACCEPT" if v.is_valid else "REJECT",
                "rejection_reason": v.rejection_reason if not v.is_valid else None,
                "model_name": model_name
            })

        if len(buffer_records) >= 20:
            flush_buffer(buffer_records)

        time.sleep(delay_sec)

    # Ghi nốt phần còn lại
    flush_buffer(buffer_records)

    with engine.connect() as conn:
        total_in_db = conn.execute(text("SELECT count(*) FROM extracted_skills")).scalar()
        total_acc = conn.execute(text("SELECT count(*) FROM extracted_skills WHERE verifier_status='ACCEPT'")).scalar()

    print("\n" + "=" * 80)
    print(f"🎉 HOÀN TẤT TRÍCH XUẤT TOÀN BỘ DỮ LIỆU!")
    print(f"📌 Tổng số bản ghi trong bảng 'extracted_skills': {total_in_db}")
    print(f"  ✅ Kỹ năng đạt chuẩn (ACCEPT): {total_acc} ({total_acc/max(total_in_db,1)*100:.1f}%)")
    print("=" * 80)

    # Đồng bộ ra tệp seed data/processed/skills/extracted_skills.jsonl
    print("\n📦 Đang đồng bộ bảng 'extracted_skills' ra tệp data/processed/skills/extracted_skills.jsonl...")
    df_all_skills = pd.read_sql("SELECT * FROM extracted_skills ORDER BY id ASC;", engine)
    out_dir = os.path.join("data", "processed", "skills")
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "extracted_skills.jsonl")
    df_all_skills.to_json(out_file, orient="records", lines=True, force_ascii=False)
    print(f"✅ Đã ghi {len(df_all_skills)} bản ghi vào {out_file}")

    # Làm giàu và cập nhật vào Qdrant
    print("\n🚀 Đang cập nhật dữ liệu và kỹ năng vào Qdrant Vector Store...")
    try:
        from gem_pipeline.vector_store.qdrant_service import QdrantVectorService
        qs = QdrantVectorService()
        qs.index_all_jds()
        qs.index_all_projects()
        print("✅ Hoàn tất đồng bộ Qdrant với đầy đủ Vector BGE-M3 và nhãn kỹ năng!")
    except Exception as e:
        print(f"⚠ Lỗi khi cập nhật Qdrant: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy trích xuất hàng loạt toàn bộ kho dữ liệu GEM")
    parser.add_argument("--model", type=str, default="qwen2.5:7b", help="Mô hình trích xuất (mặc định: qwen2.5:7b)")
    parser.add_argument("--backend", type=str, default="ollama", help="Backend (ollama / gemini)")
    args = parser.parse_args()

    run_full_extraction(model_name=args.model, backend=args.backend)
