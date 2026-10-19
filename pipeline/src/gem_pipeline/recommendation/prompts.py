"""
Prompt templates and builders for GEM Recommendation Engine.
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
"""

from typing import Dict, List, Any, Optional


def build_idea_analysis_prompt(idea_text: str) -> str:
    """Prompt phân tích ý tưởng đề tài sinh viên, bóc tách module và gợi ý 3 hướng nghề nghiệp."""
    return f"""Bạn là Chuyên gia Cố vấn Công nghệ & Hướng nghiệp Đồ án CNTT của Nền tảng GEM (AISC 2026).
Nhiệm vụ: Phân tích sâu sắc ý tưởng đề tài đồ án của sinh viên sau:
Ý tưởng: "{idea_text}"

Hãy đánh giá nghiệp vụ, các thách thức kỹ thuật và lựa chọn 2-3 vị trí việc làm phù hợp nhất trong 34 vị trí việc làm IT (như Software Engineer, Backend Developer, Frontend Developer, Fullstack, AI / Machine Learning Engineer, Data Engineer, Data Analyst, Automation Tester, DevOps / Cloud, Embedded / IoT, Information Security, Business Analyst,...).

Trả về DUY NHẤT một chuỗi JSON hợp lệ theo đúng cấu trúc sau (không kèm markdown giải thích):
{{
  "domain": "Tên lĩnh vực chuyên sâu (ví dụ: Tài chính Ngân hàng & Kho Dữ liệu Lớn (FinTech / Big Data OLAP), Y tế & Trí tuệ nhân tạo (HealthTech / AI),...)",
  "problem_statement": "Tóm tắt ngắn gọn bài toán nghiệp vụ kỹ thuật sinh viên đang hướng tới",
  "technical_pillars": [
    {{"module": "Tên thành phần 1", "description": "Nhiệm vụ kỹ thuật chính"}},
    {{"module": "Tên thành phần 2", "description": "Nhiệm vụ kỹ thuật chính"}},
    {{"module": "Tên thành phần 3", "description": "Nhiệm vụ kỹ thuật chính"}},
    {{"module": "Tên thành phần 4", "description": "Nhiệm vụ kỹ thuật chính"}}
  ],
  "suggested_career_paths": [
    {{"role": "Tên vị trí việc làm 1", "reason": "Lý do đồ án này là điểm cộng lớn khi phỏng vấn vị trí này"}},
    {{"role": "Tên vị trí việc làm 2", "reason": "Lý do đồ án này là điểm cộng lớn khi phỏng vấn vị trí này"}},
    {{"role": "Tên vị trí việc làm 3", "reason": "Lý do đồ án này là điểm cộng lớn khi phỏng vấn vị trí này"}}
  ],
  "primary_role": "Vị trí được khuyến nghị hàng đầu trong 3 vị trí trên",
  "layer1_tailored": [
    {{"category": "Tầng 1 (Nguồn / Lưu trữ)", "tech": "Công nghệ cốt lõi", "purpose": "Mục đích sử dụng thực tế trong đồ án"}},
    {{"category": "Tầng 2 (Xử lý / Engine)", "tech": "Công nghệ cốt lõi", "purpose": "Mục đích sử dụng thực tế trong đồ án"}},
    {{"category": "Tầng 3 (Biến đổi / Pipeline)", "tech": "Công nghệ cốt lõi", "purpose": "Mục đích sử dụng thực tế trong đồ án"}},
    {{"category": "Tầng 4 (Giao diện / Khai thác)", "tech": "Công nghệ cốt lõi", "purpose": "Mục đích sử dụng thực tế trong đồ án"}}
  ],
  "layer3_extension": {{
    "title": "Tiêu đề phần mở rộng hướng nghiệp",
    "proposed_module": "Tên module chuyên sâu (vd: Mô hình AI phát hiện gian lận giao dịch)",
    "technologies": "Công nghệ sử dụng",
    "implementation_detail": "Phương pháp và thuật toán hiện thực cụ thể",
    "cv_value": "Giá trị khác biệt vượt trội khi phỏng vấn tuyển dụng"
  }}
}}
"""


def build_skill_gap_prompt(
    idea_text: str,
    domain: str,
    target_role: str,
    total_jds: int,
    core_skills: List[Dict[str, Any]],
    boost_skills: List[Dict[str, Any]],
) -> str:
    """Prompt phân tích độ vênh kỹ năng (Skill Gap) giữa đề tài và thị trường TopCV."""
    core_desc = [f"{s.get('canonical_name', '')} ({s.get('demand_pct', 0)}%)" for s in core_skills[:8]]
    boost_desc = [f"{s.get('canonical_name', '')} ({s.get('demand_pct', 0)}%)" for s in boost_skills[:6]]

    return f"""Bạn là Chuyên gia Cố vấn Khoa học Năng lực của "GEM - Nền tảng AI Định hướng và Khớp nối Năng lực Đồ án CNTT với Xu hướng Tuyển dụng" (AISC 2026 - UIT).

Đề tài đồ án sinh viên: "{idea_text}"
Miền nghiệp vụ: {domain}
Vị trí hướng tới: {target_role}

Dữ liệu tuyển dụng thực tế TopCV cho vị trí {target_role} ({total_jds} JDs):
- Kỹ năng cốt lõi thị trường: {core_desc}
- Kỹ năng tăng giá trị: {boost_desc}

Nhiệm vụ: Phân tích độ vênh kỹ năng (Skill Gap) giữa kế hoạch đề tài và yêu cầu thị trường:
1. "covered_skills": Những năng lực kỹ thuật mà phạm vi đề tài này TỰ NHIÊN ĐÒI HỎI PHẢI GIẢI QUYẾT trong thiết kế (ví dụ: làm web thương mại điện tử thì tự nhiên cần thiết kế CSDL quan hệ SQL, RESTful API, Git). Nêu rõ lý do kỹ thuật. (Lưu ý: Đây là phạm vi đề tài bao phủ, không tự động gán là sinh viên đã thành thạo).
2. "actionable_gaps": 2-3 kỹ năng thực chiến TopCV yêu cầu cao nhưng kế hoạch ban đầu CHƯA BAO PHỦ, và sinh viên CẦN BỔ SUNG để tăng cơ hội tuyển dụng. Bắt buộc có đủ:
   - "why_needed": Lý do kỹ thuật tại sao cần cho đề tài này.
   - "action_item": Hành động triển khai cụ thể trong code đồ án.
   - "proof_deliverable": Bằng chứng năng lực cụ thể cần nộp vào Git Repo (ví dụ: Dockerfile + docker-compose.yml, thư mục tests/ với coverage > 60%, OpenAPI spec, v.v.).
3. "deferred_or_overkill": 1-2 kỹ năng phổ biến trong ngành nhưng TẠM HOÃN hoặc TRÁNH DÙNG cho đồ án này để tránh over-engineering (ví dụ: Kafka khi traffic chưa lớn, Microservices khi chưa cần phân tán). Nêu rõ lý do cảnh báo.
4. "metrics":
   - "semantic_fit": Điểm phù hợp ngữ nghĩa bài toán với vai trò (thang 0-100, vd 85)
   - "baseline_coverage": Độ phủ kỹ năng ban đầu trước can thiệp (thang 0-100, vd 50)
   - "potential_coverage": Độ phủ kỹ năng tiềm năng sau can thiệp (thang 0-100, vd 82)

Trả về DUY NHẤT một chuỗi JSON hợp lệ theo đúng cấu trúc sau (không kèm markdown):
{{
  "metrics": {{
    "semantic_fit": 85,
    "baseline_coverage": 50,
    "potential_coverage": 82
  }},
  "covered_skills": [
    {{"skill": "Tên kỹ năng", "demand_pct": 65.0, "reason": "Lý do đồ án đã bao phủ"}}
  ],
  "actionable_gaps": [
    {{
      "skill": "Tên kỹ năng",
      "demand_pct": 32.0,
      "priority": "ƯU TIÊN CAO",
      "why_needed": "Lý do kỹ thuật cho đề tài này",
      "action_item": "Hành động cụ thể trong đồ án",
      "proof_deliverable": "Bằng chứng nộp vào Git Repo"
    }}
  ],
  "deferred_or_overkill": [
    {{
      "skill": "Tên kỹ năng",
      "demand_pct": 15.0,
      "verdict": "TẠM HOÃN",
      "reason": "Lý do cảnh báo tránh over-engineering"
    }}
  ]
}}
"""


def build_advisor_reply_prompt(
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
    """Prompt sinh lời khuyên hội thoại chuyên sâu cho Cố vấn GEM theo đúng kịch bản nghiệp vụ."""
    history_context = ""
    for h in session.get("history", [])[-2:]:
        history_context += f"Sinh viên: {h['user']}\nGEM: {h['gem']}\n"

    gap_rep = blueprint.get("skill_gap_report", {})
    covered_list = [f"{s['skill']} ({s.get('demand_pct', 0)}% JD)" for s in gap_rep.get("covered_skills", [])[:3]]
    gap_list = [f"- {s['skill']} ({s.get('demand_pct', 0)}% JD): {s.get('why_needed', '')} -> Bằng chứng nộp: {s.get('proof_deliverable', '')}" for s in gap_rep.get("actionable_gaps", [])[:3]]
    deferred_list = [f"- {s['skill']}: {s.get('reason', '')}" for s in gap_rep.get("deferred_or_overkill", [])[:2]]

    target_role = session.get("target_role", "Full-stack Developer")
    selected_tech = session.get("preferred_tech", [])
    tech_str = ", ".join(selected_tech) if selected_tech else "các công nghệ đã chọn"

    # =========================================================================
    # KỊCH BẢN TC16: CHẤT LƯỢNG DỮ LIỆU & CƠ CHẾ KHỬ TRÙNG (DATA QUALITY - NHÓM 5 - TC16 - P1)
    # =========================================================================
    if is_data_quality_query:
        dq_info = data_quality_info or {}
        dq_role = dq_info.get("target_role", target_role)
        total_jds = dq_info.get("total_jds", 88)
        top_skills = dq_info.get("top_skills", [])
        top_skills_lines = []
        for idx, s in enumerate(top_skills[:5], 1):
            top_skills_lines.append(f"{idx}. **{s['skill']}**: {s['demand_pct']}% JD ({s['jd_count']} / {total_jds} JD)")
        top_skills_str = "\n".join(top_skills_lines) if top_skills_lines else "- Java, PostgreSQL, REST API, Spring Boot, Docker/CI-CD"

        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC16 - P1): CHẤT LƯỢNG DỮ LIỆU & TÍNH MINH BẠCH VỀ CƠ CHẾ KHỬ TRÙNG (DATA QUALITY & DEDUPLICATION TRANSPARENCY).
Người dùng hỏi về các kỹ năng phổ biến nhất trong JD {dq_role} và đặt câu hỏi chất vấn: Nếu có nhiều tin tuyển dụng trùng nội dung hoặc một số JD không còn phù hợp, kết quả thống kê có bị ảnh hưởng không?
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ BẮT BUỘC các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, minh bạch, chuyên nghiệp):

### 1. Kỹ Năng Phổ Biến Nhất Dựa Trên Dữ Liệu Thực Tế ({dq_role})
- Trình bày danh sách kỹ năng phổ biến nhất từ kho dữ liệu phân tích gồm **{total_jds} tin tuyển dụng (JD)** của vị trí **{dq_role}**:
{top_skills_str}
- Nêu rõ các kỹ năng này đại diện cho tỷ lệ nhu cầu cao nhất trong tập khảo sát thực tế.

### 2. Phân Tích Rủi Ro Ảnh Hưởng Khi Tin Tuyển Dụng Bị Trùng Lặp Hoặc Không Phù Hợp
- Thẳng thắn thừa nhận cơ chế rủi ro: Nếu tin tuyển dụng bị trùng lặp (ví dụ: nhà tuyển dụng đăng lại tin nhiều lần trong tháng, hoặc đăng chéo lên nhiều kênh tuyển dụng khác nhau) hoặc lặp lại từ khóa trong cùng một JD:
  + Nếu hệ thống đếm từ khóa thô sơ (naive counting), một số kỹ năng xuất hiện dày đặc sẽ bị **đếm nhân đôi/nhân ba (overcounted)**, làm thổi phồng tỷ lệ phần trăm và làm lệch thứ hạng thực tế của các kỹ năng.
  + Các JD cũ hoặc không phù hợp (ví dụ JD tuyển lead/quản lý bị lẫn vào tuyển junior) có thể đưa vào các kỹ năng không sát với đối tượng sinh viên.

### 3. Các Cơ Chế Xử Lý Dữ Liệu Thực Tế Đã Được Triển Khai Trong Hệ Thống GEM
Khẳng định rõ GEM đã lường trước vấn đề này và triển khai 3 cơ chế xử lý dữ liệu chặt chẽ trong pipeline:
1. **Khử trùng bài đăng (Content Deduplication):** Lọc trùng lặp bài đăng trước khi phân tích dựa trên băm văn bản nội dung đã làm sạch (`content_clean`) kết hợp cặp định danh `(tiêu đề công việc, tên doanh nghiệp)`. Các tin đăng trùng lặp hoàn toàn sẽ bị loại bỏ.
2. **Đếm đơn nhất theo tài liệu (`DISTINCT doc_id`):** Ở tầng trích xuất kỹ năng, GEM áp dụng nguyên tắc `DISTINCT doc_id`. Nghĩa là dù trong một bài đăng tuyển dụng, từ khóa kỹ năng (ví dụ "Java" hay "SQL") xuất hiện lặp lại 10 lần, hệ thống cũng chỉ ghi nhận **đúng 1 lần duy nhất** cho JD đó. Do đó, tỷ lệ % phản ánh chính xác số lượng JD yêu cầu chứ không phải số lần nhắc từ khóa.
3. **Kiểm chứng ngữ cảnh bằng LLM Verifier (Skill Verifier Pipeline):** Sử dụng mô hình Verifier để kiểm chứng ngữ cảnh của từng kỹ năng được trích xuất. Hệ thống chỉ chấp nhận các kỹ năng có trạng thái `ACCEPT` (thực sự là yêu cầu kỹ thuật của công việc) và loại bỏ các trường hợp trích xuất nhầm hoặc ngoài ngữ cảnh kỹ thuật (`REJECT`).

