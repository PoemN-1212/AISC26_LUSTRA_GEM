"""
Idea Analyzer Module for GEM Recommendation Engine.
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Chức năng:
- Bóc tách phân tích ngữ nghĩa chuyên sâu mọi ý tưởng đề tài sinh viên (LLM Dynamic Analysis).
- Phân tích Domain, Problem Statement, Technical Pillars (Module cốt lõi).
- Gợi ý 2-3 hướng nghề nghiệp phù hợp nhất (Career Paths).
- Thiết kế sơ bộ Layer 1 Core Stack & Layer 3 Extension theo đặc thù đề tài.
- Fallback heuristic an toàn nếu LLM gặp sự cố.
"""

import json
from typing import Dict, Any, Optional
from gem_pipeline.llm.client import GEMAdvisorLLM, clean_json_markdown
from gem_pipeline.recommendation.prompts import build_idea_analysis_prompt


class IdeaAnalyzer:
    """Chuyên trách phân tích ý tưởng đề tài và phân rã nghiệp vụ."""

    def __init__(self, llm: Optional[GEMAdvisorLLM] = None):
        self.llm = llm or GEMAdvisorLLM()
        self._cache: Dict[str, Dict[str, Any]] = {}

    def analyze_idea(self, idea_text: str) -> Dict[str, Any]:
        """
        Phân tích sâu sắc bài toán, bóc tách module và gợi ý 2-3 hướng nghề nghiệp.
        Hoàn toàn động qua LLM, có cơ chế fallback heuristic an toàn.
        """
        cache_key = (idea_text or "").strip().lower()
        if cache_key in self._cache:
            return self._cache[cache_key]

        prompt = build_idea_analysis_prompt(idea_text)
        raw_res = self.llm.generate_text(prompt, temperature=0.2, max_tokens=800)
        clean = clean_json_markdown(raw_res)

        try:
            data = json.loads(clean)
            res = {
                "domain": data.get("domain", "Hệ thống Phần mềm Chuyên sâu"),
                "problem_statement": data.get("problem_statement", idea_text),
                "core_features": [
                    f"{m.get('module')}: {m.get('description')}"
                    for m in data.get("technical_pillars", [])
                    if isinstance(m, dict)
                ],
                "suggested_career_paths": data.get("suggested_career_paths", []),
                "primary_role": data.get("primary_role", "Backend Developer"),
                "layer1_tailored": data.get("layer1_tailored", []),
                "layer3_extension": data.get("layer3_extension", None),
            }
            if not res["core_features"]:
                res["core_features"] = [
                    "Quản lý tài khoản & phân quyền người dùng",
                    "Quản lý dữ liệu danh mục & tìm kiếm",
                    "Xử lý giao dịch / nghiệp vụ cốt lõi",
                    "Thống kê báo cáo & tích hợp API",
                ]
            self._cache[cache_key] = res
            return res
        except Exception:
            fb = self._heuristic_fallback_analysis(idea_text)
            self._cache[cache_key] = fb
            return fb

    def _heuristic_fallback_analysis(self, idea_text: str) -> Dict[str, Any]:
        """Quy tắc heuristic dự phòng an toàn khi LLM không khả dụng."""
        idea_lower = (idea_text or "").lower()

        # Nhận diện miền nghiệp vụ
        if any(k in idea_lower for k in ["bệnh", "y tế", "bác sĩ", "khám", "clinic", "health", "doctor"]):
            domain = "Y tế & Đặt lịch Khám bệnh (HealthTech / E-Health)"
            features = [
                "Hồ sơ người dùng & Phân quyền RBAC (Bệnh nhân, Bác sĩ, Tiếp tân)",
                "Quản lý danh mục Bác sĩ, Chuyên khoa & Dịch vụ khám",
                "Quản lý Ca trực & Khung giờ khám (Time Slot Availability)",
                "Đặt lịch hẹn & Chống xung đột slot (Concurrency Control)",
            ]
            primary_role = "Backend Developer"
            careers = [
                {"role": "Backend Developer", "reason": "Yêu cầu cao về tính toàn vẹn giao dịch ACID, chống đặt trùng lịch và bảo mật hồ sơ y tế."},
                {"role": "Frontend Developer", "reason": "Trải nghiệm đặt lịch nhanh, tương tác trực quan theo ca khám và hiển thị thông tin bác sĩ."},
                {"role": "Full-stack Developer", "reason": "Khả năng xây dựng trọn gói từ UI đặt lịch đến API xử lý lịch khám."},
            ]
        elif any(k in idea_lower for k in ["thương mại", "bán hàng", "shop", "ecommerce", "e-commerce", "sản phẩm"]):
            domain = "Thương mại Điện tử & Bán lẻ Trực tuyến (E-Commerce)"
            features = [
                "Danh mục sản phẩm, bộ lọc & tìm kiếm thông minh",
                "Giỏ hàng & Luồng xử lý đơn hàng (Cart & Order Processing)",
                "Thanh toán trực tuyến & Xử lý trạng thái giao dịch",
                "Quản lý sản phẩm, tồn kho & tài khoản người dùng",
            ]
            primary_role = "Backend Developer"
            careers = [
                {"role": "Backend Developer", "reason": "Quản lý tồn kho, xử lý đơn hàng và tích hợp cổng thanh toán giao dịch an toàn."},
                {"role": "Frontend Developer", "reason": "Xây dựng trải nghiệm mua sắm mượt mà, tối ưu hóa giao diện sản phẩm và giỏ hàng."},
                {"role": "Full-stack Developer", "reason": "Bao quát toàn diện cả luồng người mua (Storefront) và trang quản trị (Admin Dashboard)."},
            ]
        elif any(k in idea_lower for k in ["học", "sinh viên", "giáo dục", "lms", "elearning", "e-learning", "khóa học"]):
            domain = "Giáo dục Trực tuyến & Hệ thống Học tập (EdTech / LMS)"
            features = [
                "Quản lý khóa học, bài giảng và tài liệu đa phương tiện",
                "Hệ thống làm bài tập, thi trắc nghiệm & chấm điểm tự động",
                "Theo dõi tiến độ học tập và cấp chứng nhận hoàn thành",
                "Diễn đàn thảo luận và tương tác giảng viên - học viên",
            ]
            primary_role = "Full-stack Developer"
            careers = [
                {"role": "Full-stack Developer", "reason": "Bao phủ từ giao diện học tập tương tác đến API quản lý khóa học và phân quyền."},
                {"role": "Backend Developer", "reason": "Xử lý tiến độ học tập, chấm điểm tự động và cấu trúc cơ sở dữ liệu khóa học."},
                {"role": "Frontend Developer", "reason": "Tạo giao diện học trực tuyến thân thiện, mượt mà và trực quan hóa tiến trình."},
            ]
        elif any(k in idea_lower for k in ["dữ liệu", "olap", "kho dữ liệu", "pipeline", "etl", "clickhouse", "spark"]):
            domain = "Tài chính Ngân hàng & Kho Dữ liệu Lớn (FinTech / Big Data OLAP)"
            features = [
                "Thu thập và nạp dữ liệu giao dịch thời gian thực (Ingestion)",
                "Thiết kế mô hình kho dữ liệu đa chiều (Fact/Dimension Star Schema)",
                "Xử lý biến đổi và tổng hợp chỉ số kinh doanh qua Data Pipeline",
                "Trực quan hóa chỉ số rủi ro qua Dashboard phân tích OLAP",
            ]
            primary_role = "Data Engineer"
            careers = [
                {"role": "Data Engineer", "reason": "Làm chủ kiến trúc kho dữ liệu, tối ưu hóa câu lệnh phân tích trên hàng triệu bản ghi."},
                {"role": "Data Analyst", "reason": "Mô hình hóa chỉ số, phân tích xu hướng và xây dựng báo cáo hỗ trợ ra quyết định."},
                {"role": "Backend Developer", "reason": "Xây dựng dịch vụ API cung cấp dữ liệu phân tích cho các ứng dụng nghiệp vụ."},
            ]
        else:
            domain = "Hệ thống Phần mềm Ứng dụng & Dịch vụ Trực tuyến"
            features = [
                "Xác thực người dùng & phân quyền tài khoản (Auth & RBAC)",
                "Quản lý dữ liệu thực thể nghiệp vụ cốt lõi (CRUD)",
                "Xử lý luồng logic giao dịch chính của ứng dụng",
                "Tích hợp API và đóng gói triển khai chuẩn hóa",
            ]
            primary_role = "Backend Developer"
            careers = [
                {"role": "Backend Developer", "reason": "Xây dựng logic nghiệp vụ vững chắc, chuẩn hóa API và thiết kế cơ sở dữ liệu quan hệ."},
                {"role": "Frontend Developer", "reason": "Thiết kế giao diện hiện đại, tối ưu tương tác người dùng theo chuẩn responsive."},
                {"role": "Full-stack Developer", "reason": "Làm chủ cả hệ thống end-to-end từ giao diện đến máy chủ và cơ sở dữ liệu."},
            ]

        return {
            "domain": domain,
            "problem_statement": idea_text,
            "core_features": features,
            "suggested_career_paths": careers,
            "primary_role": primary_role,
            "layer1_tailored": [
                {"category": "Tầng Giao diện", "tech": "React (TypeScript) / Web Client", "purpose": "Tương tác và kiểm thử giao dịch người dùng."},
                {"category": "Tầng Dịch vụ Backend", "tech": "Python / Java / Node.js REST API", "purpose": "Xử lý nghiệp vụ chính và các ràng buộc dữ liệu."},
                {"category": "Tầng Cơ sở Dữ liệu", "tech": "PostgreSQL (ACID Relational DB)", "purpose": "Lưu trữ dữ liệu có cấu trúc, chuẩn hóa quan hệ."},
                {"category": "Tầng Đóng gói", "tech": "Docker & Docker Compose", "purpose": "Đóng gói triển khai môi trường chuẩn hóa."},
            ],
            "layer3_extension": {
                "title": f"Lớp 3: Phần Mở rộng Nâng tầm CV ({primary_role})",
                "proposed_module": "Module Tối ưu Hiệu năng & Giám sát Hệ thống",
                "technologies": "Redis Cache & Logging / Audit Trail",
                "implementation_detail": "Tích hợp bộ nhớ đệm giảm tải truy vấn DB và ghi vết nhật ký giao dịch phục vụ bảo mật.",
                "cv_value": "Chứng minh năng lực thiết kế hệ thống chuyên nghiệp sẵn sàng cho môi trường doanh nghiệp.",
            },
        }
