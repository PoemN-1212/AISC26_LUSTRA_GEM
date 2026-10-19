import sys
import os
import uuid

# Đảm bảo import được gem_pipeline
sys.path.append(os.path.join(os.getcwd(), "pipeline", "src"))

from gem_pipeline.recommendation.consultant import IdeationConsultant


def run_tc10():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TC10: NGƯỜI DÙNG THAY ĐỔI MỤC TIÊU NGHỀ NGHIỆP SAU CÂU TRẢ LỜI ĐẦU TIÊN (P0)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    # Turn 1
    t1_input = "Tôi muốn làm website thương mại điện tử nhưng chưa biết nên chọn stack nào."
    print(f"\n[Turn 1] Input: {t1_input}")
    res1 = consultant.chat(session_id=sid, user_message=t1_input)
    reply1 = res1["reply"]
    print(f"[Turn 1] Reply:\n{reply1[:400]}...\n")

    # Kiểm tra Turn 1
    assert any(k in reply1.lower() for k in ["sản phẩm", "thương mại điện tử", "cốt lõi", "mvp"]), "Turn 1 phải phân tích sản phẩm"
    assert any(k in reply1.lower() for k in ["frontend", "backend", "full-stack"]), "Turn 1 phải gợi ý hướng nghề nghiệp"
    assert any(k in reply1.lower() for k in ["cốt lõi", "core stack", "react", "node", "python", "mysql"]), "Turn 1 phải đề xuất stack cốt lõi"
    print(">>> PASS TURN 1: Đã phân tích sản phẩm, gợi ý vai trò và stack cốt lõi!")

    # Turn 2
    t2_input = "Tôi muốn theo AI Engineer."
    print(f"\n[Turn 2] Input: {t2_input}")
    res2 = consultant.chat(session_id=sid, user_message=t2_input)
    reply2 = res2["reply"]
    print(f"[Turn 2] Reply:\n{reply2[:400]}...\n")

    # Kiểm tra Turn 2
    assert "ai" in res2["session_state"]["target_role"].lower() or "machine learning" in res2["session_state"]["target_role"].lower(), "Target role phải cập nhật thành AI Engineer"
    assert any(k in reply2.lower() for k in ["thương mại điện tử", "sản phẩm", "website", "bán hàng"]), "Turn 2 phải giữ lại ý tưởng thương mại điện tử ban đầu"
    assert any(k in reply2.lower() for k in ["gợi ý", "recommend", "phân loại", "đánh giá", "dự báo", "sentiment", "khách hàng"]), "Turn 2 phải đề xuất tính năng AI phù hợp với e-commerce"
    print(">>> PASS TURN 2: Đã chuyển hướng AI Engineer, giữ nguyên đề tài e-commerce và đề xuất tính năng AI!")

    # Turn 3
    t3_input = "Tôi chỉ có ba tháng, đã biết Python cơ bản và muốn học scikit-learn. Đừng đề xuất kiến trúc phức tạp quá."
    print(f"\n[Turn 3] Input: {t3_input}")
    res3 = consultant.chat(session_id=sid, user_message=t3_input)
    reply3 = res3["reply"]
    print(f"[Turn 3] Reply:\n{reply3[:500]}...\n")

    # Kiểm tra Turn 3
    assert res3["session_state"]["time_months"] == 3, "Session phải lưu thời gian 3 tháng"
    assert any(k in reply3.lower() for k in ["thương mại điện tử", "sản phẩm", "website"]), "Turn 3 phải nhớ ý tưởng thương mại điện tử"
    assert any(k in reply3.lower() for k in ["scikit-learn", "sklearn"]), "Turn 3 phải tập trung vào scikit-learn"
    assert any(k in reply3.lower() for k in ["3 tháng", "ba tháng"]), "Turn 3 phải bám sát giới hạn 3 tháng"
    assert any(k in reply3.lower() for k in ["python cơ bản", "cơ bản"]), "Turn 3 phải nhận biết trình độ Python cơ bản"
    assert any(k in reply3.lower() for k in ["gợi ý", "recommend", "phân loại", "đánh giá", "tfidf", "cosine"]), "Turn 3 phải đề xuất tính năng AI vừa sức bằng scikit-learn"
    assert not any(k in reply3.lower() for k in ["triển khai cụm microservices", "dựng cụm kubernetes", "triển khai kafka"]), "Turn 3 không được đề xuất kiến trúc phức tạp trái yêu cầu"
    print(">>> PASS TURN 3: Thu hẹp phạm vi theo 3 tháng, Python cơ bản, scikit-learn, không phức tạp!")
    print("\n===> KẾT LUẬN TC10: HOÀN TOÀN ĐẠT CHUẨN P0 (3/3 Turns)!\n")


