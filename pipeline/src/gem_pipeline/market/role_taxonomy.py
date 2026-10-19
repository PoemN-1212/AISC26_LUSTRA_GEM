"""
Role Taxonomy and Career Classification Patterns.
Dự án GEM (LUSTRA_GEM) - UIT AISC'26

Cấu trúc Phân tầng 2 Cấp (Hierarchical Career Taxonomy):
Cấp 1: NGHỀ (Domain / Lĩnh vực lớn - 12 Nhóm)
Cấp 2: VỊ TRÍ CHUYÊN MÔN (Specific Job Roles - 34 Vị trí)
Kèm biểu thức chính quy (Regex Patterns) tối ưu cho việc nhận diện trên tiêu đề và mô tả tuyển dụng TopCV.
"""

# CẤU TRÚC PHÂN TẦNG: NGHỀ -> VỊ TRÍ CHUYÊN MÔN KÈM PATTERNS NHẬN DIỆN
ROLE_TAXONOMY = {
    "Software Engineering": {
        "Backend Developer": [
            r"\b(backend|back-end|back end|java developer|python developer|nodejs developer|golang developer|php developer|\.net developer|c# developer|ruby developer)\b",
            r"\b(lập trình viên backend|phát triển backend|kỹ sư backend)\b",
        ],
        "Frontend Developer": [
            r"\b(frontend|front-end|front end|reactjs|vuejs|angular|web developer frontend)\b",
            r"\b(lập trình viên frontend|phát triển giao diện|web frontend)\b",
        ],
        "Fullstack Developer": [
            r"\b(fullstack|full-stack|full stack|web developer fullstack)\b",
            r"\b(lập trình viên fullstack|kỹ sư fullstack|toàn diện)\b",
        ],
        "Mobile Developer": [
            r"\b(mobile developer|android|ios|flutter|react native|swift|kotlin mobile|mobile app)\b",
            r"\b(lập trình viên di động|lập trình viên mobile|app developer)\b",
        ],
        "Blockchain Engineer": [
            r"\b(blockchain|web3|solidity|smart contract|crypto developer)\b",
            r"\b(kỹ sư blockchain|lập trình viên blockchain)\b",
        ],
        "Software Engineer (General)": [
            r"\b(software engineer|software developer|lập trình viên phần mềm|kỹ sư phần mềm)\b",
        ],
    },
    "Artificial Intelligence (AI)": {
        "AI Engineer": [
            r"\b(ai engineer|machine learning engineer|ml engineer|deep learning engineer|trí tuệ nhân tạo|học máy)\b",
            r"\b(kỹ sư ai|kỹ sư trí tuệ nhân tạo|kỹ sư học máy)\b",
        ],
        "AI Researcher": [
            r"\b(ai researcher|research scientist|computer vision engineer|nlp engineer|llm engineer|generative ai)\b",
            r"\b(nghiên cứu ai|nghiên cứu trí tuệ nhân tạo)\b",
        ],
        "Data Labeling": [
            r"\b(data labeling|gán nhãn dữ liệu|dán nhãn dữ liệu|chú thích dữ liệu)\b",
        ],
    },
    "Data Science": {
        "Data Engineer": [
            r"\b(data engineer|kỹ sư dữ liệu|etl developer|big data engineer|data pipeline)\b",
        ],
        "Data Analyst": [
            r"\b(data analyst|chuyên viên phân tích dữ liệu|bi analyst|business intelligence|phân tích dữ liệu)\b",
        ],
        "Data Scientist": [
            r"\b(data scientist|khoa học dữ liệu|chuyên viên khoa học dữ liệu)\b",
        ],
    },
    "Software Testing": {
        "Automation Tester": [
            r"\b(automation test|automation tester|kiểm thử tự động|qc automation|qa automation)\b",
        ],
        "Manual Tester": [
            r"\b(manual test|manual tester|kiểm thử thủ công|qc manual)\b",
        ],
        "QA / QC Engineer": [
            r"\b(qa engineer|qc engineer|software tester|tester|quality assurance|chuyên viên kiểm thử|kiểm thử phần mềm)\b",
        ],
        "Game Tester": [
            r"\b(game tester|kiểm thử game)\b",
        ],
        "Process Quality Assurance (PQA)": [
            r"\b(pqa|process quality assurance|đảm bảo chất lượng quy trình)\b",
        ],
    },
    "IT Infrastructure and Operations": {
        "DevOps Engineer": [
            r"\b(devops|devops engineer|sre|site reliability engineer|ci/cd engineer)\b",
        ],
        "Cloud Engineer": [
            r"\b(cloud engineer|aws engineer|azure engineer|gcp engineer|kỹ sư điện toán đám mây)\b",
        ],
        "System Engineer / Admin": [
            r"\b(system engineer|system administrator|sysadmin|quản trị hệ thống|kỹ sư hệ thống|linux admin)\b",
        ],
        "Network Engineer": [
            r"\b(network engineer|kỹ sư mạng|quản trị mạng|network security)\b",
        ],
        "Database Administrator (DBA)": [
            r"\b(dba|database administrator|quản trị cơ sở dữ liệu)\b",
        ],
        "IT Helpdesk / IT Support": [
            r"\b(it helpdesk|it support|kỹ thuật it|hỗ trợ kỹ thuật it|it onsite)\b",
        ],
    },
    "Information Security": {
        "Cyber Security Specialist": [
            r"\b(cyber security|chuyên viên cyber security|an ninh mạng|bảo mật thông tin|soc analyst|chuyên viên bảo mật)\b",
        ],
        "Application Security Engineer": [
            r"\b(application security|appsec|bảo mật ứng dụng|kiểm thử bảo mật|pentest|penetration testing)\b",
        ],
    },
    "Product Management": {
        "Business Analyst (BA)": [
            r"\b(business analyst|ba|phân tích nghiệp vụ|chuyên viên phân tích nghiệp vụ|product analyst)\b",
        ],
        "Product Owner / Product Manager": [
            r"\b(product owner|product manager|quản lý sản phẩm|chủ sở hữu sản phẩm)\b",
        ],
    },
    "Software Design": {
        "UI/UX Designer": [
            r"\b(ui/ux|ui ux|ux/ui|ui designer|ux designer|product designer|thiết kế giao diện)\b",
        ],
        "Graphic & 3D Designer": [
            r"\b(graphic design|thiết kế đồ họa|3d modeler|dựng hình 3d|concept artist|illustration|animation)\b",
        ],
    },
    "IoT / Embedded Engineer": {
        "Embedded Engineer": [
            r"\b(embedded|lập trình nhúng|kỹ sư nhúng|firmware|vi điều khiển|plc|c/c\+\+ embedded)\b",
        ],
        "IoT Engineer": [
            r"\b(iot|internet of things|kỹ sư iot)\b",
        ],
    },
    "Game Development": {
        "Game Developer": [
            r"\b(game developer|lập trình game|unity|unreal engine|game programmer)\b",
        ],
        "AR/VR Developer": [
            r"\b(ar/vr|augmented reality|virtual reality|thực tế ảo)\b",
        ],
    },
    "IT Project Management": {
        "IT Project Manager": [
            r"\b(it project manager|quản lý dự án it|pm it)\b",
        ],
        "Scrum Master": [
            r"\b(scrum master|agile coach)\b",
        ],
        "Bridge Software Engineer (BrSE)": [
            r"\b(brse|bridge se|kỹ sư cầu nối)\b",
        ],
        "IT Comtor": [
            r"\b(it comtor|comtor|thông dịch it)\b",
        ],
    },
    "IT Architecture & Leadership": {
        "Software / Solution Architect": [
            r"\b(solution architect|software architect|system architect|kiến trúc sư giải pháp|kiến trúc sư phần mềm)\b",
        ],
        "Technical Lead / Manager": [
            r"\b(tech lead|technical lead|technical manager|truởng nhóm kỹ thuật|trưởng nhóm lập trình)\b",
        ],
    },
    "Sales IT & Consultant": {
        "Sales IT / IT Consultant": [
            r"\b(sales it|kinh doanh phần mềm|tư vấn it|it consultant|bán hàng phần mềm|kinh doanh hosting)\b",
        ],
    },
}
