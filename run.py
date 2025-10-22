#!/usr/bin/env python3
"""
PaperCast 실행 스크립트

이 스크립트는 프로젝트 루트에서 PaperCast를 실행합니다.
"""

import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import and run main
from src.main import main

if __name__ == "__main__":
    sys.exit(main())


