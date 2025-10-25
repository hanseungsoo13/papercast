"""
Repository 패턴 구현

JSON 파일 기반 데이터 접근 레이어
기존 src/ 파이프라인에서 생성된 data/podcasts/*.json 파일을 읽기 전용으로 제공
"""

import json
from pathlib import Path
from typing import List, Optional
from functools import lru_cache
from datetime import datetime

from src.models.podcast import Podcast


class PodcastRepository:
    """JSON 파일 기반 팟캐스트 저장소"""
    
    def __init__(self, data_dir: Path = Path("data/podcasts")):
        self.data_dir = data_dir
        self._cache = {}
        self._cache_ttl = 3600  # 1시간
    
    def find_all(self) -> List[Podcast]:
        """모든 팟캐스트 조회 (날짜 역순)"""
        cache_key = "all_podcasts"
        if cache_key in self._cache:
            cached_data, cached_at = self._cache[cache_key]
            if (datetime.now() - cached_at).seconds < self._cache_ttl:
                return cached_data
        
        podcasts = []
        json_files = sorted(self.data_dir.glob("*.json"), reverse=True)
        
        for json_file in json_files:
            podcast = self._load_podcast_from_file(json_file)
            if podcast:
                podcasts.append(podcast)
        
        # 캐시에 저장
        self._cache[cache_key] = (podcasts, datetime.now())
        return podcasts
    
    @lru_cache(maxsize=128)
    def find_by_id(self, podcast_id: str) -> Optional[Podcast]:
        """ID로 팟캐스트 조회"""
        file_path = self.data_dir / f"{podcast_id}.json"
        if not file_path.exists():
            return None
        
        return self._load_podcast_from_file(file_path)
    
    def find_latest(self) -> Optional[Podcast]:
        """최신 팟캐스트 조회"""
        podcasts = self.find_all()
        return podcasts[0] if podcasts else None
    
    def find_by_date_range(self, start: str, end: str) -> List[Podcast]:
        """날짜 범위로 팟캐스트 조회"""
        podcasts = self.find_all()
        return [p for p in podcasts if start <= p.id <= end]
    
    def _load_podcast_from_file(self, file_path: Path) -> Optional[Podcast]:
        """JSON 파일에서 팟캐스트 로드"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Podcast(**data)
        except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
            print(f"Error loading podcast from {file_path}: {e}")
            return None
    
    def clear_cache(self):
        """캐시 초기화"""
        self._cache.clear()
        self.find_by_id.cache_clear()


class CachedPodcastRepository(PodcastRepository):
    """캐싱 레이어가 추가된 저장소"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}
        self._cache_ttl = 3600  # 1시간
    
    def find_all(self) -> List[Podcast]:
        """캐싱이 적용된 모든 팟캐스트 조회"""
        cache_key = "all_podcasts"
        if cache_key in self._cache:
            cached_data, cached_at = self._cache[cache_key]
            if (datetime.now() - cached_at).seconds < self._cache_ttl:
                return cached_data
        
        podcasts = super().find_all()
        self._cache[cache_key] = (podcasts, datetime.now())
        return podcasts
    
    def find_by_id(self, podcast_id: str) -> Optional[Podcast]:
        """캐싱이 적용된 ID로 팟캐스트 조회"""
        cache_key = f"podcast_{podcast_id}"
        if cache_key in self._cache:
            cached_data, cached_at = self._cache[cache_key]
            if (datetime.now() - cached_at).seconds < self._cache_ttl:
                return cached_data
        
        podcast = super().find_by_id(podcast_id)
        if podcast:
            self._cache[cache_key] = (podcast, datetime.now())
        return podcast