### 4. Giới Hạn Của Dữ Liệu (Data Limitations & Transparency)
- Khẳng định trung thực: Dù đã áp dụng các cơ chế làm sạch và khử trùng nghiêm ngặt, GEM **TUYỆT ĐỐI KHÔNG tuyên bố dữ liệu là hoàn toàn sạch 100% không tì vết** hay đại diện tuyệt đối cho toàn bộ thị trường lao động Việt Nam.
- Dữ liệu phản ánh tập khảo sát thực tế ({total_jds} JD từ TopCV trong giai đoạn 2025-2026). Thị trường luôn có sự biến động và độ trễ tự nhiên. Kết quả của GEM đóng vai trò là **hệ quy chiếu tham khảo tin cậy và có căn cứ** để định hướng học tập, chứ không phải là chân lý đóng khung.
"""

    # =========================================================================
    # KỊCH BẢN TC15: KIỂM TRA CÔNG NGHỆ MỚI / THIẾU BẰNG CHỨNG DỮ LIỆU (MISSING MARKET EVIDENCE - NHÓM 5 - TC15 - P0)
    # =========================================================================
    elif is_novel_tech_query:
        nt_info = novel_tech_info or {}
        tech_name = nt_info.get("tech_name") or queried_tech or "công nghệ mới"
        is_found = nt_info.get("is_found", False)
        jd_count = nt_info.get("jd_count", 0)
        data_source = nt_info.get("data_source", "Kho dữ liệu tuyển dụng thực tế TopCV (1,732 JDs)")

        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC15 - P0): XỬ LÝ TRƯỜNG HỢP THIẾU BẰNG CHỨNG DỮ LIỆU THỊ TRƯỜNG CHO CÔNG NGHỆ MỚI ({tech_name}).
Người dùng hỏi về công nghệ mới ({tech_name}), nghe nói đang rất hot và muốn đưa vào đồ án, yêu cầu GEM xác nhận xem công nghệ đó có đang được các công ty tuyển dụng nhiều hay không dựa trên dữ liệu của GEM.
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ BẮT BUỘC các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, minh bạch, trung thực và khoa học):

### 1. Kiểm Tra & Báo Cáo Hiện Trạng Trong Dữ Liệu Tuyển Dụng GEM (Data Audit)
- Kiểm tra trực tiếp trong {data_source}:
  + Ghi nhận: Công nghệ **{tech_name}** hiện có **{jd_count} tin tuyển dụng** nhắc đến trong kho dữ liệu tuyển dụng hiện tại của GEM.
  + Tuyên bố minh bạch: **Hiện tại chưa đủ căn cứ dữ liệu tuyển dụng thực tế để xác nhận nhu cầu tuyển dụng của thị trường đối với {tech_name} tại Việt Nam**.
  + NGUYÊN TẮC BẮT BUỘC: **TUYỆT ĐỐI KHÔNG tự tạo số liệu, không bịa đặt xu hướng tuyển dụng**, không biến kiến thức chung của LLM thành số liệu thị trường của GEM. Khi dữ liệu là {jd_count}, phải nói rõ là {jd_count}.

### 2. Đánh Giá Giá Trị Kỹ Thuật (Technical Merits) — TÁCH BIỆT RẠCH RÒI Với Nhu Cầu Tuyển Dụng
- Đánh giá khách quan về mặt kỹ thuật của {tech_name}:
  + Phân tích điểm thú vị, tiềm năng hoặc ưu thế kỹ thuật nổi bật của nó (ví dụ: cú pháp hiện đại, hiệu năng tối ưu, tính năng an toàn bộ nhớ hoặc khả năng tích hợp AI/hệ thống).
  + NGUYÊN TẮC PHÂN ĐỊNH: **Tách biệt hoàn toàn giữa "Hữu ích / Tiềm năng về mặt kỹ thuật" và "Được thị trường doanh nghiệp tuyển dụng rộng rãi"**. Một công nghệ có thể rất đột phá về học thuật hoặc nghiên cứu, nhưng các doanh nghiệp cần thời gian dài để thẩm định tính ổn định, hệ sinh thái thư viện và chi phí chuyển đổi trước khi đưa vào sản xuất thương mại.

### 3. Lời Khuyên Định Hướng Cho Đồ Án Tốt Nghiệp (Pragmatic Project Guidance)
- Nếu mục tiêu chính của đồ án là **tối ưu cơ hội tuyển dụng và tìm việc làm ngay sau khi tốt nghiệp**:
  + Nên ưu tiên xây dựng phần khung sườn ứng dụng trên nền tảng các công nghệ đã được thị trường kiểm chứng với nhu cầu tuyển dụng lớn và ổn định (như Java, Python, Node.js, C#, Go...).
- Nếu sinh viên **đam mê khám phá và muốn đưa {tech_name} vào đồ án**:
  + Nên áp dụng {tech_name} dưới dạng **Module thử nghiệm độc lập (Proof of Concept - PoC)**, hoặc một dịch vụ phụ trợ / bài đo benchmark hiệu năng (performance comparison) so sánh với công nghệ truyền thống.
  + Tránh phụ thuộc toàn bộ hệ thống đồ án vào {tech_name} để phòng ngừa rủi ro thiếu thư viện hỗ trợ hoặc khó khăn khi tìm tài liệu xử lý lỗi (troubleshooting).

### 4. Phương Pháp Đánh Giá Tiếp Theo (Next Steps for Market Verification)
Gợi ý cho sinh viên các cách chủ động theo dõi và xác minh nhu cầu trong tương lai:
- Theo dõi các chỉ số quốc tế: GitHub Trending, Stack Overflow Developer Survey, TIOBE Index.
- Khảo sát trực tiếp định kỳ trên các trang tuyển dụng chuyên ngành (TopCV, ITviec, LinkedIn) theo từng quý.
- Thử nghiệm làm một pet-project nhỏ và chia sẻ lên cộng đồng công nghệ để nhận phản hồi từ các kỹ sư đi trước.
"""

    # =========================================================================
    # KỊCH BẢN TC14: SO SÁNH HAI VỊ TRÍ NGHỀ NGHIỆP DỰA TRÊN DỮ LIỆU JD (ROLE COMPARISON - NHÓM 5 - TC14 - P1)
    # =========================================================================
    elif is_role_comparison_query:
        comp = comparison_info or {}
        role_a_data = comp.get("role_a", {"name": "Backend Developer", "total_jds": 88, "top_core": []})
        role_b_data = comp.get("role_b", {"name": "Data Engineer", "total_jds": 23, "top_core": []})
        role_a_name = role_a_data.get("name", "Backend Developer")
        role_b_name = role_b_data.get("name", "Data Engineer")
        total_a = role_a_data.get("total_jds", 88)
        total_b = role_b_data.get("total_jds", 23)

        common_skills = comp.get("common_skills", [])
        exclusive_a = comp.get("exclusive_a", [])
        exclusive_b = comp.get("exclusive_b", [])

        top_a_lines = [f"- **{s.get('canonical_name') or s.get('skill') or s.get('name')}**: {s.get('demand_pct', 0)}% JD" for s in role_a_data.get("top_core", [])[:5]]
        top_b_lines = [f"- **{s.get('canonical_name') or s.get('skill') or s.get('name')}**: {s.get('demand_pct', 0)}% JD" for s in role_b_data.get("top_core", [])[:5]]
        common_lines = [f"- **{s['skill']}**: {s['demand_a']}% ({role_a_name}) vs {s['demand_b']}% ({role_b_name})" for s in common_skills[:5]]
        exclusive_a_lines = [f"- **{s['skill']}**: {s['demand_pct']}% JD ({s.get('jd_count', 0)} JD)" for s in exclusive_a[:5]]
        exclusive_b_lines = [f"- **{s['skill']}**: {s['demand_pct']}% JD ({s.get('jd_count', 0)} JD)" for s in exclusive_b[:5]]

        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC14 - P1): SO SÁNH HAI VỊ TRÍ NGHỀ NGHIỆP ({role_a_name} vs {role_b_name}) DỰA TRÊN DỮ LIỆU TUYỂN DỤNG THỰC TẾ.
Người dùng phân vân giữa hai hướng nghề nghiệp ({role_a_name} và {role_b_name}), yêu cầu so sánh dựa trên dữ liệu JD của GEM và tư vấn các điểm cần cân nhắc khi chọn hướng làm đồ án.
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ BẮT BUỘC các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, đối sánh khoa học, không thiên vị):

### 1. Hồ Sơ Kỹ Năng Riêng Biệt Cho Từng Vị Trí (TÁCH BIỆT 2 NHÓM - TUYỆT ĐỐI KHÔNG TRỘN LẪN)
- **Hồ sơ {role_a_name}** (Dựa trên tập dữ liệu phân tích **{total_a} JD**):
{chr(10).join(top_a_lines)}
- **Hồ sơ {role_b_name}** (Dựa trên tập dữ liệu phân tích **{total_b} JD**):
{chr(10).join(top_b_lines)}
- Lưu ý minh bạch quy mô dữ liệu: Nêu rõ quy mô tập dữ liệu ({total_a} JD cho {role_a_name} và {total_b} JD cho {role_b_name}) để người dùng thấy rõ độ lớn của từng tập mẫu khảo sát.

### 2. Phân Tích Kỹ Năng Giao Thoa (Chung) & Kỹ Năng Đặc Thù (Riêng)
- **Kỹ năng chung (Giao thoa giữa 2 hướng):**
{chr(10).join(common_lines) if common_lines else "- SQL, Python, Git, Docker, Kiến thức về cơ sở dữ liệu quan hệ và tối ưu truy vấn"}
  + Đây là các kỹ năng nền tảng vững chắc mà dù bạn chọn hướng nào cũng đều tận dụng được tối đa giá trị.
- **Kỹ năng đặc thù của {role_a_name}:**
{chr(10).join(exclusive_a_lines) if exclusive_a_lines else f"- Thiết kế RESTful/gRPC API, Spring Boot/Node.js, Quản lý giao dịch ACID, Caching (Redis), Kiến trúc Microservices"}
- **Kỹ năng đặc thù của {role_b_name}:**
{chr(10).join(exclusive_b_lines) if exclusive_b_lines else f"- Data Warehouse, Data Lake, Apache Kafka, Spark, ETL/ELT Pipelines, Data Modeling (Star Schema), Airflow"}

### 3. Khác Biệt Gắn Liền Với Bản Chất Công Việc Thực Tế (OLTP vs OLAP)
Giải thích rõ ràng sự khác biệt bản chất kỹ thuật trong công việc hàng ngày:
- **{role_a_name} (Hướng dịch vụ & Giao dịch - OLTP):**
  + Trọng tâm: Xây dựng các dịch vụ backend và API phục vụ người dùng cuối trực tiếp (End-users / Mobile / Web clients).
  + Thách thức chính: Độ trễ phản hồi thấp (low latency, tính bằng mili-giây), tính sẵn sàng cao (High Availability), bảo mật xác thực (AuthN/AuthZ), kiểm soát tranh chấp đồng thời (Concurrency / Race conditions) và tính toàn vẹn dữ liệu giao dịch (ACID).
- **{role_b_name} (Hướng luồng dữ liệu & Phân tích - OLAP):**
  + Trọng tâm: Thu thập (Ingestion), biến đổi (Transformation), làm sạch và vận chuyển các luồng dữ liệu khổng lồ từ nhiều nguồn khác nhau vào kho dữ liệu tập trung.
  + Thách thức chính: Khối lượng dữ liệu lớn (Volume & Velocity), độ trễ chấp nhận theo mẻ (Batch) hoặc xử lý dòng thời gian thực (Streaming), thiết kế mô hình dữ liệu đa chiều (Dimensional Modeling / Star Schema) phục vụ báo cáo BI, Data Science và huấn luyện mô hình AI.

### 4. Gợi Ý Định Hướng Đồ Án Tốt Nghiệp Cho Từng Hướng
- **Nếu chọn làm đồ án theo hướng {role_a_name}:**
  + Đề tài gợi ý: Hệ thống Thương mại điện tử, Đặt lịch khám bệnh, Nền tảng chia sẻ khóa học hoặc Ứng dụng thanh toán.
  + Điểm nhấn kỹ thuật cần thể hiện trong Git Repo: Chuẩn hóa RESTful API (Swagger), Phân quyền RBAC & JWT, Khóa giao dịch chống đặt trùng (Pessimistic / Optimistic Locking), Tích hợp Redis Caching và Unit/Integration Tests.
- **Nếu chọn làm đồ án theo hướng {role_b_name}:**
  + Đề tài gợi ý: Xây dựng Hệ thống Data Pipeline thu thập và phân tích giá thị trường (E-commerce Data Pipeline), hoặc Hệ thống theo dõi phân tích hành vi người dùng (Clickstream Analytics Pipeline).
  + Điểm nhấn kỹ thuật cần thể hiện trong Git Repo: Pipeline thu thập dữ liệu (Web Scraper / API Consumer), Xử lý làm sạch và kiểm thử chất lượng dữ liệu (Data Quality Checks), Lưu trữ vào Data Warehouse (PostgreSQL hoặc BigQuery), Điều phối luồng tự động (Apache Airflow) và trực quan hóa dashboard.

### 5. Tiêu Chí Cân Nhắc & Lời Khuyên Quyết Định
- **Nguyên tắc cốt lõi:** Tuyệt đối KHÔNG khẳng định nghề nào "tốt hơn", "dễ hơn" hay "lương cao hơn" một cách phiến diện. Cả hai đều là trụ cột kỹ thuật của các công ty công nghệ.
- Tiêu chí lựa chọn:
  + Nếu bạn thích xây dựng tính năng sản phẩm tương tác với người dùng, tối ưu API và kiến trúc web: Chọn {role_a_name}.
  + Nếu bạn thích làm việc với cấu trúc dữ liệu, tối ưu hóa các đường ống luồng dữ liệu lớn và thuật toán phân tích: Chọn {role_b_name}.
- Câu hỏi gợi mở: Bạn cảm thấy hứng thú hơn với việc xây dựng tính năng cho ứng dụng web người dùng hay với việc thiết kế đường ống xử lý dữ liệu tự động?
"""

    # =========================================================================
    # KỊCH BẢN TC13: HỆ QUY CHIẾU THỊ TRƯỜNG & XẾP HẠNG KỸ NĂNG THEO DỮ LIỆU JD THỰC TẾ (MARKET SKILL DEMAND - NHÓM 5 - TC13 - P0)
    # =========================================================================
    elif is_market_skills_demand_query:
        mr_info = market_ranking_info or {}
        mr_role = mr_info.get("target_role", target_role)
        total_jds = mr_info.get("total_jds", 88)
        data_source = mr_info.get("data_source", "Kho dữ liệu tuyển dụng thực tế TopCV (Bộ dữ liệu thị trường IT 2025-2026)")
        time_window = mr_info.get("time_window", "Dữ liệu tuyển dụng thực tế năm 2025-2026")

        core_skills = mr_info.get("core_skills", [])
        boost_skills = mr_info.get("boost_skills", [])

        core_lines = [f"{idx}. **{s['skill']}**: {s['demand_pct']}% JD ({s['jd_count']} / {total_jds} JD) — *{s.get('type', 'Nền tảng')}*" for idx, s in enumerate(core_skills[:6], 1)]
        boost_lines = [f"{idx}. **{s['skill']}**: {s['demand_pct']}% JD ({s['jd_count']} / {total_jds} JD) — *{s.get('type', 'Bổ trợ')}*" for idx, s in enumerate(boost_skills[:5], 1)]

        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC13 - P0): HỆ QUY CHIẾU THỊ TRƯỜNG & XẾP HẠNG KỸ NĂNG THEO DỮ LIỆU JD THỰC TẾ ({mr_role}).
Người dùng hỏi muốn theo {mr_role} tại Việt Nam, yêu cầu cho biết những kỹ năng nên ưu tiên học dựa trên dữ liệu tuyển dụng mà GEM đang có.
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ BẮT BUỘC các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, có căn cứ số liệu, minh bạch giới hạn):

### 1. Xác Định Rõ Nhóm JD Được Sử Dụng Để Phân Tích
- Khẳng định rõ: Kết quả phân tích dựa trên tập **{total_jds} tin tuyển dụng (JD) thực tế** cho vị trí **{mr_role}** tại thị trường Việt Nam.
- Nguồn dữ liệu và mốc thời gian: {data_source}, ghi nhận trong giai đoạn {time_window}.

### 2. Bảng Xếp Hạng Kỹ Năng Dựa Trên Dữ Liệu Tuyển Dụng Thực Tế
Trình bày các kỹ năng được sắp xếp giảm dần theo **Tỷ lệ nhu cầu thị trường (% JD)** và **Số lượng JD cụ thể**:

**Nhóm Kỹ Năng Nền Tảng / Cốt Lõi (Core Requirements):**
{chr(10).join(core_lines)}

**Nhóm Kỹ Năng Bổ Trợ / Gia Tăng Lợi Thế Cạnh Tranh (Boosters / Plus):**
{chr(10).join(boost_lines)}

- NGUYÊN TẮC: TUYỆT ĐỐI KHÔNG tự tạo số liệu, không bịa xu hướng hay thay đổi thứ hạng nếu không có trong dữ liệu trên.

### 3. Phân Biệt Giữa Tần Suất Xuất Hiện Và Mức Độ Bắt Buộc (Critical Distinctions)
- **Ý nghĩa của tần suất:** Tỷ lệ xuất hiện cao phản ánh quy mô nhu cầu phổ biến của các doanh nghiệp trên thị trường (ví dụ Java xuất hiện ở gần 50% JD, các hệ CSDL quan hệ như PostgreSQL/MySQL và thiết kế RESTful API xuất hiện ở phần lớn các JD).
- **NGUYÊN TẮC KHÔNG ĐÁNH ĐỒNG:** Không đánh đồng tần suất xuất hiện với mức độ bắt buộc sinh viên phải học hết tất cả các công nghệ.
  + Ví dụ: Thị trường tuyển nhiều Java, Node.js, C# (.NET) hay Python; sinh viên **chỉ cần chọn 1 ngôn ngữ/nền tảng cốt lõi** và học thật sâu sắc, kết hợp với kiến thức cơ sở dữ liệu quan hệ vững chắc và tư duy thiết kế API chuẩn mực, chứ không cần phải học toàn bộ các ngôn ngữ backend cùng một lúc.
  + Các kỹ năng bổ trợ (Docker, Redis, CI/CD, Message Queue) là "điểm cộng vượt trội" giúp sinh viên nổi bật hơn các ứng viên khác trong kỳ thực tập.

### 4. Minh Bạch Về Giới Hạn Của Dữ Liệu
- Khẳng định rõ: Kết quả này phản ánh **tập dữ liệu khảo sát thực tế ({total_jds} JD từ TopCV)** mà GEM đã thu thập và xử lý, đóng vai trò là **hệ quy chiếu tham khảo khoa học**, chứ không đại diện tuyệt đối cho 100% toàn bộ thị trường lao động.
- Thị trường công nghệ luôn có sự đa dạng theo từng phân khúc công ty (Product vs Outsourcing, Startup vs Doanh nghiệp lớn).

### 5. Lời Khuyên Hành Động Thiết Thực
- Gợi ý lộ trình ưu tiên cho sinh viên:
  1. Giai đoạn 1 (Nền tảng): 1 Ngôn ngữ backend chính + Thiết kế RESTful API + Cơ sở dữ liệu quan hệ (PostgreSQL/MySQL).
  2. Giai đoạn 2 (Gia tăng giá trị): Docker containerization + Redis Caching + Viết Unit/Integration Tests.
- Câu hỏi tương tác mở: Bạn đang có nền tảng hoặc định hướng với ngôn ngữ nào nhất (ví dụ Java, Python hay JavaScript/Node.js) để chúng ta cùng chọn stack phù hợp nhất cho đồ án của bạn?
"""

    # =========================================================================
    # KỊCH BẢN TC17 & TC18: TÌM ĐỒ ÁN / REPOSITORY GITHUB THAM KHẢO (NHÓM 6 - P0)
    # =========================================================================
    elif is_github_reference_query:
        gh_info = github_reference_info or {}
        gh_status = gh_info.get("status", "NOT_FOUND")
        projects = gh_info.get("projects", [])

        if gh_status == "FOUND" and len(projects) > 0:
            proj_blocks = []
            for idx, p in enumerate(projects, 1):
                proj_skills = ", ".join(p.get("skills", [])) if p.get("skills") else p.get("language", "JavaScript")
                proj_blocks.append(f"""
- **Đồ án {idx}:** `{p.get('repo_name')}` (Tác giả: `{p.get('author')}`)
  + **Đường dẫn Repository:** [{p.get('repo_url')}]({p.get('repo_url')})
  + **Ngôn ngữ / Công nghệ ghi nhận:** {proj_skills}
  + **Mô tả trích xuất từ README:** "{p.get('snippet', '')}"
""")
            proj_str = "\n".join(proj_blocks)

            scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC17 - P0): SỬ DỤNG ĐỒ ÁN HOẶC REPOSITORY GITHUB TRONG KHO DỮ LIỆU ĐỂ THAM KHẢO ĐỊNH HƯỚNG.
