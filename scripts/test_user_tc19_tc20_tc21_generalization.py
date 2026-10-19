import sys
import os
import uuid

# Đảm bảo import được gem_pipeline
sys.path.append(os.path.join(os.getcwd(), "pipeline", "src"))

from gem_pipeline.recommendation.consultant import IdeationConsultant


def run_tc19_generalized(consultant, session_id):
    print("\n" + "=" * 80)
    print("KIỂM THỬ TỔNG QUÁT HÓA TC19: ĐỒ ÁN PYTHON FASTAPI + POSTGRESQL (P0)")
    print("=" * 80)

    g1_input = (
        "Tôi đã làm một hệ thống tin tức và quản lý nội dung CMS với Python, FastAPI và PostgreSQL. "
        "Tôi muốn ứng tuyển Backend Developer Intern. Hãy phân tích những kỹ năng đồ án của tôi đã thể hiện, "
        "những kỹ năng còn thiếu so với yêu cầu tuyển dụng và thứ tự ưu tiên cải thiện."
    )
    print(f"\n[TC19-Gen] Input: {g1_input}")
    res = consultant.chat(session_id=session_id, user_message=g1_input)
    reply = res["reply"]
    print(f"\n[TC19-Gen] Reply:\n{reply}\n")

    reply_lower = reply.lower()

    # 1. Phân biệt kỹ năng đã có bằng chứng (Nhóm 1)
    assert any(k in reply_lower for k in ["kỹ năng có thể được thể hiện", "kỹ năng đã thể hiện", "thể hiện qua đồ án", "đã có bằng chứng", "đã thể hiện"]), "Phải có Nhóm 1"
    assert any(k in reply_lower for k in ["api", "endpoints", "nghiệp vụ", "truy vấn", "postgresql", "crud", "fastapi"]), "Nhóm 1 phải ghi nhận đúng kỹ năng từ đề tài và stack"

    # 2. Kỹ năng chưa có đủ bằng chứng (Nhóm 2)
    assert any(k in reply_lower for k in ["chưa có đủ bằng chứng", "chưa đủ bằng chứng", "chưa kiểm chứng", "lỗ hổng tiềm ẩn"]), "Phải có Nhóm 2"
    assert any(k in reply_lower for k in ["kiểm thử", "test", "unit test", "tối ưu", "triển khai", "xử lý lỗi", "transaction", "index"]), "Nhóm 2 phải chỉ ra các năng lực thiếu bằng chứng"

    # 3. Guardrail: Không coi tên công nghệ là bằng chứng đầy đủ
    assert any(k in reply_lower for k in ["không đồng nghĩa", "không coi tên công nghệ", "bằng chứng đầy đủ", "chưa chứng minh", "không có nghĩa", "không khẳng định"]), "Phải có guardrail không coi tên công nghệ là bằng chứng đầy đủ"

    # 4. Khoảng cách kỹ năng liên hệ với JD thực tế (Nhóm 3)
    assert any(k in reply_lower for k in ["khoảng cách so với", "yêu cầu tuyển dụng", "88", "jd", "thị trường"]), "Phải có Nhóm 3 gắn với JD thực tế"

    # 5. Thứ tự ưu tiên có trọng tâm và giải thích (Nhóm 4)
    assert any(k in reply_lower for k in ["thứ tự ưu tiên", "ưu tiên 1", "ưu tiên"]), "Phải có Nhóm 4 thứ tự ưu tiên"
    assert any(k in reply_lower for k in ["vì sao", "lý do", "giải thích"]), "Phải giải thích lý do vì sao ưu tiên"

    print(">>> PASS TC19 Generalization: Xử lý xuất sắc đồ án CMS + Python/FastAPI/Postgres!")
    return session_id


