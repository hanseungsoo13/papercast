#!/usr/bin/env python3
"""개발용 라이브 리로드 서버

파일 변경 시 자동으로 브라우저를 새로고침합니다.
"""

import os
import sys
from pathlib import Path

try:
    from livereload import Server
except ImportError:
    print("❌ livereload가 설치되지 않았습니다.")
    print("다음 명령으로 설치하세요:")
    print("  pip install livereload")
    sys.exit(1)


def main():
    """개발 서버 시작"""
    
    # 정적 사이트 디렉토리
    static_dir = Path("static-site")
    
    if not static_dir.exists():
        print(f"❌ {static_dir} 디렉토리가 없습니다.")
        print("먼저 사이트를 생성하세요:")
        print("  python -m src.main")
        sys.exit(1)
    
    print("🚀 PaperCast 개발 서버 시작 중...")
    print(f"📁 서빙 디렉토리: {static_dir.absolute()}")
    print("=" * 60)
    
    # 라이브 리로드 서버 설정
    server = Server()
    
    # 감시할 파일/디렉토리 패턴
    watch_patterns = [
        str(static_dir / "**/*.html"),
        str(static_dir / "**/*.css"),
        str(static_dir / "**/*.js"),
        str(static_dir / "**/*.json"),
    ]
    
    # 각 패턴에 대해 감시 설정
    for pattern in watch_patterns:
        server.watch(pattern)
    
    print("👀 다음 파일들의 변경을 감시 중:")
    print("  - HTML 파일 (.html)")
    print("  - CSS 파일 (.css)")
    print("  - JavaScript 파일 (.js)")
    print("  - JSON 파일 (.json)")
    print()
    print("💡 파일을 수정하면 브라우저가 자동으로 새로고침됩니다!")
    print("=" * 60)
    
    # 서버 시작
    try:
        server.serve(
            root=str(static_dir),
            host='localhost',
            port=8080,
            open_url_delay=1  # 1초 후 브라우저 자동 열기
        )
    except KeyboardInterrupt:
        print("\n\n👋 개발 서버를 종료합니다.")
    except Exception as e:
        print(f"\n❌ 서버 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