Người dùng yêu cầu sử dụng các đồ án hoặc repository GitHub mà GEM có để tham khảo các chức năng, công nghệ và kỹ năng cần cân nhắc cho đồ án "{session['idea']}".
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ BẮT BUỘC các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, minh bạch, trung thực và khoa học):

### 1. Dữ Liệu Nguồn Tham Khảo Thực Tế Từ Kho Đồ Án GEM
- Cung cấp thông tin THỰC SỰ CÓ TRONG KHO DỮ LIỆU của GEM (Kho 527 đồ án sinh viên và repository GitHub):
{proj_str}
- NGUYÊN TẮC BẮT BUỘC: **Dự án được nêu phải có thật trong kho dữ liệu. TUYỆT ĐỐI KHÔNG tự bịa tên repository hay đường dẫn không có trong nguồn trên.**

### 2. Các Điểm Giá Trị Có Thể Tham Khảo Từ Dự Án Nguồn
- **Tổ chức chức năng nghiệp vụ:** Tham khảo cách phân rã các module cốt lõi (Quản lý sản phẩm/danh mục, Giỏ hàng, Đặt hàng/Checkout, Xác thực phân quyền tài khoản).
- **Cấu trúc ứng dụng & Cách triển khai:** Mô hình phân tách rõ ràng giữa Frontend (React Client SPA) và Backend (Node.js RESTful API Service), cách thiết lập file môi trường `.env`, cấu hình CORS, và đóng gói triển khai Docker/Docker Compose.

### 3. Đối Sánh Với Yêu Cầu Đồ Án & Mục Tiêu Nghề Nghiệp ({target_role})
- Đồ án của người dùng ({session['idea']}) theo hướng {target_role}:
  + Dự án tham khảo là minh chứng trực quan về cấu trúc mã nguồn thực tế của sinh viên khóa trước.
  + Giúp người dùng hình dung rõ các artifacts cần có trong Git Repo để đi phỏng vấn tuyển dụng.

### 4. Nguyên Tắc Phân Định Rạch Ròi & Không Thổi Phồng (Critical Guardrails)
- **Phân biệt dữ liệu nguồn với phần phân tích:** Dữ liệu nguồn là thông tin khách quan từ repo cũ; phần phân tích của GEM là định hướng học tập cho đồ án mới.
- **Không mặc định dự án cũ là mẫu tốt nhất hoặc stack trong đó là bắt buộc:** Khẳng định rõ đồ án cũ có thể có những giới hạn (ví dụ dùng MongoDB thay vì PostgreSQL, hoặc chưa có Unit Test), người dùng hoàn toàn có thể cải tiến tốt hơn.
- **Không khẳng định chất lượng code, độ hoàn thiện hoặc số người dùng nếu nguồn không chứng minh:** Tuyệt đối không tán dương quá đà ("dự án triệu người dùng", "code hoàn hảo").
- **Đồ án tham khảo dùng để hỗ trợ, không thay thế việc phân tích bài toán.**

### 5. Lời Khuyên Hành Động Thiết Thực & Câu Hỏi Tương Tác Mở
- Gợi ý bước tiếp theo: Bắt đầu từ việc thiết kế sơ đồ thực thể ERD và danh sách API endpoints chuẩn RESTful.
- Câu hỏi tương tác: Bạn muốn chúng ta cùng thiết kế chi tiết luồng đặt hàng (Checkout) hay thiết kế cấu trúc database cho sản phẩm e-commerce của bạn trước?
"""
        else:
            scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC18 - P0): XỬ LÝ KHI KHÔNG TÌM THẤY ĐỒ ÁN GITHUB TƯƠNG TỰ TRONG KHO DỮ LIỆU CỦA GEM.
Người dùng yêu cầu tìm đồ án tương tự cho đề tài "{session['idea']}" (Hệ thống giám sát chất lượng không khí trong nhà bằng cảm biến IoT, có dashboard cảnh báo) theo hướng {target_role}.
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ BẮT BUỘC các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, minh bạch, trung thực và chuyên nghiệp):

### 1. Thông Báo Minh Bạch Về Giới Hạn Kho Tham Khảo Của GEM
- Khẳng định rõ ràng: Hiện tại trong kho dữ liệu của GEM (gồm **527 đồ án sinh viên và repository GitHub** đã thu thập và chọn lọc), **chưa tìm thấy dự án hoặc repository tương tự** cho bài toán giám sát chất lượng không khí trong nhà bằng cảm biến IoT.
- NGUYÊN TẮC BẮT BUỘC: **TUYỆT ĐỐI KHÔNG tự bịa tên dự án hay đường dẫn repository GitHub không có thật để lấp khoảng trống.**
- Giới hạn phạm vi tìm kiếm: Nhấn mạnh rõ GEM chỉ tìm kiếm trong tập dữ liệu 527 đồ án đã lập chỉ mục của hệ thống, **không khẳng định đã tìm kiếm toàn bộ hàng triệu dự án trên toàn mạng Internet GitHub**.

### 2. Khẳng Định Tính Khả Thi Của Đề Tài (Vượt Trội Vì Tính Độc Đáo)
- NGUYÊN TẮC: **TUYỆT ĐỐI KHÔNG suy luận rằng đề tài "không khả thi" hay "không tốt" chỉ vì chưa có ví dụ tương tự trong kho tham khảo**. 
- Ngược lại, đây là một đề tài **rất mới mẻ, độc đáo, mang tính kỹ nghệ cao và giải quyết bài toán thực tế xuất sắc**, giúp hồ sơ của sinh viên trở nên nổi bật và không bị trùng lặp với các đồ án thông thường.

### 3. Phân Tích Yêu Cầu Kỹ Thuật & Định Hướng Năng Lực Chuyên Môn Cho Bài Toán (IoT & Backend)
Tiếp tục hỗ trợ toàn diện người dùng bằng việc bẻ nhỏ kiến trúc kỹ thuật hệ thống theo 4 tầng:
1. **Tầng Cảm biến & Vi điều khiển (IoT Edge):**
   - Thu thập chỉ số môi trường: Cảm biến bụi mịn (PMS5003 / PMS7003 đo PM2.5, PM10), Cảm biến nhiệt độ & độ ẩm (DHT22 / BME280), Cảm biến chất lượng không khí / khí độc (MQ-135 đo CO2, NH3).
   - Vi điều khiển thu thập: ESP32 (có sẵn Wi-Fi/Bluetooth) hoặc Raspberry Pi để đọc tín hiệu GPIO/I2C/UART từ cảm biến.
2. **Tầng Giao thức Truyền thông (IoT Communication Protocols):**
   - Sử dụng giao thức **MQTT** (Message Queuing Telemetry Transport qua Eclipse Mosquitto Broker) — giao thức nhẹ chuẩn công nghiệp cho thiết bị IoT với băng thông thấp.
   - Cơ chế Publish/Subscribe: Thiết bị ESP32 đóng vai trò MQTT Publisher bắn gói tin định kỳ (mỗi 5-10 giây) lên Broker.
3. **Tầng Backend Xử lý & Lưu trữ (Backend & Time-series Storage):**
   - Backend (Node.js/Express, Python/FastAPI hoặc Go) đóng vai trò MQTT Subscriber để nhận dữ liệu, xác thực thiết bị và kiểm tra ngưỡng an toàn (Threshold Checking).
   - Cơ sở dữ liệu chuỗi thời gian (Time-series Database): Sử dụng **TimescaleDB** (extension trên PostgreSQL) hoặc **InfluxDB** để lưu trữ các mốc đo lường theo thời gian (timestamp, device_id, pm25, temperature, humidity).
   - Bộ máy cảnh báo (Alerting Engine): Tự động phát hiện khi chỉ số vượt ngưỡng an toàn (ví dụ PM2.5 > 75 µg/m³ hoặc AQI > 150) để gửi cảnh báo qua Webhook / Email / Telegram.
4. **Tầng Dashboard Trực Quan Hóa (Monitoring Dashboard):**
   - Web Dashboard hiển thị các biểu đồ biến thiên thời gian thực (Real-time line charts với Chart.js hoặc Recharts).
   - Hiển thị chỉ số AQI tổng hợp và trạng thái hoạt động của thiết bị cảm biến (Online/Offline status).

### 4. Câu Hỏi Tương Tác Mở (Interactive Probing)
- Đặt câu hỏi khai thác thêm về phần cứng và giao thức: *"Bạn dự định sử dụng dòng vi điều khiển nào (như ESP32 hay Raspberry Pi) và các loại cảm biến đo bụi mịn/khí gas cụ thể nào? Bạn muốn thiết kế giao tiếp qua giao thức MQTT hay HTTP REST trước?"*
"""

    # =========================================================================
    # KỊCH BẢN TC19: ĐỐI CHIẾU ĐỒ ÁN VỚI KỸ NĂNG NGHỀ NGHIỆP MỤC TIÊU & SKILL GAP (NHÓM 7 - TC19 - P0)
    # =========================================================================
    elif is_project_skill_gap_audit:
        sg_info = skill_gap_audit_info or {}
        audit_role = sg_info.get("target_role", target_role)
        total_jds = sg_info.get("total_jds", 88)

        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC19 - P0): ĐỐI CHIẾU ĐỒ ÁN VỚI KỸ NĂNG NGHỀ NGHIỆP MỤC TIÊU ({audit_role} INTERN).
Người dùng có đồ án: "{session['idea']}" với bộ công nghệ ({tech_str}) và muốn ứng tuyển {audit_role} Intern.
Yêu cầu phân tích những kỹ năng đồ án đã thể hiện, những kỹ năng còn thiếu so với yêu cầu tuyển dụng và thứ tự ưu tiên cải thiện.

BẠN LÀ CỐ VẤN CÔNG NGHỆ & HƯỚNG NGHIỆP GEM (AISC 2026). BẮT BUỘC TỔ CHỨC CÂU TRẢ LỜI THEO ĐÚNG 4 NHÓM RÕ RÀNG:

### 1. Kỹ Năng Có Thể Được Thể Hiện Qua Đồ Án (Demonstrated Capabilities)
- Liệt kê các năng lực cốt lõi mà bài toán "{session['idea']}" với bộ công nghệ ({tech_str}) có thể chứng minh:
  * **Thiết kế API / Dịch vụ:** Xây dựng các endpoints phục vụ luồng nghiệp vụ chính của đề tài và xác thực người dùng.
  * **Xử lý nghiệp vụ Backend:** Các luồng tính toán, cập nhật trạng thái nghiệp vụ cốt lõi, xác thực JWT hoặc phân quyền.
  * **Truy vấn cơ sở dữ liệu:** Thiết kế bảng, khóa ngoại (Foreign Keys), thực thi các câu lệnh CRUD dữ liệu trên CSDL đã chọn.
  * **Tương tác Frontend - Backend:** Quản lý state ở client, gọi API bất đồng bộ và hiển thị giao diện động.
- NGUYÊN TẮC: Chỉ ghi nhận khi thông tin bài toán thực sự hỗ trợ kết luận đó.

### 2. Kỹ Năng Chưa Có Đủ Bằng Chứng (Unproven Capabilities & Hidden Gaps)
- Chỉ ra các năng lực mà một đồ án sinh viên thông thường thường thiếu bằng chứng kiểm chứng cụ thể:
  * **Kiểm thử tự động (Automated Testing):** Chưa có bằng chứng về Unit Test, Integration Test (sử dụng Jest/PyTest/JUnit) để bảo vệ luồng nghiệp vụ không bị regression.
  * **Tối ưu hóa truy vấn & Toàn vẹn dữ liệu nâng cao:** Chưa có bằng chứng về xử lý Database Transactions (ACID) khi ghi nhận giao dịch; chưa có đánh chỉ mục (Index) hoặc đo đạc kế hoạch thực thi (EXPLAIN).
  * **Triển khai & Vận hành (Deployment/DevOps):** Chưa có bằng chứng về đóng gói ứng dụng (Docker, Docker Compose) hoặc tự động hóa tích hợp (CI/CD).
  * **Xử lý lỗi tập trung & Khả năng quan sát:** Chưa có bộ bắt lỗi toàn cục (Global Exception Handler) chuẩn hóa, thiếu hệ thống ghi nhật ký (Logging) có cấu trúc.
- NGUYÊN TẮC CỐT LÕI (CRITICAL GUARDRAIL): **TUYỆT ĐỐI KHÔNG coi tên công nghệ ({tech_str}) trong dự án là bằng chứng đầy đủ về năng lực.** Việc sinh viên dùng một CSDL không đồng nghĩa là đã biết tối ưu hóa database; việc dùng ngôn ngữ backend không đồng nghĩa là đã viết mã nguồn an toàn, sạch sẽ và có kiểm thử.

### 3. Khoảng Cách So Với Yêu Cầu Tuyển Dụng Thực Tế (Skill Gap with Market Telemetry)
- Đối chiếu trực tiếp với tập dữ liệu phân tích gồm **{total_jds} tin tuyển dụng (JD)** của vị trí **{audit_role}** từ GEM:
  * **Đảm bảo chất lượng mã nguồn (Testing):** Hơn 28-30% JD yêu cầu ứng viên có tư duy viết Unit Test và kiểm thử API. Đồ án thiếu phần này sẽ là một lỗ hổng lớn khi phỏng vấn.
  * **Cơ sở dữ liệu & Tối ưu hiệu năng:** Xuất hiện trong phần lớn JD ({total_jds} JD), đòi hỏi không chỉ biết viết truy vấn cơ bản mà phải hiểu về Transactions, Indexing và Caching (Redis) để giảm tải cho database.
  * **Đóng gói và môi trường (Containerization):** Khoảng 33% JD yêu cầu hiểu biết cơ bản về Docker hoặc triển khai ứng dụng.
- Nêu rõ nguyên nhân: Từng kỹ năng trên được đánh dấu là khoảng cách vì thị trường tuyển dụng Intern/Fresher hiện nay cạnh tranh rất cao, nhà tuyển dụng tìm kiếm ứng viên có tư duy sản phẩm thực tế và mã nguồn đáng tin cậy chứ không chỉ dừng lại ở đồ án môn học CRUD đơn giản.

### 4. Thứ Tự Ưu Tiên Cải Thiện Có Trọng Tâm (Actionable Priorities)
Đề xuất lộ trình ưu tiên giải quyết từng bước thay vì danh sách dàn trải:
- **Ưu tiên 1 (Nền tảng & Tạo đột phá CV): Viết Unit Test & Xử lý lỗi toàn cục.**
  * *Vì sao làm trước:* Hầu hết sinh viên đi phỏng vấn Intern đều KHÔNG có Unit Test. Việc bạn bổ sung thư mục `tests/` kiểm thử luồng nghiệp vụ cốt lõi sẽ ngay lập tức biến đồ án thành điểm sáng nổi bật, chứng minh tư duy làm phần mềm chuẩn mực.
- **Ưu tiên 2 (Toàn vẹn dữ liệu): Bổ sung Database Transactions & Đánh Index trên CSDL.**
  * *Vì sao làm tiếp:* Đảm bảo các giao dịch cập nhật trạng thái nhiều bước phải diễn ra trong 1 transaction an toàn, không sợ race condition hay sai lệch số liệu.
- **Ưu tiên 3 (Đóng gói & Hiệu năng): Viết Dockerfile & Tích hợp Redis Caching.**
  * *Vì sao làm sau:* Đóng gói Docker Compose giúp người phỏng vấn chạy thử đồ án chỉ với 1 câu lệnh; Redis cache dữ liệu thường truy cập giúp bạn tự tin trả lời các câu hỏi về tối ưu tốc độ hệ thống.

