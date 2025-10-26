"""
에피소드 엔드포인트

팟캐스트 에피소드 조회 API
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pathlib import Path

from api.dependencies import get_repository
from api.schemas import (
    EpisodeResponse, 
    EpisodeDetailResponse, 
    EpisodesListResponse,
    ErrorResponse
)

router = APIRouter()


@router.get("/episodes", response_model=EpisodesListResponse)
async def list_episodes(
    limit: int = Query(20, ge=1, le=100, description="반환할 에피소드 개수"),
    offset: int = Query(0, ge=0, description="건너뛸 에피소드 개수"),
    repo = Depends(get_repository)
):
    """
    에피소드 목록 조회
    
    모든 팟캐스트 에피소드 목록을 날짜 역순으로 반환합니다.
    - 페이지네이션 지원 (limit, offset)
    - 최신 에피소드가 먼저 나옵니다
    """
    try:
        # 모든 에피소드 조회
        all_episodes = repo.find_all()
        total = len(all_episodes)
        
        # 페이지네이션 적용
        paginated_episodes = all_episodes[offset:offset + limit]
        
        # EpisodeResponse로 변환
        episodes = [EpisodeResponse.from_podcast(episode) for episode in paginated_episodes]
        
        return EpisodesListResponse(
            episodes=episodes,
            total=total,
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"에피소드 목록 조회 실패: {str(e)}"
        )


@router.get("/episodes/latest", response_model=EpisodeDetailResponse)
async def get_latest_episode(
    repo = Depends(get_repository)
):
    """
    최신 에피소드 조회
    
    가장 최근에 생성된 에피소드의 상세 정보를 반환합니다.
    """
    try:
        # 최신 에피소드 조회
        latest_episode = repo.find_latest()
        
        if not latest_episode:
            raise HTTPException(
                status_code=404,
                detail="에피소드를 찾을 수 없습니다"
            )
        
        return EpisodeDetailResponse.from_podcast(latest_episode)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"최신 에피소드 조회 실패: {str(e)}"
        )


@router.get("/episodes/{episode_id}", response_model=EpisodeDetailResponse)
async def get_episode(
    episode_id: str,
    repo = Depends(get_repository)
):
    """
    특정 에피소드 조회
    
    ID로 특정 에피소드의 상세 정보를 반환합니다.
    - episode_id: 에피소드 ID (YYYY-MM-DD 형식)
    """
    try:
        # 에피소드 ID 형식 검증
        if not episode_id or len(episode_id) != 10 or episode_id.count('-') != 2:
            raise HTTPException(
                status_code=400,
                detail="잘못된 에피소드 ID 형식입니다. YYYY-MM-DD 형식을 사용하세요."
            )
        
        # 특정 에피소드 조회
        episode = repo.find_by_id(episode_id)
        
        if not episode:
            raise HTTPException(
                status_code=404,
                detail=f"에피소드 '{episode_id}'를 찾을 수 없습니다"
            )
        
        return EpisodeDetailResponse.from_podcast(episode)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"에피소드 조회 실패: {str(e)}"
        )


@router.get("/episodes/date-range")
async def get_episodes_by_date_range(
    start: str = Query(..., description="시작 날짜 (YYYY-MM-DD)"),
    end: str = Query(..., description="종료 날짜 (YYYY-MM-DD)"),
    repo = Depends(get_repository)
):
    """
    날짜 범위로 에피소드 조회
    
    지정된 날짜 범위의 에피소드들을 조회합니다.
    """
    try:
        # 날짜 형식 검증
        for date_str in [start, end]:
            if not date_str or len(date_str) != 10 or date_str.count('-') != 2:
                raise HTTPException(
                    status_code=400,
                    detail=f"잘못된 날짜 형식입니다: {date_str}. YYYY-MM-DD 형식을 사용하세요."
                )
        
        # 날짜 범위 조회
        episodes = repo.find_by_date_range(start, end)
        
        # EpisodeResponse로 변환
        episode_responses = [EpisodeResponse.from_podcast(episode) for episode in episodes]
        
        return {
            "episodes": episode_responses,
            "total": len(episode_responses),
            "date_range": {
                "start": start,
                "end": end
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"날짜 범위 조회 실패: {str(e)}"
        )
