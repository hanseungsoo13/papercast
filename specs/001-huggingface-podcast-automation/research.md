# 리서치: PaperCast API 레이어 추가

**날짜**: 2025-01-27  
**기능**: 001-huggingface-podcast-automation  
**상태**: 완료

## 리서치 작업

### 1. 기존 코드 구조 분석 및 재사용 전략

**결정**: 기존 `src/` 파이프라인은 그대로 유지하고 읽기 전용 API만 추가

**근거**:
- 기존 파이프라인이 완성되어 있고 안정적으로 동작함
- GitHub Actions가 기존 파이프라인에 의존하고 있음
- JSON 파일 기반 저장소가 이미 구축되어 있음
- 복잡한 데이터베이스 마이그레이션 불필요

**고려한 대안**:
- PostgreSQL 전환: 오버엔지니어링, 현재 규모에 불필요
- 기존 코드 전면 수정: 리스크 높음, 작동하는 시스템 건드리지 않기
- 마이크로서비스 아키텍처: 현재 규모에 과도함

**구현**:
```python
# API는 기존 JSON 파일을 읽기만 함
# src/main.py (파이프라인) - 변경 없음
# api/main.py (새로운 API) - 읽기 전용

# 데이터 흐름:
# 1. GitHub Actions → src/main.py → data/podcasts/*.json 생성
# 2. API → data/podcasts/*.json 읽기 → 클라이언트에 제공
```

---

### 2. FastAPI 최소 구현 패턴

**결정**: FastAPI를 경량화하여 JSON 파일 서빙에 집중

**근거**:
- 데이터베이스 없이 파일 시스템만 사용
- CRUD 중 Read만 구현 (Create/Update/Delete는 파이프라인이 담당)
- 간단한 캐싱으로 성능 최적화

**고려한 대안**:
- Flask: FastAPI가 더 현대적이고 자동 문서 생성 지원
- Express.js: Python 생태계 유지가 더 나음

**구현**:
```python
from fastapi import FastAPI
from pathlib import Path
import json

app = FastAPI(title="PaperCast API")

PODCASTS_DIR = Path("data/podcasts")

@app.get("/episodes")
async def list_episodes():
    episodes = []
    for json_file in PODCASTS_DIR.glob("*.json"):
        with open(json_file) as f:
            episodes.append(json.load(f))
    return {"episodes": sorted(episodes, key=lambda x: x['id'], reverse=True)}

@app.get("/episodes/{episode_id}")
async def get_episode(episode_id: str):
    file_path = PODCASTS_DIR / f"{episode_id}.json"
    if not file_path.exists():
        raise HTTPException(404, "Episode not found")
    with open(file_path) as f:
        return json.load(f)
```

---

### 3. 프론트엔드와 API 통합

**결정**: 기존 static-site는 유지하고, 선택적으로 Next.js 추가

**근거**:
- static-site는 이미 완성되어 있고 PDF 뷰어 등 기능 포함
- Next.js는 SEO와 동적 기능이 필요할 때만 사용
- 두 가지 옵션을 모두 제공하여 유연성 확보

**고려한 대안**:
- static-site 완전 폐기: 이미 작동하는 시스템 버리기 아까움
- Next.js만 사용: static-site의 기존 기능 재구현 필요

**구현**:
```
Option 1: static-site (기본)
- 파이프라인이 HTML 직접 생성
- CDN에서 정적 파일 서빙
- 빠르고 간단함

Option 2: Next.js (선택)
- API를 통해 데이터 가져오기
- 동적 라우팅 및 SEO 최적화
- 더 현대적인 사용자 경험
```

---

### 4. 배포 및 호스팅 전략

**결정**: API는 Vercel Serverless Functions, static-site는 GitHub Pages

**근거**:
- Vercel은 무료 티어로 충분 (월 100GB 대역폭, 100,000 요청)
- GitHub Pages는 무료로 정적 사이트 호스팅
- 별도의 서버 관리 불필요