---
### 5. Lời Khuyên Hành Động Thiết Thực & Câu Hỏi Tương Tác
- Khẳng định: Đồ án hiện tại của bạn đã là một nền móng rất tốt. Nâng cấp 3 ưu tiên trên sẽ nâng tầm đồ án từ mức "bài tập lớn sinh viên" lên "sản phẩm chuẩn doanh nghiệp".
- Đặt câu hỏi tương tác mở: Gợi ý người dùng cùng lên kế hoạch chi tiết theo tuần để cải thiện các khoảng cách này.
"""

    # =========================================================================
    # KỊCH BẢN TC20: KẾ HOẠCH HÀNH ĐỘNG 4 TUẦN CẢI THIỆN SKILL GAP (NHÓM 7 - TC20 - P1)
    # =========================================================================
    elif is_four_week_action_plan:
        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC20 - P1): LẬP KẾ HOẠCH HÀNH ĐỘNG 4 TUẦN (1 - 2 GIỜ/NGÀY) CHUẨN BỊ ỨNG TUYỂN {target_role} INTERN.
Người dùng yêu cầu lập kế hoạch cải thiện trong 4 tuần dựa trên kết quả Skill Gap vừa rồi, với quỹ thời gian khoảng 1 đến 2 giờ mỗi ngày (~7 đến 10 giờ mỗi tuần).

BẠN LÀ CỐ VẤN CÔNG NGHỆ & HƯỚNG NGHIỆP GEM (AISC 2026). BẮT BUỘC TUÂN THỦ CÁC NGUYÊN TẮC SAU:
1. **Kế thừa ngữ cảnh Skill Gap:** Giữ lại trọn vẹn các khoảng cách kỹ năng cốt lõi đã xác định ở lượt trước (Unit Test, Database Transaction/Index, Docker Compose, Redis/API Docs).
2. **Cải tiến trực tiếp đồ án hiện có:** Tập trung refactor và bổ sung tính năng trực tiếp vào đồ án "{session['idea']}" ({tech_str}) hiện có, TUYỆT ĐỐI KHÔNG yêu cầu đập đi xây lại từ đầu.
3. **Phù hợp quỹ thời gian:** Chia nhỏ công việc để hoàn thành vừa vặn trong 1 - 2 giờ/ngày.
4. **Không nhồi nhét công nghệ mới:** Tập trung làm sâu hệ sinh thái công nghệ ({tech_str}) đã chọn, không đưa thêm Kafka, Kubernetes, Microservices khi chưa cần.
5. **Mỗi tuần có Mục tiêu, Nhiệm vụ cụ thể và Đầu ra kiểm chứng được (Deliverable / Artifact).**
6. **Phân biệt rõ ràng giữa Nhiệm vụ Bắt buộc (Must-have cho Intern) và Phần làm thêm nếu còn thời gian (Nice-to-have).**

BẮT BUỘC TRÌNH BÀY ĐẦY ĐỦ 4 TUẦN. Với mỗi tuần, bạn BẮT BUỘC PHẢI DÙNG ĐẦY ĐỦ 4 ĐẦU MỤC CON CHÍNH XÁC SAU ĐÂY:
- **Mục tiêu:** [Mục tiêu kỹ thuật của tuần]
- **Nhiệm vụ cụ thể (1-2h/ngày):** [Phân bổ việc cụ thể theo ngày]
- **Kết quả có thể kiểm chứng (Deliverable / Artifact đầu ra):** [Đầu ra kiểm chứng được trên Git: file code, test pass, migration script, Dockerfile, etc.]
- **Phân loại:** [Ghi rõ **Bắt buộc (Must-have)** hoặc **Bổ trợ / Làm thêm nếu còn thời gian (Nice-to-have)**]

ĐẶC BIỆT LƯU Ý VỀ PHÂN LOẠI:
- Tuần 1, Tuần 2, Tuần 4: Ghi rõ là **Bắt buộc (Must-have)**.
- Tuần 3: Ghi rõ là **Bổ trợ / Làm thêm nếu còn thời gian (Nice-to-have)**.

BỐ CỤC CHI TIẾT KẾ HOẠCH 4 TUẦN:

### Tuần 1: Kiểm Thử Tự Động & Xử Lý Lỗi Toàn Cục (Unit Testing & Error Handling)
- **Mục tiêu:** Xây dựng tấm lưới an toàn cho luồng nghiệp vụ cốt lõi, bảo vệ logic nghiệp vụ không bị lỗi.
- **Nhiệm vụ cụ thể (1-2h/ngày):**
  * Ngày 1-2: Cài đặt framework kiểm thử phù hợp với stack ({tech_str}) (ví dụ Jest/Supertest cho Node.js, PyTest cho Python), cấu hình script chạy test.
  * Ngày 3-4: Viết bộ Unit Test cho Service nghiệp vụ cốt lõi: kiểm tra tính toán dữ liệu, xử lý đầu vào không hợp lệ và edge cases.
  * Ngày 5-6: Xây dựng middleware xử lý lỗi tập trung (Global Error Handler) và chuẩn hóa định dạng JSON lỗi trả về.
  * Ngày 7: Đo đạc độ bao phủ kiểm thử (Test Coverage Report).
- **Kết quả có thể kiểm chứng (Deliverable / Artifact đầu ra):** Thư mục `tests/` với các test case chạy xanh (`PASS`), Test Coverage đạt > 70% cho tầng Service nghiệp vụ chính.
- **Phân loại:** **BẮT BUỘC (Must-have)**.

### Tuần 2: Toàn Vẹn Dữ Liệu, Transactions & Tối Ưu Hóa CSDL (Database Integrity & Performance)
- **Mục tiêu:** Đảm bảo dữ liệu không bao giờ bị sai lệch khi có nhiều request đồng thời, tối ưu hóa tốc độ truy vấn.
- **Nhiệm vụ cụ thể (1-2h/ngày):**
  * Ngày 1-3: Tích hợp Database Transactions (ACID) vào luồng nghiệp vụ ghi nhận dữ liệu nhiều bước — đảm bảo tính nguyên tử; rollback an toàn nếu lỗi.
  * Ngày 4-5: Đánh chỉ mục (Index) trên các trường thường xuyên tìm kiếm và lọc; sử dụng lệnh `EXPLAIN` để so sánh tốc độ trước và sau khi đánh index.
  * Ngày 6-7: Viết script migration và seed dữ liệu mẫu để môi trường cơ sở dữ liệu có thể tái tạo dễ dàng.
- **Kết quả có thể kiểm chứng (Deliverable / Artifact đầu ra):** File script SQL migration, đoạn mã xử lý Transaction có try/catch rollback, tài liệu mô tả kết quả lệnh `EXPLAIN`.
- **Phân loại:** **BẮT BUỘC (Must-have)**.

### Tuần 3: Tối Ưu Hóa Bộ Nhớ Đệm Với Redis (Caching Layer)
- **Mục tiêu:** Giảm tải cho cơ sở dữ liệu đối với các truy vấn đọc dữ liệu thường xuyên.
- **Nhiệm vụ cụ thể (1-2h/ngày):**
  * Ngày 1-2: Cài đặt Redis (qua Docker hoặc cục bộ), kết nối Redis client vào dự án.
  * Ngày 3-5: Áp dụng chiến lược Cache-Aside cho API xem dữ liệu danh mục/bản ghi chính; thiết lập TTL (Time-To-Live, ví dụ 1 giờ) và cơ chế xóa cache khi dữ liệu cập nhật.
  * Ngày 6-7: Đo lường thời gian phản hồi API (Response Time) trước và sau khi có cache (ví dụ: giảm từ 120ms xuống 15ms).
- **Kết quả có thể kiểm chứng (Deliverable / Artifact đầu ra):** Middleware Redis Cache trong mã nguồn, biểu đồ hoặc số liệu so sánh Response Time ghi trong báo cáo.
- **Phân loại:** **Bổ trợ / Làm thêm nếu còn thời gian (Nice-to-have)**.

### Tuần 4: Đóng Gói Docker, Hoàn Thiện Tài Liệu & Sẵn Sàng Ứng Tuyển (DevOps & Git Portfolio)
- **Mục tiêu:** Đảm bảo đồ án có thể khởi chạy chỉ bằng một câu lệnh duy nhất, biến Git Repository thành hồ sơ ứng tuyển chuyên nghiệp.
- **Nhiệm vụ cụ thể (1-2h/ngày):**
  * Ngày 1-3: Viết `Dockerfile` cho ứng dụng và file `docker-compose.yml` kết nối ứng dụng với CSDL và Redis.
  * Ngày 4-5: Viết tài liệu API hoàn chỉnh (Postman Collection xuất file JSON hoặc Swagger UI `/api-docs`).
  * Ngày 6-7: Hoàn thiện file `README.md` chuyên nghiệp (có sơ đồ kiến trúc, hướng dẫn cài đặt 1 lệnh `docker compose up`, ảnh chụp màn hình kết quả Unit Test).
- **Kết quả có thể kiểm chứng (Deliverable / Artifact đầu ra):** File `Dockerfile`, `docker-compose.yml`, tài liệu Postman/Swagger và file `README.md` chuyên nghiệp trên GitHub.
- **Phân loại:** **BẮT BUỘC (Must-have cho Dockerfile + README)**.

---
### Cách Kiểm Tra Tiến Độ & Đánh Giá Cuối Cùng
- **Tiêu chí nghiệm thu:** Cuối mỗi tuần, bạn tự kiểm tra xem đã có đúng artifact đầu ra tương ứng trên Git chưa.
- **Sẵn sàng phỏng vấn:** Khi hoàn thành 4 tuần này, bạn đã sở hữu một sản phẩm hoàn chỉnh với Unit Test, Transactions, Caching và Docker — vượt xa 80% ứng viên Intern thông thường.
- **Câu hỏi tương tác:** Bạn muốn chúng ta bắt tay vào việc cấu hình kiểm thử và viết test case đầu tiên cho Tuần 1 ngay bây giờ không?
"""

    # =========================================================================
    # KỊCH BẢN TC21: GIẢI THÍCH ĐIỂM SỐ PHÙ HỢP / READINESS SCORE (NHÓM 7 - TC21 - P0)
    # =========================================================================
    elif is_readiness_score_explanation:
        score_val = int(round((readiness_score_info or {}).get("score", 72)))
        score_role = (readiness_score_info or {}).get("target_role", target_role)
        total_jds = (readiness_score_info or {}).get("total_jds", 88)
        gap_val = int(round(100 - score_val))
        boost_skills = (readiness_score_info or {}).get("boost_skills", [])
        boost_sample = ", ".join(boost_skills[:3]) if boost_skills else "Redis, Docker, CI/CD"

        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC21 - P0): TÍNH MINH BẠCH VÀ GIẢI THÍCH ĐIỂM SỐ PHÙ HỢP ({score_val}% MATCHING / READINESS SCORE).
Người dùng hỏi về điểm số đánh giá mức độ phù hợp {score_val}% giữa đồ án của họ và vị trí {score_role}: Điểm này có nghĩa là gì, được tính dựa trên những yếu tố nào và cần làm gì để tăng điểm?

BẠN LÀ CỐ VẤN CÔNG NGHỆ & HƯỚNG NGHIỆP GEM (AISC 2026). BẮT BUỘC TUÂN THỦ CÁC NGUYÊN TẮC SAU:

### 1. Ý Nghĩa Của Điểm Số {score_val}% Và Công Thức Tính Thực Tế Của GEM
- Giải thích rõ ràng và minh bạch công thức định lượng được triển khai trong hệ thống GEM:
  $$\\text{{Readiness Score}} = 0.35 \\times \\text{{Semantic Fit}} + 0.65 \\times \\text{{Coverage Rate}}$$
- **Thành phần 1: Độ tương đồng ngữ nghĩa (Semantic Fit - Trọng số 35%):**
  * Được tính bằng thuật toán cosine similarity giữa vector mô tả đồ án và không gian vector của các tin tuyển dụng {score_role} trong Qdrant Vector Database (sử dụng mô hình embedding BGE-M3 1024 chiều). Đồ án có độ tương đồng ngữ cảnh rất cao với bài toán thực tế (đạt ~85-90 điểm).
- **Thành phần 2: Tỷ lệ bao phủ kỹ năng (Coverage Rate - Trọng số 65%):**
  * Được tính bằng tỷ lệ giữa các kỹ năng mà đồ án hiện tại đã thể hiện ({tech_str}) so với tổng số các kỹ năng cốt lõi được yêu cầu trong kho **{total_jds} tin tuyển dụng (JD)** của vị trí {score_role} tại GEM.
  * Hiện tại đồ án mới chỉ đáp ứng được phần lập trình chức năng cơ bản, nên tỷ lệ bao phủ ở mức ~60-65%, kéo điểm tổng về mức {score_val}%.

### 2. Nguyên Tắc Phân Định Cốt Lõi (Critical Guardrail)
- **TUYỆT ĐỐI KHÔNG KHẲNG ĐỊNH RẰNG {score_val}% ĐỒNG NGHĨA VỚI {score_val}% CƠ HỘI ĐƯỢC TUYỂN DỤNG HAY XÁC SUẤT CÓ VIỆC LÀM.**
- Cần giải thích rõ cho người dùng: 
  * Điểm {score_val}% là một chỉ số kỹ thuật phản ánh **mức độ trùng khớp giữa các từ khóa kỹ năng trên giấy tờ của đồ án so với bản mô tả công việc (JD)**.
  * Quá trình tuyển dụng thực tế không chỉ xét mỗi tech stack, mà phụ thuộc rất lớn vào năng lực giải quyết vấn đề, tư duy thiết kế hệ thống, khả năng trình bày trong phỏng vấn và thái độ làm việc của ứng viên.

### 3. Yếu Tố Nào Đang Làm Giảm Mức Độ Phù Hợp ({gap_val}% Khoảng Cách)?
Dựa trên phân tích từ kho {total_jds} JD {score_role} của GEM, những yếu tố chính khiến điểm số dừng lại ở {score_val}% thay vì 85-90%:
1. **Thiếu kiểm thử tự động (Unit Test / Integration Test):** Chiếm ~28% yêu cầu trong JD {score_role}, đồ án hiện tại chưa có bằng chứng kiểm thử.
2. **Thiếu giải pháp tối ưu hiệu năng hoặc công nghệ bổ trợ (Boosters như {boost_sample}):** Kỹ năng phổ biến trong JD {score_role} để xử lý dữ liệu và tải cao, đồ án mới chỉ dừng ở mức xử lý cơ bản.
3. **Thiếu đóng gói và triển khai (Docker / CI-CD):** Chiếm ~33% JD {score_role}, đồ án chưa có Dockerfile và docker-compose.
4. **Thiếu kỹ thuật tối ưu hóa CSDL / kiến trúc dữ liệu chuyên sâu:** Chưa có đo đạc kế hoạch truy vấn (Index, EXPLAIN) hay xử lý Transactions đồng thời.

### 4. Đề Xuất Hành Động Cụ Thể Để Tăng Điểm Lên 85%+
Để tăng điểm số phù hợp gắn trực tiếp với các thành phần điểm trên cho vị trí {score_role}:
- **Tăng Coverage Rate:**
  * Bổ sung bộ Unit Test cho luồng nghiệp vụ/logic chính $\\rightarrow$ cộng ngay điểm kiểm thử chất lượng.
  * Viết file `docker-compose.yml` tích hợp ứng dụng, CSDL và các dịch vụ phụ trợ $\\rightarrow$ cộng điểm triển khai và containerization.
  * Tích hợp giải pháp tối ưu (Caching Redis hoặc Message Queue / tối ưu truy vấn) $\\rightarrow$ cộng điểm tối ưu hiệu năng.
- **Tăng Semantic Fit:**
  * Viết lại file `README.md` chuẩn kỹ thuật với sơ đồ kiến trúc, mô tả các API/dịch vụ cốt lõi và hướng dẫn chạy kiểm thử.

---
### 5. Câu Hỏi Tương Tác Mở
- Nhắc nhở sinh viên: {score_val}% là điểm xuất phát rất tốt cho một đồ án tự làm.
- Hỏi người dùng muốn cùng GEM tập trung bổ sung thành phần nào trước (Unit Test, Docker hay tối ưu hóa dữ liệu) để nâng điểm matching của đồ án lên mốc 85%?
"""

    # =========================================================================
    # KỊCH BẢN TC11: YÊU CẦU GIẢI THÍCH CĂN CỨ ĐỀ XUẤT CÔNG NGHỆ (DATA GROUNDING - NHÓM 4 - TC11 - P0)
    # =========================================================================
    elif is_justification_request:
        target_tech = queried_tech or "Docker"
        if market_telemetry and market_telemetry.get("is_found"):
            market_evidence_block = f"""
- **Tập dữ liệu phân tích:** Đã phân tích tổng cộng **{market_telemetry['total_jds']} tin tuyển dụng (JD)** thực tế cho vị trí **{target_role}**.
- **Số lượng JD đề cập {target_tech}:** **{market_telemetry['jd_count']} / {market_telemetry['total_jds']} JD**.
- **Tỷ lệ nhu cầu thị trường tương ứng:** **{market_telemetry['demand_pct']}%** trong tập JD đó.
- **Thời gian thu thập dữ liệu / Nguồn:** {market_telemetry.get('time_window', 'Dữ liệu tuyển dụng thực tế 2025-2026')} từ {market_telemetry.get('data_source', 'TopCV')}.
- **Phân loại kỹ năng:** **{market_telemetry['skill_type']}**.
- **Nguyên tắc phân định rạch ròi:** Khẳng định rõ {target_tech} là kỹ năng gia tăng lợi thế cạnh tranh (Booster / Kỹ năng ưu tiên), KHÔNG kết luận nó là bắt buộc tuyệt đối chỉ vì nó hữu ích về mặt kỹ thuật, mà dựa hoàn toàn trên bằng chứng dữ liệu tuyển dụng thực tế.
"""
        else:
            market_evidence_block = f"""
