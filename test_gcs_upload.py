#!/usr/bin/env python3
"""
GCS 업로드 테스트 스크립트

Google Cloud Storage에 데이터가 정상적으로 업로드되는지 테스트
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
import sys
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.uploader import GCSUploader
from src.utils.config import config


def test_gcs_connection():
    """GCS 연결 테스트"""
    print("🔍 GCS 연결 테스트 시작...")
    
    try:
        # GCS 업로더 초기화
        uploader = GCSUploader(
            bucket_name=config.gcs_bucket_name,
            credentials_path=config.google_credentials_path
        )
        
        print(f"✅ GCS 클라이언트 초기화 성공")
        print(f"📦 버킷 이름: {config.gcs_bucket_name}")
        print(f"🔑 인증 파일: {config.google_credentials_path}")
        
        return uploader
        
    except Exception as e:
        print(f"❌ GCS 연결 실패: {e}")
        return None


def test_json_upload(uploader):
    """JSON 데이터 업로드 테스트"""
    print("\n📄 JSON 업로드 테스트 시작...")
    
    try:
        # 테스트용 JSON 데이터 생성
        test_data = {
            "id": "test-2025-01-23",
            "title": "GCS 테스트 에피소드",
            "description": "GCS 업로드 테스트를 위한 더미 데이터",
            "created_at": datetime.now().isoformat(),
            "papers": [
                {
                    "id": "test-paper-1",
                    "title": "테스트 논문 1",
                    "authors": ["테스트 저자 1", "테스트 저자 2"],
                    "summary": "이것은 GCS 업로드 테스트를 위한 더미 논문입니다.",
                    "url": "https://example.com/paper1"
                }
            ],
            "test": True
        }
        
        # GCS에 JSON 업로드
        destination = "test/podcast-test.json"
        public_url = uploader.upload_json(test_data, destination)
        
        print(f"✅ JSON 업로드 성공!")
        print(f"🔗 Public URL: {public_url}")
        
        return public_url
        
    except Exception as e:
        print(f"❌ JSON 업로드 실패: {e}")
        return None


def test_file_upload(uploader):
    """파일 업로드 테스트"""
    print("\n📁 파일 업로드 테스트 시작...")
    
    try:
        # 임시 텍스트 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("이것은 GCS 업로드 테스트를 위한 더미 파일입니다.\n")
            temp_file.write(f"생성 시간: {datetime.now().isoformat()}\n")
            temp_file.write("테스트 완료!")
            temp_file_path = temp_file.name
        
        print(f"📝 임시 파일 생성: {temp_file_path}")
        
        # GCS에 파일 업로드
        destination = "test/test-file.txt"
        public_url = uploader.upload_file(
            local_path=temp_file_path,
            destination_path=destination,
            content_type="text/plain"
        )
        
        print(f"✅ 파일 업로드 성공!")
        print(f"🔗 Public URL: {public_url}")
        
        # 임시 파일 삭제
        os.unlink(temp_file_path)
        print(f"🗑️ 임시 파일 삭제 완료")
        
        return public_url
        
    except Exception as e:
        print(f"❌ 파일 업로드 실패: {e}")
        return None


def test_file_listing(uploader):
    """GCS 파일 목록 조회 테스트"""
    print("\n📋 GCS 파일 목록 조회 테스트 시작...")
    
    try:
        # test/ 접두사로 파일 목록 조회
        files = uploader.list_files(prefix="test/")
        
        print(f"✅ 파일 목록 조회 성공!")
        print(f"📁 발견된 파일 수: {len(files)}")
        
        for file_path in files:
            print(f"  - {file_path}")
        
        return files
        
    except Exception as e:
        print(f"❌ 파일 목록 조회 실패: {e}")
        return []


def test_file_existence(uploader, test_files):
    """파일 존재 여부 테스트"""
    print("\n🔍 파일 존재 여부 테스트 시작...")
    
    try:
        for file_path in test_files:
            exists = uploader.file_exists(file_path)
            status = "✅ 존재" if exists else "❌ 없음"
            print(f"  {status}: {file_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 파일 존재 여부 확인 실패: {e}")
        return False


def test_public_url_generation(uploader, test_files):
    """Public URL 생성 테스트"""
    print("\n🔗 Public URL 생성 테스트 시작...")
    
    try:
        for file_path in test_files:
            public_url = uploader.get_public_url(file_path)
            print(f"  📄 {file_path}")
            print(f"     🔗 {public_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Public URL 생성 실패: {e}")
        return False


def cleanup_test_files(uploader, test_files):
    """테스트 파일 정리"""
    print("\n🧹 테스트 파일 정리 시작...")
    
    try:
        for file_path in test_files:
            if file_path.startswith("test/"):
                uploader.delete_file(file_path)
                print(f"🗑️ 삭제됨: {file_path}")
        
        print("✅ 테스트 파일 정리 완료")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 파일 정리 실패: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("🚀 GCS 업로드 테스트 시작")
    print("=" * 50)
    
    # 환경 변수 확인
    print(f"🔧 환경 설정:")
    print(f"  - GCS_BUCKET_NAME: {config.gcs_bucket_name}")
    print(f"  - GOOGLE_APPLICATION_CREDENTIALS: {config.google_credentials_path}")
    print(f"  - GEMINI_API_KEY: {'설정됨' if config.gemini_api_key else '설정되지 않음'}")
    
    # 1. GCS 연결 테스트
    uploader = test_gcs_connection()
    if not uploader:
        print("❌ GCS 연결 실패로 테스트 중단")
        return False
    
    # 2. JSON 업로드 테스트
    json_url = test_json_upload(uploader)
    if not json_url:
        print("❌ JSON 업로드 실패로 테스트 중단")
        return False
    
    # 3. 파일 업로드 테스트
    file_url = test_file_upload(uploader)
    if not file_url:
        print("❌ 파일 업로드 실패로 테스트 중단")
        return False
    
    # 4. 파일 목록 조회 테스트
    files = test_file_listing(uploader)
    if not files:
        print("❌ 파일 목록 조회 실패")
        return False
    
    # 5. 파일 존재 여부 테스트
    test_file_existence(uploader, files)
    
    # 6. Public URL 생성 테스트
    test_public_url_generation(uploader, files)
    
    # 7. 테스트 파일 정리
    cleanup_test_files(uploader, files)
    
    print("\n" + "=" * 50)
    print("🎉 GCS 업로드 테스트 완료!")
    print("✅ 모든 테스트가 성공적으로 완료되었습니다.")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
