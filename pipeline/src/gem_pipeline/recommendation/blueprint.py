"""
Blueprint & Architecture Generation Module for GEM.
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Chức năng:
- Xây dựng bản thiết kế kiến trúc công nghệ 3 lớp:
  + Lớp 1: Core Foundation Stack (Sản phẩm chạy được - MVP)
  + Lớp 2: Career Boosters (3-5 kỹ năng thị trường thực tế TopCV để nâng tầm CV)
  + Lớp 3: Personal Extension (Module mở rộng hướng nghiệp chuyên sâu)
- Lập lộ trình Sprint theo thời gian (Roadmap) gắn liền với Bằng chứng Thực hành (Artifacts).
- Kết hợp dữ liệu thị trường thực tế (PostgreSQL) và dữ liệu ngữ nghĩa (Qdrant).
"""

from typing import Dict, List, Any, Optional


class BlueprintGenerator:
    """Tạo lập bản kiến trúc công nghệ 3 lớp và lộ trình thực hiện đồ án."""

    def __init__(self):
        pass

    def build_dynamic_roadmap(
        self,
        analysis: Dict[str, Any],
        time_months: int,
        target_role: str,
        gap_report: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Xây dựng lộ trình Sprint thông minh gắn liền với Bằng chứng Thực hành (Artifacts).
        Hỗ trợ số tháng linh hoạt (1, 2, 3, 4, 5, 6 tháng) và phân hóa theo Role Archetype.
        Quy tắc:
        - d <= 2 tháng: Nén thành 2 Sprint cấp tốc.
        - d >= 3 tháng: Phân rã thành đúng d giai đoạn (Tháng 1 đến Tháng d).
        - Mỗi giai đoạn đảm bảo tối thiểu 2-3 cột mốc kiểm chứng được.
        """
        domain = analysis.get("domain", "")
        gaps = gap_report.get("actionable_gaps", []) if gap_report else []
        gap_deliverables = [f"Bàn giao {g['skill']}: {g['proof_deliverable']}" for g in gaps]

        role_lower = (target_role or "").lower()
        domain_lower = (domain or "").lower()

        is_data = "data" in role_lower or "olap" in domain_lower
        is_ai = "ai" in role_lower or "machine learning" in role_lower or "trí tuệ nhân tạo" in domain_lower

        num_phases = 2 if time_months <= 2 else time_months

        # Luồng 1: Data Engineer / Data Science Archetype
        if is_data:
            if num_phases == 2:
                return [
                    {
                        "phase": "Giai đoạn 1 (Sprint 1): Thiết kế Schema & Pipeline Ingestion",
                        "milestones": [
                            "Mô hình hóa dữ liệu (Star/Snowflake Schema).",
                            "Thu thập dữ liệu nguồn và đẩy vào CSDL cột (ClickHouse/PostgreSQL).",
                            gap_deliverables[0] if len(gap_deliverables) > 0 else "Xây dựng pipeline nạp dữ liệu Ingestion.",
                        ],
                    },
                    {
                        "phase": "Giai đoạn 2 (Sprint 2): Xây dựng Truy vấn OLAP & Dashboard Bàn giao",
                        "milestones": [
                            "Tối ưu các câu lệnh Aggregation đa chiều.",
                            "Trực quan hóa chỉ số báo cáo qua Dashboard Superset.",
                            gap_deliverables[1] if len(gap_deliverables) > 1 else "Đóng gói pipeline bằng Docker bàn giao repo.",
                        ],
                    },
                ]
            else:
                base_phases = [
                    {
                        "phase": "Tháng 1: Thiết kế Kiến trúc Dữ liệu & Pipeline (Data Pipeline MVP)",
                        "milestones": [
                            "Xây dựng thiết kế mô hình dữ liệu đa chiều (Fact, Dimension, Star Schema).",
                            "Thiết lập luồng nạp dữ liệu Ingestion (Debezium hoặc Python script).",
                            "Triển khai Kho dữ liệu OLAP (ClickHouse) tối ưu Sorting Key theo thời gian.",
                        ],
                    },
                    {
                        "phase": "Tháng 2: Phát triển Module Phân tích Chuyên sâu & Giải quyết Skill Gap",
                        "milestones": [
                            "Xây dựng các khối tính toán tổng hợp (Aggregation Cubes) và chỉ số phân tích rủi ro.",
                            gap_deliverables[0] if len(gap_deliverables) > 0 else "Hoàn thiện script DDL và benchmark hiệu năng truy vấn.",
                            gap_deliverables[1] if len(gap_deliverables) > 1 else "Tự động hóa pipeline biến đổi dữ liệu qua dbt models.",
                        ],
                    },
                    {
                        "phase": "Tháng 3: Tối ưu Hóa Hiệu Năng, Dashboard & Đóng Gói Triển Khai",
                        "milestones": [
                            "Tối ưu hóa chỉ mục (Partitioning, Primary Sorting Key) trên dữ liệu hàng triệu bản ghi.",
                            gap_deliverables[2] if len(gap_deliverables) > 2 else "Kết nối hệ thống BI Dashboard trực quan hóa (Apache Superset).",
                            "Đóng gói toàn bộ hệ thống bằng Docker Compose, chuẩn bị bằng chứng phỏng vấn.",
                        ],
                    },
                    {
                        "phase": "Tháng 4: Mở rộng Xử lý Phân tán & Giám sát Pipeline",
                        "milestones": [
                            "Mở rộng xử lý phân tán với Spark/PySpark trên tập dữ liệu quy mô lớn.",
                            "Thiết lập giám sát chất lượng dữ liệu (Data Observability) và cảnh báo tự động.",
                        ],
                    },
                    {
                        "phase": "Tháng 5: Chuẩn hóa CI/CD & Kiểm thử Tự động Pipeline",
                        "milestones": [
                            "Tự động hóa quy trình kiểm thử chất lượng dữ liệu và kiểm thử tích hợp qua CI/CD.",
                            "Đo lường hiệu năng và độ trễ dữ liệu từ lúc nạp đến lúc phân tích.",
                        ],
                    },
                    {
                        "phase": "Tháng 6: Hoàn thiện Hồ sơ Năng lực Doanh nghiệp (Portfolio Defense)",
                        "milestones": [
                            "Tài liệu hóa toàn bộ kiến trúc kho dữ liệu Data Catalog và Data Dictionary.",
                            "Đóng gói demo hoàn chỉnh, chuẩn bị báo cáo đồ án và bằng chứng phỏng vấn.",
                        ],
                    },
                ]
                return base_phases[:num_phases]

        # Luồng 2: AI / Machine Learning Engineer Archetype
        elif is_ai:
            if num_phases == 2:
                return [
                    {
                        "phase": "Giai đoạn 1 (Sprint 1): Khám phá Dữ liệu & Huấn Luyện Baseline",
                        "milestones": [
                            "Thu thập, làm sạch và gán nhãn tập dữ liệu (EDA & Data Preprocessing).",
                            "Xây dựng mô hình Huấn Luyện Baseline bằng Scikit-Learn / PyTorch.",
                            gap_deliverables[0] if len(gap_deliverables) > 0 else "Thiết lập pipeline đánh giá độ chính xác (Precision/Recall/F1).",
                        ],
                    },
                    {
                        "phase": "Giai đoạn 2 (Sprint 2): Tinh chỉnh Mô hình & Đóng Gói Inference API",
                        "milestones": [
                            "Fine-tuning hoặc tối ưu hóa siêu tham số mô hình.",
                            "Đóng gói mô hình thành dịch vụ FastAPI / ONNX Runtime kèm Docker.",
                            gap_deliverables[1] if len(gap_deliverables) > 1 else "Viết tài liệu Swagger API và báo cáo thực nghiệm.",
                        ],
                    },
                ]
            else:
                base_ai_phases = [
                    {
                        "phase": "Tháng 1: Khám phá Dữ liệu & Huấn Luyện Baseline",
                        "milestones": [
                            "Thu thập, tiền xử lý và phân tích khám phá dữ liệu (EDA).",
                            "Xây dựng và đánh giá mô hình Huấn Luyện Baseline ban đầu.",
                            gap_deliverables[0] if len(gap_deliverables) > 0 else "Thiết lập ma trận đánh giá hiệu năng (Metrics Evaluation).",
                        ],
                    },
                    {
                        "phase": "Tháng 2: Tối ưu Hóa Mô hình & Giải quyết Skill Gap",
                        "milestones": [
                            "Thực nghiệm các kiến trúc mô hình sâu hơn (Deep Learning / Transformers / RAG).",
                            gap_deliverables[1] if len(gap_deliverables) > 1 else "Tối ưu hóa độ trễ suy luận (Model Quantization / ONNX).",
                            "Theo dõi thí nghiệm và lưu trữ phiên bản mô hình (Experiment Tracking).",
                        ],
                    },
                    {
                        "phase": "Tháng 3: Triển khai Serving API & Đóng Gói Sản Phẩm",
                        "milestones": [
                            "Xây dựng Inference API hiệu năng cao với FastAPI và streaming response.",
                            gap_deliverables[2] if len(gap_deliverables) > 2 else "Đóng gói toàn bộ mô hình và dịch vụ bằng Docker Compose.",
                            "Hoàn thiện báo cáo thực nghiệm so sánh các phương pháp phục vụ phỏng vấn.",
                        ],
                    },
                    {
                        "phase": "Tháng 4: Mở rộng Tác tử Thông minh & Lưu trữ Vector",
                        "milestones": [
                            "Tích hợp cơ sở dữ liệu Vector (Qdrant) hỗ trợ tìm kiếm ngữ nghĩa.",
                            "Xây dựng luồng tác tử tự động hóa (LangGraph / Multi-Agent).",
                        ],
                    },
                    {
                        "phase": "Tháng 5: Kiểm thử Tải & Giám sát Mô hình Thực tế (Model Monitoring)",
                        "milestones": [
                            "Kiểm thử chịu tải đồng thời trên Inference Endpoint.",
                            "Giám sát độ lệch dữ liệu (Data Drift / Concept Drift).",
                        ],
                    },
                    {
                        "phase": "Tháng 6: Đóng Gói Luận Văn & Portfolio Tuyển Dụng",
                        "milestones": [
                            "Hoàn thiện báo cáo khoa học đồ án tốt nghiệp.",
                            "Đưa các Artifacts mô hình và benchmark lên GitHub tạo điểm nhấn CV.",
                        ],
                    },
                ]
                return base_ai_phases[:num_phases]

        # Luồng 3: Mặc định cho Software Engineering (Backend, Frontend, Fullstack, DevOps, QA, Mobile)
        else:
            if num_phases == 2:
                return [
                    {
                        "phase": "Giai đoạn 1 (Tuần 1-2): MVP Cốt lõi & Kiểm thử",
                        "milestones": [
                            "Hiện thực CSDL và các API dịch vụ chính.",
                            "Viết Unit test cho luồng giao dịch/đặt hàng chính.",
                            gap_deliverables[0] if len(gap_deliverables) > 0 else "Xác thực luồng dữ liệu cơ bản.",
                        ],
                    },
                    {
                        "phase": "Giai đoạn 2 (Tuần 3-4): Tích hợp & Đóng gói Docker",
                        "milestones": [
                            "Ghép nối giao diện, đóng gói Docker Compose.",
                            "Viết tài liệu Swagger API và hướng dẫn triển khai trong README.",
                            gap_deliverables[1] if len(gap_deliverables) > 1 else "Chuẩn bị bản demo hoàn chỉnh.",
                        ],
                    },
                ]
            else:
                base_se_phases = [
                    {
                        "phase": "Tháng 1: Hoàn thiện Nền tảng Vận hành Cốt lõi (Core MVP)",
                        "milestones": [
                            "Thiết kế CSDL quan hệ chuẩn hóa (khóa ngoại, chỉ mục, ràng buộc toàn vẹn).",
                            "Phát triển các API dịch vụ cốt lõi theo chuẩn RESTful.",
                            "Xây dựng giao diện tương tác ban đầu và kiểm thử luồng nghiệp vụ chính.",
                        ],
                    },
                    {
                        "phase": "Tháng 2: Thu hẹp Skill Gap & Bổ sung Bằng chứng Thực hành",
                        "milestones": [
                            gap_deliverables[1] if len(gap_deliverables) > 1 else "Viết bộ kiểm thử tự động (Unit / Integration Test) đạt coverage > 60%.",
                            "Tích hợp xác thực phân quyền an toàn (JWT Authentication & RBAC).",
                            gap_deliverables[0] if len(gap_deliverables) > 0 else "Viết Dockerfile và cấu hình docker-compose kết nối API cùng PostgreSQL.",
                        ],
                    },
                    {
                        "phase": "Tháng 3: Chuẩn hóa Sản phẩm Doanh nghiệp & Hồ sơ Năng lực (Portfolio)",
                        "milestones": [
                            gap_deliverables[2] if len(gap_deliverables) > 2 else "Tự động sinh tài liệu Swagger OpenAPI và Postman collection.",
                            "Kiểm thử tải và kiểm tra khả năng chạy lại ứng dụng trong môi trường mới.",
                            "Hoàn thiện báo cáo đồ án, tự tin đưa các bằng chứng năng lực (Artifacts) vào CV.",
                        ],
                    },
                    {
                        "phase": "Tháng 4: Tối ưu Hóa Hiệu Năng & Bộ Nhớ Đệm (Caching Layer)",
                        "milestones": [
                            "Tích hợp Redis Caching cho các truy vấn dữ liệu phổ biến.",
                            "Tối ưu hóa thời gian phản hồi của các API phức tạp.",
                        ],
                    },
                    {
                        "phase": "Tháng 5: Thiết lập CI/CD & Kiểm thử Chịu Tải (Load Testing)",
                        "milestones": [
                            "Thiết lập GitHub Actions tự động build và chạy test mỗi khi push code.",
                            "Thực hiện kiểm thử tải bằng k6 hoặc Locust, đánh giá throughput.",
                        ],
                    },
                    {
                        "phase": "Tháng 6: Hoàn thiện Bảo vệ Đồ án & Hồ sơ Tuyển Dụng",
                        "milestones": [
                            "Kiểm toán bảo mật (Security Audit) và rà soát mã nguồn.",
                            "Đóng gói tài liệu bàn giao, sẵn sàng bảo vệ đồ án tốt nghiệp xuất sắc.",
                        ],
                    },
                ]
                return base_se_phases[:num_phases]

    def build_blueprint(
        self,
        idea_text: str,
        analysis: Dict[str, Any],
        target_role: str,
        role_profile: Dict[str, Any],
        relevant_jds: List[Dict[str, Any]],
        similar_projects: List[Dict[str, Any]],
        skill_gap_report: Dict[str, Any],
        time_months: int = 3,
        preferred_tech: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Tập hợp đầy đủ bản thiết kế kiến trúc 3 lớp và lộ trình."""
        core_market_skills = role_profile.get("core_skills", [])
        boost_market_skills = role_profile.get("boost_skills", [])

        # LỚP 1: Core Foundation Stack
        tailored_l1 = analysis.get("layer1_tailored", [])
        if not tailored_l1:
            tailored_l1 = [
                {"category": "Giao diện / Khai thác", "tech": "Web Dashboard / REST API", "purpose": "Tương tác và kiểm thử chức năng."},
                {"category": "Máy chủ / Xử lý", "tech": "Python / Java / Node.js", "purpose": "Xử lý logic và dịch vụ chính."},
                {"category": "Cơ sở dữ liệu", "tech": "PostgreSQL / ClickHouse", "purpose": "Lưu trữ dữ liệu theo đúng mô hình nghiệp vụ."},
                {"category": "Bảo mật & Tích hợp", "tech": "Docker & Authentication", "purpose": "Đóng gói triển khai chuẩn hóa."},
            ]

        layer1_core = {
            "title": "Lớp 1: Công nghệ Nền tảng (Core Foundation Stack)",
            "description": f"Bộ công nghệ tối thiểu bắt buộc để xây dựng hoàn chỉnh sản phẩm hoạt động được theo đúng bài toán {analysis.get('domain', '')}.",
            "components": tailored_l1,
        }

        # LỚP 2: Career Value Enhancers
        layer2_boosters = []
        candidate_skills = boost_market_skills[:4] if len(boost_market_skills) >= 4 else (core_market_skills + boost_market_skills)[:4]
        for s in candidate_skills:
            pct = s.get("demand_pct", 15.0)
            cname = s.get("canonical_name", "Technology")
            layer2_boosters.append({
                "skill": cname,
                "market_evidence": f"Xuất hiện trong {pct:.1f}% tin tuyển dụng vị trí {target_role}",
                "why_matter": f"Được các doanh nghiệp săn đón mạnh mẽ để tối ưu hóa quy trình kỹ thuật cho vị trí {target_role}.",
            })

        if len(layer2_boosters) < 3:
            layer2_boosters.append({
                "skill": "Docker & Containerization",
                "market_evidence": "Tiêu chuẩn bắt buộc trong hơn 20% JD phần mềm & dữ liệu",
                "why_matter": "Đóng gói ứng dụng chạy đồng nhất trên mọi môi trường, ghi điểm lớn khi phỏng vấn.",
            })
            layer2_boosters.append({
                "skill": "CI/CD & Git Workflow",
                "market_evidence": "Kỹ năng thực hành bắt buộc tại các công ty công nghệ",
                "why_matter": "Chứng minh tác phong làm việc bài bản, sẵn sàng hòa nhập dự án thực tế.",
            })

        # LỚP 3: Personal Goal Extensions
        layer3_extension = analysis.get("layer3_extension")
        if not layer3_extension:
            layer3_extension = {
                "title": f"Lớp 3: Phần Mở rộng Hướng nghiệp ({target_role})",
                "target_role": target_role,
                "proposed_module": "Module Nâng cao & Tối ưu hóa Hiệu năng Chuyên sâu",
                "technologies": "Công nghệ phân tích & tối ưu dữ liệu thực tế",
                "implementation_detail": "Hiện thực các thuật toán tối ưu hóa hoặc kiểm soát rủi ro bài toán nghiệp vụ.",
                "cv_value": "Chứng minh khả năng giải quyết bài toán phức tạp vượt trên mức đồ án thông thường.",
            }
        else:
            layer3_extension["target_role"] = target_role

        # Lộ trình Roadmap
        roadmap = self.build_dynamic_roadmap(analysis, time_months, target_role, skill_gap_report)

        # Tham khảo Đồ án cũ
        if similar_projects:
            reference_note = {
                "status": "FOUND",
                "message": f"Tìm thấy {len(similar_projects)} đồ án liên quan trong kho mã nguồn GitHub.",
                "projects": similar_projects,
            }
        else:
            reference_note = {
                "status": "NOT_FOUND_OR_SPARSE",
                "message": (
                    "Đề tài có tính chuyên môn hóa cao. "
                    "Đề xuất trên được GEM cố vấn độc lập dựa trên Chuẩn kiến trúc Công nghệ phần mềm "
                    "và Dữ liệu tuyển dụng thực tế TopCV."
                ),
                "projects": [],
            }

        # Kiến trúc đề xuất theo Role
        if "backend" in target_role.lower():
            recommended_arch = "Layered Architecture (Controller -> Service -> Repository -> Database) / Modular Monolith"
            tech_stack_summary = [
                {"category": "Core Framework (Tùy chọn)", "options": ["Java (Spring Boot 3)", "TypeScript (NestJS)", "Python (FastAPI)"]},
                {"category": "Cơ sở dữ liệu", "options": ["PostgreSQL (Relational DB / ACID Compliant)"]},
                {"category": "Giao thức & Tài liệu", "options": ["RESTful API / OpenAPI Swagger 3.0"]},
                {"category": "Bảo mật & Phân quyền", "options": ["JWT Authentication", "Role-Based Access Control (RBAC)", "Mã hóa AES-256"]},
            ]
        elif "frontend" in target_role.lower():
            recommended_arch = "Component-Driven Architecture (Feature-based Modular Structure)"
            tech_stack_summary = [
                {"category": "Frontend Framework", "options": ["React (TypeScript / Vite)", "Next.js", "Vue 3"]},
                {"category": "State Management", "options": ["Zustand", "Redux Toolkit", "TanStack Query"]},
                {"category": "UI & Styling", "options": ["Tailwind CSS", "Ant Design", "Shadcn/UI"]},
            ]
        elif "ai" in target_role.lower() or "machine learning" in target_role.lower():
            recommended_arch = "Hybrid AI Architecture (Decoupled AI Inference Service + Web Client)"
            tech_stack_summary = [
                {"category": "AI Framework & Service", "options": ["Python (FastAPI / PyTorch / Scikit-Learn)"]},
                {"category": "Vector DB / RAG", "options": ["Qdrant", "ChromaDB", "LangChain"]},
                {"category": "Cơ sở dữ liệu", "options": ["PostgreSQL"]},
            ]
        elif "data" in target_role.lower():
            recommended_arch = "Modern Data Platform Architecture (Ingestion -> Warehouse/OLAP -> Analytics/BI)"
            tech_stack_summary = [
                {"category": "Ingestion & Transform", "options": ["Python", "dbt", "Debezium"]},
                {"category": "OLAP Data Warehouse", "options": ["ClickHouse", "PostgreSQL"]},
                {"category": "BI & Visualization", "options": ["Apache Superset", "Streamlit"]},
            ]
        else:
            recommended_arch = "Modular Monolith / Layered Architecture"
            tech_stack_summary = [
                {"category": "Backend / Dịch vụ", "options": ["Node.js / Java / Python"]},
                {"category": "Cơ sở dữ liệu", "options": ["PostgreSQL"]},
                {"category": "Triển khai", "options": ["Docker & Docker Compose"]},
            ]

        return {
            "domain": analysis.get("domain", ""),
            "target_role": target_role,
            "time_months": time_months,
            "preferred_tech": preferred_tech or [],
            "core_features": analysis.get("core_features", []),
            "suggested_career_paths": analysis.get("suggested_career_paths", []),
            "recommended_architecture": recommended_arch,
            "tech_stack_summary": tech_stack_summary,
            "layer1_foundation": layer1_core,
            "layer2_boosters": layer2_boosters,
            "layer3_extension": layer3_extension,
            "skill_gap_report": skill_gap_report,
            "readiness_metrics": skill_gap_report.get("metrics", {}),
            "roadmap": roadmap,
            "market_evidence": {
                "total_jds_analyzed": role_profile.get("total_jds", 0),
                "top_demanded_skills": [s["canonical_name"] for s in core_market_skills[:6]],
                "sample_jds": [j["title"] for j in relevant_jds[:2]],
            },
            "matched_jds": relevant_jds,
            "reference_projects": reference_note,
        }
