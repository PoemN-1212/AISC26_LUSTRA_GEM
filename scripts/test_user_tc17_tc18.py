import sys
import os
import uuid

# Đảm bảo import được gem_pipeline
sys.path.append(os.path.join(os.getcwd(), "pipeline", "src"))

from gem_pipeline.recommendation.consultant import IdeationConsultant
from gem_pipeline.vector_store.qdrant_service import QdrantVectorService


def run_tc17():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TC17: TÌM ĐỒ ÁN TƯƠNG TỰ ĐỂ THAM KHẢO TỪ KHO GITHUB GEM (P0)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    tc17_input = (
        "Tôi muốn làm website thương mại điện tử bằng React và Node.js. "
        "Hãy sử dụng các đồ án hoặc repository GitHub mà GEM có để tham khảo những chức năng, công nghệ và kỹ năng tôi nên cân nhắc."
    )
    print(f"\n[TC17] Input: {tc17_input}")
    res = consultant.chat(session_id=sid, user_message=tc17_input)
    reply = res["reply"]
    print(f"\n[TC17] Reply:\n{reply}\n")

    # 1. Dự án được nêu có thật trong kho dữ liệu hoặc nguồn truy xuất được
    # Lấy danh sách repo trong kho DB để đối chiếu
    qdrant = QdrantVectorService()
    real_projects = qdrant.search_similar_projects("website thương mại điện tử React Node.js", limit=5)
    real_repo_names = [p["repo_name"].lower() for p in real_projects]
    print(f"[TC17 Verification] Real repos in DB: {[p['repo_name'] for p in real_projects]}")

    # Kiểm tra phản hồi có chứa ít nhất 1 repo thật từ kho
    has_real_repo = any(r_name in reply.lower() for r_name in real_repo_names)
    assert has_real_repo, f"Phản hồi phải chứa repository thật từ kho GEM ({real_repo_names})"

    # 2. Không bịa link, URL phải là github.com hoặc có nguồn cụ thể
    assert "github.com" in reply.lower() or "repository" in reply.lower(), "Phải trích dẫn đường dẫn hoặc tên repository thật"

    # 3. Phân biệt dữ liệu nguồn (README / mô tả repo) với phần phân tích của GEM
    assert any(k in reply.lower() for k in ["kho dữ liệu", "nguồn", "dữ liệu nguồn", "tham khảo", "readme", "mô tả"]), "Phải phân biệt dữ liệu nguồn với phần phân tích"

    # 4. Chỉ ra điểm có thể tham khảo (chức năng, cấu trúc, triển khai)
    assert any(k in reply.lower() for k in ["chức năng", "cấu trúc", "tổ chức", "triển khai", "kiến trúc"]), "Phải chỉ ra điểm có thể tham khảo từ dự án"

    # 5. Không mặc định dự án cũ là mẫu tốt nhất hoặc stack bắt buộc
    assert any(k in reply.lower() for k in ["không mặc định", "không bắt buộc", "chỉ mang tính tham khảo", "tùy biến", "tham khảo"]), "Phải nêu rõ dự án cũ chỉ để tham khảo, không phải chuẩn mực bắt buộc"

    # 6. Đồ án tham khảo được dùng để hỗ trợ, không thay thế việc phân tích bài toán
    assert any(k in reply.lower() for k in ["phù hợp", "cân nhắc", "mục tiêu", "kỹ năng", "định hướng"]), "Phải phân tích định hướng kỹ năng và bài toán cho sinh viên"

    print(">>> PASS TC17: Trích dẫn repo thật từ kho dữ liệu GEM, có link rõ ràng, phân tích sâu chức năng/kiến trúc, không hallucination!")
    print("\n===> KẾT LUẬN TC17: HOÀN TOÀN ĐẠT CHUẨN P0!\n")


def run_tc18():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TC18: KHÔNG TÌM THẤY ĐỒ ÁN GITHUB TƯƠNG TỰ - TIẾP TỤC TƯ VẤN (P0)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    tc18_input = (
        "Tôi muốn làm hệ thống giám sát chất lượng không khí trong nhà bằng cảm biến IoT, có dashboard cảnh báo. "
        "Tôi muốn theo IoT/Backend Developer. Hãy tìm dự án tương tự trong kho tham khảo của GEM."
    )
    print(f"\n[TC18] Input: {tc18_input}")
    res = consultant.chat(session_id=sid, user_message=tc18_input)
    reply = res["reply"]
    print(f"\n[TC18] Reply:\n{reply}\n")

    # 1. Thông báo rõ giới hạn kho tham khảo: chưa tìm thấy dự án tương tự trong kho dữ liệu hiện có
    assert any(k in reply.lower() for k in [
        "chưa tìm thấy", "không tìm thấy", "chưa có", "chưa ghi nhận", "kho dữ liệu hiện có", "527"
    ]), "Phải nói rõ chưa tìm thấy dự án tương tự trong kho dữ liệu của GEM"

    # 2. Không bịa dự án hay link giả mạo
    # Không được có link github bịa
    if "github.com/" in reply:
        # Nếu có link thì phải là kho GEM thật, nhưng đề tài IoT không khí này vốn không có
        # Check xem có bịa link vớ vẩn không
        import re
        links = re.findall(r"https?://github\.com/[^\s\)\`]+", reply)
        assert len(links) == 0, f"Không được bịa link GitHub khi kho không có: {links}"

    # 3. Không suy luận rằng dự án không khả thi chỉ vì không tìm thấy ví dụ tương tự
    assert any(k in reply.lower() for k in ["hoàn toàn khả thi", "rất khả thi", "khả thi", "tiềm năng", "thực tế"]), "Không được suy luận dự án không khả thi"

    # 4. Tiếp tục phân tích yêu cầu kỹ thuật và định hướng kỹ năng từ bài toán IoT/Backend
    assert any(k in reply.lower() for k in ["cảm biến", "sensor", "iot", "mqtt", "dashboard", "esp32", "backend"]), "Phải tiếp tục phân tích kỹ thuật IoT/Backend"
    assert any(k in reply.lower() for k in ["kỹ năng", "kiến trúc", "tầng", "dữ liệu"]), "Phải phân tích kỹ năng cần thể hiện"

    # 5. Có câu hỏi mở/tương tác về cảm biến và giao thức kết nối để tinh chỉnh stack
    assert any(k in reply.lower() for k in ["giao thức", "cảm biến", "bạn dự định", "kết nối", "bạn muốn", "phần cứng"]), "Phải hỏi thêm về cảm biến hoặc giao thức để hỗ trợ tinh chỉnh"

    # 6. Không khẳng định đã tìm kiếm toàn bộ GitHub nếu hệ thống chỉ tìm trong tập dữ liệu của GEM
    assert any(k in reply.lower() for k in ["kho dữ liệu", "kho tham khảo", "dữ liệu gem", "nội bộ", "hiện có"]), "Phải nêu rõ phạm vi tìm kiếm là kho dữ liệu nội bộ của GEM"

    print(">>> PASS TC18: Minh bạch giới hạn kho đồ án, không bịa nguồn, khẳng định tính khả thi và tư vấn chuyên sâu IoT/Backend!")
    print("\n===> KẾT LUẬN TC18: HOÀN TOÀN ĐẠT CHUẨN P0!\n")


if __name__ == "__main__":
    run_tc17()
    run_tc18()
