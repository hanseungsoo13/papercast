"""
FastAPI 메인 애플리케이션

PaperCast API 서버의 진입점
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime

from api.routes.health import router as health_router
from api.routes.episodes import router as episodes_router
from api.routes.papers import router as papers_router
from api.schemas import HealthResponse, ErrorResponse


# FastAPI 앱 생성
app = FastAPI(
    title="PaperCast API",
    description="AI 논문 팟캐스트 API - Hugging Face 논문을 자동으로 수집하여 한국어로 요약하고 TTS로 변환한 팟캐스트 제공",
    version="1.0.0",
    contact={
        "name": "PaperCast Team",
        "email": "hanseungsoo13@gmail.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서 모든 오리진 허용
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health_router, prefix="/api", tags=["System"])
app.include_router(episodes_router, prefix="/api", tags=["Episodes"])
app.include_router(papers_router, prefix="/api", tags=["Papers"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """HTTP 예외 처리"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
            details={"status_code": exc.status_code}
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """일반 예외 처리"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="서버 내부 오류가 발생했습니다",
            details={"error_type": exc.__class__.__name__}
        ).dict()
    )


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("🚀 PaperCast API 서버가 시작되었습니다")
    print("📖 API 문서: http://localhost:8000/docs")
    print("🔍 ReDoc 문서: http://localhost:8000/redoc")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    print("🛑 PaperCast API 서버가 종료되었습니다")


# 루트 엔드포인트
@app.get("/", response_model=HealthResponse)
async def root():
    """루트 엔드포인트 - 기본 헬스 체크"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


# 개발 서버 실행
if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