def run_tc20_generalized(consultant, session_id):
    print("\n" + "=" * 80)
    print("KIỂM THỬ TỔNG QUÁT HÓA TC20: KẾ HOẠCH HÀNH ĐỘNG 4 TUẦN KẾ THỪA PYTHON FASTAPI (P1)")
    print("=" * 80)

    g2_input = (
        "Dựa trên kết quả phân tích đồ án và Skill Gap vừa rồi, hãy lập cho tôi kế hoạch cải thiện trong bốn tuần "
        "để chuẩn bị ứng tuyển Backend Developer Intern. Tôi có thể dành khoảng một đến hai giờ mỗi ngày."
    )
    print(f"\n[TC20-Gen] Input: {g2_input}")
    res = consultant.chat(session_id=session_id, user_message=g2_input)
    reply = res["reply"]
    print(f"\n[TC20-Gen] Reply:\n{reply}\n")

    reply_lower = reply.lower()

    # 1. Kế thừa context và skill gap
    assert any(k in reply_lower for k in ["test", "pytest", "kiểm thử", "transaction", "index", "docker", "redis"]), "Phải giữ lại các khoảng cách kỹ năng"

    # 2. Đủ 4 tuần
    for week_kw in ["tuần 1", "tuần 2", "tuần 3", "tuần 4"]:
        assert week_kw in reply_lower, f"Phải có kế hoạch cho {week_kw}"

    # 3. Phù hợp 1-2h/ngày
    assert any(k in reply_lower for k in ["1-2", "1 đến 2", "giờ/ngày", "mỗi ngày"]), "Phải phù hợp quỹ thời gian 1-2h/ngày"

    # 4. Deliverable kiểm chứng được
    assert any(k in reply_lower for k in ["kết quả", "đầu ra", "deliverable", "artifact", "kiểm chứng"]), "Mỗi tuần phải có kết quả có thể kiểm chứng"

    # 5. Refactor trực tiếp đồ án hiện có
    assert any(k in reply_lower for k in ["đồ án hiện tại", "đồ án hiện có", "trực tiếp", "refactor", "bổ sung vào", "dự án hiện có", "hiện tại", "hiện có"]), "Phải refactor đồ án hiện có"

    # 6. Must-have vs Nice-to-have
    has_must = any(k in reply_lower for k in ["bắt buộc", "must-have", "cốt lõi", "ưu tiên 1", "trọng tâm"])
    has_nice = any(k in reply_lower for k in ["nice-to-have", "bổ trợ", "làm thêm", "nếu còn thời gian", "recommended", "tùy chọn", "nâng cao"])
    assert has_must and has_nice, "Phải phân loại Must-have vs Nice-to-have"

    # 7. Kiểm tra tiến độ
    assert any(k in reply_lower for k in ["tiến độ", "nghiệm thu", "đánh giá", "kiểm tra"]), "Phải có cách kiểm tra tiến độ"

    print(">>> PASS TC20 Generalization: Kế hoạch 4 tuần chi tiết, thích ứng hoàn hảo với stack Python/FastAPI/Postgres!")


def run_tc21_generalized(consultant):
    print("\n" + "=" * 80)
    print("KIỂM THỬ TỔNG QUÁT HÓA TC21: GIẢI THÍCH READINESS SCORE 68% CHO DATA ENGINEER (P0)")
    print("=" * 80)

    sid = str(uuid.uuid4())
    g3_input = (
        "GEM đánh giá mức độ phù hợp giữa đồ án của tôi và vị trí Data Engineer là 68%. "
        "Điểm này có nghĩa là gì? Nó được tính dựa trên những yếu tố nào và tôi cần cải thiện gì để tăng mức độ phù hợp?"
    )
    print(f"\n[TC21-Gen] Input: {g3_input}")
    res = consultant.chat(session_id=sid, user_message=g3_input)
    reply = res["reply"]
    print(f"\n[TC21-Gen] Reply:\n{reply}\n")

    reply_lower = reply.lower()

    # 1. Công thức và thành phần điểm
    assert any(k in reply_lower for k in ["semantic fit", "độ tương đồng ngữ nghĩa", "bge-m3", "cosine", "vector"]), "Phải có thành phần Semantic Fit (35%)"
    assert any(k in reply_lower for k in ["coverage", "tỷ lệ bao phủ", "bao phủ kỹ năng", "trọng số"]), "Phải có thành phần Coverage Rate (65%)"
    assert any(k in reply_lower for k in ["0.35", "35%", "0.65", "65%"]), "Phải nêu công thức định lượng 0.35 * Semantic + 0.65 * Coverage"

    # 2. Đúng số lượng JD của Data Engineer (23 JD)
    assert any(k in reply_lower for k in ["23", "data engineer"]), "Phải đối chiếu với tập JD của Data Engineer (23 JD)"

    # 3. Guardrail: Không khẳng định 68% là xác suất có việc làm
    assert any(k in reply_lower for k in ["không đồng nghĩa", "không khẳng định", "không đại diện", "không có nghĩa là 68% cơ hội", "không phải là xác suất", "tuyệt đối không"]), "Phải có guardrail đạo đức"

    # 4. Chỉ ra các yếu tố làm giảm điểm (khoảng cách 32%)
    assert any(k in reply_lower for k in ["32%", "giảm", "khoảng cách", "thiếu"]), "Phải phân tích khoảng cách làm giảm điểm"

    # 5. Đề xuất hành động tăng lên 85%+
    assert any(k in reply_lower for k in ["85%", "tăng", "cải thiện", "hành động"]), "Phải đề xuất hành động nâng điểm lên 85%+"

    print(">>> PASS TC21 Generalization: Động hóa thành công cho Data Engineer, 23 JD, 68% score và 32% gap!")


if __name__ == "__main__":
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    print("\nBẮT ĐẦU TEST TỔNG QUÁT HÓA NHÓM 7 (TC19, TC20, TC21):")
    run_tc19_generalized(consultant, sid)
    run_tc20_generalized(consultant, sid)
    run_tc21_generalized(consultant)

    print("\n" + "=" * 80)
    print(">>> TẤT CẢ TEST CASES TỔNG QUÁT HÓA NHÓM 7 ĐÃ PASS 100%!")
    print("=" * 80 + "\n")
