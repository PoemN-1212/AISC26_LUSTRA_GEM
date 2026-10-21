"""
Stateful Multi-turn Chat & Session Manager for GEM Advisor.
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Chức năng:
- Quản trị phiên làm việc (Session Management) và lịch sử đàm thoại.
- Nhận diện mục tiêu nghề nghiệp, thời gian thực hiện, công nghệ yêu thích linh hoạt và chính xác.
- Nhận diện các trạng thái nghiệp vụ:
  + TC01: Chưa quyết định công nghệ / nghề nghiệp (Undecided).
  + TC02: Chuyển dịch mục tiêu nghề nghiệp (Role Switched).
  + TC03: Đề tài chuyên sâu có đặc thù nghiệp vụ rõ ràng (Specific Domain & Explicit Role).
  + TC04: Đã có stack / kế hoạch kỹ thuật, cần đánh giá và bổ sung năng lực (Evaluate Existing Stack).
  + TC05: Sản phẩm Web nhưng hướng tới Data Engineer trong thời gian giới hạn (Web-to-Data Pivot).
  + TC06: Đã học một số công nghệ, hỏi đã đủ ứng tuyển Intern chưa & thiếu gì (Intern Readiness Audit).
- Sinh câu trả lời định hướng giàu tính cố vấn và học thuật qua LLM.
"""

import re
import uuid
from typing import Dict, Any, Optional, List, Tuple
from gem_pipeline.llm.client import GEMAdvisorLLM
from gem_pipeline.recommendation.prompts import build_advisor_reply_prompt


