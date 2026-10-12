"""
Role-Skill Profiler Module for GEM.
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Xây dựng Hồ sơ Kỹ năng theo từng vị trí nghề nghiệp chuyên môn (Role-Skill Profiles)
từ dữ liệu tuyển dụng TopCV đã được chuẩn hóa.

Cấu trúc Phân tầng 2 Cấp (Hierarchical Career Taxonomy):
Cấp 1: NGHỀ (Domain / Lĩnh vực lớn)
Cấp 2: VỊ TRÍ CHUYÊN MÔN (Specific Job Roles)
Bao gồm:
1. Software Engineering (Backend, Frontend, Fullstack, Mobile, Blockchain, Software Engineer)
2. Software Testing & QA (Automation Tester, Manual Tester, QA Engineer, PQA, Game Tester)
3. Artificial Intelligence (AI Engineer, AI Researcher, Data Labeling)
4. Data Science & Big Data (Data Engineer, Data Analyst, Data Scientist)
5. IT Infrastructure & Operations (DevOps, Cloud Engineer, System Engineer, Network, DBA, IT Support)
6. Information Security (Cyber Security, IT Security, AppSec)
7. IoT & Embedded Systems (Embedded Engineer, IoT Engineer)
8. Product & Business Analysis (Business Analyst - BA, Product Owner, Product Manager)
9. Software Design & Creative (UI/UX Designer, Graphic Design, 3D Modeler)
10. Game Development (Game Developer, AR/VR Developer, Game Design)
11. IT Project Management (IT Project Manager, Scrum Master, BrSE, IT Comtor)
12. IT Management & Architecture (Solution Architect, Software Architect, Tech Lead)
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
from sqlalchemy import create_engine
from gem_pipeline.normalization.normalizer import SkillNormalizer


# CẤU TRÚC PHÂN TẦNG: NGHỀ -> VỊ TRÍ CHUYÊN MÔN KÈM PATTERNS NHẬN DIỆN
ROLE_TAXONOMY = {
    "Software Engineering": {
        "Backend Developer": [
            r"\b(backend|back-end|back end|java developer|python developer|nodejs developer|golang developer|php developer|\.net developer|c# developer|ruby developer)\b",
            r"\b(lập trình viên backend|phát triển backend|kỹ sư backend)\b",
        ],
        "Frontend Developer": [
            r"\b(frontend|front-end|front end|reactjs|vuejs|angular|web developer frontend)\b",
            r"\b(lập trình viên frontend|phát triển giao diện|web frontend)\b",
        ],
        "Fullstack Developer": [
            r"\b(fullstack|full-stack|full stack|web developer fullstack)\b",
            r"\b(lập trình viên fullstack|kỹ sư fullstack|toàn diện)\b",
        ],
        "Mobile Developer": [
            r"\b(mobile developer|android|ios|flutter|react native|swift|kotlin mobile|mobile app)\b",
            r"\b(lập trình viên di động|lập trình viên mobile|app developer)\b",
        ],
        "Blockchain Engineer": [
            r"\b(blockchain|web3|solidity|smart contract|crypto developer)\b",
            r"\b(kỹ sư blockchain|lập trình viên blockchain)\b",
        ],
        "Software Engineer (General)": [
            r"\b(software engineer|software developer|lập trình viên phần mềm|kỹ sư phần mềm)\b",
        ],
    },
    "Artificial Intelligence (AI)": {
        "AI Engineer": [
            r"\b(ai engineer|machine learning engineer|ml engineer|deep learning engineer|trí tuệ nhân tạo|học máy)\b",
            r"\b(kỹ sư ai|kỹ sư trí tuệ nhân tạo|kỹ sư học máy)\b",
        ],
        "AI Researcher": [
            r"\b(ai researcher|research scientist|computer vision engineer|nlp engineer|llm engineer|generative ai)\b",
            r"\b(nghiên cứu ai|nghiên cứu trí tuệ nhân tạo)\b",
        ],
        "Data Labeling": [
            r"\b(data labeling|gán nhãn dữ liệu|dán nhãn dữ liệu|chú thích dữ liệu)\b",
        ],
    },
    "Data Science": {
        "Data Engineer": [
            r"\b(data engineer|kỹ sư dữ liệu|etl developer|big data engineer|data pipeline)\b",
        ],
        "Data Analyst": [
            r"\b(data analyst|chuyên viên phân tích dữ liệu|bi analyst|business intelligence|phân tích dữ liệu)\b",
        ],
        "Data Scientist": [
            r"\b(data scientist|khoa học dữ liệu|chuyên viên khoa học dữ liệu)\b",
        ],
    },
    "Software Testing": {
        "Automation Tester": [
            r"\b(automation test|automation tester|kiểm thử tự động|qc automation|qa automation)\b",
        ],
        "Manual Tester": [
            r"\b(manual test|manual tester|kiểm thử thủ công|qc manual)\b",
        ],
        "QA / QC Engineer": [
            r"\b(qa engineer|qc engineer|software tester|tester|quality assurance|chuyên viên kiểm thử|kiểm thử phần mềm)\b",
        ],
        "Game Tester": [
            r"\b(game tester|kiểm thử game)\b",
        ],
        "Process Quality Assurance (PQA)": [
            r"\b(pqa|process quality assurance|đảm bảo chất lượng quy trình)\b",
        ],
    },
    "IT Infrastructure and Operations": {
        "DevOps Engineer": [
            r"\b(devops|devops engineer|sre|site reliability engineer|ci/cd engineer)\b",
        ],
        "Cloud Engineer": [
            r"\b(cloud engineer|aws engineer|azure engineer|gcp engineer|kỹ sư điện toán đám mây)\b",
        ],
        "System Engineer / Admin": [
            r"\b(system engineer|system administrator|sysadmin|quản trị hệ thống|kỹ sư hệ thống|linux admin)\b",
        ],
        "Network Engineer": [
            r"\b(network engineer|kỹ sư mạng|quản trị mạng|network security)\b",
        ],
        "Database Administrator (DBA)": [
            r"\b(dba|database administrator|quản trị cơ sở dữ liệu)\b",
        ],
        "IT Helpdesk / IT Support": [
            r"\b(it helpdesk|it support|kỹ thuật it|hỗ trợ kỹ thuật it|it onsite)\b",
        ],
    },
    "Information Security": {
        "Cyber Security Specialist": [
            r"\b(cyber security|chuyên viên cyber security|an ninh mạng|bảo mật thông tin|soc analyst|chuyên viên bảo mật)\b",
        ],
        "Application Security Engineer": [
            r"\b(application security|appsec|bảo mật ứng dụng|kiểm thử bảo mật|pentest|penetration testing)\b",
        ],
    },
    "Product Management": {
        "Business Analyst (BA)": [
            r"\b(business analyst|ba|phân tích nghiệp vụ|chuyên viên phân tích nghiệp vụ|product analyst)\b",
        ],
        "Product Owner / Product Manager": [
            r"\b(product owner|product manager|quản lý sản phẩm|chủ sở hữu sản phẩm)\b",
        ],
    },
    "Software Design": {
        "UI/UX Designer": [
            r"\b(ui/ux|ui ux|ux/ui|ui designer|ux designer|product designer|thiết kế giao diện)\b",
        ],
        "Graphic & 3D Designer": [
            r"\b(graphic design|thiết kế đồ họa|3d modeler|dựng hình 3d|concept artist|illustration|animation)\b",
        ],
    },
    "IoT / Embedded Engineer": {
        "Embedded Engineer": [
            r"\b(embedded|lập trình nhúng|kỹ sư nhúng|firmware|vi điều khiển|plc|c/c\+\+ embedded)\b",
        ],
        "IoT Engineer": [
            r"\b(iot|internet of things|kỹ sư iot)\b",
        ],
    },
    "Game Development": {
        "Game Developer": [
            r"\b(game developer|lập trình game|unity|unreal engine|game programmer)\b",
        ],
        "AR/VR Developer": [
            r"\b(ar/vr|augmented reality|virtual reality|thực tế ảo)\b",
        ],
    },
    "IT Project Management": {
        "IT Project Manager": [
            r"\b(it project manager|quản lý dự án it|pm it)\b",
        ],
        "Scrum Master": [
            r"\b(scrum master|agile coach)\b",
        ],
        "Bridge Software Engineer (BrSE)": [
            r"\b(brse|bridge se|kỹ sư cầu nối)\b",
        ],
        "IT Comtor": [
            r"\b(it comtor|comtor|thông dịch it)\b",
        ],
    },
    "IT Architecture & Leadership": {
        "Software / Solution Architect": [
            r"\b(solution architect|software architect|system architect|kiến trúc sư giải pháp|kiến trúc sư phần mềm)\b",
        ],
        "Technical Lead / Manager": [
            r"\b(tech lead|technical lead|technical manager|truởng nhóm kỹ thuật|trưởng nhóm lập trình)\b",
        ],
    },
    "Sales IT & Consultant": {
        "Sales IT / IT Consultant": [
            r"\b(sales it|kinh doanh phần mềm|tư vấn it|it consultant|bán hàng phần mềm|kinh doanh hosting)\b",
        ],
    },
}


class RoleSkillProfiler:
    """
    Quản lý phân loại JD theo Hệ thống Nghề & Vị trí Chuyên môn TopCV,
    tổng hợp hồ sơ kỹ năng (Core Must-Have vs Differentiating Boosters)
    dựa trên dữ liệu thực tế.
    """

    def __init__(self, db_uri: Optional[str] = None):
        self.db_uri = db_uri or self._get_default_db_uri()
        self.engine = create_engine(self.db_uri)
        self.normalizer = SkillNormalizer()
        self.taxonomy = ROLE_TAXONOMY
        self._profiles_cache: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _get_default_db_uri() -> str:
        pg_user = os.getenv("POSTGRES_USER", "gem_admin")
        pg_pass = os.getenv("POSTGRES_PASSWORD", "gem_secret_password")
        pg_host = os.getenv("POSTGRES_HOST", "localhost")
        pg_port = os.getenv("POSTGRES_PORT", "5432")
        pg_name = os.getenv("POSTGRES_DB", "gem_database")
        return f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_name}"

    def classify_role(self, title: str, content: str = "") -> Tuple[str, str]:
        """
        Phân loại một JD vào cặp (Domain, Specific Role).
        Ưu tiên đối sánh Tiêu đề trước, sau đó đối sánh nội dung tóm tắt.
        
        Returns:
            Tuple[domain, specific_role] (ví dụ: ("Software Engineering", "Backend Developer"))
        """
        title_lower = (title or "").lower()
        content_lower = (content or "").lower()[:600]

        # Vòng 1: Kiểm tra đối sánh trên Title
        for domain, roles in self.taxonomy.items():
            for role_name, patterns in roles.items():
                for pat in patterns:
                    if re.search(pat, title_lower, re.IGNORECASE):
                        return domain, role_name

        # Vòng 2: Kiểm tra đối sánh trên Content nếu Title chung chung
        for domain, roles in self.taxonomy.items():
            for role_name, patterns in roles.items():
                for pat in patterns:
                    if re.search(pat, content_lower, re.IGNORECASE):
                        return domain, role_name

        return "Software Engineering", "Software Engineer (General)"

    def get_role_skill_profile(self, target_role: str, top_k: int = 25) -> Dict[str, Any]:
        """
        Tổng hợp hồ sơ kỹ năng cho một vị trí nghề nghiệp chuyên môn (hoặc domain) từ PostgreSQL:
        - Tổng số JD thuộc vị trí này
        - Top Core Must-Have Skills (Tần suất xuất hiện cao nhất)
        - Top Differentiating Skills (Kỹ năng tạo lợi thế cạnh tranh)
        - Phân nhóm TECHNOLOGY vs ABILITY
        """
        cache_key = f"{target_role}_{top_k}"
        if cache_key in self._profiles_cache:
            return self._profiles_cache[cache_key]

        # 1. Lấy tất cả JDs
        query_jds = "SELECT id, title, content_clean FROM cleaned_job_postings;"
        df_jds = pd.read_sql(query_jds, self.engine)

        if df_jds.empty:
            return {"role": target_role, "domain": "", "total_jds": 0, "core_skills": [], "boost_skills": []}

        # Gán domain và specific_role cho từng JD
        classified = df_jds.apply(
            lambda r: self.classify_role(r["title"], r["content_clean"]), axis=1
        )
        df_jds["domain"] = [c[0] for c in classified]
        df_jds["specific_role"] = [c[1] for c in classified]

        # Lọc theo target_role (có thể khớp specific_role hoặc domain)
        role_jds = df_jds[
            (df_jds["specific_role"].str.lower() == target_role.lower())
            | (df_jds["domain"].str.lower() == target_role.lower())
        ]

        if role_jds.empty:
            # Fallback nếu tên có chứa từ khóa
            kw = target_role.lower().split()[0]
            role_jds = df_jds[
                df_jds["specific_role"].str.lower().str.contains(kw, na=False)
                | df_jds["domain"].str.lower().str.contains(kw, na=False)
            ]

        total_role_jds = len(role_jds)
        domain_name = role_jds["domain"].iloc[0] if not role_jds.empty else "Software Engineering"

        if total_role_jds == 0:
            return {
                "role": target_role,
                "domain": domain_name,
                "total_jds": 0,
                "core_skills": [],
                "boost_skills": [],
                "summary": "Chưa có đủ số lượng JD tuyển dụng đặc thù cho vị trí này.",
            }

        role_jd_ids = set(role_jds["id"].astype(str))

        # 2. Lấy các kỹ năng đã trích xuất từ các JD này
        query_skills = """
        SELECT doc_id, skill, type, evidence
        FROM extracted_skills
        WHERE source_type = 'job' AND verifier_status = 'ACCEPT';
        """
        df_skills = pd.read_sql(query_skills, self.engine)

        if df_skills.empty:
            return {
                "role": target_role,
                "domain": domain_name,
                "total_jds": total_role_jds,
                "core_skills": [],
                "boost_skills": [],
            }

        def match_jd_id(doc_id_val: str) -> bool:
            num = re.sub(r"[^\d]", "", str(doc_id_val))
            return num in role_jd_ids or str(doc_id_val) in role_jd_ids

        role_skills_df = df_skills[df_skills["doc_id"].apply(match_jd_id)].copy()

        if role_skills_df.empty:
            role_skills_df = df_skills.copy()

        # Chuẩn hóa Canonical
        role_skills_df["canonical_name"] = role_skills_df["skill"].apply(
            lambda s: self.normalizer.normalize(str(s))[0]
        )

        # Đếm số lượng distinct JD cho mỗi kỹ năng trong role này
        distinct_counts = (
            role_skills_df.groupby(["canonical_name", "type"])["doc_id"]
            .nunique()
            .reset_index(name="jd_count")
        )
        distinct_counts["demand_pct"] = (distinct_counts["jd_count"] / max(total_role_jds, 1)) * 100
        distinct_counts = distinct_counts.sort_values(by="demand_pct", ascending=False)

        # Tách Core Must-Have (Top cao nhất) và Differentiating Boosters
        tech_skills = distinct_counts[distinct_counts["type"] == "TECHNOLOGY"].to_dict("records")
        ability_skills = distinct_counts[distinct_counts["type"] == "ABILITY"].to_dict("records")

        core_tech = tech_skills[:8]
        boost_tech = tech_skills[8:20]

        profile_result = {
            "role": target_role,
            "domain": domain_name,
            "total_jds": total_role_jds,
            "core_skills": core_tech,
            "boost_skills": boost_tech,
            "abilities": ability_skills[:8],
        }
        self._profiles_cache[cache_key] = profile_result
        return profile_result

    def get_all_role_summaries(self) -> Dict[str, Any]:
        """
        Thống kê tổng quan số lượng JD phân bổ trên từng Lĩnh vực (Domain)
        và từng Vị trí chuyên môn (Specific Role).
        """
        query_jds = "SELECT id, title, content_clean FROM cleaned_job_postings;"
        df_jds = pd.read_sql(query_jds, self.engine)

        if df_jds.empty:
            return {"domains": [], "roles": [], "total_jds": 0}

        classified = df_jds.apply(
            lambda r: self.classify_role(r["title"], r["content_clean"]), axis=1
        )
        df_jds["domain"] = [c[0] for c in classified]
        df_jds["specific_role"] = [c[1] for c in classified]

        # Thống kê theo Domain
        domain_counts = df_jds["domain"].value_counts().reset_index()
        domain_counts.columns = ["domain", "jd_count"]
        domain_counts["share_pct"] = (domain_counts["jd_count"] / len(df_jds)) * 100

        # Thống kê theo Specific Role
        role_counts = df_jds.groupby(["domain", "specific_role"]).size().reset_index(name="jd_count")
        role_counts["share_pct"] = (role_counts["jd_count"] / len(df_jds)) * 100
        role_counts = role_counts.sort_values(by="jd_count", ascending=False)

        return {
            "total_jds": len(df_jds),
            "domains": domain_counts.to_dict("records"),
            "roles": role_counts.to_dict("records"),
        }