- **Minh bạch về giới hạn dữ liệu:** Hiện tại hệ thống dữ liệu tuyển dụng của GEM chưa ghi nhận số liệu thống kê riêng biệt cho công nghệ "{target_tech}" trong tập JD của vị trí {target_role}.
- **Nguyên tắc trung thực:** GEM cam kết minh bạch và TUYỆT ĐỐI KHÔNG đưa ra bất kỳ con số phỏng đoán hay số liệu bịa đặt nào khi chưa có nguồn dữ liệu kiểm chứng. Lời khuyên cho công nghệ này hoàn toàn xuất phát từ góc độ thực tiễn kỹ thuật (Technical Best Practices).
"""

        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC11): GIẢI THÍCH CĂN CỨ ĐỀ XUẤT CÔNG NGHỆ ({target_tech}) CHO VỊ TRÍ {target_role}.
Người dùng hỏi tại sao lại đề xuất {target_tech}, có thật sự nhiều JD yêu cầu không hay chỉ là gợi ý theo kiến thức chung.
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ BẮT BUỘC các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, minh bạch, tách bạch 2 phần riêng biệt):

### 1. Lý Do Kỹ Thuật (Technical Justification)
- Phân tích rõ ràng giá trị kỹ thuật thực chất của {target_tech} đối với đồ án ({session['idea']}):
  + Với Docker: Hỗ trợ đóng gói toàn bộ ứng dụng (Application Containerization) cùng các phụ thuộc vào một image duy nhất.
  + Đảm bảo môi trường chạy nhất quán giữa các máy tính khác nhau ("chạy trên máy phát triển của bạn được thì chạy trên máy kiểm thử hoặc máy chấm thi của hội đồng giảng viên cũng được"), loại bỏ hoàn toàn các lỗi xung đột phiên bản môi trường (Node, Python, Java runtime) hay biến môi trường hệ điều hành.
  + Giúp sinh viên dễ dàng khởi chạy các dịch vụ phụ trợ (như PostgreSQL, MySQL, Redis) thông qua Docker Compose chỉ với một câu lệnh mà không cần cài đặt trực tiếp lên máy tính cá nhân.
  + Giúp sinh viên làm quen với chuẩn mực đóng gói và vận hành phần mềm trong môi trường kỹ nghệ doanh nghiệp hiện đại.

### 2. Căn Cứ Từ Thị Trường Tuyển Dụng Thực Tế (Market Evidence & Data Grounding)
Trình bày minh bạch bằng chứng từ dữ liệu tuyển dụng thực tế:
{market_evidence_block}

### 3. Lời Khuyên Hành Động Thực Tế (Pragmatic Action Plan)
- Đưa ra lời khuyên vừa sức: Sinh viên chưa cần học các kỹ thuật Docker chuyên sâu (như Multi-stage builds phức tạp hay cụm Swarm).
- Chỉ cần: 1 file `Dockerfile` chuẩn cho ứng dụng và 1 file `docker-compose.yml` để khởi chạy ứng dụng cùng database. Đây là "bằng chứng thép" (Proof of Work) trong Git Repo để gây ấn tượng mạnh với nhà tuyển dụng.
- Câu hỏi tương tác: Bạn có muốn tôi gợi ý một mẫu file `docker-compose.yml` đơn giản kết hợp backend và database cho đồ án của bạn không?
"""

    # =========================================================================
    # KỊCH BẢN TC10 TURN 3 & TC12: ĐIỀU CHỈNH PHƯƠNG ÁN THEO RÀNG BUỘC MỚI (CONSTRAINT UPDATE)
    # =========================================================================
    elif is_constraint_update:
        # Nhánh con: Nếu người dùng theo AI Engineer với Scikit-learn, 3 tháng, Python cơ bản (TC10 Turn 3)
        if any(k in user_message.lower() for k in ["scikit-learn", "sklearn"]) or ("ai" in target_role.lower() and session.get("time_months", 3) <= 3 and any(k in user_message.lower() for k in ["cơ bản", "phức tạp", "ba tháng", "3 tháng"])):
            scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC10 - TURN 3): ĐIỀU CHỈNH PHƯƠNG ÁN THEO RÀNG BUỘC (3 THÁNG, PYTHON CƠ BẢN, SCIKIT-LEARN, KHÔNG PHỨC TẠP).
Người dùng xác định rõ: Chỉ có ba tháng, trình độ Python cơ bản, muốn học scikit-learn và yêu cầu: "Đừng đề xuất kiến trúc phức tạp quá".
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, tinh gọn và thực tế):

### 1. Ghi Nhận Ngữ Cảnh & Điều Chỉnh Phạm Vi Phù Hợp với 3 Tháng & Python Cơ Bản
- Nhớ trọn vẹn ngữ cảnh: Giữ vững ý tưởng đề tài ban đầu là **"{session['idea']}"** và mục tiêu **"{target_role}"**.
- Ủng hộ mạnh mẽ: Lựa chọn **Scikit-learn** với nền tảng Python cơ bản trong 3 tháng là **quyết định rất thông minh, thực tế và vừa sức nhất** để bắt đầu con đường AI Engineer.
- NGUYÊN TẮC BẮT BUỘC: TUYỆT ĐỐI KHÔNG bắt người dùng nhập lại thông tin. TUYỆT ĐỐI KHÔNG tiếp tục đề xuất kiến trúc phân tán lớn, không Microservices, không Deep Learning nặng (PyTorch/TensorFlow lớn) hay RAG/LLM đa tác tử phức tạp trái với yêu cầu tinh gọn.

### 2. Đề Xuất 1 Tính Năng AI Tinh Gọn, Khả Thi Dùng Scikit-learn Tích Hợp Vào Sản Phẩm
Đề xuất tính năng AI vừa vặn, giá trị thực tiễn cao và hoàn toàn giải quyết bằng Scikit-learn:
- **Tính năng đề xuất:** **Hệ thống Gợi ý Sản phẩm Tinh gọn (Content-Based Recommendation Engine)** dựa trên mô tả/danh mục sản phẩm (sử dụng `TfidfVectorizer` kết hợp `cosine_similarity` từ Scikit-learn) HOẶC **Hệ thống Phân loại Đánh giá / Phản hồi Khách hàng (Sentiment Analysis)** dùng `CountVectorizer`/`TfidfVectorizer` kết hợp thuật toán `LogisticRegression` hoặc `MultinomialNB` từ Scikit-learn.
- **Luồng tích hợp đơn giản:**
  + Huấn luyện mô hình offline bằng Scikit-learn và xuất ra file model `.joblib` hoặc `.pkl`.
  + Tích hợp trực tiếp vào backend Python (dùng FastAPI hoặc Flask đơn giản) để gọi hàm dự đoán `model.predict()` khi có yêu cầu từ giao diện web.

### 3. Lộ Trình 3 Tháng Tinh Gọn (3-Month Pragmatic Roadmap)
- **Tháng 1: Củng Cố Nền Tảng Python & Khởi Tạo Ứng Dụng (Core App & Python Skills)**
  + Ôn tập lập trình Python hướng đối tượng, làm việc với JSON, danh sách và từ điển.
  + Xây dựng backend/web đơn giản hiển thị danh mục sản phẩm thương mại điện tử với dữ liệu mẫu.
- **Tháng 2: Khám Phá Dữ Liệu & Huấn Luyện Mô Hình Scikit-learn (Data & Model Training)**
  + Sử dụng Pandas để làm sạch dữ liệu mô tả sản phẩm / đánh giá khách hàng.
  + Áp dụng Scikit-learn chia tập train/test, huấn luyện thuật toán gợi ý/phân loại và đánh giá độ chính xác (Precision, Recall).
- **Tháng 3: Tích Hợp Mô Hình Vào Website & Hoàn Thiện Demo (Serving & Demo Polish)**
  + Tạo một API endpoint đơn giản bằng FastAPI nhận ID sản phẩm và trả về danh sách 5 sản phẩm tương đồng nhất.
  + Hiển thị khối "Sản phẩm gợi ý dành cho bạn" trên giao diện web.
  + Viết file `README.md` giải thích cách thức hoạt động của thuật toán và chuẩn bị kịch bản demo bảo vệ đồ án.

### 4. Câu Hỏi Tương Tác Mở
- Bạn thích bài toán gợi ý sản phẩm liên quan (Recommendation) hay bài toán phân loại đánh giá tích cực/tiêu cực của khách hàng hơn? Chúng ta cùng bắt đầu thu thập một tập dữ liệu nhỏ nhé!
"""
        else:
            # Nhánh chung cho TC12: Ràng buộc 1 người, thời gian ngắn (6 tuần), chưa từng deploy, từ chối AI, ưu tiên demo
            time_desc = f"{session.get('time_months', 1.5) * 4:.0f} tuần (~{session.get('time_months', 1.5)} tháng)" if session.get('time_months') else "sáu tuần (~1.5 tháng)"
            scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC12): ĐIỀU CHỈNH PHƯƠNG ÁN THEO RÀNG BUỘC MỚI (LÀM 1 MÌNH, {time_desc}, CHƯA TỪNG DEPLOY, CHƯA CẦN AI, ƯU TIÊN BẢN DEMO CHẠY ĐƯỢC).
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, thực tế và có tính định hướng cao):

### 1. Giữ Trọn Vẹn Bài Toán Cốt Lõi Nhưng Điều Chỉnh Quy Mô Thực Tế
- Nhớ bài toán gốc: Giữ vững ý tưởng đề tài **"{session['idea']}"** theo hướng **"{target_role}"**.
- Thấu cảm và điều chỉnh: Làm đồ án **một mình trong vòng {time_desc}** là một giới hạn lớn về nguồn lực. Vì vậy, chiến lược thành công duy nhất là **tối giản hóa phạm vi (Scope Pruning)** để chắc chắn có sản phẩm chạy được thay vì ôm đồm để rồi dở dang.

### 2. Tôn Trọng Tuyệt Đối Yêu Cầu "Chưa Cần Tính Năng AI"
- NGUYÊN TẮC BẮT BUỘC: **TUYỆT ĐỐI KHÔNG tiếp tục ép thêm AI hay gợi ý thêm các tính năng Machine Learning/LLM** khi người dùng đã nói rõ "chưa cần tính năng AI".
- Khẳng định: Một website hoàn chỉnh, nghiệp vụ mượt mà, không lỗi và có link demo chạy thật giá trị hơn gấp nhiều lần một ứng dụng gắn AI gượng ép nhưng các chức năng cơ bản bị lỗi.

### 3. Tinh Gọn Các Luồng Nghiệp Vụ Cốt Lõi (Core MVP Flows)
Tập trung 100% vào các luồng nghiệp vụ quan trọng nhất của bài toán học trực tuyến:
- **Quản lý Khóa học & Bài học (Courses & Lessons):** Hiển thị danh mục khóa học, video bài giảng (nhúng video hoặc lưu link phát video).
- **Làm Bài Kiểm Tra (Quizzes & Assessments):** Sinh viên làm bài trắc nghiệm và hệ thống tự động chấm điểm, hiển thị kết quả.
- **Theo Dõi Tiến Độ Học Tập (Progress Tracking):** Đánh dấu bài học đã hoàn thành và hiển thị thanh tiến độ (% hoàn thành khóa học).
- **Tạm hoãn / Chuyển sang phần mở rộng:** Tạm hoãn hệ thống gợi ý AI, thanh toán đa cổng phức tạp, phòng chat thời gian thực hoặc diễn đàn đa cấp.

### 4. Đưa Triển Khai Ứng Dụng (Deployment) & Kiểm Thử Vào Kế Hoạch Thay Vì Chỉ Viết Code
- Vì sinh viên chưa từng triển khai ứng dụng lên server, kế hoạch bắt buộc phải dành thời gian thích đáng cho phần triển khai:
  + Chọn nền tảng triển khai miễn phí, dễ dùng và ổn định: **Render / Vercel / Railway** hoặc đóng gói bằng **Docker Compose**.
  + Hướng dẫn thiết lập biến môi trường an toàn (`.env`), kết nối database trên cloud và cấu hình CORS giữa Frontend và Backend.
  + Viết một số bài kiểm thử tự động (Unit Test / Integration Test) cho các luồng nghiệp vụ cốt lõi (như logic chấm điểm trắc nghiệm và ghi nhận tiến độ).

### 5. Kế Hoạch 6 Tuần Chi Tiết Cho 1 Người (6-Week Feasible Solo Plan)
- **Tuần 1: Thiết Kế Mô Hình CSDL & Khởi Tạo Backend API**
  + Thiết kế mô hình ERD: Bảng `Users`, `Courses`, `Lessons`, `Quizzes`, `UserProgress`.
  + Khởi tạo dự án Monolith, kết nối database và viết API xác thực người dùng cơ bản (JWT).
- **Tuần 2: Hiện Thực Hóa API Khóa Học, Bài Học & Bài Kiểm Tra**
  + Xây dựng các API xem khóa học, danh sách bài học và nộp bài kiểm tra trắc nghiệm.
- **Tuần 3: Xây Dựng Giao Diện Người Dùng (Frontend UI)**
  + Thiết kế trang chủ khóa học, trang xem video bài giảng và giao diện làm bài kiểm tra.
- **Tuần 4: Tích Hợp Frontend - Backend & Tính Năng Tiến Độ Học Tập**
  + Kết nối gọi API, cập nhật và hiển thị trực quan thanh tiến độ hoàn thành khóa học.
- **Tuần 5: Triển Khai Ứng Dụng Lên Server Thực Tế (Deployment & Testing)**
  + Triển khai Backend và Database lên Render/Railway, Frontend lên Vercel.
  + Kiểm thử toàn bộ luồng người dùng trên môi trường production thật để đảm bảo không lỗi.
- **Tuần 6: Sửa Lỗi (Bug Fixing), Chuẩn Bị Kịch Bản Demo & Tài Liệu**
  + Chuẩn bị dữ liệu mẫu đẹp mắt, quay video demo dự phòng và hoàn thiện slide báo cáo.

### 6. Câu Hỏi Tương Tác Mở
- Bạn dự định dùng ngôn ngữ/framework nào mà bạn cảm thấy tự tin nhất (ví dụ React + Node.js, hay Python FastAPI/Django) để chúng ta bắt đầu thiết kế bảng dữ liệu cho Tuần 1?
"""

    # =========================================================================
    # KỊCH BẢN TC07: ĐỒ ÁN QUÁ THAM VỌNG SO VỚI THỜI GIAN NGẮN (NHÓM 3 - TC07 - P0)
    # =========================================================================
    elif is_overambitious_scope:
        time_limit = session.get('time_months', 1)
        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC07): ĐỒ ÁN QUÁ THAM VỌNG SO VỚI THỜI GIAN ({time_limit} THÁNG).
Người dùng muốn triển khai cùng lúc nhiều công nghệ phân tán / AI nặng ({tech_str}) trong thời gian rất ngắn ({time_limit} tháng / ~4 tuần).
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, thẳng thắn và xây dựng):

### 1. Cảnh Báo Trực Diện Về Nguy Cơ Vỡ Tiến Độ (Scope & Time Mismatch)
- Phân tích thẳng thắn nhưng mang tính xây dựng: Việc xây dựng một sản phẩm hoàn chỉnh kết hợp cả Microservices, Kubernetes, Kafka, AI Agent, RAG và triển khai Cloud trong vòng {time_limit} tháng (~4 tuần) là **bất khả thi và mang rủi ro cực lớn**, đặc biệt đối với sinh viên chưa có nhiều năm kinh nghiệm vận hành hạ tầng DevOps phức tạp.
- Nêu rõ nguyên nhân kỹ thuật:
  + Dựng cụm Kubernetes (K8s) và Kafka đòi hỏi cấu hình hạ tầng rất nặng, giải quyết bài toán networking, volume, partition và quản lý broker lag.
  + Microservices đòi hỏi xử lý phân tán giao dịch (Saga / 2PC), Service Discovery, API Gateway và tracing lỗi phân tán.
  + AI Agent và RAG đòi hỏi chuẩn bị dữ liệu, vector database và tối ưu hóa prompt/latency.
  + Nếu cố nhồi nhét, sinh viên sẽ mất 80% thời gian để cấu hình môi trường mà không có nổi một tính năng nghiệp vụ nào chạy được.
- NGUYÊN TẮC: TUYỆT ĐỐI KHÔNG chiều theo và không đề xuất triển khai toàn bộ các công nghệ này trong 1 tháng.

### 2. Thu Hẹp Phạm Vi Về MVP Khả Thi Cốt Lõi (Core MVP in 1 Month)
Định hình một kiến trúc **Monolithic / Modular Monolith** tinh gọn, tập trung hoàn thiện trọn vẹn luồng nghiệp vụ chính:
- **Frontend:** Giao diện người dùng sạch sẽ, hoàn thiện luồng trải nghiệm khách hàng (xem danh mục/sản phẩm, giỏ hàng, đặt hàng/thanh toán mô phỏng).
- **Backend:** Xây dựng một Backend Service duy nhất (Monolith với Node.js / Spring Boot / FastAPI) với kiến trúc phân tầng chuẩn (Controller -> Service -> Repository).
- **Database:** Sử dụng 1 CSDL quan hệ duy nhất (PostgreSQL hoặc MySQL) để đảm bảo giao dịch ACID mượt mà cho giỏ hàng và đơn hàng.
- **Nghiệp vụ cốt lõi:** Xác thực người dùng (JWT), danh mục sản phẩm, quản lý đơn hàng.

### 3. Đề Xuất 1-2 Phần Mở Rộng Thực Tế (Pragmatic Extensions)
Thay vì các công nghệ phân tán quá khổ, hãy gợi ý các phần mở rộng có giá trị thực tiễn cao nhất mà sinh viên có thể làm kịp:
- **Docker & Docker Compose:** Đóng gói toàn bộ ứng dụng (Web + Backend + Database) chạy "1-click" trên máy tính của bất kỳ ai.
- **Kiểm thử tự động (Automated Testing):** Viết Unit Test và Integration Test cho luồng tính toán đơn hàng và trừ kho để chứng minh chất lượng code.

### 4. Tạm Hoãn (Deferred / Phase 2) Các Công Nghệ Phức Tạp
- Nêu rõ quyết định dời toàn bộ: **Microservices, Kubernetes, Kafka, AI Agent và RAG** sang giai đoạn 2 (khi hệ thống thực sự có nhu cầu nghiệp vụ quy mô lớn hoặc khi bạn có thêm 3-6 tháng sau khi hoàn thành đồ án môn học).

### 5. Lộ Trình Khả Thi Theo Từng Tuần (4-Week Feasible Roadmap)
- **Tuần 1: Thiết Kế & Khởi Tạo Nền Tảng (Core Setup & Schema)**
  + Thiết kế mô hình CSDL (ERD) chuẩn 3NF.
  + Khởi tạo project Backend Monolith và kết nối PostgreSQL/MySQL.
  + Viết các API CRUD cơ bản cho sản phẩm và tài khoản.
- **Tuần 2: Hiện Thực Hóa Luồng Nghiệp Vụ Cốt Lõi (Business Flow & Transactions)**
  + Xây dựng luồng giỏ hàng, đặt hàng và quản lý đơn hàng.
  + Đảm bảo giao dịch ACID trong CSDL khi trừ tồn kho và xác nhận đơn.
- **Tuần 3: Tích Hợp Giao Diện & Trải Nghiệm Người Dùng (Frontend Integration)**
  + Xây dựng giao diện Web (React / Vue / HTML5) kết nối API Backend.
  + Xử lý đầy đủ các trạng thái UX: Loading, Error, Empty, Success.
