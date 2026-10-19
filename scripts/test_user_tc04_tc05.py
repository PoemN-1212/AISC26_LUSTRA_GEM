"""
Verification Script for User Test Cases:
- TC04: Đã chọn React, Node.js và MySQL (Mục tiêu Full-stack Developer)
- TC05: Sản phẩm web nhưng mục tiêu là Data Engineer trong giới hạn 3 tháng
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath("pipeline/src"))
sys.stdout.reconfigure(encoding="utf-8")

from gem_pipeline.recommendation.consultant import IdeationConsultant


def test_tc04_evaluate_existing_stack():
    print("\n=======================================================")
    print("▶ CHẠY TEST CASE 04: ĐÃ CHỌN REACT, NODE.JS VÀ MYSQL (FULL-STACK)")
    print("=======================================================")
    consultant = IdeationConsultant(db_uri=None)

    msg_tc04 = (
        "Tôi định làm website thương mại điện tử bằng React, Node.js và MySQL. "
        "Tôi muốn theo Full-stack Developer. Bạn hãy đánh giá stack này và cho biết tôi "
        "còn cần bổ sung gì để đồ án có giá trị khi ứng tuyển."
    )

    resp = consultant.chat(session_id=None, user_message=msg_tc04)
    reply = resp["reply"]
    blueprint = resp["blueprint"]
    state = resp["session_state"]

    print(f"\n[TC04] Target Role: {state['target_role']}")
    print(f"[TC04] Preferred Tech: {state['preferred_tech']}")
    print(f"[TC04] Blueprint Role: {blueprint['target_role']}")
    print("\n--- TRÍCH ĐOẠN PHẢN HỒI GEM CHO TC04 ---")
    print(reply)

    # Kiểm tra các tiêu chí bắt buộc của TC04
    reply_lower = reply.lower()

    # 1. Giữ lại stack đã chọn, không bắt đổi công nghệ
    assert any(k in reply_lower for k in ["phù hợp", "thích hợp", "hoàn toàn phù hợp", "rất thực tế"]), "Phải đánh giá tính phù hợp của stack hiện tại"
    assert any(k in reply_lower for k in ["giữ nguyên", "không cần đổi", "không bắt buộc đổi", "không nhất thiết", "không cần thiết phải đổi"]), "Phải khẳng định giữ lại stack đã chọn"

    # 2. Phân biệt đã sử dụng công nghệ vs đã chứng minh năng lực
    assert any(k in reply_lower for k in ["đã sử dụng", "sử dụng công nghệ", "năng lực", "chứng minh", "engineering competence"]), "Phải phân biệt sử dụng công nghệ vs chứng minh năng lực thực tế"

    # 3. Chỉ ra các tầng năng lực (Frontend, Backend, Database, Chất lượng phần mềm, Triển khai)
    assert any(k in reply_lower for k in ["frontend", "giao diện", "state", "trạng thái"]), "Phải đề cập năng lực Frontend"
    assert any(k in reply_lower for k in ["backend", "api", "xác thực", "phân quyền", "rbac"]), "Phải đề cập năng lực Backend"
    assert any(k in reply_lower for k in ["database", "cơ sở dữ liệu", "3nf", "index", "truy vấn", "erd"]), "Phải đề cập năng lực Database"
    assert any(k in reply_lower for k in ["chất lượng", "kiểm thử", "test", "bảo mật", "security"]), "Phải đề cập Chất lượng phần mềm"
    assert any(k in reply_lower for k in ["docker", "triển khai", "ci/cd", "deployment"]), "Phải đề cập Triển khai"

    # 4. Phân cấp mức độ ưu tiên
    assert any(k in reply_lower for k in ["ưu tiên", "bắt buộc", "mở rộng", "booster"]), "Phải phân cấp mức độ ưu tiên"

    # 5. Dẫn chứng TopCV
    assert any(k in reply_lower for k in ["topcv", "jd", "nhà tuyển dụng", "thị trường"]), "Phải liên hệ với số liệu JD / TopCV"

    print("\n>>> TC04 VALIDATION PASSED 100%!")


def test_tc05_web_to_data_engineer_pivot():
    print("\n=======================================================")
    print("▶ CHẠY TEST CASE 05: SẢN PHẨM WEB NHƯNG MỤC TIÊU DATA ENGINEER (3 THÁNG)")
    print("=======================================================")
    consultant = IdeationConsultant(db_uri=None)

    msg_tc05 = (
        "Tôi đang làm website theo dõi doanh thu bán hàng, hiện dùng React, Node.js và MySQL. "
        "Tôi muốn hướng tới Data Engineer nhưng chỉ còn ba tháng. Tôi nên bổ sung gì vào đồ án để phù hợp hơn?"
    )

    resp = consultant.chat(session_id=None, user_message=msg_tc05)
    reply = resp["reply"]
    blueprint = resp["blueprint"]
    state = resp["session_state"]

    print(f"\n[TC05] Target Role: {state['target_role']}")
    print(f"[TC05] Time Months: {state['time_months']}")
    print(f"[TC05] Preferred Tech: {state['preferred_tech']}")
    print("\n--- TRÍCH ĐOẠN PHẢN HỒI GEM CHO TC05 ---")
    print(reply)

    reply_lower = reply.lower()

    # 1. Giữ website làm nguồn dữ liệu (Data Source / OLTP)
    assert any(k in reply_lower for k in ["nguồn dữ liệu", "data source", "oltp", "giữ nguyên website", "không cần phải đập bỏ", "không cần đập bỏ"]), "Phải giữ website làm nguồn dữ liệu"

    # 2. Đề xuất luồng dữ liệu 5 bước
    assert any(k in reply_lower for k in ["thu thập", "ingestion", "trích xuất"]), "Phải có bước Thu thập dữ liệu"
    assert any(k in reply_lower for k in ["làm sạch", "cleaning", "kiểm tra", "validation"]), "Phải có bước Làm sạch dữ liệu"
    assert any(k in reply_lower for k in ["biến đổi", "transform"]), "Phải có bước Biến đổi dữ liệu"
    assert any(k in reply_lower for k in ["lưu trữ", "kho", "star schema", "warehouse", "olap"]), "Phải có bước Lưu trữ phân tích"
    assert any(k in reply_lower for k in ["chất lượng dữ liệu", "lỗi", "giám sát", "observability"]), "Phải có bước Theo dõi lỗi & chất lượng dữ liệu"

    # 3. Phân biệt Data Engineer vs Data Analyst / Scientist
    assert any(k in reply_lower for k in ["data analyst", "data scientist", "hạ tầng", "đường ống", "pipes"]), "Phải phân biệt Data Engineer với Analyst/Scientist"

    # 4. Giới hạn 3 tháng & Phân chia bắt buộc vs mở rộng
    assert any(k in reply_lower for k in ["bắt buộc", "core", "mở rộng", "3 tháng", "ba tháng"]), "Phải cân nhắc giới hạn 3 tháng và phân chia Core/Bonus"

    # 5. Cảnh báo over-engineering
    assert any(k in reply_lower for k in ["over-engineering", "tránh", "hadoop", "spark", "kafka"]), "Phải cảnh báo tránh over-engineering"

    print("\n>>> TC05 VALIDATION PASSED 100%!")


if __name__ == "__main__":
    test_tc04_evaluate_existing_stack()
    test_tc05_web_to_data_engineer_pivot()
    print("\n=======================================================")
    print("NHÓM 2 (TC04 & TC05) KIỂM THỬ THÀNH CÔNG RỰC RỠ 100%!")
    print("=======================================================")
