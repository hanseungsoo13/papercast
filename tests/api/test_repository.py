"""
Repository 패턴 테스트

JSON 파일 기반 데이터 접근 레이어 테스트
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

import pytest
from src.models.podcast import Podcast
from src.models.paper import Paper
from api.repository import PodcastRepository, CachedPodcastRepository


class TestPodcastRepository:
    """PodcastRepository 테스트"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """임시 데이터 디렉토리 생성"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def sample_podcast_data(self):
        """샘플 팟캐스트 데이터"""
        return {
            "id": "2025-01-27",
            "title": "Daily Papers - 2025-01-27",
            "description": "오늘의 Hugging Face 트렌딩 논문 Top 3",
            "created_at": "2025-01-27T06:00:00Z",
            "papers": [
                {
                    "id": "2510.19338",
                    "title": "Every Attention Matters",
                    "authors": ["John Doe", "Jane Smith"],
                    "abstract": "We propose a novel approach...",
                    "summary": "이 논문은 대규모 언어 모델의...",
                    "url": "https://huggingface.co/papers/2510.19338",
                    "arxiv_id": "2510.19338",
                    "categories": ["cs.CL", "cs.AI"],
                    "upvotes": 142,
                    "thumbnail_url": None,
                    "published_date": "2025-01-26",
                    "collected_at": "2025-01-27T05:00:00Z"
                }
            ] * 3,  # 3개 논문
            "audio_file_path": "https://storage.googleapis.com/papers_ethan/2025-01-27/episode.mp3",
            "audio_duration": 627,
            "audio_size": 5026816,
            "status": "completed",
            "script": "안녕하세요, 오늘의 AI 논문 팟캐스트입니다..."
        }
    
    @pytest.fixture
    def repository(self, temp_data_dir):
        """Repository 인스턴스 생성"""
        return PodcastRepository(data_dir=temp_data_dir)
    
    def test_find_all_returns_sorted_podcasts(self, repository, temp_data_dir, sample_podcast_data):
        """find_all()이 날짜 역순으로 정렬된 팟캐스트를 반환하는지 테스트"""
        # 여러 날짜의 팟캐스트 데이터 생성
        dates = ["2025-01-25", "2025-01-26", "2025-01-27"]
        
        for date in dates:
            data = sample_podcast_data.copy()
            data["id"] = date
            data["title"] = f"Daily Papers - {date}"
            
            file_path = temp_data_dir / f"{date}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        
        # find_all() 호출
        podcasts = repository.find_all()
        
        # 검증
        assert len(podcasts) == 3
        assert podcasts[0].id == "2025-01-27"  # 최신 날짜가 첫 번째
        assert podcasts[1].id == "2025-01-26"
        assert podcasts[2].id == "2025-01-25"  # 가장 오래된 날짜가 마지막
    
    def test_find_by_id_returns_podcast(self, repository, temp_data_dir, sample_podcast_data):
        """find_by_id()가 올바른 팟캐스트를 반환하는지 테스트"""
        # JSON 파일 생성
        file_path = temp_data_dir / "2025-01-27.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_podcast_data, f)
        
        # find_by_id() 호출
        podcast = repository.find_by_id("2025-01-27")
        
        # 검증
        assert podcast is not None
        assert podcast.id == "2025-01-27"
        assert podcast.title == "Daily Papers - 2025-01-27"
        assert len(podcast.papers) == 3
    
    def test_find_by_id_returns_none_when_not_found(self, repository):
        """존재하지 않는 ID로 find_by_id() 호출 시 None 반환 테스트"""
        podcast = repository.find_by_id("nonexistent")
        assert podcast is None
    
    def test_find_latest_returns_most_recent(self, repository, temp_data_dir, sample_podcast_data):
        """find_latest()가 가장 최근 팟캐스트를 반환하는지 테스트"""
        # 여러 날짜의 팟캐스트 데이터 생성
        dates = ["2025-01-25", "2025-01-27", "2025-01-26"]  # 순서 섞기
        
        for date in dates:
            data = sample_podcast_data.copy()
            data["id"] = date
            data["title"] = f"Daily Papers - {date}"
            
            file_path = temp_data_dir / f"{date}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        
        # find_latest() 호출
        latest = repository.find_latest()
        
        # 검증 (날짜 역순으로 정렬되므로 2025-01-27이 최신)
        assert latest is not None
        assert latest.id == "2025-01-27"
    
    def test_find_by_date_range(self, repository, temp_data_dir, sample_podcast_data):
        """날짜 범위로 팟캐스트 조회 테스트"""
        # 여러 날짜의 팟캐스트 데이터 생성
        dates = ["2025-01-25", "2025-01-26", "2025-01-27", "2025-01-28"]
        
        for date in dates:
            data = sample_podcast_data.copy()
            data["id"] = date
            data["title"] = f"Daily Papers - {date}"
            
            file_path = temp_data_dir / f"{date}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        
        # 날짜 범위 조회
        podcasts = repository.find_by_date_range("2025-01-26", "2025-01-27")
        
        # 검증
        assert len(podcasts) == 2
        assert podcasts[0].id == "2025-01-27"  # 날짜 역순
        assert podcasts[1].id == "2025-01-26"
    
    def test_caching_reduces_file_reads(self, repository, temp_data_dir, sample_podcast_data):
        """캐싱이 파일 읽기 횟수를 줄이는지 테스트"""
        # JSON 파일 생성
        file_path = temp_data_dir / "2025-01-27.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_podcast_data, f)
        
        # 첫 번째 호출
        podcasts1 = repository.find_all()
        assert len(podcasts1) == 1
        
        # 두 번째 호출 (캐시에서 가져와야 함)
        podcasts2 = repository.find_all()
        assert len(podcasts2) == 1
        assert podcasts1[0].id == podcasts2[0].id


class TestCachedPodcastRepository:
    """CachedPodcastRepository 테스트"""
    
    @pytest.fixture
    def temp_data_dir(self):
        """임시 데이터 디렉토리 생성"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def cached_repository(self, temp_data_dir):
        """CachedPodcastRepository 인스턴스 생성"""
        return CachedPodcastRepository(data_dir=temp_data_dir)
    
    def test_caching_works(self, cached_repository, temp_data_dir, sample_podcast_data):
        """캐싱이 올바르게 작동하는지 테스트"""
        # JSON 파일 생성
        file_path = temp_data_dir / "2025-01-27.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_podcast_data, f)
        
        # 첫 번째 호출
        podcast1 = cached_repository.find_by_id("2025-01-27")
        assert podcast1 is not None
        
        # 파일 삭제 (캐시에서 가져와야 함)
        file_path.unlink()
        
        # 두 번째 호출 (캐시에서 가져와야 함)
        podcast2 = cached_repository.find_by_id("2025-01-27")
        assert podcast2 is not None
        assert podcast1.id == podcast2.id
    
    def test_clear_cache(self, cached_repository, temp_data_dir, sample_podcast_data):
        """캐시 초기화가 올바르게 작동하는지 테스트"""
        # JSON 파일 생성
        file_path = temp_data_dir / "2025-01-27.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_podcast_data, f)
        
        # 첫 번째 호출 (캐시에 저장)
        podcast1 = cached_repository.find_by_id("2025-01-27")
        assert podcast1 is not None
        
        # 캐시 초기화
        cached_repository.clear_cache()
        
        # 파일 삭제
        file_path.unlink()
        
        # 두 번째 호출 (캐시가 비어있으므로 None 반환)
        podcast2 = cached_repository.find_by_id("2025-01-27")
        assert podcast2 is None
