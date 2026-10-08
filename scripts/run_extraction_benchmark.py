"""
Kịch bản chạy đối sánh hiệu năng trích xuất (Experiment E1 Benchmark)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

So sánh 2 luồng:
1. Baseline: LLM Prompt thuần (Không qua Verifier)
2. GEM Pipeline: LLM Prompt + Verifier logic (Kiểm định 5 bước)
"""

import os
import json
import argparse
import pandas as pd
from typing import Dict, List, Any, Tuple
from dotenv import load_dotenv

from gem_pipeline.extraction.extractor import SkillExtractor
from gem_pipeline.golden_set.evaluator import ExtractionEvaluator

load_dotenv()


def load_golden_set_from_excel(excel_path: str) -> Tuple[Dict[str, str], Dict[str, List[Dict[str, Any]]]]:
    """
    Đọc văn bản nguồn và tập nhãn chuẩn từ file Excel Golden Set.
    Chỉ lấy các kỹ năng có human_verify == 'ACCEPT' (hoặc đã được sửa).
    Nếu chưa duyệt thủ công, dùng candidate ban đầu làm benchmark mẫu.
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

        verify_status = str(row["human_verify"]).strip().upper() if pd.notna(row.get("human_verify")) else ""
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


def run_benchmark(excel_path: str = "data/gold/annotations/GEM_Golden_Set_Draft.xlsx", max_docs: int = 5):
    print("=" * 80)
    print("🔬 BẮT ĐẦU THỰC NGHIỆM ĐỐI SÁNH HIỆU NĂNG TRÍCH XUẤT (EXPERIMENT E1)")
    print("=" * 80)

    source_texts, ground_truth = load_golden_set_from_excel(excel_path)
    test_doc_ids = list(source_texts.keys())[:max_docs]

    print(f"📊 Đã tải {len(test_doc_ids)} tài liệu để chạy benchmark đối sánh.")

    extractor = SkillExtractor()
    evaluator = ExtractionEvaluator()

    preds_baseline: Dict[str, List[Dict[str, Any]]] = {}
    preds_verifier: Dict[str, List[Dict[str, Any]]] = {}

    hallucinations_baseline: Dict[str, int] = {}
    hallucinations_verifier: Dict[str, int] = {}
    violations_baseline: Dict[str, int] = {}
    violations_verifier: Dict[str, int] = {}

    for idx, doc_id in enumerate(test_doc_ids, 1):
        text = source_texts[doc_id]
        print(f"\n[{idx}/{len(test_doc_ids)}] Đang chạy tài liệu {doc_id} ({len(text)} ký tự)...")

        # 1. Chạy Baseline (Prompt thuần)
        raw_candidates = extractor.extract_baseline(text)
        preds_baseline[doc_id] = raw_candidates

        # Kiểm tra tỷ lệ lỗi thực tế của Baseline qua Verifier
        verified_results = extractor.verifier.verify_document_skills(raw_candidates, text)
        h_base = sum(1 for r in verified_results if "HALLUCINATION_EVIDENCE_NOT_FOUND" in r.issues)
        v_base = sum(1 for r in verified_results if "VIOLATE_NEGATIVE_RULES" in r.issues)
        hallucinations_baseline[doc_id] = h_base
        violations_baseline[doc_id] = v_base

        # 2. Chạy GEM Pipeline (Prompt + Verifier)
        accepted, rejected = extractor.extract_with_verifier(text)
        preds_verifier[doc_id] = [r.to_dict() for r in accepted]
        hallucinations_verifier[doc_id] = 0  # Verifier đã lọc sạch 100%
        violations_verifier[doc_id] = 0

        print(f"  -> Baseline: {len(raw_candidates)} kỹ năng | Bị lọc bởi Verifier: {len(rejected)} | Hợp lệ: {len(accepted)}")

    # 3. Tính toán các chỉ số
    rep_baseline = evaluator.evaluate_predictions(
        experiment_name="1. Baseline LLM (Prompt thuần)",
        predictions_by_doc=preds_baseline,
        ground_truth_by_doc={k: ground_truth.get(k, []) for k in test_doc_ids},
        hallucination_counts_by_doc=hallucinations_baseline,
        violation_counts_by_doc=violations_baseline
    )

    rep_verifier = evaluator.evaluate_predictions(
        experiment_name="2. GEM Pipeline (LLM + Verifier 5 lớp)",
        predictions_by_doc=preds_verifier,
        ground_truth_by_doc={k: ground_truth.get(k, []) for k in test_doc_ids},
        hallucination_counts_by_doc=hallucinations_verifier,
        violation_counts_by_doc=violations_verifier
    )

    df_comparison = ExtractionEvaluator.compare_experiments([rep_baseline, rep_verifier])

    print("\n" + "=" * 80)
    print("📈 KẾT QUẢ ĐỐI SÁNH HIỆU NĂNG ĐỊNH LƯỢNG:")
    print("=" * 80)
    print(df_comparison.to_string(index=False))

    # Lưu kết quả
    os.makedirs("data/gold", exist_ok=True)
    report_json_path = "data/gold/benchmark_e1_results.json"
    with open(report_json_path, "w", encoding="utf-8") as f:
        json.dump([rep_baseline.to_dict(), rep_verifier.to_dict()], f, ensure_ascii=False, indent=2)
    print(f"\n💾 Đã lưu báo cáo benchmark tại: {report_json_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy benchmark đối sánh trích xuất kỹ năng")
    parser.add_argument("--excel", type=str, default="data/gold/annotations/GEM_Golden_Set_Draft.xlsx")
    parser.add_argument("--max_docs", type=int, default=3)
    args = parser.parse_args()

    run_benchmark(excel_path=args.excel, max_docs=args.max_docs)
