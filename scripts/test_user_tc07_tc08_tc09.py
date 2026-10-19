"""
Verification Script for User Test Cases:
- TC07 (P0): Đồ án quá tham vọng so với thời gian (1 tháng)
- TC08 (P1): Đồ án phụ thuộc phần cứng / thông tin chưa xác định
- TC09 (P1): Người dùng yêu cầu công nghệ không phù hợp bài toán (Overkill)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
"""

import sys
import os

sys.path.insert(0, os.path.abspath("pipeline/src"))
sys.stdout.reconfigure(encoding="utf-8")

from gem_pipeline.recommendation.consultant import IdeationConsultant


def test_tc07_overambitious_scope():
    print("\n=======================================================")
    print("▶ CHẠY TEST CASE 07: ĐỒ ÁN QUÁ THAM VỌNG SO VỚI THỜI GIAN (P0)")
    print("=======================================================")
    consultant = IdeationConsultant(db_uri=None)

    msg_tc07 = (
        "Tôi có một tháng để làm website thương mại điện tử. "
        "Tôi muốn dùng microservices, Kubernetes, Kafka, AI Agent, RAG và triển khai trên cloud. "
        "Hãy đề xuất kiến trúc tốt nhất."
    )

    resp = consultant.chat(session_id=None, user_message=msg_tc07)
    reply = resp["reply"]
    state = resp["session_state"]

    print(f"\n[TC07] Time Months: {state['time_months']}")
    print(f"[TC07] Target Role: {state['target_role']}")
    print("\n--- PHẢN HỒI CỦA CỐ VẤN GEM CHO TC07 ---")
    print(reply)

    reply_lower = reply.lower()

    # 1. Nhận diện sự không tương xứng & Cảnh báo rủi ro
    cond_warn = any(k in reply_lower for k in [
        "vượt quá", "rủi ro", "quá tham vọng", "bất khả thi", "vỡ tiến độ",
        "không nên", "quá tải", "phức tạp", "scope"
    ])
    assert cond_warn, "Phải cảnh báo rủi ro không tương xứng giữa phạm vi và thời gian 1 tháng"

    # 2. Không đồng ý triển khai toàn bộ stack phân tán mù quáng
    assert not ("triển khai toàn bộ microservices, kubernetes, kafka và rag trong 1 tháng" in reply_lower), "Không được hứa hẹn làm hết đống công nghệ phân tán trong 1 tháng"

    # 3. Có MVP cụ thể cốt lõi (giao diện, backend, database, luồng mua hàng)
    cond_mvp = (
        any(k in reply_lower for k in ["mvp", "cốt lõi", "monolith", "modular monolith"])
        and any(k in reply_lower for k in ["giao diện", "frontend"])
        and any(k in reply_lower for k in ["backend", "api"])
        and any(k in reply_lower for k in ["database", "cơ sở dữ liệu", "postgresql", "mysql"])
        and any(k in reply_lower for k in ["mua hàng", "đơn hàng", "giỏ hàng", "thanh toán"])
    )
    assert cond_mvp, "Phải xác định rõ MVP cốt lõi gồm giao diện, backend, db và luồng mua hàng"

    # 4. Đưa microservices, k8s, kafka sang giai đoạn sau (Phase 2 / Tạm hoãn)
    cond_deferred = any(k in reply_lower for k in [
        "giai đoạn 2", "giai đoạn sau", "phase 2", "tạm hoãn", "dời", "sau khi"
    ])
    assert cond_deferred, "Phải đưa microservices, k8s, kafka, AI sang giai đoạn sau"

    # 5. Lộ trình theo tuần (Tuần 1, Tuần 2, Tuần 3, Tuần 4)
    cond_weeks = (
        "tuần 1" in reply_lower
        and "tuần 2" in reply_lower
        and "tuần 3" in reply_lower
        and "tuần 4" in reply_lower
    )
    assert cond_weeks, "Phải có lộ trình cụ thể phân chia theo 4 tuần"

    print("\n>>> TC07 VALIDATION PASSED 100%!")


