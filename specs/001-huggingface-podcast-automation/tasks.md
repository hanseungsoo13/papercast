# 구현 작업 목록: PaperCast API 레이어 추가

**날짜**: 2025-01-27  
**기능**: 001-huggingface-podcast-automation  
**상태**: 계획 완료, 구현 대기

## 작업 개요

기존 `src/` 파이프라인을 유지하면서 FastAPI 웹 API 레이어를 추가합니다.

## Phase 1: 프로젝트 정리 및 준비

### Task 1.1: backend/ 폴더 정리
- **설명**: 중복 생성된 backend/ 폴더 삭제
- **우선순위**: P0 (즉시)
- **예상 시간**: 5분
- **작업**:
  - [x] `backend/` 폴더 전체 삭제
  - [x] `.gitignore` 확인 (backend/ 제외 규칙 제거)

### Task 1.2: api/ 폴더 구조 생성
- **설명**: 새로운 API 디렉토리 구조 생성
- **우선순위**: P0 (즉시)
- **예상 시간**: 10분
- **작업**:
  - [x] `api/` 폴더 생성
  - [x] `api/__init__.py` 생성
  - [x] `api/routes/` 폴더 생성
  - [x] `tests/api/` 폴더 생성

### Task 1.3: 의존성 업데이트
- **설명**: requirements.txt에 FastAPI 추가
- **우선순위**: P0 (즉시)
- **예상 시간**: 5분
- **작업**:
  - [x] `fastapi` 추가
  - [x] `uvicorn[standard]` 추가
  - [x] 중복 의존성 제거

---

## Phase 2: API 레이어 구현

### Task 2.1: Repository 패턴 구현
- **설명**: JSON 파일 기반 데이터 접근 레이어
- **우선순위**: P0 (핵심)
- **예상 시간**: 30분
- **파일**: `api/repository.py`
- **작업**:
  - [x] `PodcastRepository` 클래스 생성
  - [x] `find_all()` 메서드 구현
  - [x] `find_by_id()` 메서드 구현
  - [x] `find_latest()` 메서드 구현
  - [x] LRU 캐싱 추가
  - [x] 단위 테스트 작성

**테스트 케이스**:
```python
def test_find_all_returns_sorted_podcasts()
def test_find_by_id_returns_podcast()
def test_find_by_id_returns_none_when_not_found()
def test_find_latest_returns_most_recent()
def test_caching_reduces_file_reads()
```

### Task 2.2: Pydantic 스키마 정의
- **설명**: API 응답용 스키마
- **우선순위**: P0 (핵심)
- **예상 시간**: 20분
- **파일**: `api/schemas.py`
- **작업**:
  - [x] `EpisodeResponse` 스키마 정의
  - [x] `EpisodeDetailResponse` 스키마 정의
  - [x] `Paper` 스키마 (기존 모델 재사용)
  - [x] `from_podcast()` 변환 메서드
  - [x] 단위 테스트 작성

### Task 2.3: FastAPI 메인 앱 구현
- **설명**: FastAPI 앱 초기화 및 설정
- **우선순위**: P0 (핵심)
- **예상 시간**: 30분
- **파일**: `api/main.py`
- **작업**:
  - [x] FastAPI 앱 생성
  - [x] CORS 설정
  - [x] 라우터 등록
  - [x] 에러 핸들러 추가
  - [x] startup/shutdown 이벤트

**코드 스니펫**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="PaperCast API",
    description="AI 논문 팟캐스트 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_methods=["GET"],
    allow_headers=["*"]
)
```

### Task 2.4: 헬스 체크 엔드포인트
- **설명**: /api/health 엔드포인트 구현
- **우선순위**: P1 (높음)
- **예상 시간**: 15분
- **파일**: `api/routes/health.py`
- **작업**:
  - [ ] 헬스 체크 라우터 생성
  - [ ] 버전 정보 포함
  - [ ] 데이터 디렉토리 존재 확인
  - [ ] 테스트 작성

### Task 2.5: 에피소드 엔드포인트
- **설명**: /api/episodes 관련 엔드포인트
- **우선순위**: P0 (핵심)
- **예상 시간**: 1시간
- **파일**: `api/routes/episodes.py`
- **작업**:
  - [ ] `GET /api/episodes` (목록)
  - [ ] `GET /api/episodes/latest` (최신)
  - [ ] `GET /api/episodes/{id}` (상세)
  - [ ] 페이지네이션 구현
  - [ ] 404 에러 처리
  - [ ] 통합 테스트 작성

**엔드포인트 상세**:
```python
@router.get("/episodes")
async def list_episodes(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    repo: PodcastRepository = Depends(get_repository)
):
    podcasts = repo.find_all()
    total = len(podcasts)
    paginated = podcasts[offset:offset+limit]
    
    return {
        "episodes": [EpisodeResponse.from_podcast(p) for p in paginated],
        "total": total,
        "limit": limit,
        "offset": offset
    }
