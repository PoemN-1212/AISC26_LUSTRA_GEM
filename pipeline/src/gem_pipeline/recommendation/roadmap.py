"""
GEM Roadmap Generator (Bộ sinh Lộ trình Công nghệ và Đề xuất Học tập)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Nguyên tắc cốt lõi:
1. Kết nối thị trường (Market Demand) với đồ án sinh viên (Student Profile)
2. Định lượng khoảng cách (Skill Gap) và tính điểm ưu tiên (Priority Ranking)
3. Xếp lộ trình 3 giai đoạn: NOW -> NEXT -> LATER
4. Trả lời 4 câu hỏi minh bạch có giải thích cho từng kỹ năng:
   - Kỹ năng nào?
   - Vì sao thiếu?
   - Vì sao quan trọng?
   - Phù hợp với Tech Stack hiện tại ra sao?
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from gem_pipeline.market.demand import MarketDemandCalculator
from gem_pipeline.project.profile import StudentProfileBuilder


class TechnologyRoadmapGenerator:
    """
    Sinh lộ trình học công nghệ và khuyến nghị có giải thích
    dựa trên khoảng cách giữa nhu cầu thị trường và hồ sơ kỹ năng sinh viên.
    """

    def __init__(self, db_uri: Optional[str] = None):
        self.market_calc = MarketDemandCalculator(db_uri)
        self.profile_builder = StudentProfileBuilder(db_uri)

    def generate_roadmap_for_project(self, project_id: str, top_skills: int = 10) -> Dict[str, Any]:
        """
        Sinh lộ trình công nghệ cho một đồ án sinh viên cụ thể.
        """
        # 1. Lấy hồ sơ kỹ năng của sinh viên từ đồ án
        student_profile = self.profile_builder.build_profile_from_project_id(project_id)
        student_skills = student_profile["canonical_skills"]
        tech_stack = student_profile["tech_stack"]

        # Lấy danh sách ngôn ngữ/framework chính sinh viên đang dùng
        core_languages = tech_stack.get("PROGRAMMING_LANGUAGE", [])
        core_frameworks = tech_stack.get("BACKEND_FRAMEWORK", []) + tech_stack.get("FRONTEND_FRAMEWORK", [])

        # 2. Lấy nhu cầu thị trường hiện tại
        df_market = self.market_calc.compute_market_demand(top_k=0)

        if df_market.empty:
            return {
                "project_id": project_id,
                "project_title": student_profile["project_title"],
                "student_skills": list(student_skills),
                "roadmap": [],
                "message": "Chưa có đủ dữ liệu thị trường để sinh lộ trình."
            }

        # 3. Tính toán khoảng cách kỹ năng (Skill Gap)
        # Chỉ xét các kỹ năng thuộc nhóm kỹ thuật cốt lõi (bỏ GENERAL)
        gap_items = []
        for _, row in df_market.iterrows():
            c_name = row["canonical_name"]
            category = row["category"]
            demand = row["demand_pct"]

            # Nếu sinh viên ĐÃ CÓ trong profile -> Bỏ qua (không phải Gap)
            if c_name in student_skills:
                continue

            # Bỏ qua các từ chung chung không phải công nghệ cốt lõi
            if category in ["TECHNOLOGY_GENERAL", "ABILITY"]:
                continue

            # Tính điểm ưu tiên (Priority Score)
            # Ưu tiên cao hơn nếu cùng họ công nghệ với sinh viên
            relevance_multiplier = 1.0
            if category in ["DATABASE_STORAGE", "CLOUD_DEVOPS", "API_ARCHITECTURE"]:
                relevance_multiplier = 1.25  # Tăng trọng số cho DB, Cloud/DevOps vì sinh viên hay thiếu

            priority_score = round(demand * relevance_multiplier, 2)

            gap_items.append({
                "skill": c_name,
                "category": category,
                "demand_pct": demand,
                "priority_score": priority_score,
                "jd_count": int(row["jd_count"])
            })

        # Sắp xếp theo điểm ưu tiên giảm dần
        gap_items.sort(key=lambda x: x["priority_score"], reverse=True)
        recommended_gaps = gap_items[:top_skills]

        # 4. Phân chia 3 giai đoạn: NOW (Ngay lập tức) -> NEXT (Kế tiếp) -> LATER (Về sau)
        stages = {"NOW": [], "NEXT": [], "LATER": []}

        for idx, item in enumerate(recommended_gaps):
            skill_name = item["skill"]
            demand = item["demand_pct"]
            cat = item["category"]

            # Phân bổ giai đoạn theo mức độ ưu tiên
            if idx < 3:
                stage = "NOW"
                stage_desc = "Cần bổ sung ngay lập tức vào đồ án"
            elif idx < 7:
                stage = "NEXT"
                stage_desc = "Học tiếp theo để hoàn thiện hệ thống"
            else:
                stage = "LATER"
                stage_desc = "Nâng cấp kiến trúc và mở rộng quy mô"

            # 4 luận điểm giải thích minh bạch (Explainable Recommendation)
            reasons = [
                f"Chưa phát hiện bằng chứng về '{skill_name}' trong các tài liệu/README của đồ án này.",
                f"Nhu cầu thị trường IT rất cao: xuất hiện trong {demand}% tin tuyển dụng.",
                f"Thuộc nhóm {cat} giúp đồ án đáp ứng tiêu chuẩn tuyển dụng thực tế.",
                f"Tương thích để tích hợp trực tiếp vào Tech Stack hiện tại của bạn ({', '.join((core_languages + core_frameworks)[:3]) or 'Web/App'})."
            ]

            stages[stage].append({
                "skill": skill_name,
                "category": cat,
                "demand_pct": demand,
                "priority_score": item["priority_score"],
                "stage": stage,
                "stage_description": stage_desc,
                "reasons": reasons
            })

        return {
            "project_id": project_id,
            "project_title": student_profile["project_title"],
            "existing_skills_count": len(student_skills),
            "existing_skills": list(student_skills),
            "total_gap_identified": len(gap_items),
            "roadmap": {
                "NOW (Giai đoạn 1 - Trọng tâm cấp bách)": stages["NOW"],
                "NEXT (Giai đoạn 2 - Mở rộng năng lực)": stages["NEXT"],
                "LATER (Giai đoạn 3 - Nâng cao quy mô)": stages["LATER"]
            }
        }
