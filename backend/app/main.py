"""
GEM Backend API (LUSTRA_GEM) - UIT AISC'26
Cung cấp REST API cho Hệ thống Cố vấn Đồ án & Định hướng Nghề nghiệp IT.
"""

import sys
import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel

# Thêm pipeline/src vào sys.path để import các module GEM
pipeline_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "pipeline", "src"))
if pipeline_src not in sys.path:
    sys.path.insert(0, pipeline_src)

from gem_pipeline.market.role_profiler import RoleSkillProfiler
from gem_pipeline.recommendation.consultant import IdeationConsultant

app = FastAPI(
    title="GEM - Nền tảng AI định hướng và khớp nối năng lực Đồ án CNTT với xu hướng tuyển dụng",
    description="Hệ thống AI Cố vấn Ý tưởng Đồ án, Phân tích Thị trường IT và Khớp nối Tuyển dụng (AISC 2026 - UIT)",
    version="1.0.0",
)

# Cấu hình CORS cho Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cấu hình Mount Thư mục Tĩnh Frontend (Vanilla UI)
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "static"))
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Khởi tạo singleton services
profiler = RoleSkillProfiler()
consultant = IdeationConsultant()


# Pydantic Request Models
class IdeaAnalysisRequest(BaseModel):
    idea_text: str


class BlueprintRequest(BaseModel):
    idea_text: str
    target_role: Optional[str] = "Backend Developer"
    time_months: Optional[int] = 3
    preferred_tech: Optional[List[str]] = []


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


@app.get("/", tags=["UI & Web App"])
def root():
    """Phục vụ Giao diện Người dùng Web App (Single Page Application)."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "project": "GEM (LUSTRA_GEM)",
        "event": "AISC 2026 - UIT",
        "description": "AI Ideation & Career Co-Pilot for IT Students",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/api/info", tags=["Health"])
def api_info():
    return {
        "project": "GEM (LUSTRA_GEM)",
        "event": "AISC 2026 - UIT",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


# ==========================================
# CÁC ENDPOINT CỐ VẤN Ý TƯỞNG & ĐỒNG HÀNH (CO-PILOT)
# ==========================================


@app.post("/api/consultation/analyze-idea", tags=["Consultation"])
def analyze_idea(req: IdeaAnalysisRequest):
    """
    Trụ cột 1: Phân tích ý tưởng sơ khởi, nhận diện miền bài toán,
    các chức năng cần có và gợi ý 2-3 hướng nghề nghiệp phù hợp.
    """
    if not req.idea_text.strip():
        raise HTTPException(status_code=400, detail="Vui lòng nhập mô tả ý tưởng đồ án.")
    return consultant.analyze_idea(req.idea_text)


@app.post("/api/consultation/blueprint", tags=["Consultation"])
def generate_blueprint(req: BlueprintRequest):
    """
    Trụ cột 2 & 3: Đề xuất Kiến trúc Công nghệ 3 Lớp:
    - Lớp 1: Core Foundation (Chạy được sản phẩm)
    - Lớp 2: Career Boosters (3-5 kỹ năng thị trường TopCV)
    - Lớp 3: Personal Extension (Module hướng nghiệp, e.g. AI/Data)
    Kèm Lộ trình theo thời gian và Tham khảo đồ án cũ từ Qdrant.
    """
    if not req.idea_text.strip():
        raise HTTPException(status_code=400, detail="Vui lòng nhập mô tả ý tưởng đồ án.")
    return consultant.generate_blueprint(
        idea_text=req.idea_text,
        target_role=req.target_role,
        time_months=req.time_months or 3,
        preferred_tech=req.preferred_tech or [],
    )


@app.post("/api/consultation/chat", tags=["Consultation"])
def chat_copilot(req: ChatRequest):
    """
    Trụ cột 4: Hội thoại Đa lượt (Stateful Multi-turn Co-Pilot).
    Cho phép sinh viên chat tiếp để:
    - Đổi mục tiêu nghề nghiệp (e.g. chuyển sang AI Engineer)
    - Điều chỉnh quỹ thời gian / công nghệ ưu tiên
    - Yêu cầu giải thích đề xuất và cập nhật lộ trình.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Nội dung tin nhắn không được để trống.")
    return consultant.chat(session_id=req.session_id, user_message=req.message)


# ==========================================
# CÁC ENDPOINT THỊ TRƯỜNG LAO ĐỘNG (TOPCV INSIGHTS)
# ==========================================


@app.get("/api/market/roles", tags=["Market Data"])
def get_roles_summary():
    """Lấy danh sách các nhóm vị trí việc làm IT và tỷ trọng trong kho JD TopCV."""
    return profiler.get_all_role_summaries()


@app.get("/api/market/role-profile/{role_name}", tags=["Market Data"])
def get_role_profile(role_name: str):
    """Lấy Hồ sơ Kỹ năng (Core Must-Have vs Differentiating Boosters) của một vị trí."""
    return profiler.get_role_skill_profile(role_name)


@app.post("/api/market/match-jds", tags=["Market Data"])
def match_jds(req: IdeaAnalysisRequest):
    """Tìm kiếm ngữ nghĩa các tin tuyển dụng thực tế TopCV phù hợp nhất với ý tưởng đồ án qua Qdrant."""
    if not req.idea_text.strip():
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp mô tả ý tưởng đồ án.")
    return consultant.vector_service.search_relevant_jds(req.idea_text, limit=6)
