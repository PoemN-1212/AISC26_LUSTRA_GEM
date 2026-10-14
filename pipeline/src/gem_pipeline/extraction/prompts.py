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
2. MINIMAL MEANINGFUL SPAN (RANH GIỚI HẸP NHẤT): 
   - Tuyệt đối chỉ lấy đúng tên công nghệ ngắn gọn nhất, không lấy kèm từ ngữ râu ria hoặc hành động chung chung.
   - Bỏ hoàn toàn: "có kinh nghiệm về", "thành thạo", "hiểu biết về", "nắm vững", "ưu tiên", "sử dụng", "lập trình", "proficient in", "experience with"...
   - Ví dụ: "Thành thạo lập trình Python" -> evidence: "Python" (TECHNOLOGY), cấm lấy "lập trình Python".
   - Ví dụ: "Biết sử dụng Docker" -> evidence: "Docker" (TECHNOLOGY), cấm lấy "sử dụng Docker".
   - Ví dụ: "Có kinh nghiệm phát triển REST API" -> evidence: "phát triển REST API" (ABILITY).
3. QUY TẮC TÁCH KỸ NĂNG GHÉP:
   - Khi văn bản có gạch chéo hoặc liệt kê như "CI/CD", "React/Next.js", "HTML/CSS", "Docker/Kubernetes", PHẢI tách thành các bản ghi riêng biệt:
     + "CI" và "CD"
     + "React" và "Next.js"
     + "HTML" và "CSS"
     + "Docker" và "Kubernetes"
   - Không gộp nhiều kỹ năng vào một bản ghi ("React, Node.js và PostgreSQL" -> 3 bản ghi riêng biệt).
4. TUYỆT ĐỐI BỎ QUA (NEGATIVE RULES):
   - Chức danh công việc (Software Engineer, Backend Developer, Tech Lead, Thực tập sinh...)
   - Tên công ty / nền tảng (TopCV, ITviec, FPT, Shopee, Google...)
   - Chế độ, phúc lợi (Lương, thưởng, BHXH, laptop, cơm trưa, du lịch...)
   - Kỹ năng mềm chung chung (chăm chỉ, hòa đồng, chịu áp lực, giao tiếp tốt, tiếng Anh giao tiếp...).
5. TUYỆT ĐỐI KHÔNG BỊA ĐẶT (KHÔNG HALLUCINATION): Chỉ trích xuất những gì có trong văn bản gốc.

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
        "input": "Yêu cầu ứng viên có từ 2 năm kinh nghiệm lập trình Java, thành thạo framework Spring Boot và cơ sở dữ liệu PostgreSQL. Ưu tiên ứng viên có kinh nghiệm xây dựng hệ thống microservices và biết sử dụng Docker, Kubernetes.",
        "output": [
            {"evidence": "Java", "skill": "Java", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "Spring Boot", "skill": "Spring Boot", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "PostgreSQL", "skill": "PostgreSQL", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "xây dựng hệ thống microservices", "skill": "xây dựng hệ thống microservices", "type": "ABILITY", "context": "preferred"},
            {"evidence": "Docker", "skill": "Docker", "type": "TECHNOLOGY", "context": "preferred"},
            {"evidence": "Kubernetes", "skill": "Kubernetes", "type": "TECHNOLOGY", "context": "preferred"}
        ]
    },
    {
        "input": "Dự án quản lý kho hàng thương mại điện tử sử dụng React/Next.js, TypeScript và TailwindCSS. Backend được viết bằng FastAPI kết nối MongoDB. Nhóm đã thực hiện tối ưu hóa truy vấn cơ sở dữ liệu và triển khai pipeline CI/CD qua GitHub Actions.",
        "output": [
            {"evidence": "React", "skill": "React", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "Next.js", "skill": "Next.js", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "TypeScript", "skill": "TypeScript", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "TailwindCSS", "skill": "TailwindCSS", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "FastAPI", "skill": "FastAPI", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "MongoDB", "skill": "MongoDB", "type": "TECHNOLOGY", "context": "required"},
            {"evidence": "tối ưu hóa truy vấn cơ sở dữ liệu", "skill": "tối ưu hóa truy vấn cơ sở dữ liệu", "type": "ABILITY", "context": "mentioned"},
            {"evidence": "CI", "skill": "CI", "type": "TECHNOLOGY", "context": "mentioned"},
            {"evidence": "CD", "skill": "CD", "type": "TECHNOLOGY", "context": "mentioned"},
            {"evidence": "GitHub Actions", "skill": "GitHub Actions", "type": "TECHNOLOGY", "context": "mentioned"}
        ]
    }
]


