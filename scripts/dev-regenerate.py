#!/usr/bin/env python3
"""개발 전용: 기존 팟캐스트 데이터로 정적 사이트 재생성

⚠️  이 스크립트는 개발 환경에서만 사용하세요!
운영 환경에서는 항상 'python run.py'를 사용하세요.

사용법:
    python scripts/dev-regenerate.py
"""

import os
import sys
from pathlib import Path
import json

# 운영 환경에서 실행 방지
if os.getenv('GITHUB_ACTIONS') or os.getenv('PRODUCTION'):
    print("❌ 이 스크립트는 개발 환경에서만 사용하세요.")
    print("운영 환경에서는 'python run.py'를 사용하세요.")
    print("GitHub Actions에서는 자동으로 전체 파이프라인이 실행됩니다.")
    sys.exit(1)

print("🔧 개발 모드: 사이트 재생성 중...")

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.services.generator import StaticSiteGenerator
from src.models.podcast import Podcast
from src.models.paper import Paper
from datetime import datetime


def load_podcasts_from_json():
    """data/podcasts/에서 모든 팟캐스트 JSON 로드"""
    podcasts = []
    podcasts_dir = Path('data/podcasts')
    
    if not podcasts_dir.exists():
        print(f"❌ {podcasts_dir} 디렉토리가 없습니다.")
        print("먼저 팟캐스트를 생성하세요: python run.py")
        return []
    
    json_files = sorted(podcasts_dir.glob('*.json'), reverse=True)
    
    if not json_files:
        print(f"❌ {podcasts_dir}에 JSON 파일이 없습니다.")
        print("먼저 팟캐스트를 생성하세요: python run.py")
        return []
    
    print(f"📂 {len(json_files)}개의 팟캐스트 JSON 파일 발견")
    print("-" * 60)
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Paper 객체 변환
            papers = []
            for p_data in data.get('papers', []):
                try:
                    paper = Paper(
                        id=p_data['id'],
                        title=p_data['title'],
                        authors=p_data['authors'],
                        abstract=p_data['abstract'],
                        url=p_data['url'],
                        published_date=p_data.get('published_date'),
                        upvotes=p_data.get('upvotes', 0),
                        collected_at=datetime.fromisoformat(p_data['collected_at']) if 'collected_at' in p_data else datetime.now(),
                        arxiv_id=p_data.get('arxiv_id'),
                        categories=p_data.get('categories'),
                        thumbnail_url=p_data.get('thumbnail_url'),
                        embed_supported=p_data.get('embed_supported'),
                        view_count=p_data.get('view_count'),
                        summary=p_data.get('summary', '')[:1000] if p_data.get('summary') else None
                    )
                    papers.append(paper)
                except Exception as e:
                    print(f"  ⚠️  논문 파싱 오류 ({p_data.get('id', 'unknown')}): {e}")
            
            if not papers:
                print(f"  ⚠️  {json_file.name}: 논문 데이터 없음")
                continue
            
            # Podcast 객체 생성
            podcast = Podcast(
                id=data['id'],
                title=data['title'],
                description=data.get('description', ''),
                created_at=datetime.fromisoformat(data['created_at']),
                papers=papers,
                audio_file_path=data['audio_file_path'],
                audio_duration=data.get('audio_duration', 0),
                audio_size=data.get('audio_size', 0),
                status=data.get('status', 'completed')
            )
            
            podcasts.append(podcast)
            print(f"  ✓ {json_file.name}: {len(papers)}개 논문")
            
        except Exception as e:
            print(f"  ❌ {json_file.name}: {e}")
    
    print("-" * 60)
    return podcasts


def main():
    """메인 함수"""
    print("=" * 60)
    print("🔄 PaperCast 정적 사이트 재생성")
    print("=" * 60)
    print()
    
    # 팟캐스트 로드
    podcasts = load_podcasts_from_json()
    
    if not podcasts:
        print("\n❌ 사이트를 생성할 팟캐스트가 없습니다.")
        sys.exit(1)
    
    print(f"\n📊 총 {len(podcasts)}개의 팟캐스트 로드 완료")
    print()
    
    # 사이트 생성
    try:
        print("🏗️  정적 사이트 생성 중...")
        print("-" * 60)
        
        generator = StaticSiteGenerator(output_dir='static-site')
        generator.generate_site(podcasts)
        
        print("-" * 60)
        print()
        print("=" * 60)
        print("✅ 사이트 생성 완료!")
        print("=" * 60)
        print()
        print(f"📁 출력 디렉토리: static-site/")
        print(f"📝 생성된 페이지:")
        print(f"   - index.html (메인 페이지)")
        print(f"   - episodes/*.html ({len(podcasts)}개 에피소드)")
        print(f"   - assets/css/styles.css")
        print(f"   - assets/js/script.js")
        print(f"   - podcasts/index.json")
        print()
        print("🚀 다음 명령으로 서버를 시작하세요:")
        print("   python dev_server.py")
        print()
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ 사이트 생성 실패: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

