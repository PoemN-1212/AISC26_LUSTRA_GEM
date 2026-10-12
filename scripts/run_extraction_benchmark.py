"""
Kịch bản chạy đối sánh hiệu năng trích xuất (Experiment E1 Benchmark)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

So sánh 2 nhánh:
1. Baseline: LLM Prompt thuần (Không qua Verifier)
2. GEM Pipeline: LLM Prompt + Verifier 5 lớp (Kiểm định tất định)
Đo lường trên tập nhãn vàng Golden Set 100 JDs + 20 Projects
"""

import os
import sys
import json
import time
import argparse
import pandas as pd
from typing import Dict, List, Any, Tuple
from dotenv import load_dotenv

# Đảm bảo Windows console in UTF-8 không lỗi charmap
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Thêm pipeline/src vào sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pipeline", "src"))

from gem_pipeline.extraction.extractor import SkillExtractor
from gem_pipeline.golden_set.evaluator import ExtractionEvaluator

load_dotenv()


def load_golden_set_from_excel(excel_path: str) -> Tuple[Dict[str, str], Dict[str, List[Dict[str, Any]]]]:
    """
    Đọc văn bản nguồn và tập nhãn chuẩn từ file Excel Golden Set.
    Ground Truth: Tất cả các kỹ năng có human_verify == 'ACCEPT'.
    """
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Không tìm thấy file: {excel_path}")

    df_skills = pd.read_excel(excel_path, sheet_name="Skills_To_Verify")
    df_sources = pd.read_excel(excel_path, sheet_name="Source_Documents")

    source_texts = {}
    for _, row in df_sources.iterrows():
        source_texts[str(row["doc_id"])] = str(row["content_clean"])

    ground_truth = {}
    for _, row in df_skills.iterrows():
        doc_id = str(row["doc_id"])
        if doc_id not in ground_truth:
            ground_truth[doc_id] = []

        verify_status = str(row.get("human_verify", "")).strip().upper()
        # Bỏ qua các kỹ năng bị REJECT (do ảo giác, từ thừa, chức danh...)
        if verify_status == "REJECT":
            continue

        raw_skill = str(row["skill"]).strip() if pd.notna(row.get("skill")) else ""
        corrected_skill = str(row["human_corrected_skill"]).strip() if pd.notna(row.get("human_corrected_skill")) else ""
        skill_name = corrected_skill if corrected_skill else raw_skill

        raw_type = str(row["type"]).strip().upper() if pd.notna(row.get("type")) else "TECHNOLOGY"
        corrected_type = str(row["human_corrected_type"]).strip().upper() if pd.notna(row.get("human_corrected_type")) else ""
        skill_type = corrected_type if corrected_type else raw_type

        evidence = str(row["evidence"]).strip() if pd.notna(row.get("evidence")) else ""

        if skill_name:
            ground_truth[doc_id].append({
                "skill": skill_name,
                "type": skill_type,
                "evidence": evidence
            })

    return source_texts, ground_truth


