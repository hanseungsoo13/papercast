"""
논문 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from api.schemas import PaperResponse
from api.dependencies import get_repository
from api.repository import PodcastRepository
from src.models.paper import Paper

router = APIRouter()


@router.get("/papers/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: str,
    repo: PodcastRepository = Depends(get_repository)
):
    """
    특정 논문 조회
    
    ID로 특정 논문의 상세 정보를 반환합니다.
    """
    try:
        # 모든 에피소드에서 논문 검색
        episodes = repo.find_all()
        
        for episode in episodes:
            for paper in episode.papers:
                if paper.id == paper_id:
                    return PaperResponse.from_paper(paper)
        
        # 논문을 찾지 못한 경우
        raise HTTPException(
            status_code=404,
            detail=f"논문 '{paper_id}'를 찾을 수 없습니다"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"논문 조회 실패: {str(e)}"
        )


@router.get("/papers", response_model=List[PaperResponse])
async def get_papers(
    limit: int = 20,
    offset: int = 0,
    repo: PodcastRepository = Depends(get_repository)
):
    """
    논문 목록 조회
    
    모든 에피소드의 논문들을 조회합니다.
    """
    try:
        episodes = repo.find_all()
        all_papers = []
        
        for episode in episodes:
            for paper in episode.papers:
                all_papers.append(PaperResponse.from_paper(paper))
        
        # 페이지네이션 적용
        start_idx = offset
        end_idx = offset + limit
        paginated_papers = all_papers[start_idx:end_idx]
        
        return paginated_papers
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"논문 목록 조회 실패: {str(e)}"
        )
