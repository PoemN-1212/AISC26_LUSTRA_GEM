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


STUDENT_INFERENCE_PROMPT = """Bạn là chuyên gia AI cao cấp về trích xuất thực thể kỹ năng CNTT (IT Skill NER).
Nhiệm vụ: Phân tích kỹ lưỡng văn bản tuyển dụng (Job Description) hoặc mô tả dự án sinh viên (Project README) dưới đây và trích xuất TOÀN BỘ kỹ năng kỹ thuật có trong bài.

CÁC NGUYÊN TẮC BẮT BUỘC (CRITICAL RULES):
1. TÁCH NGUYÊN TỬ TỪNG KỸ NĂNG (ATOMIC EXTRACTION):
   - Mỗi đối tượng JSON CHỈ ĐƯỢC CHỨA ĐÚNG 1 KỸ NĂNG ĐỘC LẬP.
   - TUYỆT ĐỐI CẤM gộp nhiều kỹ năng bằng dấu phẩy, gạch chéo hoặc liên từ.
     * CẤM: {"skill": "Python, Java, C++"} -> BẮT BUỘC TÁCH: {"skill": "Python"}, {"skill": "Java"}, {"skill": "C++"}
     * CẤM: {"skill": "HTML/CSS/JS"} -> BẮT BUỘC TÁCH: {"skill": "HTML"}, {"skill": "CSS"}, {"skill": "JS"}
     * CẤM: {"skill": "Docker và Kubernetes"} -> BẮT BUỘC TÁCH: {"skill": "Docker"}, {"skill": "Kubernetes"}

2. BẰNG CHỨNG XÁC THỰC (EVIDENCE GROUNDING):
   - 'evidence' BẮT BUỘC là từ hoặc cụm từ ngắn gọn (1-5 từ) XUẤT HIỆN NGUYÊN VĂN 100% trong văn bản nguồn.
   - TUYỆT ĐỐI KHÔNG tự bịa đặt, không tóm tắt, không diễn giải lại.

3. RANH GIỚI TỐI THIỂU CÓ NGHĨA (MINIMAL MEANINGFUL SPAN):
   - Chỉ giữ lại tên kỹ năng cốt lõi. Loại bỏ toàn bộ từ ngữ râu ria hoặc từ đệm như:
     "thành thạo", "có kinh nghiệm về", "hiểu biết", "nắm vững", "ưu tiên", "sử dụng", "lập trình"...
     * "Thành thạo lập trình Python" -> evidence: "Python", skill: "Python" (TECHNOLOGY)
     * "Có kinh nghiệm với Docker" -> evidence: "Docker", skill: "Docker" (TECHNOLOGY)

4. HỆ THỐNG NHÃN (CHỈ DÙNG 2 LOẠI):
   - 'TECHNOLOGY': Ngôn ngữ lập trình, framework, thư viện, CSDL, Cloud, DevOps, công cụ kiểm thử, giao thức mạng, kiến trúc hệ thống, và CHỨNG CHỈ CÔNG NGHỆ (ví dụ: Python, React, PostgreSQL, Docker, AWS, TCP/IP, DNS, LAN, WAN, CCNA, MCSA, Azure Fundamentals, OOP, CI/CD, Git, REST API).
   - 'ABILITY': Hành động kỹ thuật cụ thể theo mẫu [Động từ kỹ thuật] + [Đối tượng công nghệ/dữ liệu/hệ thống] (ví dụ: 'phát triển REST API', 'thiết kế cơ sở dữ liệu', 'tối ưu truy vấn SQL', 'viết unit test', 'cấu hình hệ thống mạng', 'quản trị máy chủ'). TUYỆT ĐỐI CẤM các hành động mềm/quản trị chung chung ('phối hợp', 'hướng dẫn nhân viên', 'chăm sóc khách hàng', 'giải quyết sự cố chung').

5. PHẠM VI LOẠI BỎ (NEGATIVE RULES):
   - Cấm lấy: Chức danh công việc (developer, engineer, intern...), Tên công ty/nền tảng (TopCV, Shopee, FPT...), Phúc lợi (lương, thưởng, BHXH, laptop...), Kỹ năng mềm mơ hồ hoặc hành chính (chăm chỉ, giao tiếp tốt, hướng dẫn, phối hợp...).

--- VÍ DỤ MINH HỌA (FEW-SHOT EXAMPLES) ---
[Ví dụ 1]
Văn bản: "Yêu cầu có từ 2 năm kinh nghiệm lập trình Java, thành thạo framework Spring Boot và cơ sở dữ liệu PostgreSQL. Ưu tiên ứng viên có kinh nghiệm xây dựng hệ thống microservices và biết sử dụng Docker/Kubernetes."
Kết quả trích xuất:
[
  {"evidence": "Java", "skill": "Java", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "Spring Boot", "skill": "Spring Boot", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "PostgreSQL", "skill": "PostgreSQL", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "xây dựng hệ thống microservices", "skill": "xây dựng hệ thống microservices", "type": "ABILITY", "context": "preferred"},
  {"evidence": "Docker", "skill": "Docker", "type": "TECHNOLOGY", "context": "preferred"},
  {"evidence": "Kubernetes", "skill": "Kubernetes", "type": "TECHNOLOGY", "context": "preferred"}
]

[Ví dụ 2]
Văn bản: "Dự án quản lý kho hàng sử dụng React/Next.js, TypeScript và CSS. Backend FastAPI kết nối MongoDB. Nhóm đã thực hiện tối ưu hóa truy vấn SQL và thiết lập pipeline CI/CD."
Kết quả trích xuất:
[
  {"evidence": "React", "skill": "React", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "Next.js", "skill": "Next.js", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "TypeScript", "skill": "TypeScript", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "CSS", "skill": "CSS", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "FastAPI", "skill": "FastAPI", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "MongoDB", "skill": "MongoDB", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "tối ưu hóa truy vấn SQL", "skill": "tối ưu hóa truy vấn SQL", "type": "ABILITY", "context": "mentioned"},
  {"evidence": "CI", "skill": "CI", "type": "TECHNOLOGY", "context": "mentioned"},
  {"evidence": "CD", "skill": "CD", "type": "TECHNOLOGY", "context": "mentioned"}
]

[Ví dụ 3 (Văn bản Tiếng Anh - IT Infrastructure & Software)]
Văn bản: "Looking for an IT Engineer to administer Microsoft 365, Azure, Domain, DNS, and VMware servers. Experience with Firewall, LAN/WAN networks, and Active Directory is a plus. Must have experience in troubleshooting network issues and SQL query optimization."
Kết quả trích xuất:
[
  {"evidence": "Microsoft 365", "skill": "Microsoft 365", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "Azure", "skill": "Azure", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "Domain", "skill": "Domain", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "DNS", "skill": "DNS", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "VMware", "skill": "VMware", "type": "TECHNOLOGY", "context": "required"},
  {"evidence": "Firewall", "skill": "Firewall", "type": "TECHNOLOGY", "context": "preferred"},
  {"evidence": "LAN", "skill": "LAN", "type": "TECHNOLOGY", "context": "preferred"},
  {"evidence": "WAN", "skill": "WAN", "type": "TECHNOLOGY", "context": "preferred"},
  {"evidence": "Active Directory", "skill": "Active Directory", "type": "TECHNOLOGY", "context": "preferred"},
  {"evidence": "troubleshooting network issues", "skill": "troubleshooting network issues", "type": "ABILITY", "context": "required"},
  {"evidence": "SQL query optimization", "skill": "SQL query optimization", "type": "ABILITY", "context": "required"}
]

ĐỊNH DẠNG ĐẦU RA BẮT BUỘC:
Trả về DUY NHẤT một JSON array hợp lệ. Không viết thêm bất kỳ lời chào hay giải thích nào.
"""


def build_student_prompt(text: str) -> str:
    """Prompt trích xuất tự nhiên độc lập dùng cho Inference/Benchmark với Few-Shot."""
    return f"{STUDENT_INFERENCE_PROMPT}\n\n--- VĂN BẢN CẦN TRÍCH XUẤT THỰC TẾ ---\n{text}\n\nJSON array kết quả trích xuất:"

