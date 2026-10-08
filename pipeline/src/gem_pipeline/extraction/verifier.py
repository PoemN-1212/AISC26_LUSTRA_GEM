"""
GEM Extraction Verifier (Bộ thẩm định kỹ năng trích xuất)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Cài đặt 5 lớp kiểm định logic tất định (Deterministic Verification):
1. Evidence exists? (Bằng chứng có tồn tại nguyên văn trong văn bản gốc không)
2. Valid boundary? (Ranh giới tối thiểu có nghĩa, loại bỏ filler words như 'thành thạo', 'kinh nghiệm')
3. Valid type? (Bắt buộc thuộc taxonomy: TECHNOLOGY hoặc ABILITY)
4. Duplicate? (Khử trùng lặp kỹ năng trong cùng một tài liệu)
5. Hallucination & Negative Rules? (Phát hiện ảo giác, loại bỏ chức danh, tên cty, phúc lợi, soft skills)
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


# 1. Danh sách các từ đệm/filler cần cắt tỉa (Boundary Triggers)
FILLER_PATTERNS = [
    # Tiếng Việt
    r"^có\s+(?:trên\s+)?(?:\d+\s+năm\s+)?kinh\s+nghiệm\s+(?:với|về|trong)?\s*",
    r"^(?:thành\s+thạo|nắm\s+vững|nắm\s+chắc|hiểu\s+biết\s+(?:sâu\s+)?về|quen\s+thuộc\s+với)\s*",
    r"^(?:ưu\s+tiên|yêu\s+cầu|bắt\s+buộc|có\s+khả\s+năng|biết\s+sử\s+dụng|sử\s+dụng\s+tốt)\s*",
    r"^(?:nhiệt\s+huyết|tự\s+giác|có\s+tinh\s+thần|chủ\s+động)\s*",
    # Tiếng Anh
    r"^(?:have\s+)?(?:proven\s+)?(?:strong\s+)?(?:hands-on\s+)?experience\s+(?:with|in|of)\s*",
    r"^(?:proficient\s+in|familiar\s+with|knowledge\s+of|strong\s+understanding\s+of)\s*",
    r"^(?:skilled\s+in|ability\s+to|good\s+command\s+of|deep\s+understanding\s+of)\s*",
    r"^(?:required\s+to|preferred\s+to)\s*",
]

# 2. Danh sách Negative Rules: Chức danh, tên công ty, chế độ phúc lợi, soft skills mơ hồ
NEGATIVE_KEYWORDS = [
    # Chức danh công việc (Job Roles)
    "software engineer", "developer", "backend developer", "frontend developer", "fullstack developer",
    "mobile developer", "devops engineer", "data engineer", "data scientist", "ai engineer",
    "qa engineer", "qc engineer", "tester", "product owner", "project manager", "scrum master",
    "tech lead", "team lead", "solution architect", "lập trình viên", "kỹ sư phần mềm",
    "chuyên viên", "nhân viên", "thực tập sinh", "intern", "fresher", "junior", "senior",
    # Tên công ty / nền tảng tuyển dụng
    "topcv", "vietnamworks", "itviec", "linkedin", "fpt", "viettel", "vnpt", "vng",
    "shopee", "tiki", "lazada", "momo", "vnpay", "grab", "tập đoàn", "công ty",
    # Chế độ, phúc lợi & hành chính
    "bhxh", "bhyt", "lương tháng 13", "thưởng tết", "phụ cấp", "cơm trưa", "du lịch hàng năm",
    "khám sức khỏe", "teambuilding", "macbook", "laptop", "gửi xe miễn phí", "thời gian làm việc",
    # Kỹ năng mềm ngoài phạm vi kỹ thuật
    "chăm chỉ", "trung thực", "nhiệt tình", "hòa đồng", "chịu được áp lực", "ham học hỏi",
    "tinh thần trách nhiệm", "giao tiếp tốt", "kỹ năng thuyết trình", "làm việc độc lập"
]

# 3. Chuẩn hóa Type hợp lệ
VALID_TYPES = {"TECHNOLOGY", "ABILITY"}
TYPE_SYNONYMS = {
    "TECH": "TECHNOLOGY",
    "TOOL": "TECHNOLOGY",
    "FRAMEWORK": "TECHNOLOGY",
    "LANGUAGE": "TECHNOLOGY",
    "DATABASE": "TECHNOLOGY",
    "CLOUD": "TECHNOLOGY",
    "SKILL": "ABILITY",
    "ACTION": "ABILITY",
    "COMPETENCE": "ABILITY"
}


@dataclass
class VerificationResult:
    is_valid: bool
    status: str                         # ACCEPTED | MODIFIED | REJECTED
    skill: str
    evidence: str
    type: str                           # TECHNOLOGY | ABILITY
    context: str                        # required | preferred | mentioned
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    issues: List[str] = field(default_factory=list)
    rejection_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SkillExtractionVerifier:
    """
    Bộ thẩm định kỹ năng trích xuất 5 bước độc lập và tất định.
    """

    def __init__(self, case_sensitive_evidence: bool = False):
        self.case_sensitive = case_sensitive_evidence

    def clean_boundary(self, text: str) -> str:
        """Cắt bỏ filler words / từ đệm đầu câu để thu về Minimal Meaningful Span."""
        cleaned = text.strip()
        for pattern in FILLER_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
        # Loại bỏ dấu câu thừa đầu và cuối span
        cleaned = re.sub(r"^[\s,;:.\-–—]+|[\s,;:.\-–—]+$", "", cleaned)
        return cleaned

    def check_negative_rules(self, skill: str, evidence: str) -> Optional[str]:
        """Kiểm tra vi phạm Negative Rules (chức danh, phúc lợi, cty, soft skills)."""
        lower_skill = skill.lower().strip()
        lower_evidence = evidence.lower().strip()

        for neg in NEGATIVE_KEYWORDS:
            # So sánh chính xác hoặc là cụm từ chính
            if lower_skill == neg or lower_evidence == neg:
                return f"Vi phạm Negative Rule: trùng với từ cấm/chức danh/phúc lợi '{neg}'"
            if lower_skill.startswith(neg + " ") or lower_skill.endswith(" " + neg):
                return f"Vi phạm Negative Rule: chứa chức danh/từ cấm '{neg}'"

        return None

    def verify_single(self, candidate: Dict[str, Any], source_text: str) -> VerificationResult:
        """
        Thực hiện kiểm định chi tiết cho một candidate skill.
        """
        issues: List[str] = []
        raw_evidence = (candidate.get("evidence") or "").strip()
        raw_skill = (candidate.get("skill") or "").strip()
        raw_type = (candidate.get("type") or "TECHNOLOGY").strip().upper()
        raw_context = (candidate.get("context") or "required").strip().lower()

        # [BƯỚC 1]: Kiểm tra Evidence tồn tại (Evidence exists?)
        if not raw_evidence:
            return VerificationResult(
                is_valid=False,
                status="REJECTED",
                skill=raw_skill,
                evidence=raw_evidence,
                type=raw_type,
                context=raw_context,
                issues=["EMPTY_EVIDENCE"],
                rejection_reason="Evidence rỗng"
            )

        # Tìm vị trí xuất hiện của evidence trong source_text
        if self.case_sensitive:
            idx = source_text.find(raw_evidence)
        else:
            idx = source_text.lower().find(raw_evidence.lower())

        if idx == -1:
            return VerificationResult(
                is_valid=False,
                status="REJECTED",
                skill=raw_skill,
                evidence=raw_evidence,
                type=raw_type,
                context=raw_context,
                issues=["HALLUCINATION_EVIDENCE_NOT_FOUND"],
                rejection_reason=f"Ảo giác (Hallucination): evidence '{raw_evidence}' không tồn tại trong văn bản gốc"
            )

        start_char = idx
        end_char = idx + len(raw_evidence)

        # [BƯỚC 2]: Kiểm tra và cắt tỉa ranh giới (Valid boundary / Minimal span)
        cleaned_evidence = self.clean_boundary(raw_evidence)
        cleaned_skill = self.clean_boundary(raw_skill)

        is_modified = False
        if cleaned_evidence != raw_evidence or cleaned_skill != raw_skill:
            issues.append("TRIMMED_FILLER_WORDS")
            is_modified = True

        if len(cleaned_skill) < 2:
            return VerificationResult(
                is_valid=False,
                status="REJECTED",
                skill=cleaned_skill,
                evidence=cleaned_evidence,
                type=raw_type,
                context=raw_context,
                issues=["BOUNDARY_TOO_SHORT"],
                rejection_reason="Sau khi cắt tỉa từ đệm, độ dài kỹ năng quá ngắn (< 2 ký tự)"
            )

        # [BƯỚC 3]: Kiểm tra Type hợp lệ (Valid type?)
        final_type = TYPE_SYNONYMS.get(raw_type, raw_type)
        if final_type not in VALID_TYPES:
            return VerificationResult(
                is_valid=False,
                status="REJECTED",
                skill=cleaned_skill,
                evidence=cleaned_evidence,
                type=raw_type,
                context=raw_context,
                issues=["INVALID_TAXONOMY_TYPE"],
                rejection_reason=f"Type '{raw_type}' không thuộc taxonomy chuẩn (chỉ chấp nhận TECHNOLOGY hoặc ABILITY)"
            )

        # [BƯỚC 4]: Kiểm tra Negative Rules & Hallucination
        neg_reason = self.check_negative_rules(cleaned_skill, cleaned_evidence)
        if neg_reason:
            return VerificationResult(
                is_valid=False,
                status="REJECTED",
                skill=cleaned_skill,
                evidence=cleaned_evidence,
                type=final_type,
                context=raw_context,
                issues=["VIOLATE_NEGATIVE_RULES"],
                rejection_reason=neg_reason
            )

        # Hợp lệ
        return VerificationResult(
            is_valid=True,
            status="MODIFIED" if is_modified else "ACCEPTED",
            skill=cleaned_skill,
            evidence=cleaned_evidence,
            type=final_type,
            context=raw_context,
            start_char=start_char,
            end_char=end_char,
            issues=issues,
            rejection_reason=None
        )

    def verify_document_skills(
        self,
        candidates: List[Dict[str, Any]],
        source_text: str
    ) -> List[VerificationResult]:
        """
        Kiểm định toàn bộ danh sách candidate skills của một tài liệu,
        bao gồm cả bước 4: Khử trùng lặp (Deduplication).
        """
        verified_list: List[VerificationResult] = []
        seen_skills: Dict[str, VerificationResult] = {}

        # Mức độ ưu tiên của context khi gộp trùng lặp
        context_priority = {"required": 3, "preferred": 2, "mentioned": 1}

        for cand in candidates:
            res = self.verify_single(cand, source_text)
            if not res.is_valid:
                verified_list.append(res)
                continue

            # Kiểm tra trùng lặp (Duplicate Check) theo chuẩn hóa chữ thường + type
            key = f"{res.skill.lower()}::{res.type}"
            if key in seen_skills:
                # Trùng lặp! Cập nhật context nếu candidate mới có độ ưu tiên cao hơn
                existing = seen_skills[key]
                existing.issues.append(f"DUPLICATE_MERGED_FROM_{res.evidence}")
                if context_priority.get(res.context, 1) > context_priority.get(existing.context, 1):
                    existing.context = res.context
                # Bản ghi hiện tại bị đánh dấu là trùng lặp đã gộp
                res.is_valid = False
                res.status = "REJECTED"
                res.issues.append("DUPLICATE_SKILL_REMOVED")
                res.rejection_reason = f"Trùng lặp với kỹ năng đã duyệt trước đó '{existing.skill}'"
                verified_list.append(res)
            else:
                seen_skills[key] = res
                verified_list.append(res)

        return verified_list
