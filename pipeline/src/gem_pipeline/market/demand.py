"""
GEM Market Demand Engine (Module Tính toán Nhu cầu Kỹ năng Thị trường)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Công thức chuẩn khoa học:
Demand(skill) = (Số JD phân biệt yêu cầu skill / Tổng số JD phân tích) * 100%
Đảm bảo: Một JD nhắc lại một skill 10 lần cũng chỉ đóng góp +1 vào nhu cầu tuyển dụng.
"""

import os
import sys
from typing import Dict, List, Any, Optional
import pandas as pd
from sqlalchemy import create_engine, text

from gem_pipeline.normalization.normalizer import normalizer


class MarketDemandCalculator:
    """
    Tính toán nhu cầu tuyển dụng thị trường (Distinct-JD Demand)
    từ dữ liệu kỹ năng đã được kiểm định trong PostgreSQL.
    """

    def __init__(self, db_uri: Optional[str] = None):
        self.db_uri = db_uri or self._get_default_db_uri()
        self.engine = create_engine(self.db_uri)

    @staticmethod
    def _get_default_db_uri() -> str:
        pg_user = os.getenv("POSTGRES_USER", "gem_admin")
        pg_pass = os.getenv("POSTGRES_PASSWORD", "gem_secret_password")
        pg_host = os.getenv("POSTGRES_HOST", "localhost")
        pg_port = os.getenv("POSTGRES_PORT", "5432")
        pg_name = os.getenv("POSTGRES_DB", "gem_database")
        return f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_name}"

    def compute_market_demand(self, top_k: int = 50) -> pd.DataFrame:
        """
        Tính toán nhu cầu tuyển dụng của từng Canonical Skill.
        
        Returns:
            DataFrame gồm: [canonical_name, category, jd_count, total_jds, demand_pct, sample_evidences]
        """
        query = """
        SELECT source_id, doc_id, skill, type, evidence
        FROM extracted_skills
        WHERE source_type = 'job' AND verifier_status = 'ACCEPT';
        """
        df_raw = pd.read_sql(query, self.engine)

        if df_raw.empty:
            return pd.DataFrame(columns=["canonical_name", "category", "jd_count", "total_jds", "demand_pct"])

        # Tính tổng số JD phân biệt có trong bảng
        total_unique_jds = df_raw["source_id"].nunique()

        # Chuẩn hóa từng kỹ năng về Canonical Skill
        records = []
        for _, row in df_raw.iterrows():
            raw_s = str(row["skill"]).strip()
            s_type = str(row["type"]).strip().upper()
            c_name, category, conf = normalizer.normalize(raw_s, s_type)
            if c_name:
                records.append({
                    "jd_id": row["source_id"],
                    "canonical_name": c_name,
                    "category": category,
                    "type": s_type,
                    "evidence": row["evidence"]
                })

        df_norm = pd.DataFrame(records)

        # Gom nhóm theo (canonical_name, category) và đếm số JD phân biệt
        grouped = df_norm.groupby(["canonical_name", "category", "type"]).agg(
            jd_count=("jd_id", "nunique"),
            sample_evidence=("evidence", lambda evs: list(set(evs))[:3])
        ).reset_index()

        # Tính tỷ lệ phần trăm Demand
        grouped["total_jds"] = total_unique_jds
        grouped["demand_pct"] = (grouped["jd_count"] / total_unique_jds * 100).round(2)

        # Sắp xếp theo nhu cầu giảm dần
        grouped = grouped.sort_values(by="demand_pct", ascending=False).reset_index(drop=True)

        if top_k > 0:
            return grouped.head(top_k)
        return grouped

    def get_category_breakdown(self) -> pd.DataFrame:
        """Thống kê tổng số lượng kỹ năng và phân bố theo từng danh mục kỹ thuật."""
        df_demand = self.compute_market_demand(top_k=0)
        if df_demand.empty:
            return pd.DataFrame()

        breakdown = df_demand.groupby("category").agg(
            total_skills=("canonical_name", "count"),
            avg_demand=("demand_pct", "mean"),
            top_skill=("canonical_name", "first")
        ).reset_index().sort_values(by="total_skills", ascending=False)
        return breakdown
