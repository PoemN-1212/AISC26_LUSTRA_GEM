import os
import pandas as pd
from sqlalchemy import create_engine
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# 1. Cấu hình Database
CLOUD_DB_URL = os.getenv("CLOUD_DB_URL")
if CLOUD_DB_URL and CLOUD_DB_URL.startswith("postgresql://"):
    CLOUD_DB_URL = CLOUD_DB_URL.replace("postgresql://", "postgresql+psycopg2://")
    
engine = create_engine(CLOUD_DB_URL)

# 2. Cấu hình API Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 3. Lấy 80 JD ngẫu nhiên
print("Đang kết nối Database lấy 80 JD...")
query = """
    SELECT id, title, full_content 
    FROM raw_job_postings 
    WHERE LENGTH(full_content) > 500
    ORDER BY RANDOM() 
    LIMIT 80;
"""
df_sample = pd.read_sql(query, engine)
print(f"✅ Đã lấy thành công {len(df_sample)} JD.")

SYSTEM_PROMPT = """
Bạn là chuyên gia phân tích dữ liệu tuyển dụng IT. 
Trích xuất các kỹ năng công nghệ (Skill/Technology) từ văn bản Job Description (JD).
QUY TẮC:
1. Chỉ trích xuất kỹ năng CÓ THẬT trong văn bản. Không tự suy luận thêm.
2. 'evidence': Trích dẫn chính xác cụm từ chứa kỹ năng đó trong JD.
3. 'context': Phân loại là 'required' (bắt buộc), 'preferred' (ưu tiên), hoặc 'mentioned' (chỉ nhắc đến).
4. CHỈ trả về JSON array.
Định dạng bắt buộc: [{"skill": "Python", "evidence": "Experience with Python", "context": "required"}]
"""

# Hàm trích xuất có trang bị cơ chế tự động thử lại (Retry)
def extract_skills(jd_text, max_retries=3):
    full_prompt = f"{SYSTEM_PROMPT}\n\n--- VĂN BẢN JD ---\n{jd_text}"
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
            )
            return response.text
        
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "503" in error_msg:
                # Nếu bị chặn hoặc server quá tải, lùi thời gian chờ (15s, 30s...)
                wait_time = 15 * (attempt + 1)
                print(f"  ⏳ Gặp chặn API (Lần thử {attempt + 1}/{max_retries}). Tạm nghỉ {wait_time}s rồi gọi lại...")
                time.sleep(wait_time)
            else:
                print(f"  ❌ Lỗi API không xác định: {error_msg}")
                break
                
    return "[]" # Nếu thử 3 lần vẫn thất bại thì trả về mảng rỗng để code chạy tiếp

# 5. Xử lý qua AI
results = []
for index, row in df_sample.iterrows():
    print(f"Đang phân tích JD {index + 1}/80: {row['title']}")
    
    raw_json = extract_skills(row['full_content'])
    
    try:
        skills_extracted = json.loads(raw_json)
        for item in skills_extracted:
            if isinstance(item, dict):
                results.append({
                    "jd_id": row['id'],
                    "job_title": row['title'],
                    "skill": item.get("skill", ""),
                    "evidence": item.get("evidence", ""),
                    "context": item.get("context", ""),
                    "human_verify": "",
                    "note": ""
                })
    except json.JSONDecodeError:
        print(f"⚠ JD {row['id']} bị lỗi format JSON, bỏ qua.")
        
    # BẮT BUỘC NGHỈ 15 GIÂY GIỮA MỖI JD:
    # Google giới hạn 5 request/phút -> 60s / 5 = 12s. Ta nghỉ 15s cho chắc ăn.
    time.sleep(15)

# 6. Xuất file
if results:
    df_results = pd.DataFrame(results)
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    output_path = os.path.join(data_dir, "GEM_Golden_Set_Draft.xlsx")
    df_results.to_excel(output_path, index=False)
    print(f"\n🎉 HOÀN THÀNH! Đã lưu file tại: {output_path}")
else:
    print("\n❌ Không trích xuất được dữ liệu nào.")