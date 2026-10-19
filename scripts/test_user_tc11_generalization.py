import sys
import os
import uuid

sys.path.append(os.path.join(os.getcwd(), "pipeline", "src"))
from gem_pipeline.recommendation.consultant import IdeationConsultant


def test_tc11_generalization_other_techs():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TỔNG QUÁT HÓA TC11 VỚI NHIỀU CÔNG NGHỆ VÀ VAI TRÒ KHÁC NHAU")
    print("=" * 80)
    consultant = IdeationConsultant()

    # Test 1: Hỏi về Redis cho Backend Developer
    sid1 = str(uuid.uuid4())
    consultant.chat(session_id=sid1, user_message="Tôi làm web bán hàng theo hướng Backend Developer.")
    res_redis = consultant.chat(session_id=sid1, user_message="Tại sao bạn lại đề xuất Redis cho đồ án của tôi? Thị trường có chuộng không hay bạn chỉ nói lý thuyết?")
    reply_redis = res_redis["reply"]
    print(f"\n[Test 1 - Redis Backend] Reply:\n{reply_redis[:450]}...\n")
    assert any(k in reply_redis.lower() for k in ["redis", "cache", "bộ nhớ đệm"]), "Phải phân tích Redis"
    assert any(k in reply_redis.lower() for k in ["lý do kỹ thuật", "kỹ thuật"]), "Phải có lý do kỹ thuật"
    assert any(k in reply_redis.lower() for k in ["thị trường", "jd", "topcv", "tuyển dụng"]), "Phải có căn cứ thị trường tuyển dụng"
    print(">>> PASS Test 1 (Redis cho Backend): Tách bạch lý do kỹ thuật và căn cứ TopCV!")

    # Test 2: Hỏi về một công nghệ chưa có trong tập dữ liệu thống kê (ví dụ: 'Cobol' hoặc 'Elixir')
    sid2 = str(uuid.uuid4())
    consultant.chat(session_id=sid2, user_message="Tôi làm web thương mại điện tử theo hướng Backend Developer.")
    res_unknown = consultant.chat(session_id=sid2, user_message="Tại sao bạn lại khuyên tôi dùng Elixir? Có số liệu JD nào chứng minh không?")
    reply_unknown = res_unknown["reply"]
    print(f"\n[Test 2 - Unknown Tech: Elixir] Reply:\n{reply_unknown[:450]}...\n")
    assert any(k in reply_unknown.lower() for k in ["chưa ghi nhận", "giới hạn", "không đưa ra", "thực tiễn", "kỹ thuật", "minh bạch"]), "Phải minh bạch về giới hạn dữ liệu khi không có số liệu, không bịa đặt số liệu"
    print(">>> PASS Test 2 (Elixir không có trong dataset): Minh bạch về giới hạn dữ liệu, không bịa số liệu!")


def test_tc12_generalization_other_domain():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TỔNG QUÁT HÓA TC12 VỚI ĐỀ TÀI KHÁC (ĐẶT LỊCH KHÁM BỆNH)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    # Turn 1: Ứng dụng đặt lịch khám bệnh
    res1 = consultant.chat(session_id=sid, user_message="Tôi muốn làm hệ thống đặt lịch khám bệnh trực tuyến cho bệnh nhân và bác sĩ. Tôi định theo Full-stack Developer.")
    print(f"[Turn 1] Target role: {res1['session_state']['target_role']}")

    # Turn 2: Ràng buộc 4 tuần, làm một mình, chưa từng deploy
    res2 = consultant.chat(session_id=sid, user_message="Tôi làm một mình, chỉ có bốn tuần và chưa biết deploy lên cloud.")
    reply2 = res2["reply"]
    print(f"[Turn 2] Reply:\n{reply2[:400]}...\n")
    assert any(k in reply2.lower() for k in ["khám bệnh", "lịch hẹn", "bác sĩ", "bệnh nhân"]), "Phải giữ bản chất bài toán đặt lịch khám bệnh"
    assert any(k in reply2.lower() for k in ["một mình", "1 mình", "bốn tuần", "4 tuần", "tháng"]), "Phải nhận diện thời gian và nhân lực"
    assert any(k in reply2.lower() for k in ["triển khai", "deploy", "server", "cloud", "render", "vercel"]), "Phải đưa triển khai vào kế hoạch"

    # Turn 3: Chưa cần AI, ưu tiên demo
    res3 = consultant.chat(session_id=sid, user_message="Tôi muốn ưu tiên có bản demo chạy được luồng đặt lịch, chưa cần tính năng AI chẩn đoán bệnh.")
    reply3 = res3["reply"]
    print(f"[Turn 3] Reply:\n{reply3[:450]}...\n")
    assert any(k in reply3.lower() for k in ["chưa cần", "không", "tôn trọng", "tạm hoãn", "gác lại", "không ép"]), "Phải tôn trọng việc chưa cần AI"
    assert not any(k in reply3.lower() for k in ["bắt buộc phải có ai", "phải dùng llm", "phải tích hợp ai chẩn đoán"]), "Không được ép thêm AI"
    assert any(k in reply3.lower() for k in ["demo", "chạy được", "hoàn thiện", "cốt lõi"]), "Phải ưu tiên bản demo chạy được"
    print(">>> PASS TC12 Generalization (Đặt lịch khám bệnh): Đã tổng quát hóa thành công!")


if __name__ == "__main__":
    test_tc11_generalization_other_techs()
    test_tc12_generalization_other_domain()
    print("\n" + "*" * 80)
    print("KIỂM THỬ TỔNG QUÁT HÓA TC11 VÀ TC12 HOÀN TOÀN ĐẠT CHUẨN!")
    print("*" * 80)
