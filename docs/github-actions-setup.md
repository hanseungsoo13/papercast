# GitHub Actions 설정 가이드

PaperCast의 GitHub Actions를 활성화하고 사용하는 방법입니다.

## 🎯 GitHub Actions란?

GitHub Actions는 GitHub에서 제공하는 CI/CD 플랫폼으로, 코드 변경, 일정(schedule) 등의 이벤트에 따라 자동으로 워크플로우를 실행할 수 있습니다.

**PaperCast에서의 활용**:
- 매일 아침 6시(KST)에 자동으로 팟캐스트 생성
- HuggingFace 논문 수집 → Gemini 요약 → TTS 변환 → GCS 업로드
- 성공/실패 시 Slack 알림

---

## 🔑 필수 설정: GitHub Secrets

### 1️⃣ Secrets 페이지로 이동

1. GitHub Repository로 이동: https://github.com/hanseungsoo13/papercast
2. **Settings** 탭 클릭
3. 좌측 메뉴에서 **Secrets and variables** → **Actions** 클릭
4. **New repository secret** 클릭

### 2️⃣ 필수 Secrets 추가

다음 4개의 Secrets를 추가해야 합니다:

#### Secret 1: `GEMINI_API_KEY`

**설명**: Google Gemini API 키 (논문 요약에 사용)

**발급 방법**:
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. **Create API Key** 클릭
3. 생성된 키 복사

**값 예시**:
```
AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

---

#### Secret 2: `GCP_SERVICE_ACCOUNT_KEY`

**설명**: GCP Service Account JSON (base64 인코딩)

**발급 방법**:
1. [GCP Console](https://console.cloud.google.com/) 접속
2. **IAM & Admin** → **Service Accounts** 클릭
3. Service Account 생성 또는 선택
4. **Keys** 탭 → **Add Key** → **Create new key** → **JSON** 선택
5. 다운로드된 JSON 파일을 base64로 인코딩:

**Linux/Mac**:
```bash
base64 -w 0 < service-account-key.json
# 또는
cat service-account-key.json | base64 -w 0
```

**Windows (PowerShell)**:
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("service-account-key.json"))
```

**결과 확인** (중요!):
```bash
# 인코딩된 값을 복사한 후, 디코딩해서 JSON이 맞는지 확인
echo "YOUR_BASE64_STRING" | base64 --decode | python3 -m json.tool
# JSON이 정상적으로 출력되면 OK!
```

**값 예시**:
```
eyJ0eXBlIjoic2VydmljZV9hY2NvdW50IiwicHJvamVjdF9pZCI6InBhcGVyY2FzdC0xMjM0NTYiLCAi...
```

**필요한 권한**:
- `Cloud Text-to-Speech User`
- `Storage Object Admin`

---

#### Secret 3: `GCS_BUCKET_NAME`

**설명**: Google Cloud Storage 버킷 이름