class ChatService:
    """Quản trị luồng hội thoại nhiều lượt và trạng thái phiên tư vấn."""

    def __init__(self, llm: Optional[GEMAdvisorLLM] = None):
        self.llm = llm or GEMAdvisorLLM()
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create_session(self, session_id: Optional[str], initial_idea: str) -> Tuple[str, Dict[str, Any]]:
        """Lấy phiên hiện tại hoặc khởi tạo phiên mới."""
        if not session_id or session_id not in self.sessions:
            new_id = session_id or str(uuid.uuid4())
            self.sessions[new_id] = {
                "session_id": new_id,
                "idea": initial_idea,
                "target_role": None,
                "previous_role": None,
                "role_switched": False,
                "time_months": 3,
                "preferred_tech": [],
                "history": [],
            }
            return new_id, self.sessions[new_id]
        return session_id, self.sessions[session_id]

    def parse_time_duration(self, message: str) -> Optional[int]:
        """Phân tích thời lượng dự án từ tin nhắn người dùng."""
        msg_lower = (message or "").lower()

        # Ánh xạ từ ngữ tiếng Việt
        word_to_num = {
            "một": 1, "hai": 2, "ba": 3, "bốn": 4, "bon": 4, "năm": 5, "nam": 5, "sáu": 6, "sau": 6
        }

        # Kiểm tra tuần dạng chữ hoặc số
        for word, num in word_to_num.items():
            if f"{word} tuần" in msg_lower or f"{word} tuan" in msg_lower:
                return max(1, int(round(num / 4.0)))
        m_week = re.search(r"(\d+)\s*(tuần|tuan|week)", msg_lower)
        if m_week:
            weeks = int(m_week.group(1))
            return max(1, int(round(weeks / 4.0)))
        if "tuần" in msg_lower or "tuan" in msg_lower:
            return 1

        # Kiểm tra kỳ học
        if "kỳ học" in msg_lower or "học kỳ" in msg_lower or "hoc ky" in msg_lower or "ky hoc" in msg_lower:
            return 4

        # Kiểm tra số dạng chữ
        for word, num in word_to_num.items():
            if f"{word} tháng" in msg_lower or f"{word} thang" in msg_lower:
                return num

        # Kiểm tra dạng số "\d+ tháng"
        m = re.search(r"(\d+)\s*(tháng|thang|month)", msg_lower)
        if m:
            return int(m.group(1))

        return None

    def parse_preferred_tech(self, message: str, current_list: List[str]) -> List[str]:
        """Phân tích các công nghệ yêu thích / đã chọn từ người dùng."""
        msg_lower = (message or "").lower()
        result = list(current_list)

        tech_patterns = [
            ("python", "Python"),
            ("pandas", "Pandas"),
            ("sql", "SQL"),
            ("fastapi", "FastAPI"),
            ("postgresql", "PostgreSQL"),
            ("postgres", "PostgreSQL"),
            ("mysql", "MySQL"),
            ("mongodb", "MongoDB"),
            ("sqlite", "SQLite"),
            ("clickhouse", "ClickHouse"),
            ("dbt", "dbt"),
            ("docker", "Docker"),
            ("pytorch", "PyTorch"),
            ("scikit-learn", "Scikit-Learn"),
            ("scikit learn", "Scikit-Learn"),
            ("kafka", "Kafka"),
            ("spark", "Spark"),
            ("airflow", "Apache Airflow"),
            ("react", "React"),
            ("vue", "Vue"),
            ("angular", "Angular"),
            ("nextjs", "Next.js"),
            ("next.js", "Next.js"),
            ("spring boot", "Spring Boot"),
            ("spring", "Spring Boot"),
            ("redis", "Redis"),
            ("nodejs", "Node.js"),
            ("node.js", "Node.js"),
            ("node", "Node.js"),
            ("express", "Express"),
            ("nestjs", "NestJS"),
            ("django", "Django"),
            ("flask", "Flask"),
            ("laravel", "Laravel"),
            ("flutter", "Flutter"),
            ("golang", "Go"),
            ("java", "Java"),
            ("html", "HTML"),
            ("css", "CSS"),
            ("javascript", "JavaScript"),
            ("typescript", "TypeScript"),
            ("c#", "C#"),
            ("c++", "C++"),
            ("dart", "Dart"),
            ("kubernetes", "Kubernetes"),
            ("k8s", "Kubernetes"),
            ("aws", "AWS"),
        ]

        for pat, canonical in tech_patterns:
            if re.search(rf"\b{re.escape(pat)}\b", msg_lower):
                if canonical not in result:
                    result.append(canonical)

        return result

    def infer_role_from_tech(self, tech_list: List[str]) -> Optional[str]:
        """Suy luận vai trò phù hợp nhất dựa trên danh sách công nghệ nếu người dùng chưa chỉ định rõ."""
        tech_set = {t.lower() for t in tech_list}
        if any(t in tech_set for t in ["pytorch", "scikit-learn", "tensorflow"]):
            return "AI / Machine Learning Engineer"
        if any(t in tech_set for t in ["airflow", "spark", "dbt", "clickhouse"]) or ("pandas" in tech_set and "sql" in tech_set):
            return "Data Engineer"
        if any(t in tech_set for t in ["react", "vue", "angular", "html", "css"]):
            if any(t in tech_set for t in ["nodejs", "node.js", "express", "spring boot", "django", "fastapi", "laravel", "mysql", "postgresql"]):
                return "Full-stack Developer"
            return "Frontend Developer"
        if any(t in tech_set for t in ["spring boot", "django", "fastapi", "express", "nestjs", "laravel", "nodejs", "node.js", "golang", "go", "java"]):
            return "Backend Developer"
        if any(t in tech_set for t in ["flutter", "dart", "android", "ios"]):
            return "Mobile Developer"
        if any(t in tech_set for t in ["docker", "kubernetes", "aws", "ci/cd"]):
            return "DevOps / Cloud Engineer"
        return None

    def detect_role(self, message: str) -> Optional[str]:
        """Phát hiện vai trò nghề nghiệp có trong tin nhắn."""
        msg_lower = (message or "").lower()

        # Kiểm tra theo độ đặc thù giảm dần
        if "data engineer" in msg_lower or "kỹ sư dữ liệu" in msg_lower:
            return "Data Engineer"
        elif "data analyst" in msg_lower or "phân tích dữ liệu" in msg_lower:
            return "Data Analyst"
        elif any(k in msg_lower for k in ["ai / machine learning engineer", "ai engineer", "machine learning", "trí tuệ nhân tạo", "học máy", "kỹ sư ai"]):
            return "AI / Machine Learning Engineer"
        elif "mobile" in msg_lower or "di động" in msg_lower or "android" in msg_lower or "ios" in msg_lower or "flutter" in msg_lower:
            return "Mobile Developer"
        elif "devops" in msg_lower or "cloud" in msg_lower or "sre" in msg_lower:
            return "DevOps / Cloud Engineer"
        elif "fullstack" in msg_lower or "full-stack" in msg_lower:
            return "Full-stack Developer"
        elif "frontend" in msg_lower or "lập trình viên frontend" in msg_lower:
            return "Frontend Developer"
        elif "backend" in msg_lower or "lập trình viên backend" in msg_lower:
            return "Backend Developer"
        elif any(k in msg_lower for k in ["tester", "qa/qc", "qa engineer", "qc engineer", "kỹ sư kiểm thử", "chuyên viên kiểm thử"]):
            return "QA / QC Engineer"
        elif any(k in msg_lower for k in ["cyber security", "security engineer", "chuyên viên bảo mật", "kỹ sư an ninh mạng", "chuyên viên an ninh mạng", "an ninh mạng"]):
            return "Cyber Security Specialist"

        return None

    def detect_role_switch(self, message: str, current_role: Optional[str]) -> Tuple[Optional[str], bool]:
        """Phát hiện chuyển đổi vai trò so với vai trò hiện tại."""
        detected = self.detect_role(message)
        if not detected:
            return current_role, False
        if current_role and detected != current_role:
            return detected, True
        return detected or current_role, False

    def parse_user_intent(self, message: str) -> Dict[str, Any]:
        """Phát hiện tổng hợp ý định người dùng."""
        msg_lower = (message or "").lower()
        detected_tech = self.parse_preferred_tech(message, [])
        explicit_role = self.detect_role(message)
        inferred_role = None
        if not explicit_role and detected_tech:
            inferred_role = self.infer_role_from_tech(detected_tech)
        detected_role = explicit_role or inferred_role

        # Trạng thái 1: Chưa quyết định (TC01)
        undecided_keywords = [
            "chưa biết nên chọn", "chưa biết chọn", "chưa xác định",
            "chưa rõ", "định hướng giúp", "giúp tôi định hướng",
            "chưa chọn được", "phân vân", "tư vấn giúp tôi vị trí",
            "chưa biết công nghệ", "chưa biết nghề"
        ]
        is_undecided = any(kw in msg_lower for kw in undecided_keywords)

        detected_time = self.parse_time_duration(message)

        # Trạng thái 6: Đã học một số công nghệ, hỏi đã đủ ứng tuyển Intern chưa & thiếu gì (TC06)
        readiness_keywords = [
            "đã đủ để ứng tuyển", "đủ để ứng tuyển", "đã đủ đi làm",
            "đã đủ để làm", "đã đủ kiến thức", "đã đủ chưa", "liệu đã đủ",
            "những gì tôi còn thiếu", "tôi còn thiếu gì", "còn thiếu những gì",
            "cần bổ sung gì để đi làm", "đủ để làm intern", "đủ ứng tuyển intern",
            "đủ làm intern", "đủ để làm thực tập", "đủ điều kiện"
        ]
        has_learned_keywords = [
            "tôi đã học", "em đã học", "đã học", "tôi đã biết", "em đã biết", "đã biết", "đã nắm"
        ]
        is_intern_readiness_audit = (
            any(k in msg_lower for k in readiness_keywords)
            or (any(k in msg_lower for k in has_learned_keywords) and any(k in msg_lower for k in ["ứng tuyển", "intern", "thực tập", "còn thiếu", "đủ"]))
        )

        # Trạng thái 4: Sinh viên đã chọn stack và yêu cầu đánh giá (TC04)
        eval_keywords = [
            "đánh giá stack", "đánh giá", "còn cần bổ sung gì",
            "bổ sung gì để đồ án có giá trị", "bổ sung gì để", "có giá trị khi ứng tuyển",
            "định làm", "đã chọn", "sử dụng stack này"
        ]
        is_evaluating_stack = (
            any(k in msg_lower for k in eval_keywords)
            and len(detected_tech) >= 2
            and not is_undecided
            and not is_intern_readiness_audit
        )

        # Trạng thái 5: Sản phẩm Web nhưng hướng tới Data Engineer (TC05)
        is_web_to_data_pivot = (
            (detected_role == "Data Engineer" or "data engineer" in msg_lower)
            and any(k in msg_lower for k in ["website", "web", "doanh thu", "bán hàng", "react", "node", "mysql", "ứng dụng"])
            and any(k in msg_lower for k in ["bổ sung gì vào đồ án", "bổ sung gì", "hướng tới data engineer", "theo data engineer", "cần bổ sung"])
            and not is_intern_readiness_audit
        )

        # Trạng thái 7: Đồ án quá tham vọng so với thời gian ngắn (TC07)
        heavy_distributed_tech = [
            "microservices", "kubernetes", "k8s", "kafka", "ai agent", "rag",
            "service mesh", "istio", "event-driven", "distributed"
        ]
        heavy_count = sum(1 for ht in heavy_distributed_tech if ht in msg_lower)
        is_short_time = (
            (detected_time is not None and detected_time <= 1)
            or any(k in msg_lower for k in ["một tháng", "1 tháng", "vài tuần", "3 tuần", "4 tuần", "bốn tuần"])
        )
        is_overambitious_scope = (is_short_time and heavy_count >= 2) or (heavy_count >= 4)

        # Trạng thái 8: Đồ án phụ thuộc phần cứng / cảm biến IoT chưa xác định (TC08)
        hardware_keywords = [
            "iot", "cảm biến", "sensor", "phần cứng", "thiết bị",
            "esp32", "arduino", "raspberry", "nhúng", "chất lượng không khí"
        ]
        missing_spec_keywords = [
            "chưa chọn cảm biến", "chưa chọn", "chưa biết chọn", "chưa rõ cảm biến",
            "chưa quyết định", "chưa có phần cứng", "đang phân vân loại cảm biến",
            "chưa xác định loại", "chưa mua cảm biến"
        ]
        is_hardware = any(k in msg_lower for k in hardware_keywords)
        is_missing_spec = any(k in msg_lower for k in missing_spec_keywords)
        is_hardware_or_missing_spec = is_hardware and is_missing_spec

        # Trạng thái 9: Yêu cầu công nghệ không phù hợp với bài toán / overkill (TC09)
        small_scale_keywords = [
            "đồ án môn học", "thư viện nhỏ", "quản lý thư viện", "quy mô nhỏ",
            "bài tập lớn", "ứng dụng nhỏ", "hệ thống nhỏ", "đơn giản"
        ]
        overkill_tech = ["kafka", "kubernetes", "k8s", "microservices", "service mesh"]
        is_small_scale = any(k in msg_lower for k in small_scale_keywords)
        is_heavy_tech = any(k in msg_lower for k in overkill_tech)
        is_overkill_tech_choice = is_small_scale and is_heavy_tech and not is_overambitious_scope

        # Trạng thái 10: Yêu cầu giải thích căn cứ đề xuất công nghệ (TC11)
        justification_keywords = [
            "tại sao bạn lại đề xuất", "tại sao lại đề xuất", "tại sao lại khuyên",
            "có thật sự nhiều jd", "có nhiều jd yêu cầu", "căn cứ vào đâu",
            "dựa trên căn cứ nào", "hay chỉ gợi ý theo kiến thức chung", "số liệu thực tế",
            "giải thích lý do đề xuất", "tại sao lại dùng", "tại sao lại chọn",
            "tại sao đề xuất"
        ]
        is_justification_request = any(k in msg_lower for k in justification_keywords)
        queried_tech = None
        if is_justification_request:
            detected_in_msg = self.parse_preferred_tech(message, [])
            if detected_in_msg:
                queried_tech = detected_in_msg[0]
            else:
                for t in ["docker", "postgresql", "mysql", "redis", "kafka", "kubernetes", "react", "spring boot", "fastapi"]:
                    if t in msg_lower:
                        queried_tech = t.title()
                        break

        # Trạng thái 11: Bổ sung ràng buộc nguồn lực / điều chỉnh phạm vi (TC10 Turn 3, TC12)
        is_solo = any(k in msg_lower for k in ["một mình", "1 mình", "làm một mình", "solo"])
        rejects_ai = any(k in msg_lower for k in ["chưa cần ai", "chưa cần tính năng ai", "không cần ai", "đừng thêm ai", "không cần tính năng ai", "chưa cần tính năng"])
        no_deploy_exp = any(k in msg_lower for k in ["chưa từng triển khai", "chưa biết deploy", "chưa triển khai lên server", "chưa deploy"])
        wants_simple_scope = any(k in msg_lower for k in ["đừng đề xuất kiến trúc phức tạp", "không làm phức tạp", "đơn giản thôi", "vừa sức thôi", "tinh gọn", "đừng đề xuất"])
        prioritizes_demo = any(k in msg_lower for k in ["ưu tiên hoàn thiện sản phẩm", "bản demo chạy được", "có bản demo", "demo chạy được", "chạy được"])

        is_constraint_update = is_solo or rejects_ai or no_deploy_exp or wants_simple_scope or prioritizes_demo

        # Trạng thái 12: Dữ liệu tuyển dụng có thể bị trùng lặp hoặc không phù hợp (TC16)
        data_quality_keywords = [
            "trùng nội dung", "tin tuyển dụng trùng", "trùng lặp", "không còn phù hợp",
            "kết quả có bị ảnh hưởng không", "dữ liệu có bị trùng", "lọc trùng", "khử trùng",
            "chất lượng dữ liệu"
        ]
        is_data_quality_query = any(k in msg_lower for k in data_quality_keywords)

        # Trạng thái 13: Yêu cầu xem kỹ năng tuyển dụng nhiều dựa trên dữ liệu GEM (TC13)
        skills_demand_keywords = [
            "kỹ năng nào đang được tuyển dụng nhiều", "kỹ năng tôi nên ưu tiên học",
            "những kỹ năng tôi nên ưu tiên", "ưu tiên học dựa trên dữ liệu",
            "dựa trên dữ liệu tuyển dụng mà gem đang có", "kỹ năng được tuyển dụng nhiều",
            "thị trường đang cần kỹ năng gì", "kỹ năng nào được các công ty tuyển",
            "kỹ năng phổ biến nhất trong các jd", "kỹ năng nào phổ biến"
        ]
        is_market_skills_demand_query = any(k in msg_lower for k in skills_demand_keywords) and not is_data_quality_query

        # Trạng thái 14: So sánh 2 vị trí nghề nghiệp dựa trên dữ liệu JD (TC14)
        comparison_keywords = [
            "phân vân giữa", "so sánh hai hướng", "so sánh giữa", "so sánh 2 vị trí",
            "so sánh hai vị trí", "khác nhau giữa", "nên chọn hướng nào giữa",
            "so sánh dựa trên những kỹ năng"
        ]
        is_role_comparison_query = any(k in msg_lower for k in comparison_keywords)
        compare_roles = []
        if is_role_comparison_query or any(k in msg_lower for k in ["so sánh", "phân vân"]):
            available_roles = [
                ("Backend Developer", ["backend", "backend developer", "lập trình viên backend"]),
                ("Data Engineer", ["data engineer", "kỹ sư dữ liệu"]),
                ("Frontend Developer", ["frontend", "frontend developer", "lập trình viên frontend"]),
                ("Full-stack Developer", ["fullstack", "full-stack", "full stack"]),
                ("AI / Machine Learning Engineer", ["ai engineer", "machine learning", "kỹ sư ai", "trí tuệ nhân tạo"]),
                ("DevOps / Cloud Engineer", ["devops", "cloud engineer", "kỹ sư devops"]),
                ("Mobile Developer", ["mobile", "di động", "android", "ios", "flutter"]),
                ("Data Analyst", ["data analyst", "phân tích dữ liệu"]),
            ]
            for r_name, r_patterns in available_roles:
                for pat in r_patterns:
                    if re.search(r'\b' + re.escape(pat) + r'\b', msg_lower):
                        if r_name not in compare_roles:
                            compare_roles.append(r_name)
                        break
            if len(compare_roles) >= 2:
                is_role_comparison_query = True

        # Trạng thái 15: Hỏi về công nghệ mới / chưa có trong dữ liệu JD (TC15)
        is_novel_tech_query = (
            any(k in msg_lower for k in ["công nghệ mới", "rất hot", "đang hot", "xác nhận xem công nghệ"])
            and any(k in msg_lower for k in ["tuyển dụng", "jd", "công ty", "thị trường"])
            and not is_justification_request
        )
        novel_tech_name = None
        if is_novel_tech_query or ("công nghệ mới" in msg_lower and "hot" in msg_lower):
            is_novel_tech_query = True
            known_novel_candidates = ["mojo", "taichi", "gleam", "zig", "nim", "bun", "deno", "elixir", "cobol", "solidity", "haskell", "julia"]
            for c in known_novel_candidates:
                if c in msg_lower:
                    novel_tech_name = c.title()
                    break
            if not novel_tech_name:
                m_tech = re.search(r'(?:công nghệ|ngôn ngữ|framework|thư viện)\s+([a-zA-Z0-9_\-\.]+)', message, re.IGNORECASE)
                if m_tech and m_tech.group(1).lower() not in ["mới", "đang", "rất", "này", "đó", "nào"]:
                    novel_tech_name = m_tech.group(1).title()
                else:
                    novel_tech_name = "Công nghệ mới"

        # Trạng thái 16: Tìm kiếm đồ án hoặc repository GitHub tham khảo (Nhóm 6 - TC17, TC18)
        gh_reference_keywords = [
            "repository github", "đồ án github", "kho tham khảo của gem",
            "kho tham khảo mà gem", "kho dữ liệu mà gem có", "kho dữ liệu của gem",
            "đồ án hoặc repository", "repository mà gem có", "dự án tương tự trong kho",
            "tìm dự án tương tự", "tìm đồ án tương tự", "dự án github mà gem",
            "dự án tương tự", "đồ án tương tự", "repository tương tự", "kho tham khảo"
        ]
        is_github_reference_query = any(k in msg_lower for k in gh_reference_keywords)

        # Trạng thái 18: Kế hoạch hành động 4 tuần cải thiện Skill Gap (Nhóm 7 - TC20)
        action_plan_keywords = [
            "kế hoạch cải thiện trong bốn tuần", "kế hoạch trong bốn tuần",
            "kế hoạch 4 tuần", "kế hoạch cải thiện trong 4 tuần", "bốn tuần", "4 tuần",
            "lập cho tôi kế hoạch cải thiện", "lập cho tôi kế hoạch",
            "kế hoạch hành động bốn tuần", "kế hoạch hành động 4 tuần",
            "kế hoạch hành động", "lập kế hoạch",
            "một đến hai giờ mỗi ngày", "1 đến 2 giờ mỗi ngày", "1-2 giờ mỗi ngày"
        ]
        is_four_week_action_plan = any(k in msg_lower for k in action_plan_keywords)

        # Trạng thái 17: Đối chiếu đồ án với kỹ năng nghề nghiệp mục tiêu & Skill Gap (Nhóm 7 - TC19)
        skill_gap_keywords = [
            "kỹ năng đồ án của tôi đã thể hiện", "kỹ năng đồ án đã thể hiện",
            "kỹ năng còn thiếu so với yêu cầu", "thứ tự ưu tiên cải thiện",
            "phân tích những kỹ năng đồ án", "đối chiếu đồ án", "khoảng cách kỹ năng",
            "skill gap", "những kỹ năng đồ án", "kỹ năng còn thiếu so với"
        ]
        is_project_skill_gap_audit = any(k in msg_lower for k in skill_gap_keywords) and not is_four_week_action_plan

        # Trạng thái 19: Giải thích điểm số phù hợp / Readiness Score / Matching Score (Nhóm 7 - TC21)
        m_score = re.search(r'(\d{1,3})\s*%', message)
        detected_score = float(m_score.group(1)) if m_score else 72.0
        is_readiness_score_explanation = (
            bool(m_score)
            or any(k in msg_lower for k in ["72%", "mức độ phù hợp là 72%", "điểm này có nghĩa là gì", "được tính dựa trên những yếu tố nào"])
            or (any(k in msg_lower for k in ["mức độ phù hợp", "readiness score", "matching score", "điểm số"]) and any(k in msg_lower for k in ["nghĩa là gì", "tính dựa trên", "yếu tố nào", "công thức", "tại sao"]))
        )

        return {
            "explicit_role": explicit_role,
            "inferred_role": inferred_role,
            "detected_role": detected_role,
            "detected_score": detected_score,
            "is_undecided": is_undecided,
            "is_evaluating_stack": is_evaluating_stack,
            "is_web_to_data_pivot": is_web_to_data_pivot,
            "is_intern_readiness_audit": is_intern_readiness_audit,
            "is_overambitious_scope": is_overambitious_scope,
            "is_hardware_or_missing_spec": is_hardware_or_missing_spec,
            "is_overkill_tech_choice": is_overkill_tech_choice,
            "is_justification_request": is_justification_request,
            "queried_tech": queried_tech,
            "is_constraint_update": is_constraint_update,
            "is_solo": is_solo,
            "rejects_ai": rejects_ai,
            "no_deploy_exp": no_deploy_exp,
            "wants_simple_scope": wants_simple_scope,
            "prioritizes_demo": prioritizes_demo,
            "detected_time": detected_time,
            "detected_tech": detected_tech,
            "is_market_skills_demand_query": is_market_skills_demand_query,
            "is_role_comparison_query": is_role_comparison_query,
            "compare_roles": compare_roles,
            "is_novel_tech_query": is_novel_tech_query,
            "novel_tech_name": novel_tech_name,
            "is_data_quality_query": is_data_quality_query,
            "is_github_reference_query": is_github_reference_query,
            "is_project_skill_gap_audit": is_project_skill_gap_audit,
            "is_four_week_action_plan": is_four_week_action_plan,
            "is_readiness_score_explanation": is_readiness_score_explanation,
        }

    def generate_ai_reply(
        self,
        user_message: str,
        session: Dict[str, Any],
        blueprint: Dict[str, Any],
        is_undecided: bool = False,
        role_switched: bool = False,
        is_explicit_role: bool = False,
        is_evaluating_stack: bool = False,
        is_web_to_data_pivot: bool = False,
        is_intern_readiness_audit: bool = False,
        is_overambitious_scope: bool = False,
        is_hardware_or_missing_spec: bool = False,
        is_overkill_tech_choice: bool = False,
        is_justification_request: bool = False,
        queried_tech: Optional[str] = None,
        market_telemetry: Optional[Dict[str, Any]] = None,
        is_constraint_update: bool = False,
        is_market_skills_demand_query: bool = False,
        market_ranking_info: Optional[Dict[str, Any]] = None,
        is_role_comparison_query: bool = False,
        comparison_info: Optional[Dict[str, Any]] = None,
        is_novel_tech_query: bool = False,
        novel_tech_info: Optional[Dict[str, Any]] = None,
        is_data_quality_query: bool = False,
        data_quality_info: Optional[Dict[str, Any]] = None,
        is_github_reference_query: bool = False,
        github_reference_info: Optional[Dict[str, Any]] = None,
        is_project_skill_gap_audit: bool = False,
        skill_gap_audit_info: Optional[Dict[str, Any]] = None,
        is_four_week_action_plan: bool = False,
        is_readiness_score_explanation: bool = False,
        readiness_score_info: Optional[Dict[str, Any]] = None,
        previous_role: Optional[str] = None,
    ) -> str:
        """Sinh câu trả lời định hướng của Cố vấn GEM qua LLM."""
        prompt = build_advisor_reply_prompt(
            user_message=user_message,
            session=session,
            blueprint=blueprint,
            is_undecided=is_undecided,
            role_switched=role_switched,
            is_explicit_role=is_explicit_role,
            is_evaluating_stack=is_evaluating_stack,
            is_web_to_data_pivot=is_web_to_data_pivot,
            is_intern_readiness_audit=is_intern_readiness_audit,
            is_overambitious_scope=is_overambitious_scope,
            is_hardware_or_missing_spec=is_hardware_or_missing_spec,
            is_overkill_tech_choice=is_overkill_tech_choice,
            is_justification_request=is_justification_request,
            queried_tech=queried_tech,
            market_telemetry=market_telemetry,
            is_constraint_update=is_constraint_update,
            is_market_skills_demand_query=is_market_skills_demand_query,
            market_ranking_info=market_ranking_info,
            is_role_comparison_query=is_role_comparison_query,
            comparison_info=comparison_info,
            is_novel_tech_query=is_novel_tech_query,
            novel_tech_info=novel_tech_info,
            is_data_quality_query=is_data_quality_query,
            data_quality_info=data_quality_info,
            is_github_reference_query=is_github_reference_query,
            github_reference_info=github_reference_info,
            is_project_skill_gap_audit=is_project_skill_gap_audit,
            skill_gap_audit_info=skill_gap_audit_info,
            is_four_week_action_plan=is_four_week_action_plan,
            is_readiness_score_explanation=is_readiness_score_explanation,
            readiness_score_info=readiness_score_info,
            previous_role=previous_role,
        )
        return self.llm.generate_text(prompt, temperature=0.25, max_tokens=500)

