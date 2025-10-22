# Data Model: HuggingFace Podcast Automation

**Feature**: 001-huggingface-podcast-automation  
**Date**: 2025-01-27  
**Phase**: 1 - Data Design

## Overview

이 문서는 HuggingFace Podcast Automation 시스템의 데이터 모델을 정의합니다.

---

## 1. Paper

**Purpose**: Hugging Face에서 수집된 논문 정보를 표현합니다.

### Fields

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| id | string | Yes | 논문의 고유 식별자 (Hugging Face paper ID) | 비어있지 않아야 함 |
| title | string | Yes | 논문 제목 | 최대 500자 |
| authors | list[string] | Yes | 저자 목록 | 최소 1명 이상 |
| abstract | string | Yes | 논문 초록 | 최대 5000자 |
| url | string | Yes | 논문 링크 (Hugging Face URL) | 유효한 URL 형식 |
| published_date | string | No | 게시일 (ISO 8601 형식) | YYYY-MM-DD |
| upvotes | integer | No | 추천 수 | >= 0 |
| summary | string | No | Gemini Pro로 생성된 요약 | 최대 1000자 |
| collected_at | string | Yes | 수집 시각 (ISO 8601) | YYYY-MM-DDTHH:MM:SSZ |

### Relationships
- Paper는 Podcast의 일부로 포함됩니다 (many-to-one)

### State Transitions
```
collected → summarized → included_in_podcast
```

### Example JSON
```json
{
  "id": "2401.12345",
  "title": "Efficient Transformers with Dynamic Attention",
  "authors": ["John Doe", "Jane Smith"],
  "abstract": "We propose a novel approach to...",
  "url": "https://huggingface.co/papers/2401.12345",
  "published_date": "2025-01-27",
  "upvotes": 142,
  "summary": "이 논문은 동적 어텐션을 사용하여...",
  "collected_at": "2025-01-27T06:00:00Z"
}
```

---

## 2. Podcast

**Purpose**: 생성된 팟캐스트 에피소드 정보를 표현합니다.

### Fields

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| id | string | Yes | 팟캐스트 고유 식별자 (날짜 기반: YYYY-MM-DD) | YYYY-MM-DD 형식 |
| title | string | Yes | 에피소드 제목 | 최대 200자 |
| description | string | Yes | 에피소드 설명 | 최대 1000자 |
| created_at | string | Yes | 생성 시각 (ISO 8601) | YYYY-MM-DDTHH:MM:SSZ |
| papers | list[Paper] | Yes | 포함된 논문 목록 | 정확히 3개 |
| audio_file_path | string | Yes | MP3 파일 경로 (GCS URL) | 유효한 URL 형식 |
| audio_duration | integer | Yes | 오디오 길이 (초) | > 0 |
| audio_size | integer | Yes | 파일 크기 (bytes) | > 0 |
| status | string | Yes | 처리 상태 | enum: [pending, processing, completed, failed] |
| error_message | string | No | 오류 메시지 (실패 시) | 최대 500자 |

### Relationships
- Podcast는 여러 Paper를 포함합니다 (one-to-many)
- Podcast는 ProcessingLog를 가집니다 (one-to-many)

### State Transitions
```
pending → processing → completed
                    ↓
                  failed (with retry)
```

### Example JSON
```json
{
  "id": "2025-01-27",
  "title": "Daily AI Papers - January 27, 2025",
  "description": "오늘의 Hugging Face 트렌딩 논문 Top 3",
  "created_at": "2025-01-27T06:15:30Z",
  "papers": [
    { "id": "2401.12345", "title": "...", ... },
    { "id": "2401.12346", "title": "...", ... },
    { "id": "2401.12347", "title": "...", ... }
  ],
  "audio_file_path": "https://storage.googleapis.com/papercast-podcasts/2025-01-27/episode.mp3",
  "audio_duration": 480,
  "audio_size": 7680000,
  "status": "completed"
}
```

---

## 3. ProcessingLog

**Purpose**: 시스템 실행 로그 및 각 단계별 상태를 기록합니다.