- **Tuần 4: Kiểm Thử, Đóng Gói Docker & Hoàn Thiện (Testing & Polish)**
  + Viết Unit Test cho logic đặt hàng.
  + Viết file `docker-compose.yml` đóng gói toàn bộ hệ thống.
  + Hoàn thiện tài liệu `README.md` với sơ đồ kiến trúc và video demo sẵn sàng bảo vệ.

### 6. Giả Định Về Kinh Nghiệm & Câu Hỏi Tương Tác Mở
- Nêu rõ giả định: Lộ trình này giả định bạn đã có kiến thức cơ bản về lập trình Web/Backend và có thể dành khoảng 15-20 giờ/tuần cho đồ án.
- Câu hỏi tương tác: Bạn dự kiến sử dụng ngôn ngữ/framework nào đã quen thuộc nhất (ví dụ Node.js, Python hay Java) để cùng bắt tay vào thiết kế CSDL cho Tuần 1?
"""

    # =========================================================================
    # KỊCH BẢN TC08: PHỤ THUỘC PHẦN CỨNG / THIẾU THÔNG SỐ CẢM BIẾN (NHÓM 3 - TC08 - P1)
    # =========================================================================
    elif is_hardware_or_missing_spec:
        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC08): ĐỒ ÁN PHỤ THUỘC PHẦN CỨNG / CẢM BIẾN IOT CHƯA ĐƯỢC XÁC ĐỊNH ({session['idea']}).
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, chuyên nghiệp và có tư duy hệ thống):

### 1. Phân Tích Kiến Trúc 6 Tầng Cốt Lõi Của Hệ Thống Giám Sát IoT
Phân tích mạch lạc bức tranh tổng thể từ phần cứng đến giao diện:
1. **Tầng Cảm biến & Vi điều khiển (Sensor & Edge Layer):** Thu thập các tín hiệu vật lý từ môi trường và chuyển đổi thành dữ liệu số.
2. **Tầng Thu thập & Giao thức Truyền tải (Data Ingestion & Transport):** Gửi dữ liệu từ vi điều khiển về máy chủ qua giao thức mạng phù hợp (MQTT hoặc HTTP/REST qua Wi-Fi/4G).
3. **Tầng Backend Xử lý & Xác thực (Backend Service):** Tiếp nhận luồng telemetry, giải mã gói tin (decode payload), kiểm tra tính hợp lệ và xác thực định danh thiết bị.
4. **Tầng Lưu trữ Dữ liệu (Storage Layer):** Lưu trữ dữ liệu chuỗi thời gian (Time-series Database như InfluxDB, TimescaleDB hoặc PostgreSQL có index thời gian).
5. **Tầng Dashboard Giám sát (Monitoring UI):** Hiển thị biểu đồ theo thời gian thực (Line chart, gauge) các chỉ số chất lượng không khí.
6. **Tầng Cảnh báo Tức thời (Alerting Engine):** Kiểm tra ngưỡng an toàn (Threshold validation) và kích hoạt gửi thông báo (Email / Telegram Bot / Webhook) khi chỉ số vượt ngưỡng nguy hiểm.

### 2. Khẳng Định Lựa Chọn Thiết Bị & Giao Thức Ảnh Hưởng Trực Tiếp Đến Kiến Trúc Backend
- Nêu rõ: Quyết định về loại cảm biến và vi điều khiển không chỉ là chuyện phần cứng, mà quyết định trực tiếp tới thiết kế phần mềm Backend:
  + Nếu dùng cảm biến khí độc/khói (MQ-135, MQ-2, MQ-7): Tín hiệu là điện áp analog (Analog to Digital - ADC), cần thuật toán hiệu chuẩn (Calibration) trong code vi điều khiển.
  + Nếu dùng cảm biến bụi mịn (PMS5003 / PMS7003): Dữ liệu truyền qua UART chuẩn digital (PM1.0, PM2.5, PM10).
  + Tần suất đo: Đẩy dữ liệu theo giây (cần MQTT / WebSocket nhẹ, non-blocking) hay theo phút (có thể dùng HTTP POST).
  + Vi điều khiển: Dùng ESP32 (tích hợp Wi-Fi giá rẻ, mạnh mẽ) hay Arduino (cần module ngoài).

### 3. Đưa Ra Phương Án Sơ Bộ (Preliminary Solution) Kèm Giả Định Rõ Ràng
- Nêu rõ: "Đây là **phương án kiến trúc sơ bộ** dựa trên một số giả định kỹ thuật phổ biến nhất hiện nay cho đồ án sinh viên":
  + **Giả định phần cứng:** Sử dụng vi điều khiển **ESP32** (tích hợp Wi-Fi) kết hợp module cảm biến nhiệt ẩm (DHT22) và cảm biến bụi mịn/khí (PMS5003 hoặc MQ-135).
  + **Giao thức truyền:** **MQTT** qua Broker trung gian (Eclipse Mosquitto hoặc HiveMQ public/local) vì tiết kiệm băng thông và tối ưu cho thiết bị IoT.
  + **Backend:** **Python (FastAPI)** hoặc **Node.js** subscribe MQTT topic, xử lý dữ liệu và phát WebSockets lên Dashboard.
  + **Database:** **PostgreSQL** (hoặc SQLite/TimescaleDB) lưu lịch sử.
  + **Dashboard:** Web UI (React hoặc Vue) cập nhật biểu đồ thời gian thực.
- NGUYÊN TẮC BẮT BUỘC: PHÂN BIỆT RÕ phương án sơ bộ này với quyết định công nghệ cuối cùng (quyết định cuối cùng chỉ chốt sau khi người dùng xác định rõ phần cứng).
- TUYỆT ĐỐI KHÔNG tự ý gán hay mặc định rằng người dùng đã chốt loại cảm biến nào.

### 4. Xử Lý Khi Chưa Có Dự Án GitHub Tương Tự
- Nếu kho tham khảo của hệ thống chưa có một repo GitHub giống hệt 100%, hãy nói rõ giới hạn nguồn tham khảo này và **vẫn tiếp tục tư vấn chuyên sâu theo bản chất kỹ thuật của bài toán**.
- Tuyệt đối KHÔNG bịa đặt link repo GitHub không tồn tại, và TUYỆT ĐỐI KHÔNG để việc thiếu dự án làm dừng toàn bộ việc tư vấn.

### 5. Câu Hỏi Tương Tác Làm Rõ Trực Tiếp Kiến Trúc
Đặt câu hỏi quan trọng để chốt kiến trúc:
1. Bạn dự kiến hệ thống sẽ đo lường **những chỉ số cụ thể nào** (Ví dụ: Nồng độ bụi mịn PM2.5/PM10, khí CO/CO2, hay chủ yếu là nhiệt độ & độ ẩm)?
2. Thiết bị của bạn dự kiến sẽ kết nối mạng theo hình thức nào (Wi-Fi qua chip ESP32 trong nhà, hay cần giải pháp không dây khác)?
"""

    # =========================================================================
    # KỊCH BẢN TC09: PHẢN BIỆN KỸ THUẬT VỀ CÔNG NGHỆ KHÔNG PHÙ HỢP / OVERKILL (NHÓM 3 - TC09 - P1)
    # =========================================================================
    elif is_overkill_tech_choice:
        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC09): PHẢN BIỆN KỸ THUẬT VỀ VIỆC CHỌN CÔNG NGHỆ OVERKILL KHÔNG PHÙ HỢP VỚI BÀI TOÁN ({session['idea']}).
Người dùng muốn áp dụng Kafka, Kubernetes và Microservices cho một bài toán quy mô nhỏ (quản lý thư viện / đồ án môn học) vì cảm thấy "rất chuyên nghiệp".
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, phản biện sắc sảo, tôn trọng mục tiêu học tập):

### 1. Phản Biện Kỹ Thuật: Công Nghệ Phục Vụ Nghiệp Vụ (Technology Follows Business Needs)
- Thẳng thắn và mang tính khai phóng: Trong kỹ nghệ phần mềm chuyên nghiệp, **chất lượng đồ án không nằm ở việc sử dụng công nghệ phức tạp nhất**, mà nằm ở việc **chọn giải pháp phù hợp nhất để giải quyết triệt để bài toán nghiệp vụ với độ tin cậy cao và chi phí tối ưu**.
- Khẳng định: Việc áp dụng Kafka, Kubernetes và Microservices cho một hệ thống quản lý thư viện nhỏ của đồ án môn học là một trường hợp **Over-Engineering (Lãng phí tài nguyên và phức tạp hóa bài toán)**.

### 2. Nêu Rõ Các Rủi Ro Kỹ Thuật Khi Dùng Kiến Trúc Phân Tán Cho Bài Toán Nhỏ
1. **Gánh nặng độ phức tạp (Complexity Overhead):** Bạn sẽ phải tiêu tốn 70% thời gian để viết Dockerfile, cấu hình K8s Ingress, Service, Persistent Volumes, quản lý cụm Kafka/KRaft brokers thay vì tập trung vào nghiệp vụ quản lý mượn trả sách.
2. **Phá vỡ tính toàn vẹn giao dịch (ACID vs. Distributed Transactions):** Nghiệp vụ cốt lõi của thư viện là *Mượn và Trả sách*. Thao tác này đòi hỏi tính toàn vẹn ACID tuyệt đối (kiểm tra sách còn không -> tạo phiếu mượn -> giảm số lượng sách khả dụng). Nếu tách thành Microservices và Kafka, bạn sẽ phải đối mặt với bài toán Distributed Transactions (Saga pattern, Eventual Consistency, xử lý bù trừ) cực kỳ phức tạp và dễ dẫn đến sai lệch số lượng sách.
3. **Lưu lượng truy cập không đòi hỏi (Throughput Mismatch):** Apache Kafka được thiết kế để xử lý hàng trăm nghìn sự kiện/giây (như log phân tích, streaming). Một thư viện nhỏ với vài chục người dùng chỉ phát sinh vài thao tác mỗi phút, dùng Kafka giống như "dùng đại bác để bắn chim sẻ".
4. **Tiêu hao tài nguyên phần cứng:** Việc chạy minikube/K8s và cụm Kafka sẽ ngốn từ 8GB - 16GB RAM máy tính cá nhân, dễ gây đơ máy khi phát triển.

### 3. Đề Xuất Kiến Trúc Tinh Gọn Chuẩn Mực Thay Thế
Đề xuất kiến trúc phù hợp hoàn hảo với quy mô đồ án thư viện:
- **Kiến trúc:** **Monolithic / Layered Architecture** hoặc **Modular Monolith** (tách package theo domain: `book-management`, `user-management`, `lending-management`).
- **Tech Stack:**
  + Backend: Spring Boot (Java), NestJS (TypeScript) hoặc FastAPI (Python).
  + Cơ sở dữ liệu: **PostgreSQL** hoặc **MySQL** với thiết kế ERD chuẩn 3NF, tận dụng cơ chế giao dịch `@Transactional` ACID để ngăn chặn triệt để việc 2 người cùng mượn 1 cuốn sách cuối cùng.
  + Giao diện: Web giao diện sạch sẽ, thân thiện.
- **Tiêu chí chuyên nghiệp thực tế:** Đồ án sẽ cực kỳ chuyên nghiệp nếu bạn chứng minh được: Thiết kế API chuẩn RESTful, mô hình ERD chặt chẽ, bắt lỗi tập trung (Global Exception Handling), viết Unit Test cho logic mượn/trả và đóng gói bằng Docker Compose.

### 4. Tôn Trọng Mục Tiêu Học Tập & Đề Xuất Module Thử Nghiệm Riêng (Sandbox / PoC)
- Tôn trọng đam mê khám phá công nghệ mới của sinh viên: Nếu bạn thực sự muốn tìm hiểu Kafka hoặc Kubernetes để ghi điểm với nhà tuyển dụng:
  + **Chiến lược thông minh:** Hãy hoàn thành 100% hệ thống Monolith ổn định trước.
  + **Tạo Sandbox PoC riêng:** Sau khi hệ thống chính đã chạy, hãy thiết kế một tính năng độc lập nhỏ để thử nghiệm Kafka, ví dụ: Module gửi thông báo tự động (Notification Service) - mỗi khi có sách quá hạn trả, hệ thống chính bắn một event vào Kafka topic `book-overdue-events`, và một worker độc lập tiêu thụ event để gửi email nhắc nhở.
  + Bằng cách này, bạn vừa giữ được đồ án chính an toàn, vừa có một bài thuyết trình ấn tượng về việc áp dụng Kafka đúng chỗ.

