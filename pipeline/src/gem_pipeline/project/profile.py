"""
GEM Student Project Profile Builder (Module Xây dựng Hồ sơ Kỹ năng Sinh viên)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Xây dựng hồ sơ kỹ năng có bằng chứng (Evidence-grounded Profile)
từ các đồ án GitHub của sinh viên.
"""

import os
from typing import Dict, List, Set, Any, Optional
import pandas as pd
from sqlalchemy import create_engine, text
from gem_pipeline.normalization.normalizer import normalizer


class StudentProfileBuilder:
    """
    Trích xuất và tổng hợp hồ sơ năng lực của sinh viên
    dựa trên các đồ án GitHub đã được phân tích.
    """

    def __init__(self, db_uri: Optional[str] = None):
        pg_user = os.getenv("POSTGRES_USER", "gem_admin")
        pg_pass = os.getenv("POSTGRES_PASSWORD", "gem_secret_password")
        pg_host = os.getenv("POSTGRES_HOST", "localhost")
        pg_port = os.getenv("POSTGRES_PORT", "5432")
        pg_name = os.getenv("POSTGRES_DB", "gem_database")
        self.db_uri = db_uri or f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_name}"
        self.engine = create_engine(self.db_uri)

    def build_profile_from_project_id(self, project_id: str) -> Dict[str, Any]:
        """
        Xây dựng hồ sơ kỹ năng cho một đồ án cụ thể từ database.
        """
        query = text("""
        SELECT doc_id, title, skill, type, evidence, context
        FROM extracted_skills
        WHERE source_type = 'project' AND source_id = :pid AND verifier_status = 'ACCEPT';
        """)
        with self.engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"pid": str(project_id)})

        if df.empty:
            # Thử tìm theo doc_id (ví dụ 'GH_1')
            query_doc = text("""
            SELECT doc_id, title, skill, type, evidence, context
            FROM extracted_skills
            WHERE doc_id = :did AND verifier_status = 'ACCEPT';
            """)
            with self.engine.connect() as conn:
                df = pd.read_sql(query_doc, conn, params={"did": str(project_id)})

        if df.empty:
            return {
                "project_id": project_id,
                "project_title": "Unknown Project",
                "skills": [],
                "canonical_skills": set(),
                "tech_stack": {}
            }

        project_title = df["title"].iloc[0]
        canonical_skills_map: Dict[str, Dict[str, Any]] = {}

        for _, row in df.iterrows():
            raw_s = str(row["skill"]).strip()
            s_type = str(row["type"]).strip().upper()
            c_name, category, _ = normalizer.normalize(raw_s, s_type)

            if not c_name:
                continue

            if c_name not in canonical_skills_map:
                canonical_skills_map[c_name] = {
                    "canonical_name": c_name,
                    "category": category,
                    "type": s_type,
                    "evidences": set()
                }
            canonical_skills_map[c_name]["evidences"].add(row["evidence"])

        # Format kết quả
        formatted_skills = []
        for c_name, data in canonical_skills_map.items():
            formatted_skills.append({
                "canonical_name": c_name,
                "category": data["category"],
                "type": data["type"],
                "evidences": list(data["evidences"])
            })

        # Phân loại theo category
        tech_stack: Dict[str, List[str]] = {}
        for s in formatted_skills:
            cat = s["category"]
            tech_stack.setdefault(cat, []).append(s["canonical_name"])

        return {
            "project_id": project_id,
            "project_title": project_title,
            "total_skills": len(formatted_skills),
            "canonical_skills": set(canonical_skills_map.keys()),
            "skills": formatted_skills,
            "tech_stack": tech_stack
        }
