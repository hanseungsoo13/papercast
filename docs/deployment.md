# 🚀 PaperCast 배포 및 운영 가이드

## 📋 목차
1. [현재 구조 분석](#현재-구조-분석)
2. [운영 환경 옵션](#운영-환경-옵션)
3. [권장 아키텍처](#권장-아키텍처)
4. [GitHub Actions 자동화](#github-actions-자동화)
5. [Google Cloud 활용](#google-cloud-활용)
6. [유지보수 전략](#유지보수-전략)

---

## 🔍 현재 구조 분석

### **개발 환경**
```
로컬 머신
├── python run.py          # 팟캐스트 생성
├── static-site/           # 정적 파일 생성
└── python dev_server.py   # 로컬 서버 (포트 8080)
```

### **문제점**
- ❌ 로컬에서만 접근 가능
- ❌ 서버 재시작 시 중단
- ❌ 확장성 부족
- ❌ SSL/HTTPS 미지원
- ❌ CDN 없음

---

## 🌐 운영 환경 옵션

### **Option 1: GitHub Pages (무료, 권장)**

```
GitHub Actions (매일 6AM)
    ↓ 팟캐스트 생성
Google Cloud Storage (MP3)
    ↓ 정적 사이트 생성
GitHub Pages (웹사이트 호스팅)
    ↓ 사용자 접근
https://username.github.io/papercast
```

**장점**:
- ✅ 완전 무료
- ✅ 자동 SSL/HTTPS
- ✅ CDN 제공
- ✅ 커스텀 도메인 지원
- ✅ GitHub Actions와 완벽 통합

**단점**:
- ❌ 정적 사이트만 가능
- ❌ 서버사이드 로직 불가

---

### **Option 2: Vercel/Netlify (무료 티어)**

```
GitHub Actions (팟캐스트 생성)
    ↓ Push to Repository
Vercel/Netlify (자동 배포)
    ↓ 글로벌 CDN
사용자 접근
```

**장점**:
- ✅ 자동 배포
- ✅ 글로벌 CDN
- ✅ 커스텀 도메인
- ✅ 프리뷰 배포

---

### **Option 3: Google Cloud Run (서버리스)**

```
GitHub Actions
    ↓ 컨테이너 빌드
Google Container Registry
    ↓ 배포
Google Cloud Run
    ↓ 오토스케일링
사용자 접근
```

**장점**:
- ✅ 서버사이드 로직 가능
- ✅ 오토스케일링
- ✅ 사용량 기반 과금

**단점**:
- ❌ 복잡성 증가
- ❌ 비용 발생 가능

---

### **Option 4: 전통적 VPS (Digital Ocean, AWS EC2)**

```
VPS 서버
├── Nginx (리버스 프록시)
├── PM2 (프로세스 관리)
├── Let's Encrypt (SSL)
└── 정적 파일 서빙
```

**장점**:
- ✅ 완전한 제어
- ✅ 서버사이드 로직

**단점**:
- ❌ 서버 관리 필요
- ❌ 보안 관리
- ❌ 비용

---

## 🎯 권장 아키텍처: GitHub Pages + Actions

### **전체 흐름**

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (매일 6AM)                  │
│                                                               │
│  1. 논문 수집 (Hugging Face)                                 │
│  2. 요약 생성 (Gemini Pro)                                   │
│  3. TTS 변환 (Google TTS)                                    │
│  4. MP3 업로드 (Google Cloud Storage)                       │
│  5. 정적 사이트 생성 (static-site/)                          │
│  6. GitHub Pages 배포 (gh-pages 브랜치)                     │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Pages                              │
│                                                               │
│  🌐 https://username.github.io/papercast                    │
│  📱 모바일/데스크톱 접근                                      │
│  🔒 자동 HTTPS                                               │
│  🚀 글로벌 CDN                                               │
└─────────────────────────────────────────────────────────────┘
```

### **구현 방법**

#### 1. GitHub Pages 설정

```bash
# gh-pages 브랜치 생성
git checkout --orphan gh-pages
git rm -rf .
echo "GitHub Pages" > index.html
git add index.html
git commit -m "Initial GitHub Pages"
git push origin gh-pages

# main 브랜치로 돌아가기
git checkout main
```

#### 2. GitHub Actions 워크플로우 수정

```yaml
# .github/workflows/daily-podcast.yml
name: Daily Podcast Generation and Deployment

on:
  schedule:
    - cron: '0 21 * * *'  # 매일 6AM KST
  workflow_dispatch:

jobs:
  generate-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Setup credentials
      run: |
        echo "${{ secrets.GCP_SERVICE_ACCOUNT_KEY }}" | base64 -d > credentials/service-account.json
    
    - name: Generate podcast and site
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        GOOGLE_APPLICATION_CREDENTIALS: credentials/service-account.json
        GCS_BUCKET_NAME: ${{ secrets.GCS_BUCKET_NAME }}
      run: |
        python run.py
    
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./static-site
        publish_branch: gh-pages
        cname: papercast.yourdomain.com  # 선택사항
```

#### 3. Repository 설정

```bash
# Repository Settings → Pages
# Source: Deploy from a branch
# Branch: gh-pages / (root)
```

---

## 🔧 유지보수 전략

### **1. 모니터링**

```yaml
# 워크플로우에 알림 추가
- name: Notify on failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### **2. 로그 관리**

```python
# src/utils/logger.py 개선
import logging
from datetime import datetime

def setup_production_logger():
    """운영 환경용 로거 설정"""
    logger = logging.getLogger('papercast')
    
    # GitHub Actions에서는 stdout으로
    if os.getenv('GITHUB_ACTIONS'):
        handler = logging.StreamHandler()
    else:
        # 로컬에서는 파일로
        handler = logging.FileHandler(f'logs/{datetime.now():%Y%m%d}.log')
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    return logger
```

### **3. 에러 처리**

```python
# src/main.py 개선
class PodcastPipeline:
    def run(self):
        try:
            # 기존 로직
            return podcast
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}")
            
            # Slack/Discord 알림
            self._send_alert(f"PaperCast 실패: {e}")
            
            # 이전 사이트 유지 (새 사이트 생성 실패 시)
            if os.path.exists('static-site-backup'):
                shutil.copytree('static-site-backup', 'static-site')
            
            raise
    
    def _send_alert(self, message):
        """알림 전송"""
        if webhook_url := os.getenv('SLACK_WEBHOOK_URL'):
            requests.post(webhook_url, json={'text': message})
```

### **4. 성능 최적화**

```python
# 캐싱 전략
class PaperCollector:
    def fetch_papers(self):
        cache_file = f"cache/papers_{date.today()}.json"
        
        if os.path.exists(cache_file):
            # 캐시된 데이터 사용
            with open(cache_file) as f:
                return json.load(f)
        
        # 새로 수집
        papers = self._scrape_papers()
        
        # 캐시 저장
        with open(cache_file, 'w') as f:
            json.dump(papers, f)
        
        return papers
```

---

## 💰 비용 분석

### **GitHub Pages 방식 (권장)**

| 서비스 | 비용 | 사용량 |
|--------|------|--------|
| GitHub Actions | 무료 | 2000분/월 (충분) |
| GitHub Pages | 무료 | 100GB 대역폭 |
| Google Cloud Storage | ~$1/월 | MP3 파일 저장 |
| Gemini Pro API | ~$2/월 | 일 3회 요약 |
| Google TTS | ~$1/월 | 일 3회 음성변환 |
| **총합** | **~$4/월** | |

### **Vercel/Netlify 방식**

| 서비스 | 비용 | 사용량 |
|--------|------|--------|
| Vercel/Netlify | 무료 | 100GB 대역폭 |
| 기타 | 동일 | 동일 |
| **총합** | **~$4/월** | |

### **Google Cloud Run 방식**

| 서비스 | 비용 | 사용량 |
|--------|------|--------|
| Cloud Run | ~$5/월 | 항상 실행 시 |
| 기타 | 동일 | 동일 |
| **총합** | **~$9/월** | |

---

## 🛠️ 실제 구현 단계

### **Phase 1: GitHub Pages 배포 (1시간)**

```bash
# 1. GitHub Pages 활성화
# Repository → Settings → Pages → Source: gh-pages

# 2. 워크플로우 수정
# .github/workflows/daily-podcast.yml 업데이트

# 3. 테스트
git push origin main
# Actions 탭에서 실행 확인
```

### **Phase 2: 커스텀 도메인 (선택사항)**

```bash
# 1. 도메인 구매 (예: papercast.com)
# 2. DNS 설정
# CNAME: www → username.github.io
# 3. GitHub Pages에서 커스텀 도메인 설정
```

### **Phase 3: 모니터링 추가**

```bash
# 1. Slack/Discord 웹훅 설정
# 2. 알림 로직 추가
# 3. 헬스체크 구현
```

---

## 🔄 regenerate_site.py 개선안

현재 파일을 개발 전용으로 명확히 하고, 운영에서는 제거:

```python
# scripts/dev-regenerate.py (개발 전용)
#!/usr/bin/env python3
"""개발 전용: 사이트 재생성 스크립트"""

import os
import sys

# 운영 환경에서는 실행 금지
if os.getenv('GITHUB_ACTIONS') or os.getenv('PRODUCTION'):
    print("❌ 이 스크립트는 개발 환경에서만 사용하세요.")
    print("운영 환경에서는 'python run.py'를 사용하세요.")
    sys.exit(1)

# 기존 로직...
```

---

## 📊 권장 사항 요약

### **즉시 적용 (우선순위 높음)**

1. ✅ **GitHub Pages 배포 설정**
   - 무료, 안정적, 자동 SSL
   - 예상 작업시간: 1시간

2. ✅ **워크플로우 개선**
   - 배포 자동화 추가
   - 예상 작업시간: 30분

3. ✅ **regenerate_site.py → 개발 전용으로 이동**
   - `scripts/dev-regenerate.py`로 이동
   - 운영 환경에서 실행 방지

### **중기 적용 (우선순위 중간)**

4. ⏳ **모니터링 추가**
   - Slack/Discord 알림
   - 예상 작업시간: 2시간

5. ⏳ **에러 처리 강화**
   - 실패 시 이전 사이트 유지
   - 예상 작업시간: 1시간

### **장기 적용 (우선순위 낮음)**

6. 🔮 **커스텀 도메인**
   - papercast.com 같은 도메인
   - 비용: ~$10/년

7. 🔮 **성능 최적화**
   - 캐싱, 압축 등
   - 필요 시 적용

---

## 🎯 결론

### **regenerate_site.py 필요성**
- 개발 환경: ✅ 유용함 (빠른 테스트)
- 운영 환경: ❌ 불필요함 (항상 전체 파이프라인)

### **운영 환경 권장사항**
1. **GitHub Pages + Actions** (무료, 안정적)
2. 커스텀 도메인 추가 (선택사항)
3. 모니터링 및 알림 구축
4. 에러 처리 강화

### **유지보수 전략**
- 자동화 우선 (수동 작업 최소화)
- 모니터링 및 알림 필수
- 점진적 개선 (한 번에 모든 것을 바꾸지 말고)

**총 예상 비용**: 월 $4 (매우 저렴)
**총 구축 시간**: 2-3시간 (매우 빠름)

---

이제 실제로 GitHub Pages 배포를 구현해볼까요? 🚀
