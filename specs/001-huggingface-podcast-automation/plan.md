# Implementation Plan: PaperCast API 레이어 추가 및 리팩토링

**Branch**: `001-huggingface-podcast-automation` | **Date**: 2025-01-27 | **Spec**: [spec.md](spec.md)
**Input**: 기존 파이프라인 유지 + FastAPI 웹 API 추가

**Note**: 기존 완성된 `src/` 파이프라인을 활용하여 웹 API 레이어만 추가하는 점진적 리팩토링

## Summary

기존 완성된 논문 수집 → 요약 → TTS → 업로드 → 사이트 생성 파이프라인(`src/`)은 그대로 유지하고, 생성된 데이터를 제공하는 FastAPI 웹 API 레이어(`api/`)를 추가합니다. 프론트엔드는 API를 통해 데이터를 조회하고, GitHub Actions는 기존 파이프라인을 계속 사용합니다.

## Technical Context

**Language/Version**: Python 3.11+ (백엔드), Node.js 18+ (프론트엔드)  
**Primary Dependencies**: FastAPI (신규), 기존 services (collector, summarizer, tts, uploader, generator) 재사용  
**Storage**: 기존 JSON 파일 기반 (data/podcasts/*.json) 유지, PostgreSQL은 선택사항  
**Testing**: pytest (기존 테스트 유지 + API 테스트 추가)  
**Target Platform**: 기존 GitHub Actions + 새로운 웹 API 서버  
**Project Type**: 하이브리드 (기존 단일 파이프라인 + 새로운 웹 API)  
**Performance Goals**: API 응답 <200ms, 파이프라인 실행 <30분  
**Constraints**: 기존 코드 최대한 재사용, 파이프라인 동작 방식 변경 없음  
**Scale/Scope**: 일일 1개 팟캐스트, 연간 365개 에피소드, API 동시 사용자 100명

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality Standards
- [x] 모든 코드 변경사항이 명확성, 유지보수성, 확장성을 보장하는가?
  - ✅ 기존 코드 재사용으로 복잡성 최소화
- [x] 복잡성이 정당화되었는가? YAGNI 원칙을 준수하는가?
  - ✅ API 레이어만 추가, 기존 파이프라인 유지

### Testing Standards
- [x] TDD 접근법이 계획되었는가? (테스트 우선 작성)
  - ✅ 기존 테스트 유지 + API 테스트 추가
- [x] 테스트 커버리지 80% 이상 목표가 설정되었는가?
  - ✅ 기존 커버리지 유지 + API 엔드포인트 테스트
- [x] 단위, 통합, 계약, E2E 테스트가 모두 계획되었는가?
  - ✅ 기존 테스트 구조 그대로 활용

### User Experience Consistency
- [x] 사용자 여정이 3클릭 이내로 완료 가능한가?
  - ✅ 홈 → 에피소드 → 재생 (2클릭)
- [x] 일관된 UI/UX 패턴이 정의되었는가?
  - ✅ 기존 static-site 디자인 활용
- [x] 접근성 표준(WCAG 2.1 AA) 준수가 계획되었는가?
  - ✅ 기존 접근성 표준 유지

### Performance Requirements
- [x] API 응답 시간 200ms 이내 목표가 설정되었는가?
  - ✅ JSON 파일 기반으로 빠른 응답 보장
- [x] 페이지 로딩 시간 2초 이내 목표가 설정되었는가?
  - ✅ 기존 static-site 성능 유지
- [x] 동시 사용자 1000명 지원이 계획되었는가?
  - ⚠️ 현재는 100명 목표 (정적 파일 서빙으로 충분)

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
papercast/
│
├── src/                          # 기존 파이프라인 (유지)
│   ├── models/                   # Paper, Podcast, ProcessingLog
│   │   ├── paper.py
│   │   ├── podcast.py
│   │   └── processing_log.py
│   ├── services/                 # 비즈니스 로직
│   │   ├── collector.py          # Hugging Face 스크래핑
│   │   ├── summarizer.py         # Gemini Pro 요약
│   │   ├── tts.py                # Google TTS 변환
│   │   ├── uploader.py           # GCS 업로드
│   │   └── generator.py          # Static Site 생성
│   ├── utils/                    # 유틸리티
│   │   ├── config.py
│   │   └── logger.py
│   └── main.py                   # 파이프라인 실행
│
├── api/                          # 신규: FastAPI 웹 API
│   ├── __init__.py
│   ├── main.py                   # FastAPI 앱
│   ├── schemas.py                # Pydantic 스키마
│   ├── routes/                   # API 라우터
│   │   ├── episodes.py           # GET /episodes
│   │   └── health.py             # GET /health
│   └── dependencies.py           # DI & 유틸리티
│
├── frontend/                     # Next.js 프론트엔드
│   ├── src/
│   │   ├── components/           # React 컴포넌트
│   │   ├── pages/                # Next.js 페이지
│   │   ├── services/             # API 클라이언트
│   │   └── styles/               # CSS
│   ├── package.json
│   └── next.config.js
│
├── tests/                        # 기존 테스트 (유지)
│   ├── unit/                     # 파이프라인 단위 테스트
│   ├── integration/              # 통합 테스트
│   ├── contract/                 # Contract 테스트
│   └── api/                      # 신규: API 테스트
│
├── scripts/                      # 유틸리티 스크립트
│   ├── setup.sh
│   ├── dev-server.sh
│   └── dev-regenerate.py
│
├── data/                         # 데이터 저장소
│   ├── podcasts/                 # 팟캐스트 JSON
│   ├── audio/                    # 임시 오디오 파일
│   └── logs/                     # 로그 파일
│
├── static-site/                  # 생성된 정적 사이트
│   ├── index.html
│   ├── episodes/
│   └── assets/
│
├── .github/workflows/            # GitHub Actions
│   └── daily-podcast.yml         # 자동화 워크플로우
│
├── docs/                         # 문서
├── specs/                        # 기능 명세
├── requirements.txt              # Python 의존성
├── run.py                        # 파이프라인 실행 래퍼
└── README.md                     # 프로젝트 문서
```

**Structure Decision**: 
- **기존 `src/`**: 완성된 파이프라인 그대로 유지 (GitHub Actions에서 사용)
- **신규 `api/`**: FastAPI 웹 API 추가 (data/podcasts/*.json 읽기 전용)
- **기존 `frontend/`**: Next.js 유지하되 API 엔드포인트 연결
- **`backend/` 폴더 삭제**: 중복 제거

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

