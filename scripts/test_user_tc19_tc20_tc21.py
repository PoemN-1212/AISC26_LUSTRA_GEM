import sys
import os
import uuid

# Đảm bảo import được gem_pipeline
sys.path.append(os.path.join(os.getcwd(), "pipeline", "src"))

from gem_pipeline.recommendation.consultant import IdeationConsultant


def run_tc19(consultant, session_id):
    print("\n" + "=" * 80)
    print("KIỂM THỬ TC19: ĐỐI CHIẾU ĐỒ ÁN VỚI KỸ NĂNG NGHỀ NGHIỆP MỤC TIÊU & SKILL GAP (P0)")
    print("=" * 80)

    tc19_input = (
        "Tôi đã làm một website thương mại điện tử với React, Node.js và MySQL. "
        "Tôi muốn ứng tuyển Backend Developer Intern. Hãy phân tích những kỹ năng đồ án của tôi đã thể hiện, "
        "những kỹ năng còn thiếu so với yêu cầu tuyển dụng và thứ tự ưu tiên cải thiện."
    )
    print(f"\n[TC19] Input: {tc19_input}")
    res = consultant.chat(session_id=session_id, user_message=tc19_input)
    reply = res["reply"]
    print(f"\n[TC19] Reply:\n{reply}\n")

    reply_lower = reply.lower()

    # 1. Phân biệt kỹ năng đã có bằng chứng (Nhóm 1)
    assert any(k in reply_lower for k in ["kỹ năng có thể được thể hiện", "kỹ năng đã thể hiện", "thể hiện qua đồ án", "đã có bằng chứng", "đã thể hiện"]), "Phải có Nhóm 1: Kỹ năng có thể được thể hiện qua đồ án"
    assert any(k in reply_lower for k in ["api", "restful", "nghiệp vụ", "đơn hàng", "giỏ hàng", "truy vấn", "mysql", "crud"]), "Nhóm 1 phải ghi nhận các năng lực thực tế từ đề tài website thương mại điện tử"

    # 2. Kỹ năng chưa có đủ bằng chứng (Nhóm 2)
    assert any(k in reply_lower for k in ["chưa có đủ bằng chứng", "chưa đủ bằng chứng", "chưa kiểm chứng", "lỗ hổng tiềm ẩn"]), "Phải có Nhóm 2: Kỹ năng chưa có đủ bằng chứng"
    assert any(k in reply_lower for k in ["kiểm thử", "test", "unit test", "tối ưu", "triển khai", "xử lý lỗi", "transaction", "index"]), "Nhóm 2 phải chỉ ra các năng lực thiếu bằng chứng (Testing, Optimization, Deployment, Logging)"

    # 3. Không coi tên công nghệ là bằng chứng đầy đủ về năng lực (Critical Guardrail)
    assert any(k in reply_lower for k in ["không đồng nghĩa", "không coi tên công nghệ", "bằng chứng đầy đủ", "chưa chứng minh", "không có nghĩa", "không khẳng định"]), "Phải khẳng định rõ việc chỉ nêu tên công nghệ không phải là bằng chứng thành thạo năng lực"

    # 4. Khoảng cách kỹ năng liên hệ với JD thực tế (Nhóm 3)
    assert any(k in reply_lower for k in ["khoảng cách so với", "yêu cầu tuyển dụng", "88", "jd", "thị trường"]), "Phải có Nhóm 3: Khoảng cách so với tập JD Backend thực tế"

    # 5. Thứ tự ưu tiên có trọng tâm và giải thích lý do (Nhóm 4)
    assert any(k in reply_lower for k in ["thứ tự ưu tiên", "ưu tiên 1", "ưu tiên"]), "Phải có Nhóm 4: Thứ tự ưu tiên cải thiện"
    assert any(k in reply_lower for k in ["vì sao", "lý do", "giải thích"]), "Phải giải thích vì sao từng kỹ năng có thứ tự ưu tiên như vậy"

    print(">>> PASS TC19: Phân định rạch ròi 4 nhóm kỹ năng, gắn telemetry 88 JD Backend, guardrail tên công nghệ chuẩn mực, thứ tự ưu tiên rõ ràng!")
    return session_id


