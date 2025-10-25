# 데이터 모델: PaperCast

**날짜**: 2025-01-27  
**기능**: 001-huggingface-podcast-automation  
**상태**: 완료

## 엔티티 개요

PaperCast는 기존 JSON 파일 기반 저장소를 활용합니다. 데이터베이스 대신 파일 시스템을 사용하며, API는 읽기 전용으로 동작합니다.

## 기존 데이터 모델 (유지)

### Paper (논문)

**목적**: Hugging Face에서 수집된 개별 논문 정보

**필드**:
- `id` (str, 필수): 논문 고유 ID (ArXiv ID 또는 자동 생성)
- `title` (str, 필수): 논문 제목
- `authors` (list[str], 필수): 저자 목록
- `abstract` (str, 선택): 논문 초록
- `summary` (str, 선택): AI 생성 요약 (Gemini Pro)
- `url` (HttpUrl, 필수): 논문 원본 URL (Hugging Face)
- `arxiv_id` (str, 선택): ArXiv 식별자
- `categories` (list[str], 선택): 논문 카테고리
- `upvotes` (int, 기본: 0): Hugging Face 업보트 수
- `thumbnail_url` (HttpUrl, 선택): 썸네일 이미지 URL
- `published_date` (str, 선택): 논문 게시일
- `collected_at` (datetime, 자동): 수집 시간

**검증 규칙**:
- 제목은 1-500자
- 저자는 1-20명
- 요약은 50-2000자
- URL은 HTTPS 필수
- ArXiv ID는 `\d{4}\.\d{4,5}` 패턴
- Upvotes는 0 이상

**Pydantic 모델** (기존 `src/models/paper.py`):
```python
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class Paper(BaseModel):
    id: str = Field(..., description="논문 고유 ID")
    title: str = Field(..., min_length=1, max_length=500)
    authors: List[str] = Field(..., min_items=1, max_items=20)
    abstract: Optional[str] = None
    summary: Optional[str] = Field(None, min_length=50, max_length=2000)
    url: HttpUrl
    arxiv_id: Optional[str] = Field(None, regex=r'^\d{4}\.\d{4,5}$')
    categories: Optional[List[str]] = None
    upvotes: int = Field(default=0, ge=0)
    thumbnail_url: Optional[HttpUrl] = None
    published_date: Optional[str] = None
    collected_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            HttpUrl: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }
```

---

### Podcast (팟캐스트 에피소드)

**목적**: 생성된 팟캐스트 에피소드 메타데이터

**필드**:
- `id` (str, 필수): 에피소드 ID (`YYYY-MM-DD` 형식)
- `title` (str, 필수): 에피소드 제목
- `description` (str, 선택): 에피소드 설명
- `created_at` (datetime, 자동): 생성 시간
- `papers` (list[Paper], 필수): 포함된 논문 목록 (정확히 3개)
- `audio_file_path` (HttpUrl, 필수): MP3 파일 URL (GCS)
- `audio_duration` (int, 선택): 오디오 길이 (초)
- `audio_size` (int, 선택): 파일 크기 (바이트)
- `status` (str, 기본: "pending"): 처리 상태
- `script` (str, 선택): 팟캐스트 스크립트

**검증 규칙**:
- ID는 `YYYY-MM-DD` 형식 (`^\d{4}-\d{2}-\d{2}$`)
- papers는 정확히 3개
- audio_duration은 양수
- audio_size는 양수
- status는 ["pending", "processing", "completed", "failed"] 중 하나

**Pydantic 모델** (기존 `src/models/podcast.py`):
```python
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional
from datetime import datetime

class Podcast(BaseModel):
    id: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$')
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    papers: List[Paper] = Field(..., min_items=3, max_items=3)
    audio_file_path: HttpUrl
    audio_duration: Optional[int] = Field(None, gt=0)
    audio_size: Optional[int] = Field(None, gt=0)
    status: str = Field(default="pending")
    script: Optional[str] = None
    
    @validator('papers')
    def validate_papers_count(cls, v):
        if len(v) != 3:
            raise ValueError('에피소드는 정확히 3개의 논문이 필요합니다')
        return v
    
    class Config:
        json_encoders = {
            HttpUrl: lambda v: str(v),
            datetime: lambda v: v.isoformat()
        }
```

