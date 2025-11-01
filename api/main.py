# main.py

import os
from flask import Flask
from google.cloud import firestore
from flask_cors import CORS # 1. CORS 라이브러리 추가

# Firestore 클라이언트 초기화
# Cloud Run 환경에서도 Cloud Function과 마찬가지로
# 인증 정보 없이 자동으로 연결됩니다!
db = firestore.Client()

app = Flask(__name__)
CORS(app) # 2. 모든 도메인에서 이 API를 호출할 수 있도록 허용

# API 엔드포인트 1: 모든 에피소드 목록 반환
@app.route('/episodes', methods=['GET'])
def get_episodes():
    """모든 에피소드 목록을 최신순(날짜 ID 역순)으로 반환합니다."""
    episodes_ref = db.collection('episodes').order_by(
        'id', direction=firestore.Query.DESCENDING
    )
    # 문서를 딕셔너리 리스트로 변환
    episodes = [doc.to_dict() for doc in episodes_ref.stream()]
    return {"episodes": episodes}

# API 엔드포인트 2: 특정 에피소드의 상세 정보 반환
@app.route('/episodes/<string:episode_id>', methods=['GET'])
def get_episode_detail(episode_id):
    """특정 ID의 에피소드 정보와 해당 에피소드의 'papers' 하위 컬렉션 목록을 반환합니다."""
    
    # 1. 에피소드 기본 정보 가져오기
    episode_ref = db.collection('episodes').document(episode_id)
    episode = episode_ref.get()
    
    if not episode.exists:
        return {"error": "Episode not found"}, 404
        
    episode_data = episode.to_dict()
    
    # 2. 'papers' 하위 컬렉션에서 논문 목록 가져오기
    papers_ref = episode_ref.collection('papers').stream()
    papers_list = [paper.to_dict() for paper in papers_ref]
    
    # 3. 논문 리스트를 에피소드 데이터에 추가
    episode_data['papers'] = papers_list
    
    return episode_data

# Cloud Run이 이 파일을 실행할 때 필요한 부분
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))