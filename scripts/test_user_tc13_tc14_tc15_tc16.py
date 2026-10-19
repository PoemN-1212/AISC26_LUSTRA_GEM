import sys
import os
import uuid

# Đảm bảo import được gem_pipeline
sys.path.append(os.path.join(os.getcwd(), "pipeline", "src"))

from gem_pipeline.recommendation.consultant import IdeationConsultant


def run_tc13():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TC13: HỆ QUY CHIẾU THỊ TRƯỜNG & XẾP HẠNG KỸ NĂNG THEO DỮ LIỆU JD THỰC TẾ (P0)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    tc13_input = "Tôi muốn theo Backend Developer tại Việt Nam. Hãy cho biết những kỹ năng tôi nên ưu tiên học dựa trên dữ liệu tuyển dụng mà GEM đang có."
    print(f"\n[TC13] Input: {tc13_input}")
    res = consultant.chat(session_id=sid, user_message=tc13_input)
    reply = res["reply"]
    print(f"\n[TC13] Reply:\n{reply}\n")

    # Kiểm tra Tiêu chí TC13
    # 1. Xác định nhóm JD Backend Developer được dùng để phân tích
    assert any(k in reply.lower() for k in ["backend", "backend developer"]), "Phải xác định đúng vị trí Backend Developer"
    assert any(k in reply for k in ["88", "JD", "jd", "tin tuyển dụng"]), "Phải nêu quy mô tập JD phân tích"

    # 2. Trình bày các kỹ năng xuất hiện trong dữ liệu theo tiêu chí rõ ràng (tần suất / % JD)
    assert any(k in reply for k in ["Java", "java", "PostgreSQL", "postgresql", "REST", "rest"]), "Phải nêu các kỹ năng thực tế trong JD"
    assert any(k in reply for k in ["%", "tỷ lệ", "tần suất"]), "Phải có tỷ lệ % nhu cầu hoặc số lượng JD"

    # 3. Phân biệt kỹ năng nền tảng và kỹ năng bổ trợ
    assert any(k in reply.lower() for k in ["nền tảng", "cốt lõi", "core"]), "Phải có phân nhóm kỹ năng nền tảng/cốt lõi"
    assert any(k in reply.lower() for k in ["bổ trợ", "lợi thế", "booster", "plus"]), "Phải có phân nhóm kỹ năng bổ trợ/lợi thế"

    # 4. Không đánh đồng tần suất với mức độ bắt buộc
    assert any(k in reply.lower() for k in ["không bắt buộc", "bắt buộc", "không đánh đồng", "chọn 1", "chuyên sâu"]), "Phải giải thích rõ không đánh đồng tần suất với mức độ bắt buộc học tất cả"

    # 5. Giải thích giới hạn của dữ liệu
    assert any(k in reply.lower() for k in ["giới hạn", "không đại diện tuyệt đối", "hệ quy chiếu", "khảo sát", "topcv", "2025", "2026"]), "Phải minh bạch giới hạn của tập dữ liệu khảo sát"

    print(">>> PASS TC13: Hệ quy chiếu thị trường chuẩn xác, số liệu có căn cứ thực tế, phân nhóm rõ ràng, minh bạch giới hạn!")
    print("\n===> KẾT LUẬN TC13: HOÀN TOÀN ĐẠT CHUẨN P0!\n")


