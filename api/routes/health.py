"""
헬스 체크 엔드포인트

API 서버 상태 확인 및 시스템 정보 제공
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from pathlib import Path
import os

from api.schemas import HealthResponse, ErrorResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    헬스 체크
    
    API 서버의 상태를 확인합니다.
    - 서버 상태: healthy/unhealthy
    - 응답 시간: 현재 시간
    - 버전 정보: API 버전
    - 데이터 디렉토리: data/podcasts/ 존재 여부
    """
    try:
        # 데이터 디렉토리 확인
        data_dir = Path("data/podcasts")
        data_dir_exists = data_dir.exists() and data_dir.is_dir()
        
        # JSON 파일 개수 확인
        json_files = list(data_dir.glob("*.json")) if data_dir_exists else []
        
        # 상태 결정
        status = "healthy" if data_dir_exists else "degraded"
        
        return HealthResponse(
            status=status,
            timestamp=datetime.now().isoformat(),
            version="1.0.0"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"헬스 체크 실패: {str(e)}"
        )


@router.get("/health/detailed")
async def detailed_health_check():
    """
    상세 헬스 체크
    
    시스템의 상세 정보를 제공합니다.
    """
    try:
        # 데이터 디렉토리 확인
        data_dir = Path("data/podcasts")
        data_dir_exists = data_dir.exists() and data_dir.is_dir()
        
        # JSON 파일 정보
        json_files = list(data_dir.glob("*.json")) if data_dir_exists else []
        file_count = len(json_files)
        
        # 최신 파일 확인
        latest_file = None
        if json_files:
            latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
        
        # 시스템 정보
        system_info = {
            "data_directory": {
                "path": str(data_dir),
                "exists": data_dir_exists,
                "file_count": file_count,
                "latest_file": latest_file.name if latest_file else None
            },
            "environment": {
                "python_version": os.sys.version,
                "working_directory": os.getcwd(),
                "environment_variables": {
                    "GEMINI_API_KEY": "***" if os.getenv("GEMINI_API_KEY") else None,
                    "GCS_BUCKET_NAME": os.getenv("GCS_BUCKET_NAME"),
                    "TZ": os.getenv("TZ", "UTC")
                }
            },
            "api": {
                "version": "1.0.0",
                "status": "healthy" if data_dir_exists else "degraded",
                "timestamp": datetime.now().isoformat()
            }
        }
        
        return system_info
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"상세 헬스 체크 실패: {str(e)}"
        )
