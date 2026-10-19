"""
Verification Script for User Test Cases:
- TC06: Người dùng đã biết một công nghệ nhưng chưa biết mình đang thiếu kỹ năng nào (Data Engineer Intern)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("pipeline/src"))
sys.stdout.reconfigure(encoding="utf-8")

from gem_pipeline.recommendation.consultant import IdeationConsultant


def test_tc06_intern_readiness_audit():
    print("\n=======================================================")
    print("▶ CHẠY TEST CASE 06: KIỂM TOÁN NĂNG LỰC DATA ENGINEER INTERN (TC06)")
    print("=======================================================")
    consultant = IdeationConsultant(db_uri=None)

    msg_tc06 = (
        "Tôi đã học Python, SQL và pandas, nhưng chưa biết như vậy đã đủ để ứng tuyển Data Engineer Intern chưa. "
        "Hãy phân tích những gì tôi còn thiếu và gợi ý cách thể hiện năng lực qua đồ án."
    )

    resp = consultant.chat(session_id=None, user_message=msg_tc06)
    reply = resp["reply"]
    blueprint = resp["blueprint"]
    state = resp["session_state"]

    print(f"\n[TC06] Target Role: {state['target_role']}")
    print(f"[TC06] Preferred Tech: {state['preferred_tech']}")
    print(f"[TC06] Blueprint Role: {blueprint['target_role']}")
    print("\n--- PHẢN HỒI CỦA CỐ VẤN GEM CHO TC06 ---")
    print(reply)

    reply_lower = reply.lower()

    # 1. Tiêu chí 1: Không kết luận đủ/chưa đủ chỉ dựa trên 3 công nghệ
    cond1 = any(k in reply_lower for k in [
        "không kết luận", "không thể kết luận", "chưa thể khẳng định",
        "không đồng nghĩa", "phụ thuộc", "tùy thuộc", "yêu cầu cụ thể"
    ])
    assert cond1, "Phải không kết luận vội vàng đủ hay chưa đủ chỉ dựa trên ba công nghệ"

    # 2. Tiêu chí 2: Xác định 5 nhóm năng lực cần kiểm tra/bổ sung
    # Nhóm a: SQL và mô hình hóa dữ liệu
    cond_sql = any(k in reply_lower for k in ["sql", "mô hình hóa", "data modeling", "star schema", "window function", "cte"])
    assert cond_sql, "Phải chỉ ra năng lực SQL và mô hình hóa dữ liệu"

    # Nhóm b: Pipeline ETL/ELT
    cond_etl = any(k in reply_lower for k in ["etl", "elt", "pipeline", "đường ống", "trích xuất", "luồng dữ liệu"])
    assert cond_etl, "Phải chỉ ra năng lực Pipeline ETL/ELT"

    # Nhóm c: Xử lý dữ liệu lỗi hoặc thiếu
    cond_quality = any(k in reply_lower for k in ["lỗi", "thiếu", "null", "chất lượng dữ liệu", "data quality", "làm sạch", "validation", "clean"])
    assert cond_quality, "Phải chỉ ra năng lực Xử lý dữ liệu lỗi hoặc thiếu"

    # Nhóm d: Tự động hóa và lập lịch pipeline
    cond_auto = any(k in reply_lower for k in ["tự động hóa", "automation", "lập lịch", "schedule", "airflow", "cron"])
    assert cond_auto, "Phải chỉ ra năng lực Tự động hóa và lập lịch pipeline"

    # Nhóm e: Kiểm thử, theo dõi lỗi và tài liệu hóa
    cond_test = any(k in reply_lower for k in ["kiểm thử", "test", "pytest", "log", "nhật ký", "tài liệu", "readme", "observability"])
    assert cond_test, "Phải chỉ ra năng lực Kiểm thử, theo dõi lỗi và tài liệu hóa"

    # 3. Tiêu chí 3: Phân biệt các kỹ năng thường gặp trong JD với những kỹ năng đã được chứng minh
    cond_jd_diff = any(k in reply_lower for k in [
        "jd", "nhà tuyển dụng", "liệt kê", "chứng minh", "thực tế", "bài tập", "năng lực", "competence"
    ])
    assert cond_jd_diff, "Phải phân biệt kỹ năng trong JD với kỹ năng đã được chứng minh qua sản phẩm"

    # 4. Tiêu chí 4: Đề xuất một đồ án nhỏ (mini-project) để thể hiện năng lực còn thiếu
    cond_project = any(k in reply_lower for k in [
        "đồ án", "mini-project", "dự án", "pipeline", "git", "repo", "bằng chứng"
    ])
    assert cond_project, "Phải đề xuất một đồ án nhỏ để thể hiện năng lực còn thiếu"

    # 5. Tiêu chí 5: Nêu rõ kết luận phụ thuộc vào yêu cầu của từng vị trí tuyển dụng & không cam kết có việc làm 100%
    cond_no_guarantee = any(k in reply_lower for k in [
        "không đảm bảo", "không hứa hẹn", "không chắc chắn", "phụ thuộc", "tùy thuộc", "cạnh tranh", "phỏng vấn"
    ])
    assert cond_no_guarantee, "Phải nêu rõ kết luận phụ thuộc vị trí và không cam kết hoàn thành đồ án sẽ đảm bảo có việc làm"

    print("\n" + "=" * 55)
    print(">>> TẤT CẢ TIÊU CHÍ KIỂM THỬ CỦA TC06 ĐÃ ĐẠT 100%!")
    print("=" * 55)


if __name__ == "__main__":
    test_tc06_intern_readiness_audit()
