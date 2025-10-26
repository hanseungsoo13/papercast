#!/bin/bash

# PaperCast 프론트엔드 배포 스크립트 (Vercel)

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 PaperCast 프론트엔드 배포를 시작합니다...${NC}"

# 환경 변수 확인
if [ -z "$NEXT_PUBLIC_API_URL" ]; then
    echo -e "${RED}❌ NEXT_PUBLIC_API_URL 환경 변수가 설정되지 않았습니다.${NC}"
    echo "export NEXT_PUBLIC_API_URL=https://papercast-api-xxx-uc.a.run.app"
    exit 1
fi

echo -e "${YELLOW}📋 배포 설정:${NC}"
echo "  - API URL: $NEXT_PUBLIC_API_URL"

# frontend 디렉토리로 이동
cd frontend

# 의존성 설치
echo -e "${BLUE}📦 의존성을 설치합니다...${NC}"
npm install

# 빌드 테스트
echo -e "${BLUE}🔨 빌드를 테스트합니다...${NC}"
npm run build

# Vercel 로그인 확인
echo -e "${BLUE}🔐 Vercel 로그인 상태를 확인합니다...${NC}"
if ! vercel whoami > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Vercel에 로그인이 필요합니다.${NC}"
    vercel login
fi

# Vercel 프로젝트 초기화 (처음 배포인 경우)
if [ ! -f ".vercel/project.json" ]; then
    echo -e "${BLUE}🆕 Vercel 프로젝트를 초기화합니다...${NC}"
    vercel --yes
fi

# 환경 변수 설정
echo -e "${BLUE}🔧 환경 변수를 설정합니다...${NC}"
vercel env add NEXT_PUBLIC_API_URL production <<< "$NEXT_PUBLIC_API_URL"
vercel env add NEXT_PUBLIC_API_URL preview <<< "$NEXT_PUBLIC_API_URL"
vercel env add NEXT_PUBLIC_API_URL development <<< "$NEXT_PUBLIC_API_URL"

# 프로덕션 배포
echo -e "${BLUE}🚀 프로덕션에 배포합니다...${NC}"
DEPLOYMENT_URL=$(vercel --prod)

echo -e "${GREEN}✅ 배포가 완료되었습니다!${NC}"
echo -e "${GREEN}🌐 배포 URL: $DEPLOYMENT_URL${NC}"

# 배포 테스트
echo -e "${BLUE}🔍 배포된 사이트를 테스트합니다...${NC}"
if curl -f "$DEPLOYMENT_URL" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 사이트 접근 가능${NC}"
else
    echo -e "${RED}❌ 사이트 접근 실패${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 프론트엔드 배포가 성공적으로 완료되었습니다!${NC}"
echo -e "${YELLOW}📝 다음 단계:${NC}"
echo "1. GitHub Actions에서 FRONTEND_URL을 $DEPLOYMENT_URL로 설정"
echo "2. Slack 알림 테스트"
echo "3. 전체 시스템 테스트"
