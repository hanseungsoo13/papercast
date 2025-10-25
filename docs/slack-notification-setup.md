# Slack 알림 웹사이트 링크 설정 가이드

## 🎯 개요

GitHub Actions가 실행될 때마다 Slack으로 알림을 보내며, 웹사이트 링크가 포함된 메시지를 전송합니다.

## 🔧 GitHub Secrets 설정

### 1️⃣ 기존 Secrets 확인

Repository → **Settings** → **Secrets and variables** → **Actions**에서 다음 Secrets가 있는지 확인:

- ✅ `GEMINI_API_KEY`
- ✅ `GCP_SERVICE_ACCOUNT_KEY` 
- ✅ `GCS_BUCKET_NAME`
- ✅ `SLACK_WEBHOOK_URL`
- ✅ `VERCEL_TOKEN`
- ✅ `VERCEL_ORG_ID`
- ✅ `VERCEL_PROJECT_ID`

### 2️⃣ 새로운 Secret 추가: `FRONTEND_URL`

**Name**: `FRONTEND_URL`
**Value**: 실제 배포된 웹사이트 URL

#### Vercel 배포인 경우:
```
https://papercast-xxx.vercel.app
```

#### GitHub Pages인 경우:
```
https://username.github.io/papercast
```

#### 커스텀 도메인인 경우:
```
https://papercast.yourdomain.com
```

## 📱 Slack 알림 예시

### ✅ 성공 알림
```
🎉 오늘의 AI 논문 팟캐스트가 완성되었습니다!

📅 날짜: 2025-01-23
🎧 지금 바로 들어보세요: https://papercast-xxx.vercel.app
📖 아카이브: https://papercast-xxx.vercel.app/archive

새로운 논문들이 기다리고 있습니다! 🚀
```

### ❌ 실패 알림
```
❌ 오늘의 AI 논문 팟캐스트 생성에 실패했습니다!

📅 날짜: 2025-01-23
🔍 GitHub Actions 로그를 확인해주세요
📖 기존 아카이브: https://papercast-xxx.vercel.app/archive

문제를 해결한 후 다시 시도해주세요! 🛠️
```

## 🚀 자동화 흐름

```
1. 매일 21:00 UTC (한국시간 다음날 06:00)
   ↓
2. GitHub Actions 실행
   ↓
3. 논문 수집 → 팟캐스트 생성 → 데이터베이스 저장
   ↓
4. 백엔드 배포 (Google Cloud Run)
   ↓
5. 프론트엔드 배포 (Vercel)
   ↓
6. Slack 알림 전송 (웹사이트 링크 포함)
   ↓
7. 사용자가 웹사이트에서 새로운 에피소드 확인 가능
```

## 🔍 문제 해결

### Slack 알림이 오지 않는 경우

1. **Webhook URL 확인**
   ```bash
   curl -X POST -H 'Content-type: application/json' \
   --data '{"text":"테스트 메시지"}' \
   YOUR_SLACK_WEBHOOK_URL
   ```

2. **GitHub Secrets 확인**
   - `SLACK_WEBHOOK_URL`이 올바르게 설정되었는지 확인
   - `FRONTEND_URL`이 실제 배포된 URL과 일치하는지 확인

3. **GitHub Actions 로그 확인**
   - Repository → Actions → 최근 워크플로우 실행 → 로그 확인

### 웹사이트 링크가 잘못된 경우

1. **Vercel 배포 URL 확인**
   - Vercel Dashboard → Project → Domains에서 실제 URL 확인
   - `FRONTEND_URL` Secret을 올바른 URL로 업데이트

2. **커스텀 도메인 설정**
   - Vercel에서 커스텀 도메인 설정 후
   - `FRONTEND_URL`을 커스텀 도메인으로 변경

## ✨ 추가 기능 아이디어

### 1. 에피소드별 링크 포함
```yaml
text: |
  🎉 새로운 에피소드가 완성되었습니다!
  
  📻 에피소드: "Transformer 아키텍처의 최신 동향"
  🎧 듣기: https://papercast.vercel.app/episodes/2025-01-23
  📖 아카이브: https://papercast.vercel.app/archive
```

### 2. 논문 개수 정보 포함
```yaml
text: |
  🎉 오늘의 AI 논문 팟캐스트 완성!
  
  📊 오늘 수집된 논문: 5개
  🎧 듣기: https://papercast.vercel.app
  📖 아카이브: https://papercast.vercel.app/archive
```

### 3. 주간 요약 리포트
```yaml
text: |
  📊 이번 주 PaperCast 요약
  
  📅 기간: 2025-01-20 ~ 2025-01-26
  📻 총 에피소드: 7개
  📚 총 논문: 35개
  🎧 아카이브: https://papercast.vercel.app/archive
```

---

## ✅ 설정 완료 체크리스트

- [ ] GitHub Secret `FRONTEND_URL` 설정 완료
- [ ] Slack Webhook URL 설정 완료
- [ ] 테스트 워크플로우 실행
- [ ] Slack 알림 수신 확인
- [ ] 웹사이트 링크 클릭 테스트

이제 매일 아침 6시에 자동으로 팟캐스트가 생성되고, Slack으로 웹사이트 링크가 포함된 알림을 받을 수 있습니다! 🎉