**생성 방법**:
1. [GCS Console](https://console.cloud.google.com/storage) 접속
2. **CREATE BUCKET** 클릭
3. 버킷 이름 입력 (전역적으로 고유해야 함)
4. Location: `asia-northeast3` (Seoul) 권장
5. **CREATE** 클릭

**값 예시**:
```
papercast-podcasts
```

또는
```
papercast-hanseungsoo13
```

---

#### Secret 4: `SLACK_WEBHOOK_URL` (선택사항)

**설명**: Slack Webhook URL (알림용)

**발급 방법**:
1. [Slack API](https://api.slack.com/apps) 접속
2. **Create New App** → **From scratch**
3. App 이름: `PaperCast Bot`
4. Workspace 선택
5. **Incoming Webhooks** 활성화
6. **Add New Webhook to Workspace**
7. 채널 선택 (예: `#papercast`)
8. 생성된 Webhook URL 복사

**값 예시**:
```
https://hooks.slack.com/services/YOUR_TEAM_ID/YOUR_BOT_ID/YOUR_WEBHOOK_TOKEN
```

---

## ✅ Secrets 설정 확인

모든 Secrets를 추가한 후:

1. Repository → **Settings** → **Secrets and variables** → **Actions**
2. 다음 4개의 Secrets가 있는지 확인:
   - ✅ `GEMINI_API_KEY`
   - ✅ `GCP_SERVICE_ACCOUNT_KEY`
   - ✅ `GCS_BUCKET_NAME`
   - ✅ `SLACK_WEBHOOK_URL` (선택)

---

## 🚀 GitHub Actions 실행 방법

### 방법 1: 수동 실행 (테스트용)

1. Repository → **Actions** 탭 클릭
2. 좌측에서 **Daily Podcast Generation** 워크플로우 선택
3. **Run workflow** 버튼 클릭
4. Branch 선택: `main`
5. **Run workflow** 클릭

### 방법 2: 자동 실행 (프로덕션)

워크플로우는 다음 시간에 자동으로 실행됩니다:
- **매일 21:00 UTC** (= 한국시간 다음날 06:00 AM)

예시:
- 월요일 21:00 UTC = 화요일 06:00 KST
- 화요일 21:00 UTC = 수요일 06:00 KST

---

## 📊 실행 결과 확인

### Actions 로그 보기

1. Repository → **Actions** 탭
2. 최근 워크플로우 실행 클릭
3. 각 단계별 로그 확인:
   - ✅ Checkout code
   - ✅ Set up Python
   - ✅ Install dependencies
   - ✅ Configure GCP credentials
   - ✅ Run podcast generation
   - ✅ Notify Slack

### 생성된 팟캐스트 확인

**Google Cloud Storage**:
```
https://storage.googleapis.com/YOUR_BUCKET_NAME/YYYY-MM-DD/episode.mp3
```

예시:
```
https://storage.googleapis.com/papercast-podcasts/2025-10-23/episode.mp3
```

### 로컬 메타데이터

`data/podcasts/` 폴더에 JSON 메타데이터가 저장됩니다:
```json
{
  "id": "2025-10-23",
  "title": "Daily AI Papers - 2025-10-23",
  "papers": [...],
  "audio_file_path": "https://storage.googleapis.com/..."
}
```

---

## 🔧 워크플로우 커스터마이징

### 실행 시간 변경

`.github/workflows/daily-podcast.yml` 파일 수정:

```yaml
on:
  schedule:
    # 매일 21:00 UTC (06:00 KST)
    - cron: '0 21 * * *'
```

**Cron 표현식 예시**:
- `0 21 * * *`: 매일 21:00 UTC
- `0 12 * * *`: 매일 12:00 UTC (21:00 KST)
- `0 0 * * 1`: 매주 월요일 00:00 UTC

### 알림 메시지 커스터마이징

Slack 알림 메시지 수정:

```yaml
- name: Notify Slack on success
  uses: 8398a7/action-slack@v3
  with:
    text: |
      🎉 오늘의 AI 논문 팟캐스트가 완성되었습니다!
      📅 날짜: $(date +%Y-%m-%d)
      🎧 지금 바로 들어보세요!
```

### 타임아웃 시간 조정

```yaml
jobs:
  generate-podcast:
    timeout-minutes: 30  # 기본 30분
```

---

## 🚨 문제 해결

### 워크플로우 실패 시

1. **Actions 탭**에서 실패한 워크플로우 클릭
2. 빨간색 X 표시가 있는 단계 클릭
3. 로그 확인

**일반적인 오류**:

#### 1. API Key 오류
```
Error: Invalid API key
```

**해결**: `GEMINI_API_KEY` Secret이 올바른지 확인

#### 2. GCP 권한 오류
```
403 Permission denied
```

**해결**: Service Account에 필요한 권한 부여
- Cloud Text-to-Speech User
- Storage Object Admin

#### 3. Bucket 접근 오류
```
404 Bucket not found
```

**해결**: `GCS_BUCKET_NAME`이 실제 버킷 이름과 일치하는지 확인

#### 4. Base64 디코딩 오류
```
JSONDecodeError: Expecting value: line 1 column 1 (char 0)
File ./service-account-key.json is not a valid json file
```

**원인**: `GCP_SERVICE_ACCOUNT_KEY` Secret이 올바르게 base64 인코딩되지 않음

**해결**:
1. Service Account JSON 파일을 다시 base64로 인코딩:
   ```bash
   cat service-account-key.json | base64 -w 0
   ```
2. 인코딩 결과 확인:
   ```bash
   echo "YOUR_BASE64_STRING" | base64 --decode | python3 -m json.tool
   ```
3. JSON이 정상적으로 출력되면 GitHub Secret 업데이트
4. **주의**: Secret 값 복사 시 앞뒤 공백이 없어야 함

#### 5. Slack 알림 실패
```
Error: Webhook URL is not valid
```

**해결**: `SLACK_WEBHOOK_URL` Secret 확인 (선택사항이므로 워크플로우는 계속 진행됨)

---

## 📈 워크플로우 모니터링

### 성공률 확인

1. Repository → **Actions** 탭
2. 최근 실행 기록에서 성공/실패 비율 확인
3. 실패한 워크플로우 분석

### 알림 받기

**이메일 알림**:
- Repository → **Settings** → **Notifications**
- **Email notifications** 활성화

**Slack 알림**:
- `SLACK_WEBHOOK_URL` Secret 설정 (위 참고)

---

## 🎯 다음 단계

1. ✅ GitHub Secrets 설정 완료
2. ✅ 수동으로 워크플로우 실행 테스트
3. ✅ 실행 결과 및 로그 확인
4. ✅ 생성된 팟캐스트 재생 확인
5. 🔄 자동 스케줄 대기 (매일 06:00 KST)

---

## 💡 추가 팁

### 워크플로우 디버깅

**Debug 모드 활성화**:
```yaml
- name: Run podcast generation
  run: |
    python src/main.py
  env:
    LOG_LEVEL: DEBUG
```

### 로그 저장

실패 시 로그를 Artifact로 저장:
```yaml
- name: Upload logs on failure
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: pipeline-logs
    path: data/logs/*.log
    retention-days: 7
```

### 비용 최적화

GitHub Actions 무료 사용량:
- Public Repository: 무제한
- Private Repository: 월 2000분

현재 워크플로우 예상 실행 시간: ~5분/일
→ 월 150분 사용 (무료 범위 내)

---

## ✨ 완료!

이제 PaperCast가 매일 아침 자동으로 실행되어 최신 AI 논문 팟캐스트를 생성합니다! 🎉

**문제가 발생하면**:
1. Actions 탭에서 로그 확인
2. Secrets 설정 재확인
3. 수동 실행으로 테스트

**다음 개선 사항**:
- 정적 웹사이트 생성 (GitHub Pages)
- 모니터링 대시보드
- 에러 자동 복구
