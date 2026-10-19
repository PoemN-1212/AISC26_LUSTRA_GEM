"""
Role-Skill Profiler Module for GEM.
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Xây dựng Hồ sơ Kỹ năng theo từng vị trí nghề nghiệp chuyên môn (Role-Skill Profiles)
từ dữ liệu tuyển dụng TopCV đã được chuẩn hóa.

Tái cấu trúc:
- Đảm bảo tính toàn vẹn dữ liệu: loại bỏ hoàn toàn fallback lấy toàn bộ kỹ năng thị trường.
- Chuẩn hóa đối sánh ID giữa cleaned_job_postings và extracted_skills.
- Thống kê tỷ lệ nhu cầu (demand_pct) chuẩn mực toán học và ngữ nghĩa.
- Phân định Core vs Booster dựa trên tần suất nhu cầu và tham số top_k.
"""

import os
import re
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
from sqlalchemy import create_engine
from gem_pipeline.normalization.normalizer import SkillNormalizer
from gem_pipeline.market.role_taxonomy import ROLE_TAXONOMY


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

        # 1. Lấy tất cả JDs đã làm sạch
        query_jds = "SELECT id, title, content_clean FROM cleaned_job_postings;"
        df_jds = pd.read_sql(query_jds, self.engine)

        if df_jds.empty:
            return {
                "role": target_role,
                "domain": "",
                "total_jds": 0,
                "core_skills": [],
                "boost_skills": [],
                "abilities": [],
                "summary": "Không tìm thấy dữ liệu tuyển dụng trong hệ thống."
            }

        # Gán domain và specific_role cho từng JD
        classified = df_jds.apply(
            lambda r: self.classify_role(r["title"], r["content_clean"]), axis=1
        )
        df_jds["domain"] = [c[0] for c in classified]
        df_jds["specific_role"] = [c[1] for c in classified]

        # Lọc theo target_role (khớp specific_role hoặc domain)
        role_jds = df_jds[
            (df_jds["specific_role"].str.lower() == target_role.lower())
            | (df_jds["domain"].str.lower() == target_role.lower())
        ]

        if role_jds.empty:
            # Fallback nếu tên có chứa từ khóa chính
            kw = target_role.lower().split()[0]
            role_jds = df_jds[
                df_jds["specific_role"].str.lower().str.contains(kw, na=False)
                | df_jds["domain"].str.lower().str.contains(kw, na=False)
            ]

        total_role_jds = len(role_jds)
        domain_name = role_jds["domain"].iloc[0] if not role_jds.empty else "Software Engineering"

        if total_role_jds == 0:
            profile_empty = {
                "role": target_role,
                "domain": domain_name,
                "total_jds": 0,
                "core_skills": [],
                "boost_skills": [],
                "abilities": [],
                "summary": f"Chưa có đủ số lượng JD tuyển dụng đặc thù cho vị trí '{target_role}'.",
            }
            self._profiles_cache[cache_key] = profile_empty
            return profile_empty

        # Tạo tập ID hợp lệ chuẩn tắc (hỗ trợ cả id số và định dạng 'JD_{id}')
        valid_jd_ids = set()
        for j_id in role_jds["id"]:
            s_id = str(j_id).strip()
            valid_jd_ids.add(s_id)
            valid_jd_ids.add(f"JD_{s_id}")

        # 2. Lấy các kỹ năng đã trích xuất ACCEPT từ các JD
        query_skills = """
        SELECT doc_id, skill, type, evidence
        FROM extracted_skills
        WHERE source_type = 'job' AND verifier_status = 'ACCEPT';
        """
        df_skills = pd.read_sql(query_skills, self.engine)

        if df_skills.empty:
            profile_no_skills = {
                "role": target_role,
                "domain": domain_name,
                "total_jds": total_role_jds,
                "core_skills": [],
                "boost_skills": [],
                "abilities": [],
                "summary": "Chưa có kỹ năng nào được trích xuất cho nhóm JD này."
            }
            self._profiles_cache[cache_key] = profile_no_skills
            return profile_no_skills

        # 3. Lọc chính xác theo khóa ID hợp lệ của role (Tuyệt đối KHÔNG fallback sang df_skills toàn bộ)
        role_skills_df = df_skills[df_skills["doc_id"].astype(str).isin(valid_jd_ids)].copy()

        if role_skills_df.empty:
            profile_no_match = {
                "role": target_role,
                "domain": domain_name,
                "total_jds": total_role_jds,
                "core_skills": [],
                "boost_skills": [],
                "abilities": [],
                "summary": f"Tìm thấy {total_role_jds} JD cho '{target_role}' nhưng dữ liệu kỹ năng đang trong tiến trình trích xuất."
            }
            self._profiles_cache[cache_key] = profile_no_match
            return profile_no_match

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
        # Tỷ lệ nhu cầu chính xác (không vượt quá 100%)
        distinct_counts["demand_pct"] = (
            distinct_counts["jd_count"] / max(total_role_jds, 1)
        ) * 100
        distinct_counts["demand_pct"] = distinct_counts["demand_pct"].clip(upper=100.0).round(1)
        distinct_counts = distinct_counts.sort_values(by="demand_pct", ascending=False)

        # Tách nhóm TECHNOLOGY vs ABILITY
        tech_skills = distinct_counts[distinct_counts["type"] == "TECHNOLOGY"].to_dict("records")
        ability_skills = distinct_counts[distinct_counts["type"] == "ABILITY"].to_dict("records")

        # Xác định Core vs Booster dựa trên tham số top_k và ngưỡng nhu cầu
        # Core: Kỹ năng có demand cao (>= 30% hoặc tối thiểu top 6-8 kỹ năng đầu)
        core_cutoff = min(8, max(5, int(top_k * 0.35)))
        core_tech = tech_skills[:core_cutoff]
        boost_tech = tech_skills[core_cutoff:top_k]

        profile_result = {
            "role": target_role,
            "domain": domain_name,
            "total_jds": total_role_jds,
            "core_skills": core_tech,
            "boost_skills": boost_tech,
            "abilities": ability_skills[:10],
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
        domain_counts["share_pct"] = ((domain_counts["jd_count"] / len(df_jds)) * 100).round(1)

        # Thống kê theo Specific Role
        role_counts = df_jds.groupby(["domain", "specific_role"]).size().reset_index(name="jd_count")
        role_counts["share_pct"] = ((role_counts["jd_count"] / len(df_jds)) * 100).round(1)
        role_counts = role_counts.sort_values(by="jd_count", ascending=False)

        return {
            "total_jds": len(df_jds),
            "domains": domain_counts.to_dict("records"),
            "roles": role_counts.to_dict("records"),
        }
