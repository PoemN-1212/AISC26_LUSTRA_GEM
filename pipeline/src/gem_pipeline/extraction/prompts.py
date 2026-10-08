"""
GEM Extraction Prompts & Few-Shot Templates
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
Tuân thủ GEM Annotation Guideline v1.0
"""

SYSTEM_PROMPT_EXTRACTION = """Bạn là chuyên gia phân tích kỹ năng công nghệ IT thuộc hệ thống GEM (UIT AISC'26).
Nhiệm vụ: Trích xuất chính xác toàn bộ kỹ năng công nghệ và năng lực kỹ thuật từ văn bản (Job Description hoặc Project README).

HỆ THỐNG NHÃN (CHỈ DÙNG 2 NHÃN DUY NHẤT):
1. 'TECHNOLOGY': Ngôn ngữ lập trình, framework, thư viện, cơ sở dữ liệu, cloud, công cụ DevOps, giao thức, tiêu chuẩn API.
   Ví dụ: Python, TypeScript, React, FastAPI, Spring Boot, PostgreSQL, MongoDB, Redis, Docker, Kubernetes, AWS, Git, REST API, GraphQL.
2. 'ABILITY': Năng lực hoặc hành động kỹ thuật cụ thể mà ứng viên/sinh viên thực hiện ([Động từ kỹ thuật] + [Đối tượng kỹ thuật]).
   Ví dụ: phát triển REST API, thiết kế cơ sở dữ liệu, tối ưu hóa truy vấn SQL, viết unit test, xây dựng kiến trúc microservices, debug hệ thống production, huấn luyện mô hình học máy.

QUY TẮC BẮT BUỘC (CRITICAL RULES):
1. EVIDENCE CHÍNH XÁC: 'evidence' PHẢI là chuỗi con xuất hiện nguyên văn 100% trong văn bản gốc.
2. MINIMAL MEANINGFUL SPAN: Cắt bỏ hoàn toàn các từ đệm, từ filler:
   - Bỏ: "có kinh nghiệm về", "thành thạo", "hiểu biết về", "nắm vững", "ưu tiên", "proficient in", "experience with"...
   - Ví dụ: "Thành thạo lập trình Python" -> evidence: "Python" (TECHNOLOGY).
   - Ví dụ: "Có kinh nghiệm phát triển REST API" -> evidence: "phát triển REST API" (ABILITY).
3. TÁCH RỜI KỸ NĂNG: Không gom nhiều kỹ năng vào một bản ghi ("React, Node.js và PostgreSQL" -> 3 bản ghi riêng biệt).
4. TUYỆT ĐỐI BỎ QUA (NEGATIVE RULES):
   - Chức danh công việc (Software Engineer, Backend Developer, Tech Lead...)
   - Tên công ty / nền tảng (TopCV, FPT, Shopee, Google...)
   - Chế độ, phúc lợi (Lương, thưởng, BHXH, laptop, cơm trưa...)
   - Kỹ năng mềm chung chung (chăm chỉ, hòa đồng, chịu áp lực, giao tiếp tốt...).
5. TUYỆT ĐỐI KHÔNG BỊA ĐẶT (KHÔNG HALLUCINATION): Chỉ trích xuất những gì có trong văn bản.

ĐỊNH DẠNG ĐẦU RA:
Trả về DUY NHẤT 1 JSON array hợp lệ. Không thêm chữ giải thích bên ngoài.
[
  {
    "evidence": "chuỗi con nguyên văn",
    "skill": "Tên kỹ năng",
    "type": "TECHNOLOGY" hoặc "ABILITY",
    "context": "required" hoặc "preferred" hoặc "mentioned"
  }
]
"""

FEW_SHOT_EXAMPLES = [
    {
        "input": "Yêu cầu ứng viên có từ 2 năm kinh nghiệm lập trình Java, thành thạo framework Spring Boot và cơ sở dữ liệu PostgreSQL. Ưu tiên ứng viên có kinh nghiệm xây dựng hệ thống microservices và biết sử dụng Docker.",
        "output": [
            {"evidence": "Java", "skill": "Java", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "Spring Boot", "skill": "Spring Boot", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "PostgreSQL", "skill": "PostgreSQL", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "xây dựng hệ thống microservices", "skill": "xây dựng hệ thống microservices", "type": "ABILITY", "context": "preferred"},
            {"evidence": "Docker", "skill": "Docker", "type": "TECHNOLOGY", "context": "preferred"}
        ]
    },
    {
        "input": "Dự án quản lý kho hàng thương mại điện tử sử dụng React 18, TypeScript và TailwindCSS. Backend được viết bằng FastAPI kết nối MongoDB. Nhóm đã thực hiện tối ưu hóa truy vấn cơ sở dữ liệu và triển khai CI/CD qua GitHub Actions.",
        "output": [
            {"evidence": "React", "skill": "React", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "TypeScript", "skill": "TypeScript", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "TailwindCSS", "skill": "TailwindCSS", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "FastAPI", "skill": "FastAPI", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "MongoDB", "skill": "MongoDB", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "tối ưu hóa truy vấn cơ sở dữ liệu", "skill": "tối ưu hóa truy vấn cơ sở dữ liệu", "type": "ABILITY", "context": "mentioned"},
            {"evidence": "triển khai CI/CD", "skill": "triển khai CI/CD", "type": "ABILITY", "context": "mentioned"},
            {"evidence": "GitHub Actions", "skill": "GitHub Actions", "type": "TECHNOLOGY", "context": "mentioned"}
        ]
    }
]


def build_extraction_prompt(text: str, use_few_shot: bool = True) -> str:
    """Tạo full prompt kèm few-shot examples nếu được yêu cầu."""
    prompt_parts = [SYSTEM_PROMPT_EXTRACTION]

    if use_few_shot:
        prompt_parts.append("\n--- VÍ DỤ MINH HỌA (FEW-SHOT EXAMPLES) ---")
        for i, eg in enumerate(FEW_SHOT_EXAMPLES, 1):
            import json
            prompt_parts.append(f"\n[Ví dụ {i}]")
            prompt_parts.append(f"Văn bản: {eg['input']}")
            prompt_parts.append(f"Kết quả trích xuất:\n{json.dumps(eg['output'], ensure_ascii=False, indent=2)}")

    prompt_parts.append(f"\n--- VĂN BẢN CẦN PHÂN TÍCH THỰC TẾ ---\n{text}")
    return "\n".join(prompt_parts)