**고려한 대안**:
- Google Cloud Run: 비용 발생, 현재 트래픽에 과도함
- AWS Lambda: Vercel이 더 간단하고 Next.js 통합 우수
- Heroku: 무료 티어 종료됨

**구현**:
```yaml
# Vercel 배포 (API + Next.js)
vercel.json:
{
  "rewrites": [
    { "source": "/api/:path*", "destination": "/api/:path*" }
  ]
}

# GitHub Pages 배포 (static-site)
.github/workflows/daily-podcast.yml:
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./static-site
```

---

### 5. 캐싱 및 성능 최적화

**결정**: 인메모리 캐싱 + CDN

**근거**:
- 파일 시스템 I/O는 느릴 수 있음
- 에피소드 데이터는 거의 변경되지 않음 (일일 1회)
- 간단한 딕셔너리 캐싱으로 충분

**고려한 대안**:
- Redis: 오버킬, 인프라 복잡도 증가
- 데이터베이스: 현재 규모에 불필요

**구현**:
```python
from functools import lru_cache
from datetime import datetime, timedelta

# 간단한 TTL 캐시
cache = {}
CACHE_TTL = timedelta(hours=1)

@lru_cache(maxsize=128)
def get_episode_cached(episode_id: str):
    # 파일 시스템 읽기를 캐싱
    file_path = PODCASTS_DIR / f"{episode_id}.json"
    with open(file_path) as f:
        return json.load(f)

# 또는 FastAPI Cache
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

FastAPICache.init(InMemoryBackend())

@app.get("/episodes")
@cache(expire=3600)  # 1시간 캐싱
async def list_episodes():
    pass
```

---

### 6. 모니터링 및 로깅

**결정**: FastAPI 내장 로깅 + Vercel Analytics

**근거**:
- 추가 인프라 불필요
- Vercel이 기본 분석 제공
- Python logging으로 충분

**고려한 대안**:
- Sentry: 현재 규모에 과도함
- Google Cloud Logging: 비용 발생

**구현**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

---

## 기술적 결정 요약

| 컴포넌트 | 기술 | 근거 |
|---------|------|------|
| 파이프라인 | 기존 `src/` 유지 | 완성되고 안정적, 변경 불필요 |
| API 프레임워크 | FastAPI | 경량, 자동 문서, 타입 힌트 |
| 데이터 저장 | JSON 파일 유지 | 간단, 현재 규모 충분, DB 불필요 |
| 프론트엔드 | static-site + Next.js (선택) | 유연성, 기존 기능 유지 |
| API 배포 | Vercel Serverless | 무료, 간단, Next.js 통합 |
| Static 배포 | GitHub Pages | 무료, 자동 배포 |
| 캐싱 | 인메모리 (lru_cache) | 간단, 충분한 성능 |
| 인증 | 없음 (읽기 전용 공개 API) | 현재 불필요 |

---

## 리스크 완화

### 높은 리스크 영역
1. **기존 파이프라인 중단**: API 추가로 인한 부작용
   - 완화: `src/`는 전혀 수정하지 않음
2. **파일 시스템 동시성**: API와 파이프라인이 동시 접근
   - 완화: API는 읽기만 하므로 충돌 없음
3. **배포 복잡도**: 두 개의 서비스 (API + static-site)
   - 완화: GitHub Actions에서 순차적으로 배포

### 대응 계획
1. **API 장애**: static-site는 독립적으로 작동
2. **파이프라인 실패**: 이전 에피소드는 계속 서비스됨
3. **호스팅 문제**: Vercel/GitHub Pages 장애 시 대체 호스팅 준비

---

## 다음 단계

1. **Phase 1**: data-model.md 작성 (기존 모델 활용)
2. **Phase 1**: API contracts 정의 (OpenAPI 스펙)
3. **Phase 1**: quickstart.md 작성 (API 실행 가이드)
4. **Phase 2**: tasks.md 생성 (구현 작업 분해)

---

**리서치 상태**: ✅ 완료  
**기술적 명확성**: ✅ 모두 해결됨  
**Phase 1 준비**: ✅ 완료
