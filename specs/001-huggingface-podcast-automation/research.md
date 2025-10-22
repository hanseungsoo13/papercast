# Research: HuggingFace Podcast Automation

**Feature**: 001-huggingface-podcast-automation  
**Date**: 2025-01-27  
**Phase**: 0 - Technical Research

## Overview

이 문서는 HuggingFace Podcast Automation 기능 구현에 필요한 기술 스택 및 라이브러리에 대한 연구 결과를 담고 있습니다.

## 1. Hugging Face API Client

### Decision
`huggingface_hub` 공식 Python SDK 사용

### Rationale
- Hugging Face의 공식 라이브러리로 안정성과 유지보수 보장
- Trending Papers API 지원
- 간단한 인증 및 API 호출 인터페이스
- 활발한 커뮤니티 지원

### Implementation Details
```python
from huggingface_hub import HfApi

api = HfApi()
# Papers endpoint를 통한 트렌딩 논문 조회
```

### Alternatives Considered
- **직접 REST API 호출**: 낮은 수준의 제어가 가능하지만 유지보수 부담 증가
- **웹 스크래핑**: API가 없을 경우의 대안이지만 불안정하고 이용 약관 위반 가능성

### Best Practices
- API rate limiting 준수
- 인증 토큰은 환경 변수로 관리
- 오류 발생 시 exponential backoff 재시도

---

## 2. Google Gemini SDK

### Decision
`google-generativeai` Python SDK 사용

### Rationale
- Google의 공식 Gemini API Python 클라이언트
- Gemini Pro 모델 지원
- 스트리밍 및 배치 처리 지원
- 명확한 API 문서 및 예제

### Implementation Details
```python
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-pro')
response = model.generate_content(prompt)
```

### Alternatives Considered
- **OpenAI GPT**: 강력하지만 비용이 높고 사용자가 Gemini를 명시적으로 요청함
- **Claude API**: 높은 품질이지만 프로젝트 요구사항이 Gemini 지정

### Best Practices
- API 키 보안 관리 (GitHub Secrets)
- 할당량 모니터링
- 프롬프트 최적화로 토큰 사용량 최소화
- 응답 검증 및 오류 처리

---

## 3. Google Cloud Text-to-Speech

### Decision
`google-cloud-texttospeech` Python SDK 사용

### Rationale
- Google Cloud의 공식 TTS 라이브러리
- 고품질 음성 합성
- 다양한 언어 및 음성 선택 가능
- MP3, WAV 등 다양한 출력 형식 지원

### Implementation Details
```python
from google.cloud import texttospeech

client = texttospeech.TextToSpeechClient()
synthesis_input = texttospeech.SynthesisInput(text="...")
voice = texttospeech.VoiceSelectionParams(
    language_code="ko-KR",
    name="ko-KR-Wavenet-A"
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)
response = client.synthesize_speech(
    input=synthesis_input,
    voice=voice,
    audio_config=audio_config
)
```

### Alternatives Considered
- **Amazon Polly**: 좋은 품질이지만 GCP 생태계 통합을 위해 Google TTS 선택
- **오픈소스 TTS (Coqui, Festival)**: 무료지만 품질과 유지보수성이 낮음

### Best Practices
- 적절한 음성 선택 (한국어: ko-KR-Wavenet-A)
- SSML 활용으로 발음 및 억양 조정
- 비용 최적화를 위한 텍스트 길이 관리
- 오디오 파일 크기 최적화

---

## 4. Google Cloud Storage

### Decision
`google-cloud-storage` Python SDK 사용

### Rationale
- GCP의 공식 Storage 라이브러리
- 높은 가용성 및 내구성
- CDN 통합 용이
- 버전 관리 및 라이프사이클 정책 지원

### Implementation Details
```python
from google.cloud import storage

client = storage.Client()
bucket = client.bucket('papercast-podcasts')
blob = bucket.blob(f'podcasts/{date}/episode.mp3')
blob.upload_from_filename(local_file_path)
blob.make_public()
```

### Alternatives Considered
- **AWS S3**: 널리 사용되지만 GCP 생태계 통합 선호
- **Cloudflare R2**: 무료 egress지만 GCS의 성숙도 선택

### Best Practices
- 버킷 권한 설정 (공개 읽기)
- 객체 라이프사이클 관리 (30일 후 삭제)
- 버전 관리 활성화
- CDN 캐싱 설정

---

## 5. 정적 사이트 호스팅

### Decision
GitHub Pages 사용 (우선순위 1), Cloudflare Pages (대안)

