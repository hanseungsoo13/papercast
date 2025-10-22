# Implementation Plan: HuggingFace Podcast Automation

**Branch**: `001-huggingface-podcast-automation` | **Date**: 2025-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-huggingface-podcast-automation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

매일 아침 자동으로 Hugging Face 트렌딩 논문 Top 3를 수집하여 Gemini Pro로 요약하고, Google TTS로 음성 변환한 후 Google Cloud Storage에 업로드하여 공유 플랫폼에서 재생/다운로드 가능하게 만드는 자동화 팟캐스트 서비스입니다. 모든 과정은 GitHub Actions가 자동으로 수행합니다.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: huggingface-hub (공식 SDK), google-generativeai (Gemini Pro), google-cloud-texttospeech, google-cloud-storage, requests, pydantic, tenacity (재시도), pytest  
**Storage**: 파일 기반 (JSON for metadata, MP3 for audio, Google Cloud Storage for hosting)  
**Testing**: pytest + pytest-mock + pytest-cov  
**Target Platform**: GitHub Actions (Ubuntu latest runner), 정적 사이트 호스팅 (GitHub Pages 우선, Cloudflare Pages 대안)  
**Project Type**: single (automation script + static site)  
**Performance Goals**: 전체 프로세스 30분 이내 완료, 일일 1회 실행 (매일 아침 6시 KST)  
**Constraints**: API 할당량 관리 (Gemini: 60req/min, TTS: 무료티어), GitHub Actions 실행 시간 제한, exponential backoff 재시도  
**Scale/Scope**: 일일 1개 팟캐스트 생성, 30일 히스토리 유지 (GCS 라이프사이클 정책), 논문 3개 처리

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Code Quality Standards
- [x] 모든 코드 변경사항이 명확성, 유지보수성, 확장성을 보장하는가?
  - 각 단계별 모듈화된 함수 구조
  - 명확한 에러 핸들링 및 로깅
- [x] 복잡성이 정당화되었는가? YAGNI 원칙을 준수하는가?
  - 필요한 기능만 구현 (수집 → 요약 → 음성 변환 → 업로드 → 공유)
  - 단순한 스케줄링 및 자동화

### Testing Standards
- [x] TDD 접근법이 계획되었는가? (테스트 우선 작성)
  - 각 단계별 단위 테스트 (수집, 요약, TTS, 업로드)
  - API 모킹을 통한 통합 테스트
- [x] 테스트 커버리지 80% 이상 목표가 설정되었는가?
  - 핵심 비즈니스 로직 100% 커버리지 목표
- [x] 단위, 통합, 계약, E2E 테스트가 모두 계획되었는가?
  - 단위: 각 함수별 테스트
  - 통합: API 연동 테스트 (모킹)
  - 계약: 외부 API 응답 검증
  - E2E: 전체 파이프라인 테스트

### User Experience Consistency
- [x] 사용자 여정이 3클릭 이내로 완료 가능한가?
  - 플랫폼 접속 → 최신 팟캐스트 클릭 → 재생/다운로드
- [x] 일관된 UI/UX 패턴이 정의되었는가?
  - 단순한 정적 사이트 구조
  - 표준 HTML5 오디오 플레이어 사용
- [x] 접근성 표준(WCAG 2.1 AA) 준수가 계획되었는가?
  - 시맨틱 HTML 사용
  - 키보드 네비게이션 지원

### Performance Requirements
- [x] API 응답 시간 200ms 이내 목표가 설정되었는가?
  - 정적 사이트이므로 CDN을 통한 빠른 응답 보장
- [x] 페이지 로딩 시간 2초 이내 목표가 설정되었는가?
  - 경량 HTML/CSS/JS 사용
- [x] 동시 사용자 1000명 지원이 계획되었는가?
  - CDN (Cloudflare 또는 GitHub Pages)을 통한 확장성 보장

## Project Structure

### Documentation (this feature)

```
specs/001-huggingface-podcast-automation/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
src/
├── models/              # 데이터 모델 (Paper, Podcast, ProcessingLog)
├── services/            # 핵심 서비스 로직
│   ├── collector.py     # Hugging Face 논문 수집
│   ├── summarizer.py    # Gemini Pro 요약 생성
│   ├── tts.py           # Google TTS 음성 변환
│   ├── uploader.py      # Google Cloud Storage 업로드
│   └── generator.py     # 정적 사이트 생성
├── utils/               # 유틸리티 함수
│   ├── logger.py        # 로깅
│   ├── retry.py         # 재시도 메커니즘
│   └── config.py        # 설정 관리
└── main.py              # 메인 실행 스크립트

tests/
├── unit/                # 단위 테스트
│   ├── test_collector.py
│   ├── test_summarizer.py
│   ├── test_tts.py
│   └── test_uploader.py
├── integration/         # 통합 테스트
│   └── test_pipeline.py
└── contract/            # 계약 테스트
    ├── test_huggingface_api.py
    ├── test_gemini_api.py
    └── test_gcs_api.py

.github/
└── workflows/
    └── daily-podcast.yml  # GitHub Actions 워크플로우

static-site/             # 정적 사이트 소스
├── index.html
├── styles.css
├── script.js
└── podcasts/            # 생성된 팟캐스트 메타데이터
    └── index.json
```

**Structure Decision**: Single project 구조를 선택했습니다. 이는 자동화 스크립트와 정적 사이트 생성을 포함하는 단일 Python 프로젝트로, GitHub Actions를 통해 실행되고 결과물을 정적 사이트로 배포합니다.

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

해당 사항 없음 - 모든 헌장 체크 항목을 통과했습니다.