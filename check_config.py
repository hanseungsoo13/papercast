#!/usr/bin/env python3
"""
PaperCast 설정 검증 스크립트

이 스크립트는 .env 파일과 필요한 API 키가 올바르게 설정되었는지 확인합니다.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.config import Config


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}\n")


def check_config():
    """Check if configuration is valid."""
    print_section("🔍 PaperCast 설정 검증")
    
    try:
        config = Config()
    except Exception as e:
        print(f"❌ 설정 로드 실패: {e}")
        return False
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env 파일 존재")
    else:
        print("❌ .env 파일이 없습니다!")
        print("   👉 ./setup_env.sh 를 실행하거나 수동으로 생성하세요.")
        return False
    
    # Check required fields
    print("\n📋 필수 설정 확인:")
    
    checks = [
        ("GEMINI_API_KEY", config.gemini_api_key, "Google Gemini API 키"),
        ("GOOGLE_APPLICATION_CREDENTIALS", config.google_credentials_path, "GCP Service Account 경로"),
        ("GCS_BUCKET_NAME", config.gcs_bucket_name, "GCS 버킷 이름"),
    ]
    
    all_valid = True
    for field_name, field_value, description in checks:
        if field_value:
            # Mask sensitive data
            if field_name == "GEMINI_API_KEY":
                display_value = f"{field_value[:10]}...{field_value[-4:]}" if len(field_value) > 14 else "***"
            else:
                display_value = field_value
            print(f"  ✅ {description}: {display_value}")
        else:
            print(f"  ❌ {description}: 설정되지 않음!")
            all_valid = False
    
    # Check credentials file
    print("\n🔑 인증 파일 확인:")
    creds_path = Path(config.google_credentials_path)
    if creds_path.exists():
        print(f"  ✅ Service Account JSON 파일 존재: {creds_path}")
        print(f"     크기: {creds_path.stat().st_size} bytes")
    else:
        print(f"  ❌ Service Account JSON 파일 없음: {creds_path}")
        print("     👉 GCP Console에서 Service Account 키를 다운로드하세요.")
        all_valid = False
    
    # Check directories
    print("\n📁 디렉토리 확인:")
    directories = [
        config.data_dir,
        config.podcasts_dir,
        config.logs_dir,
        config.static_site_dir,
        Path("credentials"),
    ]
    
    for directory in directories:
        if directory.exists():
            print(f"  ✅ {directory}")
        else:
            print(f"  ⚠️  {directory} (자동 생성됨)")
    
    # Optional settings
    print("\n⚙️  선택적 설정:")
    print(f"  • Timezone: {config.timezone}")
    print(f"  • Log Level: {config.log_level}")
    print(f"  • Papers to Fetch: {config.papers_to_fetch}")
    print(f"  • Podcast Title Prefix: {config.podcast_title_prefix}")
    
    # Final validation
    print_section("🎯 최종 검증 결과")
    
    if all_valid:
        print("✅ 모든 설정이 올바릅니다!")
        print("\n🚀 다음 명령어로 실행하세요:")
        print("   python src/main.py")
        return True
    else:
        print("❌ 일부 설정이 누락되었습니다.")
        print("\n📚 자세한 설정 방법:")
        print("   cat docs/API_SETUP.md")
        print("\n🔧 또는 자동 설정 스크립트 실행:")
        print("   ./setup_env.sh")
        return False


if __name__ == "__main__":
    try:
        success = check_config()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


