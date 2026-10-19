import sys
import os
import uuid

# Đảm bảo import được gem_pipeline
sys.path.append(os.path.join(os.getcwd(), "pipeline", "src"))

from gem_pipeline.recommendation.consultant import IdeationConsultant
from gem_pipeline.vector_store.qdrant_service import QdrantVectorService


def run_generalization_found():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TỔNG QUÁT HÓA - CHỦ ĐỀ CÓ ĐỒ ÁN TRONG KHO (Hệ thống quản lý khóa học / E-learning)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    user_input = (
        "Tôi muốn xây dựng hệ thống website học trực tuyến / quản lý khóa học e-learning bằng React và Spring Boot. "
        "GEM có đồ án nào tương tự trong kho tham khảo không? Hãy gợi ý những tính năng và kiến trúc tôi nên học hỏi."
    )
    print(f"\n[Scenario A] Input: {user_input}")
    res = consultant.chat(session_id=sid, user_message=user_input)
    reply = res["reply"]
    print(f"\n[Scenario A] Reply:\n{reply}\n")

    # Kiểm tra tính trung thực: lấy từ kho thật
    qdrant = QdrantVectorService()
    real_projects = qdrant.search_similar_projects("quản lý khóa học e-learning React Spring Boot", limit=5)
    real_repo_names = [p["repo_name"].lower() for p in real_projects]
    print(f"[Scenario A Verification] Candidate repos in DB: {[p['repo_name'] for p in real_projects]}")

    has_real_repo = any(r_name in reply.lower() for r_name in real_repo_names)
    assert has_real_repo, f"Phản hồi phải chứa repository thật từ kho GEM ({real_repo_names})"
    assert "github.com" in reply.lower() or "repository" in reply.lower(), "Phải có dẫn chứng cụ thể"
    assert any(k in reply.lower() for k in ["chức năng", "kiến trúc", "tham khảo", "bài toán"]), "Phải phân tích định hướng"

    print(">>> PASS Scenario A: Trích xuất chính xác repo thật, phân tích đa chiều cho chủ đề E-learning!")


def run_generalization_not_found():
    print("\n" + "=" * 80)
    print("KIỂM THỬ TỔNG QUÁT HÓA - CHỦ ĐỀ KHÔNG CÓ TRONG KHO (Hệ thống điều khiển tàu ngầm không người lái AUV bằng FPGA)")
    print("=" * 80)
    consultant = IdeationConsultant()
    sid = str(uuid.uuid4())

    user_input = (
        "Tôi muốn nghiên cứu thiết kế hệ thống điều khiển tàu ngầm tự hành dưới nước (Autonomous Underwater Vehicle - AUV) "
        "sử dụng chip FPGA và giao tiếp sóng âm thủy âm. Hãy tìm các repository tương tự trong kho của GEM để tôi tham khảo."
    )
    print(f"\n[Scenario B] Input: {user_input}")
    res = consultant.chat(session_id=sid, user_message=user_input)
    reply = res["reply"]
    print(f"\n[Scenario B] Reply:\n{reply}\n")

    # Kiểm tra phản hồi:
    # 1. Phải thông báo trung thực là chưa tìm thấy trong kho
    assert any(k in reply.lower() for k in [
        "chưa tìm thấy", "không tìm thấy", "chưa có", "chưa ghi nhận", "kho dữ liệu hiện có", "527"
    ]), "Phải báo rõ chưa có trong kho 527 đồ án của GEM"

    # 2. Không được bịa link github
    import re
    links = re.findall(r"https?://github\.com/[^\s\)\`]+", reply)
    assert len(links) == 0, f"Không được bịa link GitHub khi không có: {links}"

    # 3. Phải khẳng định đề tài khả thi / thú vị và tiếp tục tư vấn chuyên môn FPGA / AUV
    assert any(k in reply.lower() for k in ["khả thi", "thực tế", "tiềm năng", "thách thức", "hướng đi"]), "Không được suy luận dự án không khả thi"
    assert any(k in reply.lower() for k in ["fpga", "phần cứng", "cảm biến", "giao tiếp", "kiến trúc", "nhúng"]), "Phải tư vấn kiến trúc kỹ thuật tương ứng"

    print(">>> PASS Scenario B: Minh bạch không bịa repo cho chủ đề chuyên biệt FPGA/AUV, tư vấn kỹ thuật có chiều sâu!")


if __name__ == "__main__":
    run_generalization_found()
    run_generalization_not_found()
