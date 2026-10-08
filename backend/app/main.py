from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="GEM API (LUSTRA_GEM)",
    description="Hệ thống phân tích kỹ năng thị trường IT, đo khoảng cách kỹ năng sinh viên và đề xuất lộ trình công nghệ (AISC 2026 - UIT)",
    version="0.1.0",
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def root():
    return {
        "project": "GEM (LUSTRA_GEM)",
        "event": "AISC 2026",
        "status": "online",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}
