"""
GEM Skill Normalizer (Module Chuẩn hóa thực thể kỹ năng)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
Chức năng: Ánh xạ thực thể thô (extracted skill) về Canonical Skill chuẩn và phân loại danh mục.
"""

import re
from typing import Tuple, Optional
from gem_pipeline.normalization.aliases import CANONICAL_ALIASES_MAP


class SkillNormalizer:
    """
    Chuẩn hóa các cách viết khác nhau của cùng một kỹ năng về tên chuẩn (Canonical Skill).
    Áp dụng 3 tầng kiểm tra:
    1. Exact Alias Lookup (Tra cứu từ điển chuẩn hóa O(1))
    2. Version Stripping & Regex Heuristics (Gọt số phiên bản: Python 3.10 -> Python)
    3. Title-casing & Formatting Fallback
    """

    def __init__(self):
        self.aliases_map = CANONICAL_ALIASES_MAP

    def normalize(self, raw_skill: str, skill_type: str = "TECHNOLOGY") -> Tuple[str, str, float]:
        """
        Chuẩn hóa một kỹ năng thô.
        
        Args:
            raw_skill: Chuỗi kỹ năng thô (ví dụ: 'reactjs', 'Postgres', 'Python 3.11')
            skill_type: 'TECHNOLOGY' hoặc 'ABILITY'
            
        Returns:
            Tuple[canonical_name, category, confidence]
        """
        if not raw_skill or not raw_skill.strip():
            return "", "OTHER", 0.0

        cleaned = raw_skill.strip()
        cleaned_lower = cleaned.lower()

        # Đối với nhóm ABILITY (Năng lực / Hành động kỹ thuật)
        if skill_type.upper() == "ABILITY":
            # Chuẩn hóa khoảng trắng và viết thường
            norm_ability = " ".join(cleaned.split()).lower()
            return norm_ability, "ABILITY", 1.0

        # TẦNG 1: Tra cứu từ điển trực tiếp
        if cleaned_lower in self.aliases_map:
            canonical_name, category = self.aliases_map[cleaned_lower]
            return canonical_name, category, 1.0

        # TẦNG 2: Gọt số phiên bản và ký tự thừa
        # Ví dụ: "Python 3.x", "React 18", "Java 17", "Vue 3", "Bootstrap v5"
        version_stripped = re.sub(r"\s+(?:v|version\s*)?(\d+(?:\.\d+)*(?:\.x)?)$", "", cleaned_lower, flags=re.IGNORECASE).strip()
        if version_stripped in self.aliases_map:
            canonical_name, category = self.aliases_map[version_stripped]
            return canonical_name, category, 0.95

        # Tách gạch chéo hoặc dấu phẩy nếu còn sót (lấy phần đầu)
        if "/" in cleaned_lower:
            parts = [p.strip() for p in cleaned_lower.split("/") if p.strip()]
            if parts and parts[0] in self.aliases_map:
                canonical_name, category = self.aliases_map[parts[0]]
                return canonical_name, category, 0.9

        # TẦNG 3: Fallback định dạng chuẩn hóa
        # Viết hoa chữ cái đầu hoặc giữ nguyên chữ viết hoa kỹ thuật
        if cleaned.isupper() or len(cleaned) <= 4:
            fallback_name = cleaned.upper()
        else:
            fallback_name = cleaned.title()

        return fallback_name, "TECHNOLOGY_GENERAL", 0.7


# Khởi tạo singleton instance
normalizer = SkillNormalizer()