def test_tc08_hardware_or_missing_spec():
    print("\n=======================================================")
    print("▶ CHẠY TEST CASE 08: ĐỒ ÁN PHỤ THUỘC PHẦN CỨNG CHƯA XÁC ĐỊNH (P1)")
    print("=======================================================")
    consultant = IdeationConsultant(db_uri=None)

    msg_tc08 = (
        "Tôi muốn làm hệ thống giám sát chất lượng không khí trong nhà bằng cảm biến IoT, "
        "có dashboard và cảnh báo. Tôi muốn theo IoT hoặc Backend Developer. "
        "Hãy đề xuất stack cho tôi, hiện tại tôi chưa chọn cảm biến."
    )

    resp = consultant.chat(session_id=None, user_message=msg_tc08)
    reply = resp["reply"]
    state = resp["session_state"]

    print(f"\n[TC08] Target Role: {state['target_role']}")
    print("\n--- PHẢN HỒI CỦA CỐ VẤN GEM CHO TC08 ---")
    print(reply)

    reply_lower = reply.lower()

    # 1. Phân tích các thành phần kiến trúc
    cond_arch = (
        any(k in reply_lower for k in ["cảm biến", "sensor"])
        and any(k in reply_lower for k in ["truyền", "mqtt", "http", "thu thập"])
        and any(k in reply_lower for k in ["backend", "xử lý"])
        and any(k in reply_lower for k in ["lưu trữ", "database", "timescale", "postgresql"])
        and any(k in reply_lower for k in ["dashboard", "giao diện", "biểu đồ"])
        and any(k in reply_lower for k in ["cảnh báo", "alert"])
    )
    assert cond_arch, "Phải phân tích đầy đủ các tầng thành phần của hệ thống IoT"

    # 2. Nêu rõ thiết bị/giao thức ảnh hưởng đến kiến trúc
    cond_impact = any(k in reply_lower for k in [
        "ảnh hưởng", "quyết định", "tùy thuộc", "lựa chọn thiết bị", "giao thức"
    ])
    assert cond_impact, "Phải nêu rõ lựa chọn thiết bị và giao thức ảnh hưởng đến kiến trúc"

    # 3. Có phương án sơ bộ kèm giả định rõ ràng
    cond_prelim = any(k in reply_lower for k in [
        "sơ bộ", "giả định", "tạm thời", "tham khảo"
    ])
    assert cond_prelim, "Phải ghi rõ đây là phương án sơ bộ dựa trên các giả định"

    # 4. Đặt câu hỏi làm rõ quan trọng tiếp theo
    cond_ask = any(k in reply_lower for k in [
        "chỉ số", "loại cảm biến", "kết nối", "wi-fi", "bụi mịn", "pm2.5", "esp32"
    ])
    assert cond_ask, "Phải đặt câu hỏi làm rõ các biến số ảnh hưởng trực tiếp đến kiến trúc"

    print("\n>>> TC08 VALIDATION PASSED 100%!")


def test_tc09_overkill_tech_choice():
    print("\n=======================================================")
    print("▶ CHẠY TEST CASE 09: CÔNG NGHỆ OVERKILL KHÔNG PHÙ HỢP BÀI TOÁN (P1)")
    print("=======================================================")
    consultant = IdeationConsultant(db_uri=None)

    msg_tc09 = (
        "Tôi làm website quản lý thư viện nhỏ cho đồ án môn học. "
        "Tôi muốn dùng Kafka, Kubernetes và microservices vì thấy các công nghệ này rất chuyên nghiệp. "
        "Hãy thiết kế hệ thống theo hướng đó."
    )

    resp = consultant.chat(session_id=None, user_message=msg_tc09)
    reply = resp["reply"]
    state = resp["session_state"]

    print(f"\n[TC09] Target Role: {state['target_role']}")
    print("\n--- PHẢN HỒI CỦA CỐ VẤN GEM CHO TC09 ---")
    print(reply)

    reply_lower = reply.lower()

    # 1. Không đồng ý vô điều kiện, phản biện vì sao overkill
    cond_critique = any(k in reply_lower for k in [
        "không phù hợp", "over-engineering", "phức tạp", "lãng phí",
        "không nhất thiết", "không cần thiết", "nghiệp vụ", "quy mô"
    ])
    assert cond_critique, "Phải phản biện kỹ thuật việc dùng Kafka/K8s/Microservices cho thư viện nhỏ"

    # 2. Giải thích rủi ro kỹ thuật (ACID, complexity, distributed transactions)
    cond_risks = any(k in reply_lower for k in [
        "acid", "giao dịch", "phân tán", "distributed", "transaction", "độ phức tạp", "overhead"
    ])
    assert cond_risks, "Phải nêu rõ rủi ro kỹ thuật về giao dịch phân tán và độ phức tạp"

    # 3. Đề xuất kiến trúc tinh gọn thay thế (Monolith / Layered)
    cond_alt = any(k in reply_lower for k in [
        "monolith", "modular monolith", "phân tầng", "layered", "postgresql", "mysql", "spring boot", "nestjs", "fastapi"
    ])
    assert cond_alt, "Phải đề xuất kiến trúc đơn giản phù hợp (Monolith / Layered)"

    # 4. Tôn trọng mục tiêu học tập (Sandbox / PoC / Module riêng)
    cond_respect = any(k in reply_lower for k in [
        "thử nghiệm", "sandbox", "poc", "module riêng", "mở rộng", "thông báo", "học hỏi", "trải nghiệm"
    ])
    assert cond_respect, "Phải tôn trọng mục tiêu học tập bằng đề xuất module thử nghiệm riêng"

    print("\n>>> TC09 VALIDATION PASSED 100%!")


if __name__ == "__main__":
    test_tc07_overambitious_scope()
    test_tc08_hardware_or_missing_spec()
    test_tc09_overkill_tech_choice()