---

### ProcessingLog (처리 로그)

**목적**: 파이프라인 실행 로그 및 디버깅 정보

**필드**:
- `podcast_id` (str, 필수): 관련 팟캐스트 ID
- `step` (str, 필수): 처리 단계 이름
- `status` (str, 필수): 상태 (started, completed, failed)
- `started_at` (datetime, 필수): 시작 시간
- `completed_at` (datetime, 선택): 완료 시간
- `error_message` (str, 선택): 오류 메시지
- `metadata` (dict, 선택): 추가 메타데이터

**검증 규칙**:
- step은 ["collect", "summarize", "tts", "upload", "deploy", "generate_site"] 중 하나
- status는 ["started", "completed", "failed"] 중 하나

**Pydantic 모델** (기존 `src/models/processing_log.py`):
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ProcessingLog(BaseModel):
    podcast_id: str = Field(..., regex=r'^\d{4}-\d{2}-\d{2}$')
    step: str = Field(..., regex='^(collect|summarize|tts|upload|deploy|generate_site)$')
    status: str = Field(..., regex='^(started|completed|failed)$')
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def mark_completed(self):
        self.status = "completed"
        self.completed_at = datetime.now()
    
    def mark_failed(self, error: str):
        self.status = "failed"
        self.completed_at = datetime.now()
        self.error_message = error
```

---

## 데이터 저장 구조

### 파일 시스템 레이아웃

```
data/
├── podcasts/                     # 팟캐스트 메타데이터
│   ├── 2025-01-25.json          # 날짜별 JSON 파일
│   ├── 2025-01-26.json
│   └── 2025-01-27.json
│
├── logs/                         # 처리 로그
│   ├── 2025-01-25.json
│   ├── 2025-01-26.json
│   └── pipeline_YYYYMMDD.log    # 파이프라인 실행 로그
│
└── audio/                        # 임시 오디오 파일 (업로드 전)
    └── temp/
        └── episode_YYYY-MM-DD.mp3
```

### JSON 파일 예시

**data/podcasts/2025-01-27.json**:
```json
{
  "id": "2025-01-27",
  "title": "Daily Papers - 2025-01-27",
  "description": "오늘의 Hugging Face 트렌딩 논문 Top 3",
  "created_at": "2025-01-27T06:00:00Z",
  "papers": [
    {
      "id": "2510.19338",
      "title": "Every Attention Matters",
      "authors": ["John Doe", "Jane Smith"],
      "abstract": "We propose...",
      "summary": "이 논문은...",
      "url": "https://huggingface.co/papers/2510.19338",
      "arxiv_id": "2510.19338",
      "categories": ["cs.CL", "cs.AI"],
      "upvotes": 142,
      "thumbnail_url": null,
      "published_date": "2025-01-26",
      "collected_at": "2025-01-27T05:00:00Z"
    },
    // 2개 더...
  ],
  "audio_file_path": "https://storage.googleapis.com/papers_ethan/2025-01-27/episode.mp3",
  "audio_duration": 627,
  "audio_size": 5026816,
  "status": "completed",
  "script": "안녕하세요, 오늘의 AI 논문 팟캐스트입니다..."
}
```

---

## API 응답 스키마

### Episode Response

API는 기존 Podcast 모델을 Episode로 노출합니다.

```python
from pydantic import BaseModel
from typing import List

class EpisodeResponse(BaseModel):
    """API 응답용 에피소드 스키마"""
    id: str
    title: str
    publication_date: str  # YYYY-MM-DD
    audio_url: str
    duration_seconds: Optional[int]
    file_size_bytes: Optional[int]
    papers_count: int = 3
    created_at: str  # ISO 8601
    
    @classmethod
    def from_podcast(cls, podcast: Podcast):
        return cls(
            id=podcast.id,
            title=podcast.title,
            publication_date=podcast.id,  # ID가 날짜
            audio_url=str(podcast.audio_file_path),
            duration_seconds=podcast.audio_duration,
            file_size_bytes=podcast.audio_size,
            papers_count=len(podcast.papers),
            created_at=podcast.created_at.isoformat()
        )