### 5. Câu Hỏi Tương Tác Mở
- Bạn thấy phương án tiếp cận Modular Monolith trước và mở rộng Kafka bằng Module thông báo sau có phù hợp với thời gian hiện tại của bạn không? Bạn muốn cùng tôi bắt tay vào thiết kế mô hình dữ liệu (ERD) cho các bảng `Books`, `Users`, `BorrowTickets` trước không?
"""

    # =========================================================================
    # KỊCH BẢN TC06: ĐÃ HỌC CÔNG NGHỆ, HỎI ĐỦ ỨNG TUYỂN CHƯA & THIẾU KỸ NĂNG GÌ (TỔNG QUÁT HÓA MỌI VAI TRÒ)
    # =========================================================================
    elif is_intern_readiness_audit:
        role_lower = target_role.lower()
        if "data engineer" in role_lower or "kỹ sư dữ liệu" in role_lower:
            competence_1 = "1. **SQL và Mô hình hóa Dữ liệu (Data Modeling):** Nâng cấp từ truy vấn cơ bản sang SQL nâng cao (CTEs, Window Functions `ROW_NUMBER()`, `RANK()`, `LEAD()`, `LAG()`) và tư duy thiết kế kho dữ liệu dạng Star Schema / Snowflake Schema (Fact tables, Dimension tables, surrogate keys, khóa ngoại toàn vẹn)."
            competence_2 = "2. **Xây Dựng Pipeline ETL/ELT:** Năng lực thiết kế luồng dữ liệu end-to-end: Trích xuất (Extract) từ nguồn (REST API, Database OLTP, file logs/CSV), Biến đổi (Transform) dữ liệu và Nạp (Load) vào Data Warehouse/Database; bảo đảm tính Idempotency (chạy lại pipeline mà không gây trùng lặp hay sai lệch số liệu)."
            competence_3 = "3. **Xử Lý Dữ Liệu Lỗi hoặc Thiếu (Data Quality & Cleaning):** Đối mặt với dữ liệu thực tế: phát hiện và xử lý missing/null values, khử trùng lặp (deduplication), schema validation và xây dựng các bài test chất lượng dữ liệu tự động."
            competence_4 = "4. **Tự Động Hóa và Lập Lịch Pipeline (Automation & Scheduling):** Chuyển từ chạy script thủ công sang tự động hóa định kỳ bằng Apache Airflow (viết DAGs, quản lý task dependencies) hoặc Cron jobs / GitHub Actions."
            competence_5 = "5. **Kiểm Thử, Theo Dõi Lỗi và Tài Liệu Hóa (Testing, Observability & Documentation):** Cấu hình Structured Logging, viết Unit Test cho logic biến đổi với `pytest`, và viết `README.md` chuyên nghiệp kèm sơ đồ luồng dữ liệu (Data Lineage)."
            mini_proj_name = "End-to-End E-Commerce/Public Data Ingestion & Warehouse Pipeline"
            mini_proj_arch = "Ingestion (API/Web scraping) -> Processing & Quality (Python, Pandas, Schema validation) -> Storage & Modeling (PostgreSQL Star Schema) -> Automation (Airflow/Cron)."
            mini_proj_artifacts = "Thư mục `pipeline/` chứa mã nguồn ETL chuẩn mực, thư mục `schemas/` chứa DDL Star Schema, thư mục `tests/` với các test case `pytest`, file `README.md` kèm sơ đồ kiến trúc luồng dữ liệu."
        elif "backend" in role_lower:
            competence_1 = "1. **Thiết Kế RESTful API Chuẩn Mực:** Chuẩn hóa cấu trúc URI, sử dụng đúng HTTP Methods và Status Codes, quản lý phiên bản API (API Versioning) và tài liệu hóa bằng Swagger/OpenAPI 3.0."
            competence_2 = "2. **Mô Hình Hóa CSDL & Quản Lý Giao Dịch (Database Modeling & ACID Transactions):** Thiết kế mô hình dữ liệu chuẩn hóa (3NF), lập chỉ mục (Indexing) tối ưu hóa truy vấn, quản lý giao dịch ACID và cơ chế khóa chống tranh chấp đồng thời (Concurrency Locking: Pessimistic/Optimistic Locking)."
            competence_3 = "3. **Xác Thực, Phân Quyền & Bảo Mật (Authentication & Security):** Hiện thực hóa cơ chế JWT Authentication (Access/Refresh Token), phân quyền theo vai trò (RBAC), và áp dụng các biện pháp bảo mật cốt lõi (chống SQL Injection, XSS, CORS, băm mật khẩu BCrypt/Argon2)."
            competence_4 = "4. **Xử Lý Lỗi Tập Trung & Kiến Trúc Phân Tầng (Global Error Handling & Architecture):** Cấu hình Global Exception Handling theo chuẩn Problem Details (RFC 7807), phân tách kiến trúc phân tầng rõ ràng (Controller -> Service -> Repository)."
            competence_5 = "5. **Kiểm Thử Tự Động & Đóng Gói (Automated Testing & Docker):** Viết Unit Test và Integration Test kiểm chứng các luồng nghiệp vụ quan trọng (độ phủ > 60%), đóng gói ứng dụng chạy đồng nhất bằng Docker & Docker Compose."
            mini_proj_name = "Enterprise Booking or Order Management Backend API Service with RBAC & Concurrency Control"
            mini_proj_arch = "Client -> Controller (Validation) -> Service (Business Logic + Transactions) -> Repository -> PostgreSQL / MySQL."
            mini_proj_artifacts = "Thư mục `src/` phân tầng chuẩn mực, thư mục `tests/` với Unit & Integration tests, file `docker-compose.yml`, Swagger UI public endpoint, và file `README.md` hướng dẫn chạy."
        elif "frontend" in role_lower:
            competence_1 = "1. **Kiến Trúc Component & Tái Sử Dụng:** Phân tách component mạch lạc, phân biệt rõ Presentational và Container Components, tối ưu hóa khả năng tái sử dụng và khả năng bảo trì giao diện."
            competence_2 = "2. **Quản Lý Trạng Thái (State Management):** Làm chủ State nội bộ, Context API hoặc các giải pháp quản lý State tập trung (Redux Toolkit, Zustand), kiểm soát chặt chẽ luồng dữ liệu một chiều."
            competence_3 = "3. **Luồng Gọi API Bất Đồng Bộ & Xử Lý Trạng Thái UX:** Xử lý đầy đủ các trạng thái giao diện khi tương tác với API (Loading indicator, Empty state, Error boundary, Toast feedback, Caching dữ liệu với React Query/SWR)."
            competence_4 = "4. **Thiết Kế Đáp Ứng & Kiến Trúc Giao Diện (Responsive UI & Styling):** Xây dựng giao diện Responsive đa thiết bị (Mobile/Tablet/Desktop), tuân thủ Accessibility (a11y), quản lý CSS module hóa hoặc TailwindCSS."
            competence_5 = "5. **Tối Ưu Hiệu Năng & Kiểm Thử Giao Diện:** Tối ưu hóa thời gian tải trang (Lazy loading, Code splitting, tối ưu Core Web Vitals), viết Unit Test cho UI components (Jest/React Testing Library)."
            mini_proj_name = "Interactive Analytics Dashboard or E-Commerce Storefront with Real-Time Filters"
            mini_proj_arch = "React/Vue SPA -> State Management -> API Client Layer -> Backend Mock/REST API."
            mini_proj_artifacts = "Source code phân chia module/components sạch sẽ, thư mục `tests/` kiểm thử component, file `README.md` kèm ảnh chụp màn hình (screenshots) và link demo trực tiếp (Vercel/Netlify)."
        elif any(k in role_lower for k in ["ai", "machine learning"]):
            competence_1 = "1. **Tiền Xử Lý Dữ Liệu & Phân Tích Khám Phá (Data Wrangling & EDA):** Kỹ năng làm sạch dữ liệu thô, kỹ thuật trích xuất đặc trưng (Feature Engineering) và trực quan hóa phân phối dữ liệu với Pandas/NumPy/Matplotlib."
            competence_2 = "2. **Huấn Luyện & Đánh Giá Mô Hình (Model Training & Metrics):** Huấn luyện các mô hình Baseline và Nâng cao, đánh giá dựa trên các metrics chuẩn doanh nghiệp (Precision, Recall, F1-Score, AUC-ROC, RMSE), xử lý Overfitting/Underfitting."
            competence_3 = "3. **Đóng Gói & Phục Vụ Mô Hình (Model Serving API):** Đóng gói mô hình thành REST API với FastAPI hoặc Flask, tối ưu hóa độ trễ phản hồi (Latency) và xử lý dữ liệu đầu vào theo batch."
            competence_4 = "4. **Kiểm Thử & Phân Tích Lỗi (Error Analysis & Validation):** Phân tích các trường hợp mô hình dự đoán sai (Edge cases), kiểm tra độ ổn định của pipeline suy luận."
            competence_5 = "5. **Quản Lý Phiên Bản & Đóng Gói (MLOps Basics & Docker):** Quản lý phiên bản dữ liệu/mô hình, đóng gói AI Service bằng Docker để triển khai độc lập."
            mini_proj_name = "End-to-End Recommendation or Intelligent Classification Service"
            mini_proj_arch = "Data Pipeline (Preprocessing) -> Model Training & Export -> FastAPI Serving Engine -> Docker Container."
            mini_proj_artifacts = "Thư mục `notebooks/` cho EDA và Training, thư mục `service/` cho FastAPI model serving, file `Dockerfile`, và `README.md` giải thích chi tiết kiến trúc thuật toán và kết quả đánh giá metrics."
        elif "mobile" in role_lower:
            competence_1 = "1. **Kiến Trúc Giao Diện Di Động & Responsive Layout:** Thiết kế màn hình thích ứng tốt trên nhiều kích thước màn hình và hướng xoay (Portrait/Landscape), tuân thủ Material Design hoặc iOS Human Interface Guidelines."
            competence_2 = "2. **Quản Lý Trạng Thái Ứng Dụng (Mobile State Management):** Quản lý State rõ ràng (Bloc/Provider/Riverpod cho Flutter, hoặc MVVM cho Native), tách biệt UI khỏi logic nghiệp vụ."
            competence_3 = "3. **Tích Hợp REST API & Xử Lý Bất Đồng Bộ:** Kết nối mạng mượt mà, xử lý phân trang (Pagination/Infinite scroll), pull-to-refresh và xử lý lỗi mạng thân thiện với người dùng."
            competence_4 = "4. **Lưu Trữ Dữ Liệu Cục Bộ (Local Storage & Offline-First):** Sử dụng SQLite/Hive/Room để lưu trữ cache cục bộ, cho phép người dùng xem dữ liệu khi offline và tự động đồng bộ khi có mạng."
            competence_5 = "5. **Kiểm Thử & Đóng Gói Ứng Dụng (Testing & Build):** Viết Widget/UI test, quản lý quyền truy cập thiết bị (Permissions) và tạo bản build APK/IPA hoàn chỉnh."
            mini_proj_name = "Offline-First Personal Finance or Task Management Mobile App"
            mini_proj_arch = "Mobile UI -> State Controller -> Repository -> Local DB (Cache) / Remote REST API."
            mini_proj_artifacts = "Mã nguồn tổ chức theo Clean Architecture / BLoC, file APK demo, video quay trải nghiệm ứng dụng thực tế và `README.md` chi tiết."
        else:
            competence_1 = f"1. **Năng Lực Lõi Kỹ Thuật (Core Engineering Skills):** Làm chủ các nguyên lý kỹ thuật cốt lõi của vai trò {target_role}, hiểu sâu sắc cách thức vận hành bên dưới chứ không chỉ dừng ở cú pháp."
            competence_2 = f"2. **Xử Lý Dữ Liệu & Kiến Trúc Hệ Thống:** Thiết kế cấu trúc dữ liệu, luồng vận hành và tương tác giữa các thành phần một cách mạch lạc, có khả năng mở rộng."
            competence_3 = f"3. **Xử Lý Lỗi, Bảo Mật & Trường Hợp Ngoại Lệ (Edge Cases & Resilience):** Cơ chế bắt lỗi toàn cục, đối mặt với dữ liệu bất thường và áp dụng các tiêu chuẩn an toàn kỹ thuật."
            competence_4 = f"4. **Tự Động Hóa & Triển Khai (Automation & CI/CD):** Tự động hóa quy trình làm việc, thiết lập script đóng gói ứng dụng (Docker/Scripts) để chạy độc lập và nhất quán."
            competence_5 = f"5. **Kiểm Thử, Theo Dõi Lỗi & Tài Liệu Hóa (Testing & Docs):** Viết kiểm thử tự động (Unit/Integration Test), cấu hình logging và tài liệu hóa chi tiết trong README.md."
            mini_proj_name = f"End-to-End Practical Implementation Project for {target_role}"
            mini_proj_arch = "Core Logic -> Error & Edge Case Handling -> Automated Testing -> Containerization & Deployment."
            mini_proj_artifacts = "Source code chuẩn mực theo kiến trúc sạch, thư mục `tests/` kiểm thử tự động, cấu hình môi trường và file `README.md` hướng dẫn chi tiết."

        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (KIỂM TOÁN ĐỘ SẴN SÀNG INTERN/FRESHER): NGƯỜI DÙNG ĐÃ HỌC CÔNG NGHỆ ({tech_str}) VÀ MUỐN BIẾT ĐÃ ĐỦ ĐIỀU KIỆN ỨNG TUYỂN {target_role} (INTERN) CHƯA, CẦN BỔ SUNG GÌ VÀ THỂ HIỆN QUA ĐỒ ÁN.
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng, chuyên nghiệp và chặt chẽ):

### 1. Đánh giá Khách quan về Tính Đầy Đủ (Không Kết luận Vội vàng "Đủ" hay "Chưa Đủ")
- NGUYÊN TẮC BẮT BUỘC: KHÔNG KẾT LUẬN người dùng đã "đủ" hay "chưa đủ" điều kiện chỉ dựa trên danh sách công nghệ ({tech_str}).
- Giải thích rõ: Việc có đủ điều kiện ứng tuyển hay không hoàn toàn phụ thuộc vào yêu cầu cụ thể của từng vị trí tuyển dụng (JD) tại mỗi doanh nghiệp (ví dụ công ty product vs outsourcing, startup vs tập đoàn lớn), quy mô hệ thống thực tế và quan trọng nhất là mức độ thành thạo, tư duy kỹ thuật và năng lực giải quyết vấn đề thực tế của bạn, chứ không nằm ở số lượng từ khóa công nghệ bạn đã học qua cú pháp.

### 2. Phân Biệt Rạch Ròi giữa "Kỹ Năng Liệt Kê trong JD" với "Kỹ Năng Đã Được Chứng Minh Qua Sản Phẩm"
- Phân tích sâu sắc cho người dùng:
  + "Kỹ năng thường gặp trong JD": Các từ khóa như {tech_str} xuất hiện rất nhiều trong JD tuyển dụng {target_role} Intern đóng vai trò là "điều kiện cần / bộ lọc ban đầu".
  + "Kỹ năng đã được chứng minh": Nhà tuyển dụng không chỉ tìm kiếm một ứng viên biết viết cú pháp lệnh cơ bản hay làm theo các bài tập mẫu (tutorial). Họ tìm kiếm ứng viên có "Năng lực kỹ thuật thực tế (Engineering Competence)" có thể kiểm chứng được qua sản phẩm, mã nguồn và tư duy kiến trúc.
- TUYỆT ĐỐI KHÔNG đồng nhất việc "đã học/biết công nghệ" với việc "đã thành thạo kỹ năng".

### 3. 5 Nhóm Năng Lực Cốt Lõi Cần Kiểm Tra Thêm & Bổ Sung cho {target_role} Intern
Chỉ rõ các khoảng trống kỹ thuật cụ thể sinh viên cần kiểm tra và rèn luyện:
{competence_1}
{competence_2}
{competence_3}
{competence_4}
{competence_5}

### 4. Đề Xuất Một Đồ Án Nhỏ (Mini-Project) Thực Chiến để Thể Hiện Năng Lực Còn Thiếu
- Đề xuất một đồ án thực tế vừa sức (thực hiện trong 3-4 tuần):
  + **Tên đề tài gợi ý:** *{mini_proj_name}*.
  + **Kiến trúc luồng xử lý:** {mini_proj_arch}
  + **Bằng chứng nộp lên Git (Artifacts for CV):** {mini_proj_artifacts}

### 5. Khẳng Định Phụ Thuộc Vào Yêu Cầu Tuyển Dụng & Không Đảm Bảo Việc Làm Tuyệt Đối
- Nhấn mạnh rõ ràng: Hoàn thành đồ án mini-project trên sẽ giúp bạn có một "bằng chứng thép" (Proof of Work) để chứng minh năng lực vượt trội so với các ứng viên chỉ liệt kê từ khóa trong CV.
- NGUYÊN TẮC ĐẠO ĐỨC & TRUNG THỰC: TUYỆT ĐỐI KHÔNG hứa hẹn rằng hoàn thành một đồ án sẽ đảm bảo chắc chắn có việc làm 100%. Kết quả trúng tuyển còn phụ thuộc vào nhu cầu thực tế của từng doanh nghiệp, thái độ, tư duy phản biện, kỹ năng giải quyết vấn đề và sự thể hiện của bạn tại các vòng phỏng vấn chuyên môn.

### 6. Câu Hỏi Tương Tác Mở
- Đặt câu hỏi gợi mở cho người dùng: Trong 5 nhóm năng lực trên, bạn tự tin nhất ở phần nào và cảm thấy băn khoăn nhất ở phần nào? Bạn muốn bắt tay vào thiết kế mini-project với loại dữ liệu / nghiệp vụ nào?
"""

    # =========================================================================
    # KỊCH BẢN TC04: SINH VIÊN ĐÃ CHỌN STACK VÀ CẦN ĐÁNH GIÁ (NHÓM 2 - TC04)
    # =========================================================================
    elif is_evaluating_stack:
        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC04): SINH VIÊN ĐÃ CHỌN TECH STACK ({tech_str}) VÀ YÊU CẦU ĐÁNH GIÁ ĐỂ THEO HƯỚNG {target_role}.
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng):

### 1. Đánh giá Tính Phù Hợp của Tech Stack Hiện Tại với Sản Phẩm
- Đánh giá khách quan: Bộ công nghệ {tech_str} rất thực tế, phổ biến và hoàn toàn phù hợp để xây dựng sản phẩm này.
- NGUYÊN TẮC BẮT BUỘC: GIỮ NGUYÊN CÁC CÔNG NGHỆ ĐÃ CHỌN. Tuyệt đối KHÔNG bắt buộc đổi stack sang framework khác (như không ép đổi sang Spring Boot, NestJS hay Next.js) chỉ vì chúng được nhắc nhiều trên mạng, vì stack hiện tại đã đủ mạnh mẽ để đáp ứng bài toán.

### 2. Phân Biệt Rạch Ròi giữa "Đã Sử Dụng Công Nghệ" với "Đã Chứng Minh Được Năng Lực Thực Tế"
- Phân tích sâu sắc cho sinh viên: Cài đặt thư viện và làm các tính năng CRUD cơ bản theo tutorial ai cũng làm được. Nhưng nhà tuyển dụng đánh giá cao một ứng viên ở chỗ: Bạn đã chứng minh được "Năng lực làm chủ kỹ thuật (Engineering Competence)" trên chính stack đó như thế nào.
- TUYỆT ĐỐI KHÔNG giả định rằng sinh viên đã thành thạo kỹ năng chỉ vì họ đã chọn công nghệ đó. Hãy chỉ rõ những tiêu chuẩn kỹ thuật sinh viên cần đạt được qua sản phẩm.

### 3. 5 Tầng Năng Lực Cốt Lõi Cần Thể Hiện trên Chính Stack Đã Chọn
Chỉ rõ các tiêu chuẩn kỹ thuật cụ thể sinh viên cần hiện thực hóa:
1. **Frontend (ví dụ với React):** Kiến trúc phân tách Component rõ ràng; Quản lý trạng thái (State Management) hiệu quả; Luồng gọi API bất đồng bộ và xử lý UX trạng thái đầy đủ (Loading state, Error boundary, Empty state, Toast thông báo).
2. **Backend (ví dụ với Node.js):** Thiết kế RESTful API chuẩn mực (HTTP Status Codes, URI nhất quán); Cơ chế xác thực an toàn (JWT với Refresh Token); Phân quyền người dùng chặt chẽ (RBAC); và Hiện thực hóa logic nghiệp vụ phức tạp (như tính toán đơn hàng, trừ kho, chống xung đột).
3. **Database (ví dụ với MySQL):** Thiết kế mô hình dữ liệu chuẩn hóa (ERD đạt chuẩn 3NF, khóa ngoại toàn vẹn); Lập chỉ mục (Indexing) trên các trường tra cứu nhiều; Tối ưu hóa câu lệnh truy vấn SQL (tránh lỗi N+1 query); Quản lý Transaction ACID cho các thao tác đặt hàng/thanh toán.
4. **Chất lượng Phần mềm (Software Quality):** Xử lý lỗi tập trung (Global Exception Handling); Các biện pháp bảo mật cốt lõi (chống SQL Injection, XSS, CORS, băm mật khẩu bằng BCrypt/Argon2); Viết kiểm thử tự động (Unit Test cho logic nghiệp vụ, Integration Test cho API).
5. **Triển khai (Deployment & DevOps):** Quản lý cấu hình qua biến môi trường an toàn (.env); Đóng gói ứng dụng chạy đồng nhất bằng Docker & Docker Compose; hoặc thiết lập quy trình CI/CD cơ bản (GitHub Actions).

### 4. Đề Xuất Phần Bổ Sung có Mức Độ Ưu Tiên & Căn Cứ Dữ Liệu Tuyển Dụng TopCV
- Phân cấp ưu tiên rõ ràng:
  + **Ưu tiên 1 (Bắt buộc phải đạt):** Làm chủ và chứng minh trọn vẹn 5 tầng năng lực trên với chính stack {tech_str}.
  + **Ưu tiên 2 (Lợi thế cạnh tranh / Boosters):** Bổ sung Docker để đóng gói ứng dụng, Redis để caching tăng tốc độ truy vấn, hoặc viết Automated Tests.
- Dẫn chứng số liệu thực tế từ dữ liệu tuyển dụng TopCV cho vị trí {target_role}: REST API (~35%), Relational DB (~37%), Testing (~28%), Docker (~25%).

