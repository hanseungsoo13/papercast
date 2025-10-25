#!/bin/bash
# PaperCast 개발 서버 시작 스크립트

echo "🚀 PaperCast 개발 환경 시작..."
echo "================================================"

# static-site 디렉토리 확인
if [ ! -d "static-site" ] || [ ! -f "static-site/index.html" ]; then
    echo "❌ 사이트가 생성되지 않았습니다."
    echo "📝 먼저 팟캐스트를 생성하거나 사이트를 재생성하세요:"
    echo ""
    echo "   python run.py                         # 전체 파이프라인 실행"
    echo "   python scripts/dev-regenerate.py      # 사이트만 재생성 (개발용)"
    echo ""
    exit 1
fi

# 에피소드 개수 확인
EPISODE_COUNT=$(ls static-site/episodes/*.html 2>/dev/null | wc -l)
echo "📚 현재 에피소드: ${EPISODE_COUNT}개"
echo "================================================"
echo ""
echo "🌐 개발 서버를 시작합니다..."
echo "   → http://localhost:8080"
echo ""
echo "💡 Ctrl+C를 눌러 서버를 종료할 수 있습니다."
echo "================================================"
echo ""

# 개발 서버 실행
python scripts/dev-server.py

