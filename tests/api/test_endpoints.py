"""
API 엔드포인트 테스트

FastAPI 엔드포인트의 통합 테스트
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from src.models.podcast import Podcast
from src.models.paper import Paper

from api.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """헬스 체크 엔드포인트 테스트"""
    
    def test_root_endpoint(self):
        """루트 엔드포인트 테스트"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
    
    def test_health_endpoint(self):
        """헬스 체크 엔드포인트 테스트"""
        response = client.get("/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert data["version"] == "1.0.0"
    
    def test_detailed_health_endpoint(self):
        """상세 헬스 체크 엔드포인트 테스트"""
        response = client.get("/api/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "data_directory" in data
        assert "environment" in data
        assert "api" in data


class TestEpisodesEndpoints:
    """에피소드 엔드포인트 테스트"""
    
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
            ] * 3,
            "audio_file_path": "https://storage.googleapis.com/papers_ethan/2025-01-27/episode.mp3",
            "audio_duration": 627,
            "audio_size": 5026816,
            "status": "completed",
            "script": "안녕하세요, 오늘의 AI 논문 팟캐스트입니다..."
        }
    
    @pytest.fixture
    def mock_data_dir(self, sample_podcast_data):
        """임시 데이터 디렉토리 생성"""
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = Path(temp_dir) / "data" / "podcasts"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # 샘플 JSON 파일 생성
            json_file = data_dir / "2025-01-27.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(sample_podcast_data, f)
            
            yield data_dir
    
    @patch('api.routes.episodes.Path')
    def test_list_episodes_success(self, mock_path, mock_data_dir, sample_podcast_data):
        """에피소드 목록 조회 성공 테스트"""
        mock_path.return_value = mock_data_dir
        
        response = client.get("/api/episodes")
        assert response.status_code == 200
        
        data = response.json()
        assert "episodes" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert len(data["episodes"]) == 1
        assert data["total"] == 1
    
    @patch('api.routes.episodes.Path')
    def test_list_episodes_with_pagination(self, mock_path, mock_data_dir, sample_podcast_data):
        """페이지네이션 테스트"""
        mock_path.return_value = mock_data_dir
        
        response = client.get("/api/episodes?limit=10&offset=0")
        assert response.status_code == 200
        
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 0
    
    @patch('api.routes.episodes.Path')
    def test_get_latest_episode_success(self, mock_path, mock_data_dir, sample_podcast_data):
        """최신 에피소드 조회 성공 테스트"""
        mock_path.return_value = mock_data_dir
        
        response = client.get("/api/episodes/latest")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "2025-01-27"
        assert data["title"] == "Daily Papers - 2025-01-27"
        assert "papers" in data
        assert len(data["papers"]) == 3
    
    @patch('api.routes.episodes.Path')
    def test_get_episode_by_id_success(self, mock_path, mock_data_dir, sample_podcast_data):
        """ID로 에피소드 조회 성공 테스트"""
        mock_path.return_value = mock_data_dir
        
        response = client.get("/api/episodes/2025-01-27")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "2025-01-27"
        assert data["title"] == "Daily Papers - 2025-01-27"
        assert "papers" in data
        assert len(data["papers"]) == 3
    
    def test_get_episode_by_id_invalid_format(self):
        """잘못된 ID 형식 테스트"""
        response = client.get("/api/episodes/invalid-id")
        assert response.status_code == 400
        
        data = response.json()
        assert "잘못된 에피소드 ID 형식" in data["message"]
    
    @patch('api.routes.episodes.Path')
    def test_get_episode_by_id_not_found(self, mock_path, mock_data_dir):
        """존재하지 않는 에피소드 조회 테스트"""
        mock_path.return_value = mock_data_dir
        
        response = client.get("/api/episodes/2025-01-01")
        assert response.status_code == 404
        
        data = response.json()
        assert "찾을 수 없습니다" in data["message"]
    
    @patch('api.routes.episodes.Path')
    def test_get_episodes_by_date_range(self, mock_path, mock_data_dir, sample_podcast_data):
        """날짜 범위로 에피소드 조회 테스트"""
        mock_path.return_value = mock_data_dir
        
        response = client.get("/api/episodes/date-range?start=2025-01-27&end=2025-01-27")
        assert response.status_code == 200
        
        data = response.json()
        assert "episodes" in data
        assert "total" in data
        assert "date_range" in data
        assert data["date_range"]["start"] == "2025-01-27"
        assert data["date_range"]["end"] == "2025-01-27"
    
    def test_get_episodes_by_date_range_invalid_format(self):
        """잘못된 날짜 형식 테스트"""
        response = client.get("/api/episodes/date-range?start=invalid&end=2025-01-27")
        assert response.status_code == 400
        
        data = response.json()
        assert "잘못된 start 날짜 형식" in data["message"]


class TestErrorHandling:
    """에러 처리 테스트"""
    
    def test_404_error_response(self):
        """404 에러 응답 테스트"""
        response = client.get("/api/episodes/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert "message" in data
    
    def test_400_error_response(self):
        """400 에러 응답 테스트"""
        response = client.get("/api/episodes/invalid-id")
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data
        assert "message" in data
    
    def test_500_error_response(self):
        """500 에러 응답 테스트 (의도적으로 발생시키기 어려움)"""
        # 실제 500 에러를 발생시키기 어려우므로 스킵
        pass


class TestCORS:
    """CORS 설정 테스트"""
    
    def test_cors_headers(self):
        """CORS 헤더 테스트"""
        response = client.options("/api/health")
        assert response.status_code == 200
        
        # CORS 헤더 확인
        headers = response.headers
        assert "access-control-allow-origin" in headers
        assert "access-control-allow-methods" in headers
        assert "access-control-allow-headers" in headers
