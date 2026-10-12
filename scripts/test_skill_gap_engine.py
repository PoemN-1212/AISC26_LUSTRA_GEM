"""
Test Script for GEM Skill Gap Diagnosis & Actionable Plan Engine
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
"""

import sys
import os
import json

# Ensure pipeline/src is in sys.path
pipeline_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pipeline", "src"))
if pipeline_src not in sys.path:
    sys.path.insert(0, pipeline_src)

from gem_pipeline.recommendation.consultant import IdeationConsultant

def test_engine():
    print("=" * 70)
    print("KIỂM THỬ ĐỘNG CƠ CHẨN ĐOÁN & THU HẸP SKILL GAP (GEM AISC 2026)")
    print("=" * 70)

    consultant = IdeationConsultant()

    # Test Case 1: Web thương mại điện tử (Backend Developer)
    idea = "Tôi muốn xây dựng website thương mại điện tử cho các cửa hàng nhỏ, có quản lý sản phẩm, giỏ hàng, đặt hàng, thanh toán và thống kê doanh thu."
    print(f"\n[Test 1] Đề tài: {idea}")
    bp = consultant.generate_blueprint(idea, target_role="Backend Developer", time_months=3)

    gap = bp.get("skill_gap_report", {})
    metrics = bp.get("readiness_metrics", {})

    print(f"\n1. Vị trí mục tiêu: {bp.get('target_role')}")
    print(f"2. Mẫu JD TopCV phân tích: {gap.get('sample_jd_count')} JDs")
    print(f"3. Điểm Thực Chiến (Readiness Score): {metrics.get('readiness_score')}/100")
    print(f"   - Độ phù hợp ngữ nghĩa (Semantic Fit): {metrics.get('semantic_fit')}%")
    print(f"   - Độ phủ ban đầu (Baseline Coverage): {metrics.get('baseline_coverage')}%")
    print(f"   - Độ phủ sau can thiệp (Potential Coverage): {metrics.get('potential_coverage')}%")
    print(f"   - Mức thu hẹp khoảng cách (Delta): {metrics.get('gap_reduction_delta')}")

    print("\n4. KỸ NĂNG ĐÃ BAO PHỦ TỰ NHIÊN (Covered Skills):")
    for s in gap.get("covered_skills", []):
        print(f"   🟢 {s['skill']} ({s.get('demand_pct')}%) - {s.get('reason')}")

    print("\n5. KHOẢNG CÁCH NĂNG LỰC CẦN BỔ SUNG (Actionable Gaps):")
    for g in gap.get("actionable_gaps", []):
        print(f"   🟡 [{g.get('priority')}] {g['skill']} ({g.get('demand_pct')}% JD)")
        print(f"      - Lý do: {g.get('why_needed')}")
        print(f"      - Hành động: {g.get('action_item')}")
        print(f"      - Bằng chứng nộp Git: {g.get('proof_deliverable')}")

    print("\n6. TẠM HOÃN / TRÁNH OVER-ENGINEERING (Deferred):")
    for d in gap.get("deferred_or_overkill", []):
        print(f"   ⚪ {d['skill']} ({d.get('demand_pct', 0)}% JD) - {d.get('verdict')}: {d.get('reason')}")

    print("\n7. LỘ TRÌNH SPRINT THEO THỜI GIAN:")
    for r in bp.get("roadmap", []):
        print(f"   📅 {r['phase']}")
        for m in r.get("milestones", []):
            print(f"      • {m}")

    print("\n" + "=" * 70)
    print("HOÀN TẤT KIỂM THỬ THÀNH CÔNG!")
    print("=" * 70)

if __name__ == "__main__":
    test_engine()