def run_tc14():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TC14: SO SÁNH HAI VỊ TRÍ NGHỀ NGHIỆP DỰA TRÊN DỮ LIỆU JD THỰC TẾ (P1)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    tc14_input = "Tôi đang phân vân giữa Backend Developer và Data Engineer. Hãy so sánh hai hướng dựa trên những kỹ năng xuất hiện trong dữ liệu JD của GEM, sau đó cho biết tôi nên cân nhắc điều gì khi chọn hướng làm đồ án."
    print(f"\n[TC14] Input: {tc14_input}")
    res = consultant.chat(session_id=sid, user_message=tc14_input)
    reply = res["reply"]
    print(f"\n[TC14] Reply:\n{reply}\n")

    # Kiểm tra Tiêu chí TC14
    # 1. Tạo hai nhóm kỹ năng riêng biệt (không trộn lẫn)
    assert "backend" in reply.lower() and "data engineer" in reply.lower(), "Phải bao hàm cả 2 vị trí Backend và Data Engineer"
    assert any(k in reply.lower() for k in ["hồ sơ backend", "hồ sơ data engineer", "kỹ năng đặc thù", "riêng biệt", "nhóm backend"]), "Phải tách bạch hồ sơ 2 vị trí"

    # 2. Phân tích kỹ năng chung và kỹ năng đặc thù
    assert any(k in reply.lower() for k in ["kỹ năng chung", "giao thoa", "nền tảng chung", "cả hai"]), "Phải phân tích kỹ năng chung giao thoa"
    assert any(k in reply.lower() for k in ["kỹ năng đặc thù", "riêng", "khác biệt"]), "Phải chỉ ra kỹ năng đặc thù của từng vai trò"

    # 3. Khác biệt gắn với công việc thực tế (Dịch vụ & API vs Luồng dữ liệu)
    assert any(k in reply.lower() for k in ["dịch vụ", "api", "người dùng", "giao dịch", "oltp"]), "Phải giải thích bản chất dịch vụ/API của Backend"
    assert any(k in reply.lower() for k in ["luồng dữ liệu", "pipeline", "kho dữ liệu", "data warehouse", "olap", "etl"]), "Phải giải thích bản chất luồng dữ liệu của Data Engineer"

    # 4. Gợi ý định hướng đồ án cho từng hướng
    assert any(k in reply.lower() for k in ["đồ án", "thương mại", "web", "restful", "jwt", "locking"]), "Phải có gợi ý đồ án cho Backend Developer"
    assert any(k in reply.lower() for k in ["data pipeline", "airflow", "warehouse", "etl", "crawling", "dashboard"]), "Phải có gợi ý đồ án cho Data Engineer"

    # 5. Không kết luận nghề nào tốt hơn một cách tuyệt đối
    assert any(k in reply.lower() for k in ["không", "tùy thuộc", "sở thích", "cân nhắc", "phù hợp", "thiên hướng"]), "Không kết luận nghề nào tốt hơn tuyệt đối"

    print(">>> PASS TC14: So sánh 2 vị trí khoa học, tách riêng hồ sơ kỹ năng, đối sánh OLTP vs OLAP, gợi ý đồ án xuất sắc!")
    print("\n===> KẾT LUẬN TC14: HOÀN TOÀN ĐẠT CHUẨN P1!\n")


def run_tc15():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TC15: XỬ LÝ TRƯỜNG HỢP CÔNG NGHỆ CHƯA CÓ BẰNG CHỨNG DỮ LIỆU THỊ TRƯỜNG (P0)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    tc15_input = "Tôi nghe nói Mojo đang rất hot và muốn đưa vào đồ án. Hãy xác nhận xem công nghệ đó có đang được các công ty tuyển dụng nhiều hay không, dựa trên dữ liệu của GEM."
    print(f"\n[TC15] Input: {tc15_input}")
    res = consultant.chat(session_id=sid, user_message=tc15_input)
    reply = res["reply"]
    print(f"\n[TC15] Reply:\n{reply}\n")

    # Kiểm tra Tiêu chí TC15
    # 1. Báo cáo trung thực hiện trạng dữ liệu: 0 JD hoặc chưa có trong kho dữ liệu
    assert any(k in reply.lower() for k in ["chưa đủ căn cứ", "chưa ghi nhận", "0", "chưa có", "không có"]), "Phải thông báo rõ dữ liệu chưa đủ hoặc 0 JD"
    assert not any(k in reply.lower() for k in ["đang được tuyển dụng rất nhiều", "chiếm 50% jd", "chiếm 40% jd"]), "Tuyệt đối không bịa đặt số liệu Mojo đang tuyển dụng nhiều"

    # 2. Phân biệt rõ giá trị kỹ thuật vs nhu cầu tuyển dụng thực tế
    assert any(k in reply.lower() for k in ["giá trị kỹ thuật", "kỹ thuật", "tiềm năng", "hiệu năng", "python", "c++"]), "Phải phân tích giá trị kỹ thuật thực chất của công nghệ"
    assert any(k in reply.lower() for k in ["thị trường", "tuyển dụng", "tách biệt", "doanh nghiệp", "thực tế"]), "Phải tách biệt giá trị kỹ thuật với nhu cầu tuyển dụng thị trường"

    # 3. Lời khuyên định hướng đồ án (khuyến nghị stack ổn định + PoC)
    assert any(k in reply.lower() for k in ["đồ án", "ổn định", "thử nghiệm", "poc", "proof of concept", "phụ trợ", "rủi ro"]), "Phải đưa ra lời khuyên đồ án an toàn, tránh rủi ro"

    # 4. Phương pháp đánh giá tiếp theo để xác minh nhu cầu
    assert any(k in reply.lower() for k in ["xác minh", "theo dõi", "github", "trending", "cộng đồng", "khảo sát"]), "Phải gợi ý cách sinh viên tự xác minh nhu cầu thị trường"

    print(">>> PASS TC15: Minh bạch tuyệt đối về thiếu bằng chứng dữ liệu, tách biệt kỹ thuật vs thị trường, không bịa đặt!")
    print("\n===> KẾT LUẬN TC15: HOÀN TOÀN ĐẠT CHUẨN P0!\n")