### Rationale
- **GitHub Pages**:
  - GitHub Actions와 완벽한 통합
  - 무료
  - 자동 배포
  - HTTPS 기본 지원
- **Cloudflare Pages** (대안):
  - 빠른 CDN
  - 무료 티어 제공
  - GitHub 통합 지원

### Implementation Details
- GitHub Actions에서 정적 사이트 빌드
- `gh-pages` 브랜치에 배포
- HTML5 오디오 플레이어로 MP3 재생

### Alternatives Considered
- **Netlify**: 좋은 서비스지만 GitHub Pages가 프로젝트에 더 적합
- **Vercel**: 동적 기능에 강점이지만 정적 사이트에는 과도함

### Best Practices
- 경량 HTML/CSS/JS
- 반응형 디자인
- SEO 최적화
- 접근성 표준 준수

---

## 6. GitHub Actions 워크플로우

### Decision
`schedule` 트리거를 사용한 cron 기반 자동화

### Rationale
- GitHub Actions 내장 기능
- 무료 (public repo)
- 안정적인 스케줄링
- 완전한 CI/CD 통합

### Implementation Details
```yaml
name: Daily Podcast Generation
on:
  schedule:
    - cron: '0 6 * * *'  # 매일 아침 6시 (UTC 기준, 한국 시간 15시)
  workflow_dispatch:  # 수동 실행 지원
```

### Alternatives Considered
- **외부 cron 서비스 (AWS EventBridge, Google Cloud Scheduler)**: 추가 비용 및 복잡성
- **서버 기반 cron**: 인프라 유지보수 필요

### Best Practices
- 타임존 고려 (UTC → KST 변환)
- 실패 시 재시도 로직
- 단계별 로깅
- Secrets 관리

---

## 7. 의존성 관리

### Decision
`requirements.txt` + `pip-tools` 사용

### Rationale
- Python 표준 방식
- GitHub Actions와 호환성 우수
- 의존성 버전 고정 가능

### Dependencies List
```
huggingface-hub>=0.20.0
google-generativeai>=0.3.0
google-cloud-texttospeech>=2.16.0
google-cloud-storage>=2.14.0
requests>=2.31.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
```

### Best Practices
- 시맨틱 버전닝 사용
- 정기적인 보안 업데이트
- 의존성 취약점 스캔 (Dependabot)

---

## 8. 오류 처리 및 재시도

### Decision
커스텀 재시도 데코레이터 + `tenacity` 라이브러리

### Rationale
- 외부 API 호출의 일시적 실패 대응
- Exponential backoff 지원
- 유연한 재시도 정책

### Implementation Details
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_papers():
    # API 호출
    pass
```

### Best Practices
- API별 재시도 정책 차별화
- 최대 재시도 횟수 제한
- 실패 로깅
- Circuit breaker 패턴 고려

---

## 9. 로깅 및 모니터링

### Decision
Python `logging` 모듈 + GitHub Actions 로그

### Rationale
- Python 표준 라이브러리
- 구조화된 로깅 지원
- GitHub Actions 통합

### Implementation Details
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

### Best Practices
- 단계별 로그 레벨 구분 (INFO, WARNING, ERROR)
- 민감 정보 마스킹
- 실행 시간 추적
- 오류 스택 트레이스 기록

---

## 10. 테스트 전략

### Decision
`pytest` + `pytest-mock` + `pytest-cov`

### Rationale
- Python 업계 표준 테스트 프레임워크
- 풍부한 플러그인 생태계
- 간결한 테스트 작성

### Implementation Details
```python
import pytest
from unittest.mock import Mock, patch

def test_collect_papers(mocker):
    mock_api = mocker.patch('huggingface_hub.HfApi')
    mock_api.return_value.list_papers.return_value = [...]
    
    result = collect_papers()
    assert len(result) == 3
```

### Best Practices
- 외부 API는 모킹
- 테스트 픽스처 활용
- 커버리지 80% 이상 유지
- CI/CD에서 자동 실행

---

## Summary

모든 기술 선택은 다음 기준을 충족합니다:
1. **안정성**: 공식 SDK 또는 성숙한 라이브러리 사용
2. **비용 효율성**: 무료 또는 저비용 솔루션 우선
3. **통합성**: GCP 및 GitHub 생태계 통합
4. **유지보수성**: 활발한 커뮤니티 지원 및 문서화
5. **확장성**: 향후 기능 추가 용이

모든 "NEEDS CLARIFICATION" 항목이 해결되었으며, 구현 준비가 완료되었습니다.