### 5. Câu Hỏi Tương Tác Mở
Đặt câu hỏi gợi mở về phần sinh viên cảm thấy còn bỡ ngỡ nhất trong 5 tầng năng lực trên để cùng lên kế hoạch hiện thực hóa.
"""

    # =========================================================================
    # KỊCH BẢN TC05: SẢN PHẨM WEB NHƯNG HƯỚNG TỚI DATA ENGINEER (NHÓM 2 - TC05)
    # =========================================================================
    elif is_web_to_data_pivot:
        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC05): SINH VIÊN ĐANG LÀM SẢN PHẨM WEB NHƯNG MỤC TIÊU LÀ DATA ENGINEER (GIỚI HẠN THỜI GIAN 3 THÁNG).
Bạn là Cố vấn Kỹ thuật & Hướng nghiệp GEM. Yêu cầu bạn tuân thủ các nguyên tắc sau (Trình bày định dạng Markdown rõ ràng):

### 1. Giữ Nguyên Website làm Nguồn Dữ Liệu (Data Source) và Giao Diện Quan Sát
- Đánh giá chiến lược: Quyết định tuyệt vời! KHÔNG cần phải đập bỏ website hay chuyển sang một đề tài hoàn toàn xa lạ.
- Định vị vai trò của sản phẩm web: Website hiện tại ({tech_str}) đóng vai trò là **Hệ thống Vận hành Nghiệp vụ (OLTP System)** sinh ra dữ liệu giao dịch thực tế, đồng thời làm **Giao diện Giám sát (Monitoring UI)** để kiểm chứng kết quả phân tích. Đồ án của bạn sẽ mang tính thực chiến rất cao khi có cả nguồn phát sinh dữ liệu lẫn đường ống xử lý.

### 2. Đề Xuất Luồng Dữ Liệu (Data Pipeline) Khả Thi trong Giới Hạn 3 Tháng
Trình bày cụ thể luồng xử lý dữ liệu 5 bước bài bản:
1. **Thu thập dữ liệu giao dịch (Ingestion):** Trích xuất dữ liệu từ CSDL nguồn (MySQL) theo dạng định kỳ (Batch Ingestion) hoặc CDC (Change Data Capture) mô phỏng bằng Python script.
2. **Kiểm tra và làm sạch dữ liệu (Data Quality & Cleaning):** Lọc bản ghi lỗi, xử lý giá trị null, loại bỏ trùng lặp và kiểm tra tính toàn vẹn của schema dữ liệu trước khi nạp vào kho.
3. **Biến đổi dữ liệu (Transformation):** Tổng hợp dữ liệu theo các chiều phân tích (doanh thu theo ngày/tháng/quý, top sản phẩm bán chạy, phân khúc khách hàng) bằng Python hoặc SQL/dbt models.
4. **Lưu trữ phục vụ phân tích (Data Warehouse / OLAP):** Mô hình hóa dữ liệu dạng Fact / Dimension (Star Schema hoặc Snowflake Schema), lưu trữ trong cơ sở dữ liệu chuyên dụng (PostgreSQL được tối ưu hoặc ClickHouse).
5. **Theo dõi lỗi và chất lượng dữ liệu (Data Observability & Error Handling):** Ghi nhật ký thực thi (Execution Logs), cơ chế cảnh báo khi pipeline bị gián đoạn và báo cáo độ tin cậy dữ liệu.

### 3. Phân Biệt Rạch Ròi giữa Data Engineer với Data Analyst / Data Scientist
- Phân tích rõ cho sinh viên: Một Data Engineer chịu trách nhiệm chính về **Hạ tầng, Độ tin cậy và Đường ống vận chuyển dữ liệu (Data Pipes & Infrastructure)**. Trọng tâm của bạn là bảo đảm dữ liệu đi từ nguồn đến kho một cách chính xác, đúng giờ và tối ưu tài nguyên; chứ không dừng lại ở việc kéo thả biểu đồ (Data Analyst) hay huấn luyện các mô hình toán học dự báo (Data Scientist).

### 4. Phân Chia Phạm Vi: Bắt Buộc (Core) vs Mở Rộng (Bonus) Cân Nhắc Giới Hạn 3 Tháng
- **Phần Bắt Buộc (Core MVP 3 tháng):**
  + Pipeline trích xuất dữ liệu từ MySQL bằng Python.
  + Module làm sạch và kiểm tra chất lượng dữ liệu (Data Validation).
  + Thiết kế mô hình Star Schema (Fact Sales, Dim Products, Dim Dates, Dim Customers) trên CSDL phân tích.
  + Viết các câu lệnh SQL phân tích nâng cao (Window functions, CTEs, Aggregations).
- **Phần Mở Rộng (Bonus - nếu còn thời gian):**
  + Tự động hóa lịch trình chạy pipeline bằng **Apache Airflow** (hoặc cron scheduler đơn giản).
  + Đóng gói toàn bộ pipeline bằng **Docker Compose** để chạy độc lập.
- **CẢNH BÁO TRÁNH OVER-ENGINEERING:** Tuyệt đối KHÔNG sa đà vào việc dựng cụm Hadoop phân tán, Spark cluster hay Apache Kafka đa node chỉ để làm đồ án trông phức tạp trong khi lượng dữ liệu và thời gian 3 tháng không đòi hỏi điều đó.

### 5. Kỹ Năng Trọng Tâm & Bằng Chứng Nộp Git Repo (Artifacts for CV)
- SQL nâng cao (Window Functions, Indexing).
- Python lập trình hướng dữ liệu (Pandas, PyMySQL/SQLAlchemy).
- Data Modeling (Star Schema DDL script).
- Artifacts trên Git: Thư mục `pipeline/` chứa code ETL, thư mục `schemas/` chứa DDL Star Schema, và file `tests/` kiểm tra data quality.

### 6. Câu Hỏi Tương Tác Mở
Hỏi sinh viên về cấu trúc bảng dữ liệu giao dịch hiện tại trong MySQL để cùng bắt tay vào thiết kế mô hình Star Schema đầu tiên.
"""

    # =========================================================================
    # KỊCH BẢN TC03: ĐỀ TÀI ĐẶC THÙ NGHIỆP VỤ & EXPLICIT ROLE (BACKEND)
    # =========================================================================
    elif is_explicit_role and "backend" in target_role.lower() and not is_project_skill_gap_audit and not is_four_week_action_plan and not is_readiness_score_explanation:
        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC03): SINH VIÊN ĐÃ XÁC ĐỊNH RÕ MỤC TIÊU NGHỀ NGHIỆP LÀ "{target_role}".
Bạn phải tư vấn CHUYÊN SÂU theo đúng bản chất kỹ thuật của Backend Developer gắn với đặc thù nghiệp vụ của bài toán "{blueprint.get('domain', '')}".
Ưu tiên 85-90% nội dung vào năng lực Backend, KHÔNG lan man sang UI hay các mảng khác.

BẮT BUỘC TRÌNH BÀY ĐẦY ĐỦ CÁC MỤC SAU (Định dạng Markdown rõ ràng, chuyên nghiệp):

### 1. Phân tích các Phân hệ Nghiệp vụ Cốt lõi (Domain Workflows)
Phân tích chi tiết các phân hệ nghiệp vụ chính của đề tài. Với hệ thống đặt lịch / y tế / dịch vụ:
- Quản lý Tài khoản & Hồ sơ (Identity & Profile Management).
- Phân quyền người dùng (Role-Based Access Control - RBAC) chặt chẽ giữa các vai trò (Bệnh nhân, Bác sĩ, Quản trị viên/Tiếp tân).
- Quản lý Danh mục Bác sĩ, Chuyên khoa & Dịch vụ khám.
- Quản lý Lịch khám & Ca trực (Doctor Schedule & Time Slot Availability Engine) với cấu hình khung giờ khám.
- Đặt lịch & Quản lý Lịch hẹn (Booking & Appointment Engine) kèm giải pháp chống xung đột slot (Race condition / Double-booking).

### 2. Đề xuất Kiến trúc Backend Phù hợp với Quy mô Đồ án
- Đề xuất kiến trúc: Layered Architecture (Controller -> Service -> Repository/DAO -> Database) hoặc Modular Monolith (tách package theo domain module).
- Giải thích vì sao: Thích hợp hoàn hảo với quy mô đồ án 1-3 người, thời gian 3-4 tháng; giúp kiểm soát chặt chẽ giao dịch ACID và logic nghiệp vụ, tránh overhead phân tán phức tạp của Microservices (tránh distributed transactions, saga pattern, network latency, devops nặng nề).

### 3. Đề xuất Tech Stack Linh hoạt (Không mặc định Spring Boot là lựa chọn duy nhất)
- Đưa ra 2-3 lựa chọn Backend framework chuẩn doanh nghiệp theo sở trường:
  + Lựa chọn 1 (Enterprise / Nghiệp vụ chặt chẽ): Java (Spring Boot 3 + Spring Data JPA + Spring Security) - Hệ sinh thái lớn, kiểm soát transaction (@Transactional) và phân quyền RBAC mạnh mẽ.
  + Lựa chọn 2 (Hiện đại, Full-JS / Fast Delivery): TypeScript (NestJS + TypeORM/Prisma) - Kiến trúc modular phân tầng chuẩn mực, gõ tĩnh an toàn, non-blocking I/O.
  + Lựa chọn 3 (Gọn nhẹ, Xử lý nhanh): Python (FastAPI + SQLAlchemy) - Gọn gàng, phát triển nhanh, tự động sinh tài liệu Swagger OpenAPI.
- Cơ sở dữ liệu cốt lõi: PostgreSQL (Relational Database) - Đảm bảo tính toàn vẹn dữ liệu ACID, hỗ trợ cơ chế khóa (Locking) và chỉ mục mạnh mẽ cho bài toán đặt lịch.
- Giao thức: RESTful API chuẩn hóa.

### 4. Xác thực, Phân quyền & Bảo vệ Dữ liệu Nhạy cảm (Security & Sensitive Data)
- Xác thực: JWT Authentication (Access Token ngắn hạn + Refresh Token có cơ chế thu hồi/revoke).
- Phân quyền: RBAC (Role-Based Access Control) nghiêm ngặt (Bệnh nhân chỉ xem và quản lý hồ sơ/lịch hẹn của mình; Bác sĩ chỉ xem bệnh án của bệnh nhân có hẹn; Admin quản lý toàn viện).
- Bảo vệ dữ liệu nhạy cảm (với y tế là hồ sơ bệnh án EMR / PHI):
  + Mã hóa dữ liệu tĩnh (Encryption at Rest): AES-256 cho các trường nhạy cảm (bệnh lý, chẩn đoán, CCCD).
  + Mã hóa đường truyền: HTTPS/TLS.
  + Mật khẩu: Hash bằng BCrypt hoặc Argon2 với Salt ngẫu nhiên.
  + Audit Logging: Ghi vết nhật ký truy cập (ai đã xem, sửa hồ sơ bệnh án vào thời điểm nào).

### 5. 5 Kỹ năng Backend Kiểm chứng được qua Sản phẩm (Artifacts in Git Repo)
Đề xuất 5 kỹ năng backend quan trọng nhất kèm bằng chứng cụ thể sinh viên cần đưa vào Git Repo để chứng minh với nhà tuyển dụng:
1. Thiết kế RESTful API: Chuẩn hóa URI, HTTP status code (200, 201, 400, 401, 403, 404, 409 Conflict cho trùng slot), tài liệu hóa bằng OpenAPI 3.0 / Swagger UI.
2. Mô hình hóa Dữ liệu (Data Modeling & DB Constraints): Thiết kế ERD chuẩn 3NF, ràng buộc khóa ngoại, Index trên các trường tra cứu nhiều (doctor_id, work_date), và Unique Constraint ở tầng CSDL để ngăn chặn tuyệt đối double-booking.
3. Xử lý Lỗi tập trung (Global Exception Handling): Cấu hình bộ bắt lỗi toàn cục (@ControllerAdvice trong Spring Boot hoặc Exception Filters trong NestJS/FastAPI), chuẩn hóa format lỗi trả về theo chuẩn RFC 7807 (Problem Details).
4. Quản lý Giao dịch & Xử lý Tranh chấp Đồng thời (Transaction & Concurrency Locking): Quản lý giao dịch ACID (@Transactional), cơ chế khóa chống đặt trùng lịch (Pessimistic Locking 'SELECT ... FOR UPDATE' hoặc Optimistic Locking với trường version) khi nhiều bệnh nhân cùng đặt 1 slot cuối cùng.
5. Kiểm thử Tự động (Automated Testing): Unit Test cho logic ràng buộc ca trực/hạn mức, Integration Test cho luồng đặt lịch (MockMVC / TestContainers với PostgreSQL thật), độ phủ coverage > 60%.

### 6. Cảnh báo Over-Engineering & Căn cứ Dữ liệu Tuyển dụng TopCV
- Dẫn chứng tỷ lệ xuất hiện từ kho 88+ JDs TopCV cho Backend Developer (REST API ~35%, PostgreSQL ~37%, Spring Boot ~32%, Docker ~27%, Testing ~28%).
- Cảnh báo tránh sa đà vào Apache Kafka hay Microservices ở giai đoạn đồ án MVP này.
- Câu hỏi tương tác mở: Hỏi sinh viên về nền tảng ngôn ngữ hiện tại (Java, TypeScript hay Python) để cùng chốt tech stack tối ưu nhất.
"""

    # =========================================================================
    # KỊCH BẢN TC01: CHƯA QUYẾT ĐỊNH CÔNG NGHỆ / NGHỀ NGHIỆP
    # =========================================================================
    elif is_undecided:
        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC01): SINH VIÊN CÓ Ý TƯỞNG NHƯNG CHƯA BIẾT CHỌN CÔNG NGHỆ HOẶC NGHỀ NGHIỆP.
Yêu cầu bạn phải trả lời theo cấu trúc sau:
1. Phân tích sản phẩm: Các chức năng cốt lõi MVP (danh mục, tìm kiếm, giỏ hàng/lịch, đặt hàng/giao dịch, tài khoản/phân quyền). Khẳng định đây là bài toán hướng sản phẩm (Product/App-driven).
2. Đề xuất 3 hướng nghề nghiệp phù hợp với đề tài (Frontend Developer, Backend Developer, Full-stack Developer), giải thích trọng tâm kỹ thuật của từng hướng.
3. Đề xuất Tech Stack theo 2 nhóm rõ ràng:
   - Nhóm Cốt lõi (Core Stack) cho người bắt đầu (ví dụ React cho FE, Node.js/Python/Java cho BE, PostgreSQL cho DB).
   - Nhóm Mở rộng (Booster Stack) tăng sức cạnh tranh (Docker, Redis, Automated Testing).
4. Đặt câu hỏi tương tác mở (Interactive Probing) để hỏi sinh viên về sở thích hoặc thế mạnh để định hướng sâu hơn.
"""


    # =========================================================================
    # KỊCH BẢN TC02: CHUYỂN DỊCH MỤC TIÊU NGHỀ NGHIỆP (ROLE SWITCH)
    # =========================================================================
    elif role_switched:
        scenario_directive = f"""
KỊCH BẢN TƯ VẤN (TC02): SINH VIÊN CHUYỂN HƯỚNG MỤC TIÊU NGHỀ NGHIỆP TỪ "{previous_role}" SANG "{target_role}".
Yêu cầu bạn phải trả lời theo cấu trúc sau:
1. Đánh giá sự chuyển dịch mục tiêu: Ủng hộ và phân tích bản chất bài toán khi chuyển sang vai trò {target_role} (không chỉ làm nghiệp vụ thông thường mà bổ sung giá trị chuyên sâu của {target_role}).
2. Kỹ năng nền tảng có thể tái sử dụng (Reusable Skills): Nêu rõ các kỹ năng từ thiết kế đề tài ban đầu vẫn rất hữu ích (ví dụ SQL, REST API, Git).
3. Khoảng cách kỹ năng cần bổ sung (Actionable Gaps for {target_role}): Đề xuất 2-3 kỹ năng mới cốt lõi kèm Bằng chứng nộp Git Repo cụ thể (Artifacts) để đi phỏng vấn.
4. Đề xuất Module Mở rộng Lớp 3 (Layer 3 Extension) phù hợp để làm điểm nhấn CV (Nếu chuyển sang AI Engineer, hãy đề xuất 1 tính năng AI thiết thực, có giá trị ứng dụng cao tích hợp vào sản phẩm, ví dụ: Hệ thống gợi ý sản phẩm cá nhân hóa hoặc Phân loại đánh giá khách hàng).
5. Cảnh báo tránh Over-Engineering và câu hỏi tương tác mở.
"""

    # =========================================================================
    # KỊCH BẢN MẶC ĐỊNH: TIẾP DIỄN TRAO ĐỔI
    # =========================================================================
    else:
        scenario_directive = f"""
KỊCH BẢN TƯ VẤN TIẾP DIỄN / ĐIỀU CHỈNH:
Yêu cầu bạn:
1. Phân tích đúng bản chất kỹ thuật của đề tài "{session['idea']}" theo vai trò "{target_role}".
2. Khẳng định các kỹ năng mà phạm vi đề tài đòi hỏi ({', '.join(covered_list)}), không tự ý giả định sinh viên đã thành thạo nếu chưa kiểm chứng.
3. Chỉ ra 2-3 Actionable Gaps kèm Bằng chứng nộp Git cụ thể (Artifacts).
4. Cảnh báo tránh Over-Engineering (Kafka, Microservices khi chưa cần).
5. Câu hỏi tương tác mở.
"""

    return f"""Bạn là Cố vấn Công nghệ & Hướng nghiệp Đồ án GEM (AISC 2026).
Ý tưởng sinh viên: "{session['idea']}"
Vai trò hướng tới: "{target_role}"
Thời gian: {session.get('time_months', 3)} tháng
Công nghệ yêu thích / đã chọn: {selected_tech}

Lịch sử trao đổi gần nhất:
{history_context}

Người dùng vừa nói: "{user_message}"

{scenario_directive}

Trả về phản hồi định dạng Markdown hoàn chỉnh, chuẩn chỉnh, chuyên nghiệp và truyền cảm hứng.
"""
