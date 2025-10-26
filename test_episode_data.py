#!/usr/bin/env python3
"""
GCS에 테스트 에피소드 데이터 업로드

실제 에피소드 데이터를 GCS에 업로드하여 백엔드 API 테스트
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.uploader import GCSUploader
from src.utils.config import config


def create_test_episode_data():
    """테스트용 에피소드 데이터 생성"""
    episode_id = "2025-01-23"
    
    # 테스트용 논문 데이터
    papers = [
        {
            "id": "test-paper-1",
            "title": "Human-Agent Collaborative Paper-to-Page Crafting for Under $0.1",
            "authors": ["테스트 저자 1", "테스트 저자 2"],
            "abstract": "이것은 GCS 테스트를 위한 더미 논문 초록입니다. AI와 인간의 협업을 통한 문서 작성에 대한 연구입니다.",
            "summary": "이 논문은 AI와 인간의 협업을 통한 문서 작성 방법을 제안합니다. 0.1달러 미만의 비용으로 고품질 문서를 생성할 수 있는 혁신적인 접근 방식을 제시합니다.",
            "short_summary": "AI-인간 협업 문서 작성\n0.1달러 미만 비용으로 고품질 문서 생성\n혁신적인 워크플로우 제안",
            "url": "https://huggingface.co/papers/test-paper-1",
            "published_date": "2025-01-22",
            "upvotes": 150,
            "tags": ["AI", "Collaboration", "Document Generation"]
        },
        {
            "id": "test-paper-2", 
            "title": "Advanced Neural Network Architectures for Natural Language Processing",
            "authors": ["테스트 저자 3", "테스트 저자 4"],
            "abstract": "자연어 처리를 위한 고급 신경망 아키텍처에 대한 연구입니다. 트랜스포머 모델의 개선된 버전을 제안합니다.",
            "summary": "이 논문은 자연어 처리를 위한 새로운 신경망 아키텍처를 제안합니다. 기존 트랜스포머 모델의 한계를 극복하고 더 나은 성능을 달성하는 방법을 제시합니다.",
            "short_summary": "자연어 처리용 신경망 아키텍처\n트랜스포머 모델 개선\n성능 향상 방법 제시",
            "url": "https://huggingface.co/papers/test-paper-2",
            "published_date": "2025-01-21",
            "upvotes": 200,
            "tags": ["NLP", "Neural Networks", "Transformers"]
        },
        {
            "id": "test-paper-3",
            "title": "Efficient Training Methods for Large Language Models",
            "authors": ["테스트 저자 5"],
            "abstract": "대규모 언어 모델의 효율적인 훈련 방법에 대한 연구입니다. 계산 비용을 줄이면서 성능을 유지하는 방법을 제안합니다.",
            "summary": "이 논문은 대규모 언어 모델의 훈련 효율성을 개선하는 새로운 방법을 제안합니다. 계산 비용을 크게 줄이면서도 모델 성능을 유지할 수 있는 혁신적인 훈련 기법을 소개합니다.",
            "short_summary": "대규모 언어 모델 훈련 효율성\n계산 비용 절감 방법\n성능 유지 기법",
            "url": "https://huggingface.co/papers/test-paper-3",
            "published_date": "2025-01-20",
            "upvotes": 300,
            "tags": ["LLM", "Training", "Efficiency"]
        }
    ]
    
    # 에피소드 데이터 생성
    episode_data = {
        "id": episode_id,
        "title": f"Daily AI Papers - {episode_id}",
        "description": f"오늘의 Hugging Face 트렌딩 논문 Top {len(papers)}",
        "publication_date": episode_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "papers": papers,
        "audio_file_path": f"https://storage.googleapis.com/{config.gcs_bucket_name}/episodes/{episode_id}/episode.mp3",
        "audio_duration": 1800,  # 30분
        "audio_size": 15000000,  # 15MB
        "status": "completed"
    }
    
    return episode_data


def upload_test_episode():
    """테스트 에피소드를 GCS에 업로드"""
    print("🚀 테스트 에피소드 데이터 업로드 시작...")
    
    try:
        # GCS 업로더 초기화
        uploader = GCSUploader(
            bucket_name=config.gcs_bucket_name,
            credentials_path=config.google_credentials_path
        )
        
        # 테스트 데이터 생성
        episode_data = create_test_episode_data()
        episode_id = episode_data["id"]
        
        print(f"📄 에피소드 데이터 생성: {episode_id}")
        
        # GCS에 에피소드 메타데이터 업로드
        destination = f"podcasts/{episode_id}.json"
        public_url = uploader.upload_json(episode_data, destination)
        
        print(f"✅ 에피소드 메타데이터 업로드 성공!")
        print(f"🔗 Public URL: {public_url}")
        
        # 더미 오디오 파일 생성 및 업로드
        print(f"🎵 더미 오디오 파일 생성 중...")
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mp3', delete=False) as temp_file:
            # 더미 MP3 파일 내용 (실제로는 바이너리 데이터여야 함)
            temp_file.write("더미 오디오 파일 - 실제로는 MP3 바이너리 데이터")
            temp_audio_path = temp_file.name
        
        # 오디오 파일 업로드
        audio_destination = f"episodes/{episode_id}/episode.mp3"
        audio_url = uploader.upload_file(
            local_path=temp_audio_path,
            destination_path=audio_destination,
            content_type="audio/mpeg"
        )
        
        print(f"✅ 오디오 파일 업로드 성공!")
        print(f"🔗 Audio URL: {audio_url}")
        
        # 임시 파일 삭제
        os.unlink(temp_audio_path)
        
        # 상세 메타데이터 업로드
        detailed_metadata = {
            "episode_id": episode_id,
            "title": episode_data["title"],
            "description": episode_data["description"],
            "papers": episode_data["papers"],
            "audio_url": audio_url,
            "created_at": episode_data["created_at"],
            "duration_seconds": episode_data["audio_duration"],
            "file_size_bytes": episode_data["audio_size"]
        }
        
        metadata_destination = f"episodes/{episode_id}/metadata.json"
        metadata_url = uploader.upload_json(detailed_metadata, metadata_destination)
        
        print(f"✅ 상세 메타데이터 업로드 성공!")
        print(f"🔗 Metadata URL: {metadata_url}")
        
        print(f"\n🎉 테스트 에피소드 '{episode_id}' 업로드 완료!")
        print(f"📦 버킷: {config.gcs_bucket_name}")
        print(f"📁 파일들:")
        print(f"  - podcasts/{episode_id}.json")
        print(f"  - episodes/{episode_id}/episode.mp3")
        print(f"  - episodes/{episode_id}/metadata.json")
        
        return episode_id
        
    except Exception as e:
        print(f"❌ 테스트 에피소드 업로드 실패: {e}")
        return None


def main():
    """메인 함수"""
    print("🧪 GCS 테스트 에피소드 데이터 업로드")
    print("=" * 50)
    
    # 환경 설정 확인
    print(f"🔧 환경 설정:")
    print(f"  - GCS_BUCKET_NAME: {config.gcs_bucket_name}")
    print(f"  - GOOGLE_APPLICATION_CREDENTIALS: {config.google_credentials_path}")
    
    # 테스트 에피소드 업로드
    episode_id = upload_test_episode()
    
    if episode_id:
        print(f"\n✅ 테스트 완료!")
        print(f"이제 백엔드 API에서 에피소드 '{episode_id}'를 조회할 수 있습니다.")
        print(f"테스트 URL: http://localhost:8001/api/episodes")
    else:
        print(f"\n❌ 테스트 실패!")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
