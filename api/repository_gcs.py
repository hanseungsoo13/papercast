"""
GCS 기반 Repository 패턴 구현

Google Cloud Storage에서 직접 데이터를 읽어오는 저장소
GitHub Actions에서 생성된 데이터를 GCS에서 조회
"""

import json
from pathlib import Path
from typing import List, Optional
from functools import lru_cache
from datetime import datetime
import tempfile
import os

from google.cloud import storage
from google.oauth2 import service_account

from src.models.podcast import Podcast


class GCSPodcastRepository:
    """GCS 기반 팟캐스트 저장소"""
    
    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        self.bucket_name = bucket_name
        self._cache = {}
        self._cache_ttl = 3600  # 1시간
        
        # GCS 클라이언트 초기화
        if credentials_path and os.path.exists(credentials_path):
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = storage.Client(credentials=credentials)
        else:
            # 환경 변수에서 자동 인증 (Cloud Run에서)
            self.client = storage.Client()
        
        self.bucket = self.client.bucket(bucket_name)
    
    def find_all(self) -> List[Podcast]:
        """모든 팟캐스트 조회 (날짜 역순)"""
        cache_key = "all_podcasts"
        if cache_key in self._cache:
            cached_data, cached_at = self._cache[cache_key]
            if (datetime.now() - cached_at).seconds < self._cache_ttl:
                return cached_data
        
        podcasts = []
        
        # GCS에서 metadata.json 파일 목록 조회 (실제 데이터 구조에 맞게)
        print(f"DEBUG: Searching for metadata.json files in bucket '{self.bucket_name}'")
        blobs = self.bucket.list_blobs(prefix="")
        metadata_files = [blob for blob in blobs if blob.name.endswith('/metadata.json')]
        
        print(f"DEBUG: Found {len(metadata_files)} metadata files:")
        for blob in metadata_files:
            print(f"  - {blob.name}")
        
        # 날짜 역순으로 정렬 (파일명에서 날짜 추출)
        metadata_files.sort(key=lambda x: x.name, reverse=True)
        
        for blob in metadata_files:
            print(f"DEBUG: Loading podcast from {blob.name}")
            podcast = self._load_podcast_from_gcs(blob)
            if podcast:
                podcasts.append(podcast)
                print(f"DEBUG: Successfully loaded podcast {podcast.id}")
            else:
                print(f"DEBUG: Failed to load podcast from {blob.name}")
        
        print(f"DEBUG: Total podcasts loaded: {len(podcasts)}")
        
        # 캐시에 저장
        self._cache[cache_key] = (podcasts, datetime.now())
        return podcasts
    
    @lru_cache(maxsize=128)
    def find_by_id(self, podcast_id: str) -> Optional[Podcast]:
        """ID로 팟캐스트 조회"""
        blob_name = f"{podcast_id}/metadata.json"
        blob = self.bucket.blob(blob_name)
        
        if not blob.exists():
            return None
        
        return self._load_podcast_from_gcs(blob)
    
    def find_latest(self) -> Optional[Podcast]:
        """최신 팟캐스트 조회"""
        podcasts = self.find_all()
        return podcasts[0] if podcasts else None
    
    def find_by_date_range(self, start: str, end: str) -> List[Podcast]:
        """날짜 범위로 팟캐스트 조회"""
        all_podcasts = self.find_all()
        start_date = datetime.fromisoformat(start)
        end_date = datetime.fromisoformat(end)
        
        return [
            podcast for podcast in all_podcasts
            if start_date <= datetime.fromisoformat(podcast.publication_date) <= end_date
        ]
    
    def _load_podcast_from_gcs(self, blob) -> Optional[Podcast]:
        """GCS blob에서 팟캐스트 데이터 로드"""
        try:
            # 임시 파일에 다운로드
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
                blob.download_to_filename(temp_file.name)
                
                with open(temp_file.name, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 임시 파일 삭제
                os.unlink(temp_file.name)
                
                # GCS 데이터를 Podcast 모델에 맞게 변환
                podcast_data = self._convert_gcs_data_to_podcast(data)
                
                return Podcast(**podcast_data)
                
        except Exception as e:
            print(f"Error loading podcast from GCS: {e}")
            return None
    
    def _convert_gcs_data_to_podcast(self, gcs_data: dict) -> dict:
        """GCS 데이터를 Podcast 모델에 맞게 변환"""
        # 기본 필드 매핑
        podcast_data = {
            "id": gcs_data.get("id"),
            "title": gcs_data.get("title"),
            "description": gcs_data.get("description", f"Daily AI Papers - {gcs_data.get('id', 'Unknown')}"),
            "created_at": gcs_data.get("created_at"),
            "papers": gcs_data.get("papers", []),
            "audio_file_path": gcs_data.get("audio_url", ""),
            "audio_duration": gcs_data.get("duration_seconds", 1800),  # 기본값 30분
            "audio_size": gcs_data.get("file_size_bytes", 15000000),  # 기본값 15MB
            "status": "completed"
        }
        
        # papers 데이터 변환 (필요한 필드 추가)
        if "papers" in podcast_data:
            for paper in podcast_data["papers"]:
                # collected_at 필드가 없으면 created_at 사용
                if "collected_at" not in paper:
                    paper["collected_at"] = gcs_data.get("created_at")
        
        return podcast_data
    
    def get_all_papers(self) -> List[dict]:
        """모든 논문 데이터 조회 (에피소드별로 분리)"""
        all_papers = []
        podcasts = self.find_all()
        
        for podcast in podcasts:
            for paper in podcast.papers:
                # Paper 객체를 dict로 변환
                if hasattr(paper, 'dict'):
                    paper_data = paper.dict()
                else:
                    paper_data = paper
                
                paper_data['episode_id'] = podcast.id
                paper_data['episode_title'] = podcast.title
                paper_data['episode_date'] = podcast.id
                all_papers.append(paper_data)
        
        return all_papers
    
    def find_paper_by_id(self, paper_id: str) -> Optional[dict]:
        """논문 ID로 논문 데이터 조회"""
        podcasts = self.find_all()
        
        for podcast in podcasts:
            for paper in podcast.papers:
                # Paper 객체의 id 속성 확인
                paper_id_value = paper.id if hasattr(paper, 'id') else paper.get('id')
                if paper_id_value == paper_id:
                    # Paper 객체를 dict로 변환
                    if hasattr(paper, 'dict'):
                        paper_data = paper.dict()
                    else:
                        paper_data = paper
                    
                    paper_data['episode_id'] = podcast.id
                    paper_data['episode_title'] = podcast.title
                    paper_data['episode_date'] = podcast.id
                    return paper_data
        
        return None
    
    def clear_cache(self):
        """캐시 초기화"""
        self._cache.clear()
        self.find_by_id.cache_clear()


class CachedGCSPodcastRepository(GCSPodcastRepository):
    """캐시가 강화된 GCS 저장소"""
    
    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        super().__init__(bucket_name, credentials_path)
        self._cache_ttl = 1800  # 30분 (더 짧은 캐시)
    
    def find_all(self) -> List[Podcast]:
        """캐시된 모든 팟캐스트 조회"""
        return super().find_all()
    
    def find_by_id(self, podcast_id: str) -> Optional[Podcast]:
        """캐시된 ID로 팟캐스트 조회"""
        return super().find_by_id(podcast_id)
