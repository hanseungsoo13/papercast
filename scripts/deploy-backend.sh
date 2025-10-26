#!/bin/bash

# PaperCast 백엔드 배포 스크립트 (Google Cloud Run)

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 PaperCast 백엔드 배포를 시작합니다...${NC}"

# 환경 변수 확인
if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${RED}❌ GCP_PROJECT_ID 환경 변수가 설정되지 않았습니다.${NC}"
    echo "export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}❌ GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.${NC}"
    exit 1
fi

if [ -z "$GCS_BUCKET_NAME" ]; then
    echo -e "${RED}❌ GCS_BUCKET_NAME 환경 변수가 설정되지 않았습니다.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 배포 설정:${NC}"
echo "  - 프로젝트 ID: $GCP_PROJECT_ID"
echo "  - 버킷 이름: $GCS_BUCKET_NAME"
echo "  - 리전: asia-northeast3"

# Docker 이미지 빌드 및 푸시
echo -e "${BLUE}🔨 Docker 이미지를 빌드하고 푸시합니다...${NC}"
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/papercast-api

# Cloud Run에 배포
echo -e "${BLUE}🚀 Cloud Run에 배포합니다...${NC}"
gcloud run deploy papercast-api \
  --image gcr.io/$GCP_PROJECT_ID/papercast-api \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --port 8001 \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY \
  --set-env-vars GCS_BUCKET_NAME=$GCS_BUCKET_NAME \
  --timeout 300

# 배포된 서비스 URL 가져오기
SERVICE_URL=$(gcloud run services describe papercast-api --region asia-northeast3 --format="value(status.url)")

echo -e "${GREEN}✅ 배포가 완료되었습니다!${NC}"
echo -e "${GREEN}🌐 서비스 URL: $SERVICE_URL${NC}"
echo -e "${GREEN}📖 API 문서: $SERVICE_URL/docs${NC}"

# 헬스 체크
echo -e "${BLUE}🔍 헬스 체크를 수행합니다...${NC}"
if curl -f "$SERVICE_URL/api/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 헬스 체크 통과${NC}"
else
    echo -e "${RED}❌ 헬스 체크 실패${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 백엔드 배포가 성공적으로 완료되었습니다!${NC}"
echo -e "${YELLOW}📝 다음 단계:${NC}"
echo "1. Vercel에서 프론트엔드 배포"
echo "2. 환경 변수 NEXT_PUBLIC_API_URL을 $SERVICE_URL로 설정"
echo "3. 프론트엔드 배포 후 테스트"
