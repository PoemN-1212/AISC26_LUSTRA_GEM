import re
import hashlib
import unicodedata


def normalize_unicode(text: str) -> str:
    """Chuẩn hóa chuỗi tiếng Việt sang dạng dựng sẵn (NFC)."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", text)


def clean_project_readme(text: str, max_chars: int = 8000) -> str:
    """
    Làm sạch nội dung README của đồ án sinh viên (GitHub):
    - Chuẩn hóa Unicode NFC.
    - Loại bỏ thẻ HTML (<div...>, <p...>, <img...>).
    - Loại bỏ Markdown shields / badges.
    - Giữ lại nội dung text của link [Tên](url) -> Tên.
    - Xóa URL web trần.
    - Loại bỏ các khối code block lệnh terminal (git clone, npm install...).
    - Giới hạn độ dài hợp lý để tối ưu cho LLM.
    """
    if not text:
        return ""

    # 1. Chuẩn hóa Unicode tiếng Việt
    text = normalize_unicode(text)

    # 2. Xóa các khối code block lệnh terminal/shell dài dòng (thường chỉ là hướng dẫn cài đặt)
    text = re.sub(r'```(?:bash|sh|shell|cmd|powershell|console)[\s\S]*?```', '', text, flags=re.IGNORECASE)

    # 3. Xóa các thẻ HTML
    # Với các thẻ <br>, <br/>, <hr/> thay bằng xuống dòng
    text = re.sub(r'<br\s*/?>|<hr\s*/?>', '\n', text, flags=re.IGNORECASE)
    # Xóa các thẻ HTML còn lại (bao gồm div, p, img, a, span, table...)
    text = re.sub(r'<[^>]+>', ' ', text)

    # 4. Xóa Markdown badges / shields: [![alt](img_url)](link_url) hoặc ![alt](img_url)
    text = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '', text)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)

    # 5. Giữ text của link markdown, bỏ URL: [FastAPI](https://fastapi.tiangolo.com) -> FastAPI
    text = re.sub(r'\[([^\]]+)\]\(https?://[^\)]+\)', r'\1', text)

    # 6. Xóa các URL web trần còn sót lại
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # 7. Chuẩn hóa bullet points về '- '
    bullet_pattern = r'^[ \t]*[•\*\+\▪\►\✔\✓\–\—\>]\s*'
    text = re.sub(bullet_pattern, '- ', text, flags=re.MULTILINE)

    # 8. Xóa các ký tự rác zero-width, non-breaking
    text = re.sub(r'[\u200b\ufeff\xa0]', ' ', text)

    # 9. Chuẩn hóa khoảng trắng ngang
    text = re.sub(r'[ \t]+', ' ', text)

    # 10. Chuẩn hóa xuống dòng (tối đa 2 dấu xuống dòng)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    cleaned = text.strip()

    # 11. Giới hạn độ dài tối đa nếu README quá dài (ưu tiên phần đầu vì chứa tổng quan & công nghệ)
    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars].rsplit('\n', 1)[0] + "\n... [Đã cắt bớt nội dung phía sau]"

    return cleaned


def compute_content_hash(text: str) -> str:
    """Tạo mã băm MD5 phát hiện trùng lặp."""
    cleaned = re.sub(r'\s+', '', text.lower())
    return hashlib.md5(cleaned.encode('utf-8')).hexdigest()


def clean_project_record(raw_record: dict, max_readme_chars: int = 8000) -> dict:
    """
    Làm sạch toàn bộ một bản ghi đồ án GitHub.
    Input: dict chứa {'id', 'repo_name', 'author', 'description', 'readme_content', 'language', ...}
    Output: dict sạch kết hợp description + readme_clean.
    """
    raw_desc = normalize_unicode(raw_record.get("description", "") or "").strip()
    raw_readme = raw_record.get("readme_content", "") or ""
    cleaned_readme = clean_project_readme(raw_readme, max_chars=max_readme_chars)

    # Tạo văn bản tổng hợp dùng cho trích xuất kỹ năng
    combined_parts = []
    if raw_desc and raw_desc.lower() != "none" and raw_desc.lower() != "null":
        combined_parts.append(f"Mô tả đồ án: {raw_desc}")
    if cleaned_readme:
        combined_parts.append(cleaned_readme)

    combined_text = "\n\n".join(combined_parts)

    return {
        "project_id": raw_record.get("id"),
        "repo_name": raw_record.get("repo_name", ""),
        "author": raw_record.get("author", ""),
        "language": raw_record.get("language", ""),
        "description_raw": raw_desc,
        "readme_raw_length": len(raw_readme),
        "readme_clean": cleaned_readme,
        "combined_clean_text": combined_text,
        "combined_clean_length": len(combined_text),
        "content_hash": compute_content_hash(combined_text),
    }
