# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

import json
import requests
from google.cloud import firestore, storage, secretmanager

# 클라이언트 초기화
db = firestore.Client()
storage_client = storage.Client()
secret_client = secretmanager.SecretManagerServiceClient()

project_id = "gen-lang-client-0720034817" 
secret_name = "vercel-deploy-hook-url"
SECRET_VERSION_NAME = f"projects/{project_id}/secrets/{secret_name}/versions/latest"

# 4. URL을 담을 전역 변수 (캐시 용도)
VERCEL_DEPLOY_HOOK_URL = None

def process_metadata(event, context):
    """GCS에 metadata.json이 생성되면 Firestore에 데이터를 저장하는 함수"""
    
    bucket_name = event['bucket']
    file_name = event['name']

    # metadata.json 파일이 아닐 경우 함수 종료
    if not file_name.endswith('metadata.json'):
        print(f"Ignoring non-metadata file: {file_name}")
        return

    print(f"Processing file: {file_name}")

    # 1. GCS에서 metadata.json 파일 다운로드 및 파싱
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    metadata_str = blob.download_as_string()
    metadata = json.loads(metadata_str)

    episode_id = metadata['id']
    papers_data = metadata.pop('papers', []) # 논문 리스트는 따로 분리

    # 2. Firestore에 데이터 저장 (Batch 사용으로 원자적 처리)
    batch = db.batch()

    # 2-1. 'episodes' 문서 저장 (논문 리스트 제외)
    episode_ref = db.collection('episodes').document(episode_id)
    batch.set(episode_ref, metadata)

    # 2-2. 'papers' 하위 컬렉션에 각 논문 정보 저장
    for paper in papers_data:
        paper_id = paper['id']
        paper_ref = episode_ref.collection('papers').document(paper_id)
        batch.set(paper_ref, paper)

    # 3. Batch 작업 실행
    batch.commit()
    #4. ▼▼▼ Vercel 재배포 트리거 ▼▼▼
    try:
        response = requests.post(VERCEL_DEPLOY_HOOK_URL)
        if response.status_code == 200 or response.status_code == 201:
            print(f"Successfully triggered Vercel redeploy.")
        else:
            print(f"Failed to trigger Vercel redeploy: {response.status_code}")
    except Exception as e:
        print(f"Error triggering Vercel redeploy: {e}")
    print(f"Successfully processed and stored episode {episode_id} in Firestore.")