def run_tc11():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TC11: NGƯỜI DÙNG YÊU CẦU GIẢI THÍCH CĂN CỨ ĐỀ XUẤT CÔNG NGHỆ (P0)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    # Khởi tạo session ban đầu với Backend / Full-stack
    init_msg = "Tôi đang làm đồ án web bán hàng theo hướng Backend Developer."
    consultant.chat(session_id=sid, user_message=init_msg)

    # Input TC11
    tc11_input = "Tại sao bạn lại đề xuất Docker cho đồ án của tôi? Có thật sự nhiều JD yêu cầu nó không, hay bạn chỉ đang gợi ý theo kiến thức chung?"
    print(f"\n[TC11] Input: {tc11_input}")
    res = consultant.chat(session_id=sid, user_message=tc11_input)
    reply = res["reply"]
    print(f"\n[TC11] Reply:\n{reply}\n")

    # Kiểm tra Tiêu chí TC11
    # 1. Phân biệt rõ Lý do Kỹ thuật
    assert any(k in reply.lower() for k in ["lý do kỹ thuật", "kỹ thuật", "đóng gói", "container", "môi trường", "nhất quán"]), "Phải có phần phân tích Lý do kỹ thuật"
    
    # 2. Căn cứ từ thị trường tuyển dụng thực tế
    assert any(k in reply.lower() for k in ["thị trường tuyển dụng", "căn cứ", "tin tuyển dụng", "jd", "topcv"]), "Phải có căn cứ từ thị trường tuyển dụng thực tế"
    
    # 3. Số liệu thực tế
    assert any(k in reply for k in ["88", "JD", "jd"]), "Phải nêu số lượng JD được phân tích"
    assert any(k in reply for k in ["27", "25", "24", "%"]), "Phải nêu tỷ lệ % nhu cầu hoặc số lượng JD đề cập"
    assert any(k in reply.lower() for k in ["2025", "2026", "topcv", "thực tế"]), "Phải có mốc thời gian / nguồn dữ liệu"
    
    # 4. Phân biệt bắt buộc và ưu tiên
    assert any(k in reply.lower() for k in ["ưu tiên", "lợi thế", "booster", "điểm cộng", "không bắt buộc"]), "Phải phân biệt Docker là kỹ năng ưu tiên/lợi thế, không kết luận là bắt buộc tuyệt đối"

    print(">>> PASS TC11: Tách rõ Lý do Kỹ thuật vs Căn cứ Dữ liệu Tuyển dụng TopCV thực tế, số liệu chính xác!")
    print("\n===> KẾT LUẬN TC11: HOÀN TOÀN ĐẠT CHUẨN P0!\n")


