"""
AI Stock Trading System - Backend Server Entry Point
FastAPI 기반 백엔드 서버 실행 스크립트
"""

import uvicorn
from app.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.BACKEND_PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower()
    )
