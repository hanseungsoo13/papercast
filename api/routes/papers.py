"""
논문 관련 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from api.schemas import PaperResponse
from api.dependencies import get_repository
from src.models.paper import Paper

router = APIRouter()


@router.get("/papers/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: str,
    repo = Depends(get_repository)
):
    """
    특정 논문 조회
    
    ID로 특정 논문의 상세 정보를 반환합니다.
    """
    try:
        # GCS에서 논문 검색
        paper_data = repo.find_paper_by_id(paper_id)
        
        if not paper_data:
            raise HTTPException(
                status_code=404,
                detail=f"논문 '{paper_id}'를 찾을 수 없습니다"
            )
        
        return PaperResponse.from_paper(paper_data)
        
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
    repo = Depends(get_repository)
):
    """
    논문 목록 조회
    
    모든 에피소드의 논문들을 조회합니다.
    """
    try:
        # GCS에서 모든 논문 조회
        all_papers_data = repo.get_all_papers()
        
        # 페이지네이션 적용
        start_idx = offset
        end_idx = offset + limit
        paginated_papers_data = all_papers_data[start_idx:end_idx]
        
        # PaperResponse로 변환
        papers = [PaperResponse.from_paper(paper_data) for paper_data in paginated_papers_data]
        
        return papers
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"논문 목록 조회 실패: {str(e)}"
        )