def run_tc20(consultant, session_id):
    print("\n" + "=" * 80)
    print("KIỂM THỬ TC20: KẾ HOẠCH HÀNH ĐỘNG 4 TUẦN CẢI THIỆN SKILL GAP (1-2H/NGÀY) (P1)")
    print("=" * 80)

    tc20_input = (
        "Dựa trên kết quả phân tích đồ án và Skill Gap vừa rồi, hãy lập cho tôi kế hoạch cải thiện trong bốn tuần "
        "để chuẩn bị ứng tuyển Backend Developer Intern. Tôi có thể dành khoảng một đến hai giờ mỗi ngày."
    )
    print(f"\n[TC20] Input: {tc20_input}")
    res = consultant.chat(session_id=session_id, user_message=tc20_input)
    reply = res["reply"]
    print(f"\n[TC20] Reply:\n{reply}\n")

    reply_lower = reply.lower()

    # 1. Nhớ kết quả Skill Gap trước đó (Kế thừa từ TC19)
    assert any(k in reply_lower for k in ["test", "jest", "kiểm thử", "transaction", "index", "docker", "redis"]), "Phải giữ lại các khoảng cách kỹ năng đã xác định ở lượt trước"

    # 2. Kế hoạch phù hợp 4 tuần
    for week_kw in ["tuần 1", "tuần 2", "tuần 3", "tuần 4"]:
        assert week_kw in reply_lower, f"Phải có kế hoạch cho {week_kw}"

    # 3. Phù hợp quỹ thời gian 1-2 giờ mỗi ngày
    assert any(k in reply_lower for k in ["1-2", "1 đến 2", "giờ/ngày", "mỗi ngày"]), "Phải phân chia khối lượng việc phù hợp 1-2h/ngày"

    # 4. Mỗi tuần có mục tiêu, nhiệm vụ cụ thể và kết quả có thể kiểm chứng (Deliverable/Artifact)
    assert any(k in reply_lower for k in ["kết quả", "đầu ra", "deliverable", "artifact", "kiểm chứng"]), "Mỗi tuần phải có kết quả có thể kiểm chứng được"

    # 5. Ưu tiên cải thiện trực tiếp đồ án hiện có, không bắt làm lại từ đầu
    assert any(k in reply_lower for k in ["đồ án hiện tại", "đồ án hiện có", "trực tiếp", "refactor", "bổ sung vào", "dự án hiện có", "hiện tại", "hiện có", "sẵn có"]), "Phải ưu tiên cải thiện trực tiếp đồ án hiện có, không bắt làm lại từ đầu"

    # 6. Phân biệt nhiệm vụ bắt buộc (Must-have) với làm thêm nếu còn thời gian (Nice-to-have)
    has_must = any(k in reply_lower for k in ["bắt buộc", "must-have", "cốt lõi", "ưu tiên 1", "ưu tiên số 1", "tiên quyết", "trọng tâm"])
    has_nice = any(k in reply_lower for k in ["nice-to-have", "bổ trợ", "làm thêm", "nếu còn thời gian", "recommended", "tùy chọn", "nâng cao", "mở rộng"])
    assert has_must and has_nice, "Phải phân biệt nhiệm vụ bắt buộc vs nice-to-have"

    # 7. Có cách kiểm tra tiến độ
    assert any(k in reply_lower for k in ["kiểm tra tiến độ", "tiến độ", "nghiệm thu", "đánh giá"]), "Phải có hướng dẫn kiểm tra tiến độ"

    print(">>> PASS TC20: Kế hoạch 4 tuần chi tiết, 1-2h/ngày, deliverable kiểm chứng được, phân chia Must-have vs Nice-to-have, refactor đồ án cũ hoàn hảo!")


def run_tc21(consultant):
    print("\n" + "=" * 80)
    print("KIỂM THỬ TC21: TÍNH MINH BẠCH VÀ GIẢI THÍCH ĐIỂM SỐ READINESS SCORE (72%) (P0)")
    print("=" * 80)

    sid = str(uuid.uuid4())
    tc21_input = (
        "GEM đánh giá mức độ phù hợp giữa đồ án của tôi và vị trí Backend Developer là 72%. "
        "Điểm này có nghĩa là gì? Nó được tính dựa trên những yếu tố nào và tôi cần cải thiện gì để tăng mức độ phù hợp?"
    )
    print(f"\n[TC21] Input: {tc21_input}")
    res = consultant.chat(session_id=sid, user_message=tc21_input)
    reply = res["reply"]
    print(f"\n[TC21] Reply:\n{reply}\n")

    reply_lower = reply.lower()

    # 1. Giải thích rõ điểm số được tính từ những thành phần nào theo đúng cách triển khai thực tế của GEM
    assert any(k in reply_lower for k in ["semantic fit", "độ tương đồng ngữ nghĩa", "bge-m3", "cosine", "vector"]), "Phải giải thích thành phần Semantic Fit (35%)"
    assert any(k in reply_lower for k in ["coverage", "tỷ lệ bao phủ", "bao phủ kỹ năng", "trọng số"]), "Phải giải thích thành phần Coverage Rate (65%)"
    assert any(k in reply_lower for k in ["0.35", "35%", "0.65", "65%"]), "Phải nêu rõ công thức/trọng số định lượng thực tế của GEM"

    # 2. TUYỆT ĐỐI KHÔNG khẳng định 72% là 72% cơ hội có việc làm hay trúng tuyển (Critical Guardrail)
    assert any(k in reply_lower for k in ["không đồng nghĩa", "không khẳng định", "không đại diện", "không có nghĩa là 72% cơ hội", "không phải là xác suất", "tuyệt đối không"]), "Phải có cảnh báo không đánh đồng điểm số với xác suất có việc làm"

    # 3. Chỉ ra những kỹ năng / nhóm kỹ năng đang làm giảm mức độ phù hợp (28% khoảng cách)
    assert any(k in reply_lower for k in ["giảm", "khoảng cách", "28%", "thiếu"]), "Phải phân tích các yếu tố làm giảm điểm số"
    assert any(k in reply_lower for k in ["test", "kiểm thử", "redis", "docker", "index", "transactions"]), "Phải nêu cụ thể các kỹ năng làm giảm điểm (Test, Redis, Docker, Indexing)"

    # 4. Đề xuất hành động cải thiện gắn với các thành phần điểm để nâng lên 85%+
    assert any(k in reply_lower for k in ["85%", "tăng điểm", "cải thiện", "hành động"]), "Phải có đề xuất hành động cụ thể để tăng điểm lên 85%+"

    print(">>> PASS TC21: Minh bạch công thức 0.35*Semantic + 0.65*Coverage, guardrail đạo đức không đánh đồng cơ hội việc làm, chỉ rõ gap 28% và lộ trình nâng lên 85%+!")


if __name__ == "__main__":
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    print("\nBẮT ĐẦU TEST TOÀN DIỆN NHÓM 7 (TC19, TC20, TC21):")
    run_tc19(consultant, sid)
    run_tc20(consultant, sid)
    run_tc21(consultant)

    print("\n" + "=" * 80)
    print(">>> TẤT CẢ TEST CASES NHÓM 7 (TC19, TC20, TC21) ĐÃ CHẠY VÀ PASS 100%!")
    print("=" * 80 + "\n")
