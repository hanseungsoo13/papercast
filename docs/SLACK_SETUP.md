# Slack 알림 설정 가이드

PaperCast에서 GitHub Actions 실행 결과를 Slack으로 알림받는 방법입니다.

## 🔧 Slack Webhook 설정

### 1️⃣ Slack App 생성

1. [Slack API](https://api.slack.com/apps) 접속
2. **Create New App** 클릭
3. **From scratch** 선택
4. App 이름: `PaperCast Bot`
5. Workspace 선택 후 **Create App** 클릭

### 2️⃣ Incoming Webhooks 활성화

1. 좌측 메뉴에서 **Incoming Webhooks** 클릭
2. **Activate Incoming Webhooks** 토글을 **On**으로 변경
3. **Add New Webhook to Workspace** 클릭
4. 채널 선택: `#papercast` (또는 원하는 채널)
5. **Allow** 클릭

### 3️⃣ Webhook URL 복사

생성된 Webhook URL을 복사합니다:
```
https://hooks.slack.com/services/YOUR_TEAM_ID/YOUR_BOT_ID/YOUR_WEBHOOK_TOKEN
```

## 🔑 GitHub Secrets 설정

### 1️⃣ GitHub Repository 설정

1. GitHub Repository → **Settings** 탭
2. 좌측 메뉴에서 **Secrets and variables** → **Actions** 클릭
3. **New repository secret** 클릭

### 2️⃣ Secret 추가

**Name**: `SLACK_WEBHOOK_URL`
**Value**: 위에서 복사한 Webhook URL

```
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR_TEAM_ID/YOUR_BOT_ID/YOUR_WEBHOOK_TOKEN
```

## 📱 알림 메시지 예시

### ✅ 성공 알림
```
✅ PaperCast 생성 완료!
날짜: 2025-10-21
실행 시간: Mon Oct 21 06:00:00 KST 2025
새로운 팟캐스트가 준비되었습니다.
```

### 🚨 실패 알림
```
🚨 PaperCast 생성 실패
날짜: 2025-10-21
실행 시간: Mon Oct 21 06:00:00 KST 2025
로그를 확인해주세요.
```

## 🎨 커스텀 메시지 설정

`.github/workflows/daily-podcast.yml`에서 메시지를 수정할 수 있습니다:

```yaml
- name: Notify Slack on success
  uses: 8398a7/action-slack@v3
  with:
    status: success
    channel: '#papercast'
    text: |
      🎉 오늘의 AI 논문 팟캐스트가 완성되었습니다!
      📅 날짜: $(date +%Y-%m-%d)
      🎧 지금 바로 들어보세요!
    webhook_url: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 🔧 고급 설정

### 채널 변경
```yaml
channel: '#your-channel-name'
```

### 사용자 멘션 추가
```yaml
text: |
  ✅ PaperCast 생성 완료!
  <@U1234567890> 새로운 팟캐스트가 준비되었습니다.
```

### 이모지 변경
```yaml
text: |
  🎧 PaperCast 생성 완료!
  📻 오늘의 AI 논문을 들어보세요!
```

## 🚨 문제 해결

### 알림이 오지 않는 경우

1. **Webhook URL 확인**
   ```bash
   curl -X POST -H 'Content-type: application/json' \
   --data '{"text":"테스트 메시지"}' \
   YOUR_WEBHOOK_URL
   ```

2. **GitHub Secrets 확인**
   - Repository Settings → Secrets and variables → Actions
   - `SLACK_WEBHOOK_URL`이 올바르게 설정되었는지 확인

3. **Slack App 권한 확인**
   - Slack App → OAuth & Permissions
   - 필요한 권한이 있는지 확인

### 권한 오류

Slack App에 다음 권한이 필요합니다:
- `incoming-webhook`
- `chat:write`

## 📋 설정 체크리스트

- [ ] Slack App 생성 완료
- [ ] Incoming Webhooks 활성화
- [ ] Webhook URL 생성
- [ ] GitHub Secret `SLACK_WEBHOOK_URL` 설정
- [ ] 테스트 메시지 전송 확인
- [ ] GitHub Actions 실행 테스트

## 🎯 추가 기능 아이디어

### 1. 상세 로그 전송
```yaml
- name: Send detailed logs to Slack
  if: failure()
  run: |
    LOG_CONTENT=$(cat data/logs/*.log | tail -50)
    curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"상세 로그:\n\`\`\`$LOG_CONTENT\`\`\`\"}" \
    ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 2. 팟캐스트 링크 포함
```yaml
- name: Notify with podcast link
  if: success()
  run: |
    PODCAST_URL="https://storage.googleapis.com/${{ secrets.GCS_BUCKET_NAME }}/$(date +%Y-%m-%d)/episode.mp3"
    curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"✅ 새로운 팟캐스트: $PODCAST_URL\"}" \
    ${{ secrets.SLACK_WEBHOOK_URL }}
```

### 3. 주간 요약 리포트
```yaml
- name: Weekly summary
  if: github.event_name == 'schedule' && github.ref == 'refs/heads/main'
  run: |
    # 주간 통계 계산 및 전송
```

---

## ✨ 완료!

이제 매일 아침 6시에 PaperCast가 자동으로 생성되고, 성공/실패 여부를 Slack으로 알림받을 수 있습니다! 🎉

**다음 단계**: 정적 웹사이트 생성으로 사용자가 팟캐스트를 쉽게 접근할 수 있도록 개선할 수 있습니다.
