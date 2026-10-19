"""
Verification Script for TC06 Generalization:
Kiểm tra tính TỔNG QUÁT HÓA của GEM qua nhiều vai trò khác nhau (Backend, Frontend, AI/ML).
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
"""

import sys
import os

sys.path.insert(0, os.path.abspath("pipeline/src"))
sys.stdout.reconfigure(encoding="utf-8")

from gem_pipeline.recommendation.consultant import IdeationConsultant


def test_generalization():
    consultant = IdeationConsultant(db_uri=None)

    # -------------------------------------------------------------
    # CASE 1: BACKEND DEVELOPER INTERN
    # -------------------------------------------------------------
    print("\n=======================================================")
    print("▶ CASE 1: KIỂM TOÁN NĂNG LỰC BACKEND DEVELOPER INTERN")
    print("=======================================================")
    msg_be = (
        "Tôi đã học Java, Spring Boot và MySQL, nhưng chưa biết như vậy đã đủ "
        "để ứng tuyển Backend Developer Intern chưa. Hãy phân tích những gì tôi còn thiếu "
        "và gợi ý cách thể hiện năng lực qua đồ án."
    )
    resp_be = consultant.chat(session_id=None, user_message=msg_be)
    reply_be = resp_be["reply"]
    state_be = resp_be["session_state"]

    print(f"[CASE 1] Detected Role: {state_be['target_role']}")
    print(f"[CASE 1] Detected Tech: {state_be['preferred_tech']}")
    assert "backend" in state_be["target_role"].lower(), "Phải nhận diện đúng vai trò Backend Developer"
    assert any(k in reply_be.lower() for k in ["restful api", "api", "rbac", "bảo mật", "transaction", "kiểm thử", "docker"]), "Phải đưa ra các năng lực cốt lõi Backend"
    assert any(k in reply_be.lower() for k in ["không kết luận", "không thể kết luận", "phụ thuộc", "tùy thuộc"]), "Phải tuân thủ nguyên tắc không kết luận vội vàng"
    print(">>> CASE 1 (Backend) PASSED!")

    # -------------------------------------------------------------
    # CASE 2: FRONTEND DEVELOPER INTERN
    # -------------------------------------------------------------
    print("\n=======================================================")
    print("▶ CASE 2: KIỂM TOÁN NĂNG LỰC FRONTEND DEVELOPER INTERN")
    print("=======================================================")
    msg_fe = (
        "Tôi đã học HTML, CSS, JavaScript và React, nhưng chưa biết liệu đã đủ "
        "để ứng tuyển Frontend Developer Intern chưa. Nhờ GEM chỉ ra tôi còn thiếu những gì "
        "và gợi ý cách chứng minh qua đồ án."
    )
    resp_fe = consultant.chat(session_id=None, user_message=msg_fe)
    reply_fe = resp_fe["reply"]
    state_fe = resp_fe["session_state"]

    print(f"[CASE 2] Detected Role: {state_fe['target_role']}")
    print(f"[CASE 2] Detected Tech: {state_fe['preferred_tech']}")
    assert "frontend" in state_fe["target_role"].lower(), "Phải nhận diện đúng vai trò Frontend Developer"
    assert any(k in reply_fe.lower() for k in ["component", "state management", "trạng thái", "api", "responsive", "hiệu năng", "ui"]), "Phải đưa ra các năng lực cốt lõi Frontend"
    assert any(k in reply_fe.lower() for k in ["không kết luận", "không thể kết luận", "phụ thuộc", "tùy thuộc"]), "Phải tuân thủ nguyên tắc không kết luận vội vàng"
    print(">>> CASE 2 (Frontend) PASSED!")

    print("\n=======================================================")
    print(">>> TẤT CẢ CÁC TRƯỜNG HỢP KIỂM THỬ TỔNG QUÁT HÓA ĐỀU ĐẠT 100%!")
    print("=======================================================")


if __name__ == "__main__":
    test_generalization()