```

### Task 2.6: 의존성 주입 설정
- **설명**: FastAPI 의존성 주입 패턴
- **우선순위**: P1 (높음)
- **예상 시간**: 20분
- **파일**: `api/dependencies.py`
- **작업**:
  - [ ] `get_repository()` 의존성 함수
  - [ ] `get_config()` 의존성 함수
  - [ ] 싱글톤 패턴 적용

---

## Phase 3: 프론트엔드 연동

### Task 3.1: Next.js API 라우트 설정
- **설명**: Next.js에서 FastAPI 프록시
- **우선순위**: P2 (중간)
- **예상 시간**: 30분
- **파일**: `frontend/next.config.js`
- **작업**:
  - [x] rewrites 설정으로 `/api` → FastAPI 프록시
  - [x] 환경 변수 설정
  - [x] CORS 처리

### Task 3.2: API 클라이언트 수정
- **설명**: 기존 static-site 대신 API 호출
- **우선순위**: P2 (중간)
- **예상 시간**: 1시간
- **파일**: `frontend/src/services/api.ts`
- **작업**:
  - [x] `getEpisodes()` 함수 API 연결
  - [x] `getLatestEpisode()` 함수 API 연결
  - [x] `getEpisode(id)` 함수 API 연결
  - [x] 에러 처리
  - [x] 타입 정의 업데이트

### Task 3.3: 홈 페이지 API 연동
- **설명**: 홈 페이지를 API 기반으로 변경
- **우선순위**: P2 (중간)
- **예상 시간**: 1시간
- **파일**: `frontend/src/pages/index.tsx`
- **작업**:
  - [x] API 호출로 데이터 가져오기
  - [x] 로딩 상태 처리
  - [x] 에러 상태 처리
  - [x] 기존 UI 유지

---

## Phase 4: 배포 설정

### Task 4.1: Vercel 설정
- **설명**: Vercel에 API + Frontend 배포
- **우선순위**: P2 (중간)
- **예상 시간**: 30분
- **작업**:
  - [ ] `vercel.json` 파일 생성
  - [ ] API 라우트 설정
  - [ ] 환경 변수 설정
  - [ ] 빌드 스크립트 설정

**vercel.json**:
```json
{
  "buildCommand": "cd frontend && npm run build",
  "devCommand": "cd frontend && npm run dev",
  "installCommand": "pip install -r requirements.txt && cd frontend && npm install",
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/:path*"
    }
  ]
}
```

### Task 4.2: GitHub Actions 업데이트
- **설명**: 기존 워크플로우는 유지, API 배포만 추가
- **우선순위**: P2 (중간)
- **예상 시간**: 30분
- **파일**: `.github/workflows/daily-podcast.yml`
- **작업**:
  - [ ] Vercel 배포 스텝 추가
  - [ ] 기존 static-site 배포 유지
  - [ ] 환경 변수 설정

---

## Phase 5: 테스트 및 문서화

### Task 5.1: API 테스트 작성
- **설명**: 전체 API 엔드포인트 테스트
- **우선순위**: P1 (높음)
- **예상 시간**: 2시간
- **폴더**: `tests/api/`
- **작업**:
  - [ ] 헬스 체크 테스트
  - [ ] 에피소드 목록 테스트
  - [ ] 에피소드 상세 테스트
  - [ ] 404 에러 테스트
  - [ ] 페이지네이션 테스트

### Task 5.2: README 한글화
- **설명**: README.md 전체를 한글로 재작성
- **우선순위**: P1 (높음)
- **예상 시간**: 1시간
- **파일**: `README.md`
- **작업**:
  - [ ] 프로젝트 소개 한글화
  - [ ] 설치 가이드 한글화
  - [ ] API 사용법 추가
  - [ ] 아키텍처 다이어그램 업데이트

### Task 5.3: API 문서 작성
- **설명**: FastAPI 자동 생성 문서 보완
- **우선순위**: P2 (중간)
- **예상 시간**: 30분
- **작업**:
  - [ ] 엔드포인트 설명 추가
  - [ ] 예시 요청/응답 추가
  - [ ] 에러 코드 문서화

---

## Phase 6: 옵티마이제이션

### Task 6.1: 캐싱 개선
- **설명**: API 응답 캐싱 최적화
- **우선순위**: P3 (낮음)
- **예상 시간**: 1시간
- **작업**:
  - [ ] FastAPI-Cache 통합
  - [ ] TTL 설정 최적화
  - [ ] 캐시 무효화 로직

### Task 6.2: 성능 테스트
- **설명**: API 성능 벤치마크
- **우선순위**: P3 (낮음)
- **예상 시간**: 1시간
- **작업**:
  - [ ] Locust 스크립트 작성
  - [ ] 성능 목표 검증 (<200ms)
  - [ ] 병목 지점 분석

---

## 작업 순서 (권장)

```
Day 1: 기초 설정
├─ Phase 1 (전체) - 30분
└─ Task 2.1-2.2   - 50분

Day 2: API 구현
├─ Task 2.3-2.5   - 2시간
└─ Task 2.6       - 20분

Day 3: 프론트엔드 연동
├─ Phase 3 (전체) - 2.5시간
└─ Task 5.2       - 1시간

Day 4: 배포 및 테스트
├─ Phase 4 (전체) - 1시간
└─ Task 5.1, 5.3  - 2.5시간

Day 5: 최적화 (선택)
└─ Phase 6 (전체) - 2시간
```

## 완료 기준

### Phase 1-2 완료
- [ ] API 서버가 로컬에서 실행됨
- [ ] `/api/health` 엔드포인트 200 응답
- [ ] `/api/episodes` 엔드포인트가 JSON 반환
- [ ] 단위 테스트 통과

### Phase 3 완료
- [ ] 프론트엔드가 API에서 데이터 가져옴
- [ ] 기존 static-site와 동일한 UI
- [ ] 에러 처리 완료

### Phase 4 완료
- [ ] Vercel에 배포 성공
- [ ] 프로덕션 URL 접근 가능
- [ ] GitHub Actions 정상 동작

### 전체 완료
- [ ] 모든 테스트 통과
- [ ] 문서 업데이트 완료
- [ ] 성능 목표 달성 (<200ms)

---

**작업 목록 상태**: ✅ 완료  
**구현 준비**: ✅ 완료  
**구현 시작**: ⏳ 대기 중 (implement 명령 대기)