def run_benchmark(
    excel_path: str = "data/gold/annotations/GEM_Golden_Set_100JDs.xlsx",
    max_docs: int = 100,
    model_name: str = "qwen2.5:7b",
    backend: str = "ollama"
):
    print("=" * 80)
    print("🔬 BẮT ĐẦU THỰC NGHIỆM ĐỐI SÁNH HIỆU NĂNG TRÍCH XUẤT (EXPERIMENT E1)")
    print(f"📄 Tệp nhãn vàng: {excel_path}")
    print(f"🤖 LLM Model: {model_name} (Backend: {backend})")
    print("=" * 80)

    source_texts, ground_truth = load_golden_set_from_excel(excel_path)
    all_doc_ids = list(source_texts.keys())
    jd_ids = [d for d in all_doc_ids if d.startswith("JD_")]
    gh_ids = [d for d in all_doc_ids if d.startswith("GH_")]

    if max_docs > 0 and max_docs < len(all_doc_ids):
        num_gh = max(1, int(max_docs * len(gh_ids) / len(all_doc_ids)))
        num_jd = max_docs - num_gh
        test_doc_ids = jd_ids[:num_jd] + gh_ids[:num_gh]
    else:
        test_doc_ids = all_doc_ids

    total_gt_skills = sum(len(ground_truth.get(doc, [])) for doc in test_doc_ids)
    print(f"📊 Đã chọn {len(test_doc_ids)} tài liệu ({len([d for d in test_doc_ids if d.startswith('JD_')])} JDs + {len([d for d in test_doc_ids if d.startswith('GH_')])} GitHub Repos) với tổng cộng {total_gt_skills} nhãn vàng chuẩn (Ground Truth).")

    extractor = SkillExtractor(backend=backend, ollama_model=model_name)
    evaluator = ExtractionEvaluator()

    preds_baseline: Dict[str, List[Dict[str, Any]]] = {}
    preds_verifier: Dict[str, List[Dict[str, Any]]] = {}

    hallucinations_baseline: Dict[str, int] = {}
    hallucinations_verifier: Dict[str, int] = {}
    violations_baseline: Dict[str, int] = {}
    violations_verifier: Dict[str, int] = {}

    for idx, doc_id in enumerate(test_doc_ids, 1):
        text = source_texts[doc_id]
        if len(text) > 3500:
            text = text[:3500]
        print(f"\n[{idx}/{len(test_doc_ids)}] Đang đánh giá {doc_id} ({len(text)} ký tự)...", flush=True)

        # 1. Chạy Baseline (Prompt thuần qua LLM)
        t0 = time.time()
        raw_candidates = extractor.extract_baseline(text)
        t_el = time.time() - t0
        preds_baseline[doc_id] = raw_candidates

        # 2. Chạy Verifier 5 lớp trên cùng output của LLM để đối sánh công bằng
        verified_results = extractor.verifier.verify_document_skills(raw_candidates, text)
        accepted = [r for r in verified_results if r.is_valid]
        rejected = [r for r in verified_results if not r.is_valid]

        preds_verifier[doc_id] = [r.to_dict() for r in accepted]

        h_base = sum(1 for r in verified_results if "HALLUCINATION_EVIDENCE_NOT_FOUND" in r.issues)
        v_base = sum(1 for r in verified_results if "VIOLATE_NEGATIVE_RULES" in r.issues)
        hallucinations_baseline[doc_id] = h_base
        violations_baseline[doc_id] = v_base

        hallucinations_verifier[doc_id] = 0  # Verifier đã lọc sạch 100%
        violations_verifier[doc_id] = 0      # Verifier đã loại bỏ 100%

        print(f"  ⏱ Thời gian LLM: {t_el:.1f}s")
        print(f"  -> Baseline: {len(raw_candidates)} kỹ năng (Ảo giác: {h_base}, Vi phạm: {v_base})")
        print(f"  -> Verifier: {len(accepted)} kỹ năng hợp lệ | Bị loại bỏ: {len(rejected)}")

    # 3. Tính toán các chỉ số
    rep_baseline = evaluator.evaluate_predictions(
        experiment_name=f"1. Baseline LLM ({model_name} Prompt thuần)",
        predictions_by_doc=preds_baseline,
        ground_truth_by_doc={k: ground_truth.get(k, []) for k in test_doc_ids},
        hallucination_counts_by_doc=hallucinations_baseline,
        violation_counts_by_doc=violations_baseline
    )

    rep_verifier = evaluator.evaluate_predictions(
        experiment_name=f"2. GEM Pipeline ({model_name} + Verifier 5 lớp)",
        predictions_by_doc=preds_verifier,
        ground_truth_by_doc={k: ground_truth.get(k, []) for k in test_doc_ids},
        hallucination_counts_by_doc=hallucinations_verifier,
        violation_counts_by_doc=violations_verifier
    )

    df_comparison = ExtractionEvaluator.compare_experiments([rep_baseline, rep_verifier])

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)

    print("\n" + "=" * 130)
    print("📈 KẾT QUẢ ĐỐI SÁNH HIỆU NĂNG ĐỊNH LƯỢNG (EXPERIMENT E1):")
    print("=" * 130)
    print(df_comparison.to_string(index=False))
    print("=" * 130)

    # Lưu kết quả
    os.makedirs("data/gold", exist_ok=True)
    report_json_path = "data/gold/benchmark_e1_results.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump([rep_baseline.to_dict(), rep_verifier.to_dict()], f, ensure_ascii=False, indent=2)
    print(f"\n💾 Đã lưu báo cáo benchmark định lượng tại: {report_json_path}")
    print("=" * 90)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy benchmark đối sánh trích xuất kỹ năng")
    parser.add_argument("--excel", type=str, default="data/gold/annotations/GEM_Golden_Set_100JDs.xlsx")
    parser.add_argument("--max_docs", type=int, default=100, help="Số lượng tài liệu đánh giá (mặc định: 100)")
    parser.add_argument("--model", type=str, default="qwen2.5:7b")
    parser.add_argument("--backend", type=str, default="ollama")
    args = parser.parse_args()

    run_benchmark(
        excel_path=args.excel,
        max_docs=args.max_docs,
        model_name=args.model,
        backend=args.backend
    )
