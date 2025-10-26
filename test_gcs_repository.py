#!/usr/bin/env python3
"""
GCS Repository 직접 테스트

GCS Repository가 실제로 데이터를 읽는지 확인
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from api.repository_gcs import GCSPodcastRepository
from src.utils.config import config


def test_gcs_repository():
    """GCS Repository 직접 테스트"""
    print("🧪 GCS Repository 직접 테스트")
    print("=" * 50)
    
    try:
        # GCS Repository 초기화
        repository = GCSPodcastRepository(
            bucket_name=config.gcs_bucket_name,
            credentials_path=config.google_credentials_path
        )
        
        print(f"✅ GCS Repository 초기화 성공")
        print(f"📦 버킷: {config.gcs_bucket_name}")
        
        # 모든 에피소드 조회
        print(f"\n📋 모든 에피소드 조회...")
        episodes = repository.find_all()
        
        print(f"✅ 조회 완료: {len(episodes)}개 에피소드")
        
        for episode in episodes:
            print(f"  - {episode.id}: {episode.title}")
            print(f"    논문 수: {len(episode.papers)}")
            print(f"    오디오: {episode.audio_file_path}")
        
        # 특정 에피소드 조회
        if episodes:
            episode_id = episodes[0].id
            print(f"\n🔍 특정 에피소드 조회: {episode_id}")
            
            episode = repository.find_by_id(episode_id)
            if episode:
                print(f"✅ 에피소드 조회 성공: {episode.title}")
                print(f"  논문 수: {len(episode.papers)}")
                for paper in episode.papers:
                    print(f"    - {paper.id}: {paper.title}")
            else:
                print(f"❌ 에피소드 조회 실패")
        
        # 모든 논문 조회
        print(f"\n📄 모든 논문 조회...")
        papers = repository.get_all_papers()
        print(f"✅ 논문 조회 완료: {len(papers)}개 논문")
        
        for paper in papers[:3]:  # 처음 3개만 출력
            print(f"  - {paper['id']}: {paper['title']}")
            print(f"    저자: {paper.get('authors', ['Unknown'])}")
            print(f"    에피소드: {paper.get('episode_id', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ GCS Repository 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 함수"""
    print("🚀 GCS Repository 테스트 시작")
    
    # 환경 설정 확인
    print(f"🔧 환경 설정:")
    print(f"  - GCS_BUCKET_NAME: {config.gcs_bucket_name}")
    print(f"  - GOOGLE_APPLICATION_CREDENTIALS: {config.google_credentials_path}")
    
    # GCS Repository 테스트
    success = test_gcs_repository()
    
    if success:
        print(f"\n🎉 GCS Repository 테스트 성공!")
    else:
        print(f"\n❌ GCS Repository 테스트 실패!")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