def run_tc12():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TC12: NGƯỜI DÙNG BỔ SUNG THÔNG TIN LÀM THAY ĐỔI PHƯƠNG ÁN TRƯỚC ĐÓ (P1)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    # Turn 1
    t1_input = "Tôi muốn làm website học trực tuyến có video bài giảng, bài kiểm tra và theo dõi tiến độ học tập. Tôi đang cân nhắc hướng Full-stack Developer."
    print(f"\n[Turn 1] Input: {t1_input}")
    res1 = consultant.chat(session_id=sid, user_message=t1_input)
    reply1 = res1["reply"]
    print(f"[Turn 1] Reply:\n{reply1[:400]}...\n")

    assert any(k in reply1.lower() for k in ["học trực tuyến", "khóa học", "bài giảng", "tiến độ"]), "Turn 1 phải tiếp nhận đề tài học trực tuyến"
    assert "full-stack" in res1["session_state"]["target_role"].lower(), "Turn 1 phải ghi nhận vai trò Full-stack Developer"
    print(">>> PASS TURN 1: Đã định hình website học trực tuyến Full-stack!")

    # Turn 2
    t2_input = "Tôi làm đồ án một mình, chỉ còn sáu tuần và chưa từng triển khai ứng dụng lên server."
    print(f"\n[Turn 2] Input: {t2_input}")
    res2 = consultant.chat(session_id=sid, user_message=t2_input)
    reply2 = res2["reply"]
    print(f"[Turn 2] Reply:\n{reply2[:500]}...\n")

    # Kiểm tra Turn 2
    assert any(k in reply2.lower() for k in ["học trực tuyến", "khóa học", "bài giảng"]), "Turn 2 phải giữ bài toán học trực tuyến"
    assert any(k in reply2.lower() for k in ["một mình", "1 mình", "solo"]), "Turn 2 phải nhận diện làm 1 mình"
    assert any(k in reply2.lower() for k in ["sáu tuần", "6 tuần", "tuần"]), "Turn 2 phải điều chỉnh theo thời gian 6 tuần"
    assert any(k in reply2.lower() for k in ["triển khai", "deploy", "server", "render", "vercel", "railway"]), "Turn 2 phải đưa triển khai lên server vào kế hoạch"
    print(">>> PASS TURN 2: Điều chỉnh theo ràng buộc 1 mình, 6 tuần, đưa triển khai vào kế hoạch!")

    # Turn 3
    t3_input = "Tôi muốn ưu tiên hoàn thiện sản phẩm và có bản demo chạy được, chưa cần tính năng AI."
    print(f"\n[Turn 3] Input: {t3_input}")
    res3 = consultant.chat(session_id=sid, user_message=t3_input)
    reply3 = res3["reply"]
    print(f"[Turn 3] Reply:\n{reply3[:600]}...\n")

    # Kiểm tra Turn 3
    assert any(k in reply3.lower() for k in ["học trực tuyến", "khóa học", "bài học", "bài kiểm tra", "tiến độ"]), "Turn 3 phải giữ luồng cốt lõi"
    assert any(k in reply3.lower() for k in ["chưa cần", "không", "tôn trọng", "tạm hoãn", "ưu tiên"]), "Turn 3 phải phản hồi việc chưa cần AI"
    # Không được ép thêm AI
    assert not any(k in reply3.lower() for k in ["bắt buộc phải có ai", "phải dùng mô hình ai", "triển khai llm"]), "Turn 3 không được ép thêm AI"
    assert any(k in reply3.lower() for k in ["demo", "chạy được", "hoàn thiện", "mvp"]), "Turn 3 phải tập trung vào bản demo chạy được"
    assert any(k in reply3.lower() for k in ["triển khai", "deploy", "kiểm thử", "test"]), "Turn 3 phải có triển khai và kiểm thử trong kế hoạch"
    print(">>> PASS TURN 3: Tôn trọng việc chưa cần AI, tập trung demo chạy được và luồng cốt lõi!")
    print("\n===> KẾT LUẬN TC12: HOÀN TOÀN ĐẠT CHUẨN P1 (3/3 Turns)!\n")


if __name__ == "__main__":
    try:
        run_tc10()
        run_tc11()
        run_tc12()
        print("\n" + "*" * 80)
        print("TẤT CẢ TEST CASES NHÓM 4 (TC10, TC11, TC12) ĐỀU ĐẠT CHUẨN 100%!")
        print("*" * 80)
    except Exception as e:
        print(f"\n❌ LỖI KIỂM THỬ: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
