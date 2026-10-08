import re
import hashlib
import unicodedata


def normalize_unicode(text: str) -> str:
    """
    Chuẩn hóa chuỗi văn bản tiếng Việt sang dạng dựng sẵn (NFC).
    Tránh lỗi cùng 1 từ nhưng 2 cách mã hóa (dựng sẵn vs tổ hợp).
    """
    if not text:
        return ""
    return unicodedata.normalize("NFC", text)


def clean_job_text(text: str) -> str:
    """
    Làm sạch văn bản mô tả công việc (Job Description) từ TopCV:
    - Chuẩn hóa Unicode tiếng Việt.
    - Xóa URL, email, số điện thoại rác.
    - Chuẩn hóa bullet points đầu dòng về chuẩn '- '.
    - Dọn dẹp khoảng trắng, tab và ngắt dòng dư thừa.
    - Bảo toàn ký tự kỹ thuật: C++, C#, .NET, Node.js, Vue.js...
    """
    if not text:
        return ""

    # 1. Chuẩn hóa Unicode NFC (giữ tiếng Việt có dấu chuẩn)
    text = normalize_unicode(text)

    # 2. Xóa các URL web (http, https, www)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # 3. Xóa địa chỉ email tuyển dụng trong nội dung
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)

    # 4. Chuẩn hóa các ký tự bullet point phong phú về dấu gạch đầu dòng '- '
    bullet_pattern = r'^[ \t]*[•\*\+\▪\►\✔\✓\–\—\>]\s*'
    text = re.sub(bullet_pattern, '- ', text, flags=re.MULTILINE)

    # 5. Xóa các ký tự trang trí không có giá trị thông tin kỹ thuật
    text = re.sub(r'[\u200b\ufeff\xa0]', ' ', text)  # zero-width space, non-breaking space

    # 6. Chuẩn hóa khoảng trắng ngang (nhiều space/tab -> 1 space)
    text = re.sub(r'[ \t]+', ' ', text)

    # 7. Chuẩn hóa các dòng trống liên tiếp (tối đa 2 dấu xuống dòng)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def compute_content_hash(text: str) -> str:
    """Tạo mã băm MD5 để phát hiện nội dung trùng lặp."""
    cleaned = re.sub(r'\s+', '', text.lower())
    return hashlib.md5(cleaned.encode('utf-8')).hexdigest()


def clean_job_record(raw_record: dict) -> dict:
    """
    Làm sạch toàn bộ một bản ghi tuyển dụng.
    Input: dict chứa keys {'id', 'title', 'company', 'full_content', ...}
    Output: dict chứa dữ liệu đã làm sạch và metadata phục vụ LLM extraction.
    """
    raw_content = raw_record.get("full_content", "") or ""
    cleaned_content = clean_job_text(raw_content)

    return {
        "job_id": raw_record.get("id"),
        "title": normalize_unicode(raw_record.get("title", "") or "").strip(),
        "company": normalize_unicode(raw_record.get("company", "") or "").strip(),
        "salary_min": raw_record.get("salary_min"),
        "salary_max": raw_record.get("salary_max"),
        "content_raw_length": len(raw_content),
        "content_clean": cleaned_content,
        "content_clean_length": len(cleaned_content),
        "content_hash": compute_content_hash(cleaned_content),
    }