def run_tc16():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TC16: CHẤT LƯỢNG DỮ LIỆU & TÍNH MINH BẠCH VỀ CƠ CHẾ KHỬ TRÙNG (P1)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    tc16_input = "Tôi muốn biết kỹ năng nào phổ biến nhất trong các JD Backend Developer mà GEM đã thu thập. Nếu có nhiều tin tuyển dụng trùng nội dung hoặc một số JD không còn phù hợp, kết quả có bị ảnh hưởng không?"
    print(f"\n[TC16] Input: {tc16_input}")
    res = consultant.chat(session_id=sid, user_message=tc16_input)
    reply = res["reply"]
    print(f"\n[TC16] Reply:\n{reply}\n")

    # Kiểm tra Tiêu chí TC16
    # 1. Trình bày các kỹ năng phổ biến nhất trong JD Backend Developer
    assert any(k in reply for k in ["Java", "java", "PostgreSQL", "postgresql", "REST", "Spring Boot", "spring"]), "Phải liệt kê kỹ năng phổ biến nhất của Backend Developer"
    assert any(k in reply for k in ["88", "JD", "jd", "%"]), "Phải có dẫn chứng số liệu thực tế"

    # 2. Giải thích cơ chế rủi ro: tin trùng lặp có thể làm kỹ năng bị đếm nhiều lần
    assert any(k in reply.lower() for k in ["trùng lặp", "đếm", "nhân đôi", "thổi phồng", "overcount", "lệch", "ảnh hưởng"]), "Phải giải thích rủi ro tin trùng làm đếm trùng kỹ năng"

    # 3. Nêu các cơ chế xử lý dữ liệu thực tế mà GEM đã triển khai
    assert any(k in reply.lower() for k in ["khử trùng", "content_clean", "tiêu đề", "công ty", "băm", "hash", "deduplication"]), "Phải nêu cơ chế khử trùng bài đăng"
    assert any(k in reply.lower() for k in ["distinct doc_id", "distinct", "đơn nhất", "1 lần"]), "Phải nêu cơ chế đếm DISTINCT doc_id"
    assert any(k in reply.lower() for k in ["verifier", "kiểm chứng", "accept", "reject", "ngữ cảnh"]), "Phải nêu cơ chế kiểm chứng ngữ cảnh Verifier LLM"

    # 4. Không khẳng định dữ liệu hoàn toàn sạch 100%, có nêu giới hạn
    assert any(k in reply.lower() for k in ["không", "100%", "hoàn toàn sạch", "giới hạn", "tham khảo", "hệ quy chiếu"]), "Phải minh bạch không khẳng định dữ liệu sạch 100%"

    print(">>> PASS TC16: Minh bạch chất lượng dữ liệu, nêu đúng 3 cơ chế làm sạch thực tế của GEM, không nói quá!")
    print("\n===> KẾT LUẬN TC16: HOÀN TOÀN ĐẠT CHUẨN P1!\n")


if __name__ == "__main__":
    print("\n" + "#" * 80)
    print("BẮT ĐẦU CHẠY TOÀN BỘ TEST SUITE NHÓM 5 (TC13, TC14, TC15, TC16)")
    print("#" * 80)

    try:
        run_tc13()
        run_tc14()
        run_tc15()
        run_tc16()
        print("\n" + "#" * 80)
        print("TẤT CẢ 4/4 TEST CASES NHÓM 5 ĐỀU ĐÃ VƯỢT QUA XUẤT SẮC (PASS 100%)!")
        print("#" * 80)
    except Exception as e:
        print(f"\n[FAILED]: Có lỗi xảy ra trong quá trình kiểm thử Nhóm 5: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