class EpisodeDetailResponse(EpisodeResponse):
    """상세 정보 포함 에피소드 스키마"""
    description: Optional[str]
    script: Optional[str]
    papers: List[Paper]
    
    @classmethod
    def from_podcast(cls, podcast: Podcast):
        return cls(
            **EpisodeResponse.from_podcast(podcast).dict(),
            description=podcast.description,
            script=podcast.script,
            papers=podcast.papers
        )
```

---

## 데이터 접근 패턴

### 읽기 전용 Repository

```python
from pathlib import Path
import json
from typing import List, Optional

class PodcastRepository:
    """JSON 파일 기반 팟캐스트 저장소"""
    
    def __init__(self, data_dir: Path = Path("data/podcasts")):
        self.data_dir = data_dir
    
    def find_all(self) -> List[Podcast]:
        """모든 팟캐스트 조회 (날짜 역순)"""
        podcasts = []
        for json_file in sorted(self.data_dir.glob("*.json"), reverse=True):
            podcast = self.find_by_id(json_file.stem)
            if podcast:
                podcasts.append(podcast)
        return podcasts
    
    def find_by_id(self, podcast_id: str) -> Optional[Podcast]:
        """ID로 팟캐스트 조회"""
        file_path = self.data_dir / f"{podcast_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Podcast(**data)
    
    def find_latest(self) -> Optional[Podcast]:
        """최신 팟캐스트 조회"""
        podcasts = self.find_all()
        return podcasts[0] if podcasts else None
    
    def find_by_date_range(self, start: str, end: str) -> List[Podcast]:
        """날짜 범위로 팟캐스트 조회"""
        podcasts = self.find_all()
        return [p for p in podcasts if start <= p.id <= end]
```

---

## 성능 고려사항

### 캐싱 전략

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedPodcastRepository(PodcastRepository):
    """캐싱 레이어가 추가된 저장소"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}
        self._cache_ttl = timedelta(hours=1)
    
    def find_all(self) -> List[Podcast]:
        cache_key = "all_podcasts"
        if cache_key in self._cache:
            cached_data, cached_at = self._cache[cache_key]
            if datetime.now() - cached_at < self._cache_ttl:
                return cached_data
        
        podcasts = super().find_all()
        self._cache[cache_key] = (podcasts, datetime.now())
        return podcasts
    
    @lru_cache(maxsize=128)
    def find_by_id(self, podcast_id: str) -> Optional[Podcast]:
        """LRU 캐시 적용"""
        return super().find_by_id(podcast_id)
```

---

## 비즈니스 규칙

1. **에피소드 ID**: 항상 `YYYY-MM-DD` 형식 (날짜 기반)
2. **논문 개수**: 에피소드당 정확히 3개
3. **오디오 파일**: 모두 GCS에 저장, 공개 URL 제공
4. **데이터 불변성**: 한번 생성된 에피소드는 수정 불가 (재생성만 가능)
5. **캐싱**: 에피소드 데이터는 1시간 캐싱 (하루 1회 업데이트)

---

## 마이그레이션 계획

**현재**: 데이터베이스 마이그레이션 계획 없음

**이유**: 
- JSON 파일 시스템이 현재 규모에 충분
- 연간 365개 파일 (매우 관리 가능)
- 읽기 성능 우수 (파일 시스템 캐시 활용)

**미래 고려사항**:
- 연간 에피소드가 10,000개 이상이 되면 데이터베이스 고려
- 복잡한 쿼리(검색, 필터링)가 필요하면 데이터베이스 고려
- 현재는 YAGNI 원칙에 따라 단순하게 유지

---

**데이터 모델 상태**: ✅ 완료  
**기존 모델 활용**: ✅ 완료  
**API 스키마 정의**: ✅ 완료
