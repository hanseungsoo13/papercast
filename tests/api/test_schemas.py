"""
API 스키마 테스트

Pydantic 스키마의 변환 및 검증 테스트
"""

from datetime import datetime
import pytest
from src.models.podcast import Podcast
from src.models.paper import Paper
from api.schemas import (
    EpisodeResponse, 
    EpisodeDetailResponse, 
    PaperResponse,
    EpisodesListResponse,
    HealthResponse,
    ErrorResponse
)


class TestEpisodeResponse:
    """EpisodeResponse 테스트"""
    
    @pytest.fixture
    def sample_podcast(self):
        """샘플 Podcast 모델"""
        papers = [
            Paper(
                id="2510.19338",
                title="Every Attention Matters",
                authors=["John Doe", "Jane Smith"],
                abstract="We propose a novel approach...",
                summary="이 논문은 대규모 언어 모델의...",
                url="https://huggingface.co/papers/2510.19338",
                arxiv_id="2510.19338",
                categories=["cs.CL", "cs.AI"],
                upvotes=142,
                published_date="2025-01-26",
                collected_at=datetime.now()
            )
        ] * 3
        
        return Podcast(
            id="2025-01-27",
            title="Daily Papers - 2025-01-27",
            description="오늘의 Hugging Face 트렌딩 논문 Top 3",
            created_at=datetime.now(),
            papers=papers,
            audio_file_path="https://storage.googleapis.com/papers_ethan/2025-01-27/episode.mp3",
            audio_duration=627,
            audio_size=5026816,
            status="completed",
            script="안녕하세요, 오늘의 AI 논문 팟캐스트입니다..."
        )
    
    def test_from_podcast_creates_correct_response(self, sample_podcast):
        """from_podcast()가 올바른 응답을 생성하는지 테스트"""
        response = EpisodeResponse.from_podcast(sample_podcast)
        
        assert response.id == "2025-01-27"
        assert response.title == "Daily Papers - 2025-01-27"
        assert response.publication_date == "2025-01-27"
        assert response.audio_url == "https://storage.googleapis.com/papers_ethan/2025-01-27/episode.mp3"
        assert response.duration_seconds == 627
        assert response.file_size_bytes == 5026816
        assert response.papers_count == 3
        assert response.created_at is not None
    
    def test_response_serialization(self, sample_podcast):
        """응답이 올바르게 직렬화되는지 테스트"""
        response = EpisodeResponse.from_podcast(sample_podcast)
        data = response.dict()
        
        assert isinstance(data, dict)
        assert data["id"] == "2025-01-27"
        assert data["title"] == "Daily Papers - 2025-01-27"
        assert data["papers_count"] == 3


class TestEpisodeDetailResponse:
    """EpisodeDetailResponse 테스트"""
    
    @pytest.fixture
    def sample_podcast(self):
        """샘플 Podcast 모델"""
        papers = [
            Paper(
                id="2510.19338",
                title="Every Attention Matters",
                authors=["John Doe", "Jane Smith"],
                abstract="We propose a novel approach...",
                summary="이 논문은 대규모 언어 모델의...",
                url="https://huggingface.co/papers/2510.19338",
                arxiv_id="2510.19338",
                categories=["cs.CL", "cs.AI"],
                upvotes=142,
                published_date="2025-01-26",
                collected_at=datetime.now()
            )
        ] * 3
        
        return Podcast(
            id="2025-01-27",
            title="Daily Papers - 2025-01-27",
            description="오늘의 Hugging Face 트렌딩 논문 Top 3",
            created_at=datetime.now(),
            papers=papers,
            audio_file_path="https://storage.googleapis.com/papers_ethan/2025-01-27/episode.mp3",
            audio_duration=627,
            audio_size=5026816,
            status="completed",
            script="안녕하세요, 오늘의 AI 논문 팟캐스트입니다..."
        )
    
    def test_from_podcast_includes_details(self, sample_podcast):
        """from_podcast()가 상세 정보를 포함하는지 테스트"""
        response = EpisodeDetailResponse.from_podcast(sample_podcast)
        
        # 기본 정보
        assert response.id == "2025-01-27"
        assert response.title == "Daily Papers - 2025-01-27"
        
        # 상세 정보
        assert response.description == "오늘의 Hugging Face 트렌딩 논문 Top 3"
        assert response.script == "안녕하세요, 오늘의 AI 논문 팟캐스트입니다..."
        assert len(response.papers) == 3
        assert response.papers[0].title == "Every Attention Matters"
    
    def test_inherits_from_episode_response(self, sample_podcast):
        """EpisodeDetailResponse가 EpisodeResponse를 상속하는지 테스트"""
        response = EpisodeDetailResponse.from_podcast(sample_podcast)
        
        # EpisodeResponse의 모든 필드가 있는지 확인
        assert hasattr(response, 'id')
        assert hasattr(response, 'title')
        assert hasattr(response, 'publication_date')
        assert hasattr(response, 'audio_url')
        assert hasattr(response, 'duration_seconds')
        assert hasattr(response, 'file_size_bytes')
        assert hasattr(response, 'papers_count')
        assert hasattr(response, 'created_at')
        
        # 추가 필드가 있는지 확인
        assert hasattr(response, 'description')
        assert hasattr(response, 'script')
        assert hasattr(response, 'papers')