def build_extraction_prompt(text: str, use_few_shot: bool = True) -> str:
    """Tạo full prompt chuẩn Guideline kèm few-shot examples (Teacher Annotation Prompt)."""
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


STUDENT_INFERENCE_PROMPT = """Bạn là trợ lý AI chuyên trích xuất thực thể kỹ năng CNTT (IT Skill NER) từ văn bản tuyển dụng và đồ án sinh viên.
Nhiệm vụ: Trích xuất chính xác tất cả các kỹ năng kỹ thuật có trong văn bản dưới đây.

NGUYÊN TẮC TRÍCH XUẤT CỐT LÕI:
1. TÁCH ĐỘC LẬP TỪNG THỰC THỂ (ATOMIC EXTRACTION):
   - Khi gặp một danh sách nhiều công nghệ ngăn cách bởi dấu phẩy, gạch chéo hoặc liên từ (ví dụ: 'Python, Golang, Rust', 'LAN/WAN', 'Docker và Kubernetes'), PHẢI tách thành từng thực thể độc lập riêng biệt, tuyệt đối không gộp thành một chuỗi dài.
2. RANH GIỚI TỐI THIỂU CÓ NGHĨA (MINIMAL SPAN):
   - Bỏ hoàn toàn các từ đệm như: 'thành thạo', 'nắm vững', 'kinh nghiệm với', 'có khả năng'. Giữ đúng tên chuẩn của kỹ năng (ví dụ: 'Python', '.NET', 'REST API').
3. HƯỚNG DẪN PHÂN LOẠI CHUẨN XÁC:
   - 'TECHNOLOGY': Ưu tiên cao nhất cho tên ngôn ngữ lập trình, framework, thư viện, CSDL, Cloud, DevOps, công cụ kiểm thử, giao thức mạng, kiến trúc phần mềm (ví dụ: Python, React, PostgreSQL, Docker, AWS, OOP, CI/CD).
   - 'ABILITY': Chỉ trích xuất các hành động kỹ thuật cụ thể theo mẫu [Động từ kỹ thuật] + [Đối tượng công nghệ] (ví dụ: 'phát triển REST API', 'thiết kế cơ sở dữ liệu', 'tối ưu truy vấn SQL'). TUYỆT ĐỐI KHÔNG trích xuất nhiệm vụ/trách nhiệm chung chung (như 'báo cáo tiến độ', 'họp nhóm', 'giao tiếp khách hàng').

ĐỊNH DẠNG ĐẦU RA DUY NHẤT:
Trả về DUY NHẤT một JSON array hợp lệ:
[
  {
    "evidence": "đoạn trích dẫn nguyên văn từ văn bản",
    "skill": "Tên kỹ năng chuẩn",
    "type": "TECHNOLOGY" hoặc "ABILITY",
    "context": "required" hoặc "preferred" hoặc "mentioned"
  }
]
"""


def build_student_prompt(text: str) -> str:
    """Prompt trích xuất tự nhiên độc lập dùng cho Inference/Benchmark."""
    return f"{STUDENT_INFERENCE_PROMPT}\n\n--- VĂN BẢN CẦN TRÍCH XUẤT ---\n{text}"
