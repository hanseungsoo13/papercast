"""
API 응답용 Pydantic 스키마

기존 src/models의 모델을 API 응답에 맞게 변환
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from src.models.podcast import Podcast
from src.models.paper import Paper


class EpisodeResponse(BaseModel):
    """에피소드 요약 정보"""
    
    id: str = Field(..., description="에피소드 ID (YYYY-MM-DD 형식)")
    title: str = Field(..., description="에피소드 제목")
    publication_date: str = Field(..., description="발행일 (YYYY-MM-DD)")
    audio_url: str = Field(..., description="오디오 파일 URL")
    duration_seconds: Optional[int] = Field(None, description="오디오 길이 (초)")
    file_size_bytes: Optional[int] = Field(None, description="파일 크기 (바이트)")
    papers_count: int = Field(default=3, description="논문 개수")
    created_at: str = Field(..., description="생성 시간 (ISO 8601)")
    
    @classmethod
    def from_podcast(cls, podcast: Podcast) -> "EpisodeResponse":
        """Podcast 모델에서 EpisodeResponse 생성"""
        return cls(
            id=podcast.id,
            title=podcast.title,
            publication_date=podcast.id,  # ID가 날짜 형식
            audio_url=str(podcast.audio_file_path),
            duration_seconds=podcast.audio_duration,
            file_size_bytes=podcast.audio_size,
            papers_count=len(podcast.papers),
            created_at=podcast.created_at.isoformat()
        )


class EpisodeDetailResponse(EpisodeResponse):
    """에피소드 상세 정보"""
    
    description: Optional[str] = Field(None, description="에피소드 설명")
    script: Optional[str] = Field(None, description="팟캐스트 스크립트")
    papers: List[Paper] = Field(..., description="논문 목록")
    
    @classmethod
    def from_podcast(cls, podcast: Podcast) -> "EpisodeDetailResponse":
        """Podcast 모델에서 EpisodeDetailResponse 생성"""
        base_response = EpisodeResponse.from_podcast(podcast)
        return cls(
            **base_response.dict(),
            description=podcast.description,
            script=podcast.description,  # description을 script로 사용
            papers=podcast.papers
        )


class PaperResponse(BaseModel):
    """논문 정보 (API 응답용)"""
    
    id: str = Field(..., description="논문 ID")
    title: str = Field(..., description="논문 제목")
    authors: List[str] = Field(..., description="저자 목록")
    abstract: Optional[str] = Field(None, description="논문 초록")
    summary: Optional[str] = Field(None, description="AI 생성 요약")
    url: str = Field(..., description="논문 URL")
    arxiv_id: Optional[str] = Field(None, description="ArXiv ID")
    categories: Optional[List[str]] = Field(None, description="논문 카테고리")
    upvotes: int = Field(default=0, description="업보트 수")
    thumbnail_url: Optional[str] = Field(None, description="썸네일 URL")
    published_date: Optional[str] = Field(None, description="게시일")
    collected_at: str = Field(..., description="수집 시간")
    
    @classmethod
    def from_paper(cls, paper: Paper) -> "PaperResponse":
        """Paper 모델에서 PaperResponse 생성"""
        return cls(
            id=paper.id,
            title=paper.title,
            authors=paper.authors,
            abstract=paper.abstract,
            summary=paper.summary,
            url=str(paper.url),
            arxiv_id=paper.arxiv_id,
            categories=paper.categories,
            upvotes=paper.upvotes,
            thumbnail_url=str(paper.thumbnail_url) if paper.thumbnail_url else None,
            published_date=paper.published_date,
            collected_at=paper.collected_at.isoformat()
        )


class EpisodesListResponse(BaseModel):
    """에피소드 목록 응답"""
    
    episodes: List[EpisodeResponse] = Field(..., description="에피소드 목록")
    total: int = Field(..., description="전체 에피소드 개수")
    limit: int = Field(..., description="페이지 크기")
    offset: int = Field(..., description="오프셋")


class HealthResponse(BaseModel):
    """헬스 체크 응답"""
    
    status: str = Field(..., description="서버 상태")
    timestamp: str = Field(..., description="응답 시간")
    version: str = Field(..., description="API 버전")


class ErrorResponse(BaseModel):
    """에러 응답"""
    
    error: str = Field(..., description="에러 타입")
    message: str = Field(..., description="에러 메시지")
    details: Optional[dict] = Field(None, description="추가 세부사항")
