"""
FastAPI 의존성 주입 설정

Repository 및 설정 의존성을 관리
"""

from pathlib import Path
from typing import Optional
from functools import lru_cache

from api.repository import PodcastRepository, CachedPodcastRepository


@lru_cache()
def get_repository() -> PodcastRepository:
    """
    Repository 의존성 주입
    
    싱글톤 패턴으로 Repository 인스턴스를 관리합니다.
    """
    return CachedPodcastRepository(data_dir=Path("data/podcasts"))


@lru_cache()
def get_config() -> dict:
    """
    설정 의존성 주입
    
    애플리케이션 설정을 반환합니다.
    """
    return {
        "data_dir": "data/podcasts",
        "cache_ttl": 3600,  # 1시간
        "max_papers_per_episode": 3,
        "api_version": "1.0.0",
        "cors_origins": [
            "http://localhost:3000",
            "http://localhost:8080", 
            "http://localhost:8000",
            "https://papercast.vercel.app",
            "https://*.github.io"
        ]
    }


def get_pagination_params(
    limit: int = 20,
    offset: int = 0
) -> dict:
    """
    페이지네이션 파라미터 의존성
    
    페이지네이션 설정을 검증하고 반환합니다.
    """
    # 제한값 검증
    if limit < 1:
        limit = 1
    elif limit > 100:
        limit = 100
    
    if offset < 0:
        offset = 0
    
    return {
        "limit": limit,
        "offset": offset
    }


def get_episode_id_validation(episode_id: str) -> str:
    """
    에피소드 ID 검증 의존성
    
    에피소드 ID 형식을 검증합니다.
    """
    if not episode_id:
        raise ValueError("에피소드 ID가 필요합니다")
    
    if len(episode_id) != 10 or episode_id.count('-') != 2:
        raise ValueError("잘못된 에피소드 ID 형식입니다. YYYY-MM-DD 형식을 사용하세요.")
    
    return episode_id


def get_date_range_validation(start: str, end: str) -> dict:
    """
    날짜 범위 검증 의존성
    
    날짜 범위 파라미터를 검증합니다.
    """
    for date_str, param_name in [(start, "start"), (end, "end")]:
        if not date_str:
            raise ValueError(f"{param_name} 날짜가 필요합니다")
        
        if len(date_str) != 10 or date_str.count('-') != 2:
            raise ValueError(f"잘못된 {param_name} 날짜 형식입니다. YYYY-MM-DD 형식을 사용하세요.")
    
    # 날짜 순서 검증
    if start > end:
        raise ValueError("시작 날짜는 종료 날짜보다 이전이어야 합니다")
    
    return {
        "start": start,
        "end": end
    }