class TestPaperResponse:
    """PaperResponse 테스트"""
    
    @pytest.fixture
    def sample_paper(self):
        """샘플 Paper 모델"""
        return Paper(
            id="2510.19338",
            title="Every Attention Matters",
            authors=["John Doe", "Jane Smith"],
            abstract="We propose a novel approach...",
            summary="이 논문은 대규모 언어 모델의...",
            url="https://huggingface.co/papers/2510.19338",
            arxiv_id="2510.19338",
            categories=["cs.CL", "cs.AI"],
            upvotes=142,
            published_date="2025-01-26",
            collected_at=datetime.now()
        )
    
    def test_from_paper_creates_correct_response(self, sample_paper):
        """from_paper()가 올바른 응답을 생성하는지 테스트"""
        response = PaperResponse.from_paper(sample_paper)
        
        assert response.id == "2510.19338"
        assert response.title == "Every Attention Matters"
        assert response.authors == ["John Doe", "Jane Smith"]
        assert response.abstract == "We propose a novel approach..."
        assert response.summary == "이 논문은 대규모 언어 모델의..."
        assert response.url == "https://huggingface.co/papers/2510.19338"
        assert response.arxiv_id == "2510.19338"
        assert response.categories == ["cs.CL", "cs.AI"]
        assert response.upvotes == 142
        assert response.published_date == "2025-01-26"
        assert response.collected_at is not None
    
    def test_handles_optional_fields(self):
        """선택적 필드가 올바르게 처리되는지 테스트"""
        paper = Paper(
            id="2510.19338",
            title="Test Paper",
            authors=["Author"],
            url="https://example.com",
            collected_at=datetime.now()
        )
        
        response = PaperResponse.from_paper(paper)
        
        assert response.abstract is None
        assert response.summary is None
        assert response.arxiv_id is None
        assert response.categories is None
        assert response.upvotes == 0
        assert response.thumbnail_url is None
        assert response.published_date is None


class TestUtilitySchemas:
    """유틸리티 스키마 테스트"""
    
    def test_episodes_list_response(self):
        """EpisodesListResponse 테스트"""
        episodes = [
            EpisodeResponse(
                id="2025-01-27",
                title="Daily Papers - 2025-01-27",
                publication_date="2025-01-27",
                audio_url="https://example.com/audio.mp3",
                papers_count=3,
                created_at="2025-01-27T06:00:00Z"
            )
        ]
        
        response = EpisodesListResponse(
            episodes=episodes,
            total=1,
            limit=20,
            offset=0
        )
        
        assert len(response.episodes) == 1
        assert response.total == 1
        assert response.limit == 20
        assert response.offset == 0
    
    def test_health_response(self):
        """HealthResponse 테스트"""
        response = HealthResponse(
            status="healthy",
            timestamp="2025-01-27T12:00:00Z",
            version="1.0.0"
        )
        
        assert response.status == "healthy"
        assert response.timestamp == "2025-01-27T12:00:00Z"
        assert response.version == "1.0.0"
    
    def test_error_response(self):
        """ErrorResponse 테스트"""
        response = ErrorResponse(
            error="NotFound",
            message="에피소드를 찾을 수 없습니다",
            details={"episode_id": "2025-01-27"}
        )
        
        assert response.error == "NotFound"
        assert response.message == "에피소드를 찾을 수 없습니다"
        assert response.details["episode_id"] == "2025-01-27"
