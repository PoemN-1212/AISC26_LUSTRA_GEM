import sys
import os
import uuid

# Đảm bảo import được gem_pipeline
sys.path.append(os.path.join(os.getcwd(), "pipeline", "src"))

from gem_pipeline.recommendation.consultant import IdeationConsultant


def test_tc13_generalization():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TỔNG QUÁT HÓA TC13: VAI TRÒ KHÁC (FRONTEND DEVELOPER)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    tc13_gen_input = "Tôi muốn theo Frontend Developer tại Việt Nam. Hãy cho biết những kỹ năng tôi nên ưu tiên học dựa trên dữ liệu tuyển dụng mà GEM đang có."
    print(f"[Input]: {tc13_gen_input}")
    res = consultant.chat(session_id=sid, user_message=tc13_gen_input)
    reply = res["reply"]
    print(f"\n[Reply Trích đoạn]:\n{reply[:600]}...\n")

    # Kiểm tra tính động theo vai trò Frontend Developer
    assert any(k in reply.lower() for k in ["frontend", "front-end"]), "Phải nhận diện và phản hồi đúng vai trò Frontend Developer"
    assert any(k in reply for k in ["JD", "jd", "tin tuyển dụng"]), "Phải trích xuất số liệu JD thực tế"
    assert any(k in reply for k in ["JavaScript", "javascript", "React", "react", "HTML", "CSS", "TypeScript"]), "Phải liệt kê kỹ năng thực tế của Frontend"
    assert any(k in reply.lower() for k in ["nền tảng", "cốt lõi", "core"]), "Phải có phân nhóm kỹ năng nền tảng"
    assert any(k in reply.lower() for k in ["bổ trợ", "lợi thế", "booster", "plus"]), "Phải có phân nhóm kỹ năng bổ trợ"
    assert any(k in reply.lower() for k in ["không bắt buộc", "bắt buộc", "không đánh đồng", "chọn 1"]), "Không đánh đồng tần suất với mức độ bắt buộc"
    assert any(k in reply.lower() for k in ["giới hạn", "không đại diện tuyệt đối", "hệ quy chiếu", "topcv"]), "Phải nêu giới hạn dữ liệu khảo sát"
    print(">>> PASS TC13 GENERALIZATION: Hoạt động tự động và chuẩn xác với Frontend Developer!")


def test_tc14_generalization():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TỔNG QUÁT HÓA TC14: CẶP VAI TRÒ KHÁC (FRONTEND DEVELOPER vs BACKEND DEVELOPER)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    tc14_gen_input = "Tôi đang phân vân giữa Frontend Developer và Backend Developer. Hãy so sánh hai hướng dựa trên những kỹ năng xuất hiện trong dữ liệu JD của GEM, sau đó cho biết tôi nên cân nhắc điều gì khi chọn hướng làm đồ án."
    print(f"[Input]: {tc14_gen_input}")
    res = consultant.chat(session_id=sid, user_message=tc14_gen_input)
    reply = res["reply"]
    print(f"\n[Reply Trích đoạn]:\n{reply[:600]}...\n")

    # Kiểm tra tính động khi so sánh Frontend vs Backend
    assert "frontend" in reply.lower() and "backend" in reply.lower(), "Phải bao hàm cả 2 vị trí Frontend và Backend"
    assert any(k in reply.lower() for k in ["giao diện", "ui", "ux", "client", "trình duyệt"]), "Phải nêu bản chất công việc của Frontend"
    assert any(k in reply.lower() for k in ["server", "dịch vụ", "api", "cơ sở dữ liệu", "nghiệp vụ"]), "Phải nêu bản chất công việc của Backend"
    assert any(k in reply.lower() for k in ["kỹ năng chung", "giao thoa", "nền tảng chung", "cả hai"]), "Phải phân tích kỹ năng giao thoa chung (như Git, REST API, JavaScript)"
    assert any(k in reply.lower() for k in ["kỹ năng đặc thù", "riêng"]), "Phải phân tích kỹ năng riêng của từng bên"
    assert any(k in reply.lower() for k in ["đồ án", "giao diện", "api"]), "Phải gợi ý định hướng đồ án phù hợp cho từng vai trò"
    assert not any(k in reply.lower() for k in ["frontend tốt hơn backend", "backend tốt hơn frontend", "nghề nào dễ hơn"]), "Không kết luận thiên vị"
    print(">>> PASS TC14 GENERALIZATION: Hoạt động tự động và chuẩn xác với cặp Frontend vs Backend!")


def test_tc15_generalization():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TỔNG QUÁT HÓA TC15: CÔNG NGHỆ MỚI KHÁC (GLEAM)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    tc15_gen_input = "Tôi nghe nói Gleam đang rất hot và muốn đưa vào đồ án. Hãy xác nhận xem công nghệ đó có đang được các công ty tuyển dụng nhiều hay không, dựa trên dữ liệu của GEM."
    print(f"[Input]: {tc15_gen_input}")
    res = consultant.chat(session_id=sid, user_message=tc15_gen_input)
    reply = res["reply"]
    print(f"\n[Reply Trích đoạn]:\n{reply[:600]}...\n")

    # Kiểm tra tính động khi hỏi về công nghệ mới Gleam
    assert "gleam" in reply.lower(), "Phải đề cập đúng công nghệ Gleam"
    assert any(k in reply.lower() for k in ["chưa đủ căn cứ", "chưa ghi nhận", "0", "chưa có", "không có"]), "Phải thông báo trung thực chưa có trong dữ liệu"
    assert not any(k in reply.lower() for k in ["đang được tuyển dụng rất nhiều", "chiếm 50% jd", "chiếm 40% jd"]), "Tuyệt đối không bịa đặt số liệu"
    assert any(k in reply.lower() for k in ["kỹ thuật", "giá trị", "tiềm năng", "beam", "erlang", "type-safe", "ngôn ngữ"]), "Phải phân tích giá trị kỹ thuật của Gleam"
    assert any(k in reply.lower() for k in ["tách biệt", "thị trường", "tuyển dụng", "thực tế"]), "Phải tách biệt kỹ thuật với nhu cầu tuyển dụng"
    assert any(k in reply.lower() for k in ["poc", "proof of concept", "thử nghiệm", "phụ trợ", "rủi ro", "ổn định"]), "Phải có lời khuyên đồ án an toàn"
    print(">>> PASS TC15 GENERALIZATION: Hoạt động tự động và trung thực với công nghệ mới Gleam!")


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("BẮT ĐẦU CHẠY TOÀN BỘ KIỂM THỬ TỔNG QUÁT HÓA CHO NHÓM 5")
    print("#" * 80)

    try:
        test_tc13_generalization()
        test_tc14_generalization()
        test_tc15_generalization()
        print("\n" + "#" * 80)
        print("TẤT CẢ CÁC BÀI TEST TỔNG QUÁT HÓA NHÓM 5 ĐỀU ĐÃ VƯỢT QUA XUẤT SẮC (PASS 100%)!")
        print("#" * 80)
    except Exception as e:
        print(f"\n[FAILED]: Có lỗi xảy ra trong quá trình kiểm thử tổng quát hóa: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