### Fields

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| id | string | Yes | 로그 고유 식별자 (UUID) | UUID v4 형식 |
| podcast_id | string | Yes | 관련 팟캐스트 ID | YYYY-MM-DD 형식 |
| step | string | Yes | 처리 단계 | enum: [collect, summarize, tts, upload, deploy] |
| status | string | Yes | 단계 상태 | enum: [started, completed, failed, retrying] |
| started_at | string | Yes | 시작 시각 (ISO 8601) | YYYY-MM-DDTHH:MM:SSZ |
| completed_at | string | No | 완료 시각 (ISO 8601) | YYYY-MM-DDTHH:MM:SSZ |
| duration | integer | No | 실행 시간 (초) | >= 0 |
| error_message | string | No | 오류 메시지 | 최대 1000자 |
| retry_count | integer | Yes | 재시도 횟수 | >= 0, <= 3 |
| metadata | object | No | 추가 메타데이터 (JSON) | 유효한 JSON |

### Relationships
- ProcessingLog는 Podcast에 속합니다 (many-to-one)

### State Transitions
```
started → completed
       ↓
     failed → retrying → started (retry_count++)
```

### Example JSON
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "podcast_id": "2025-01-27",
  "step": "collect",
  "status": "completed",
  "started_at": "2025-01-27T06:00:00Z",
  "completed_at": "2025-01-27T06:01:15Z",
  "duration": 75,
  "retry_count": 0,
  "metadata": {
    "papers_found": 3,
    "api_calls": 1
  }
}
```

---

## Data Storage Strategy

### File-based Storage

모든 데이터는 JSON 파일로 로컬 및 GCS에 저장됩니다.

#### Local Storage (GitHub Repository)
```
data/
├── podcasts/
│   ├── 2025-01-27.json      # Podcast 메타데이터
│   ├── 2025-01-26.json
│   └── index.json            # 전체 팟캐스트 목록
└── logs/
    └── 2025-01-27.json       # ProcessingLog 목록
```

#### Cloud Storage (GCS)
```
gs://papercast-podcasts/
├── 2025-01-27/
│   ├── episode.mp3           # 오디오 파일
│   └── metadata.json         # Podcast 메타데이터
└── 2025-01-26/
    ├── episode.mp3
    └── metadata.json
```

### Data Retention

- **팟캐스트 메타데이터**: 무기한 보관 (index.json에 모든 히스토리)
- **오디오 파일**: 30일 후 자동 삭제 (GCS 라이프사이클 정책)
- **처리 로그**: 90일 후 삭제

---

## Data Validation

### Validation Rules

모든 데이터는 입력 시 다음 규칙을 따라 검증됩니다:

1. **Required 필드**: 비어있지 않아야 함
2. **URL**: 유효한 HTTP/HTTPS URL 형식
3. **Date**: ISO 8601 형식 (YYYY-MM-DDTHH:MM:SSZ)
4. **Enum**: 정의된 값 중 하나여야 함
5. **String 길이**: 최대 길이 준수
6. **Integer**: 음수 불가 (명시된 경우)

### Validation Implementation

```python
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import List, Optional

class Paper(BaseModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., max_length=500)
    authors: List[str] = Field(..., min_items=1)
    abstract: str = Field(..., max_length=5000)
    url: HttpUrl
    published_date: Optional[str] = None
    upvotes: Optional[int] = Field(None, ge=0)
    summary: Optional[str] = Field(None, max_length=1000)
    collected_at: datetime

class Podcast(BaseModel):
    id: str  # YYYY-MM-DD format
    title: str = Field(..., max_length=200)
    description: str = Field(..., max_length=1000)
    created_at: datetime
    papers: List[Paper] = Field(..., min_items=3, max_items=3)
    audio_file_path: HttpUrl
    audio_duration: int = Field(..., gt=0)
    audio_size: int = Field(..., gt=0)
    status: str = Field(..., pattern="^(pending|processing|completed|failed)$")
    error_message: Optional[str] = Field(None, max_length=500)
```

---

## Data Access Patterns

### Read Patterns
1. **최신 팟캐스트 조회**: `GET /data/podcasts/index.json` → 첫 번째 항목
2. **특정 날짜 팟캐스트**: `GET /data/podcasts/{date}.json`
3. **전체 목록**: `GET /data/podcasts/index.json`

### Write Patterns
1. **새 팟캐스트 생성**: `POST /data/podcasts/{date}.json`
2. **로그 추가**: `APPEND /data/logs/{date}.json`
3. **인덱스 업데이트**: `PUT /data/podcasts/index.json`

---

## Summary

- **3개의 주요 엔티티**: Paper, Podcast, ProcessingLog
- **JSON 기반 파일 스토리지**: 간단하고 버전 관리 용이
- **Pydantic 검증**: 타입 안전성 및 자동 검증
- **명확한 상태 전이**: 각 단계별 추적 가능
- **30일 데이터 보관**: 비용 효율적인 스토리지 관리

