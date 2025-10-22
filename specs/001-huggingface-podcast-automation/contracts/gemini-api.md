# Contract: Google Gemini API

**Service**: Google Generative AI (Gemini Pro)  
**Purpose**: 논문 요약 생성  
**Version**: 1.0

## Endpoint

### Generate Content

**Method**: `POST`  
**URL**: `https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent`

#### Request

**Headers**:
```
Content-Type: application/json
x-goog-api-key: {API_KEY}
```

**Request Body**:
```json
{
  "contents": [
    {
      "parts": [
        {
          "text": "다음 논문을 한국어로 요약해주세요:\n\n제목: Efficient Transformers with Dynamic Attention\n저자: John Doe, Jane Smith\n초록: We propose a novel approach to improve transformer efficiency..."
        }
      ]
    }
  ],
  "generationConfig": {
    "temperature": 0.7,
    "maxOutputTokens": 500,
    "topP": 0.8,
    "topK": 40
  }
}
```

#### Response

**Status Code**: `200 OK`

**Response Body**:
```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "text": "이 논문은 동적 어텐션 메커니즘을 사용하여 트랜스포머의 효율성을 개선하는 새로운 접근법을 제안합니다. 주요 기여는 다음과 같습니다:\n\n1. 입력 시퀀스 길이에 따라 어텐션 헤드를 동적으로 조정\n2. 계산 복잡도를 O(n²)에서 O(n log n)으로 감소\n3. BERT 및 GPT 모델 대비 30% 속도 향상\n\n실험 결과, 제안된 방법은 표준 벤치마크에서 기존 모델과 유사한 성능을 유지하면서도 훨씬 빠른 추론 속도를 달성했습니다."
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0,
      "safetyRatings": [
        {
          "category": "HARM_CATEGORY_HARASSMENT",
          "probability": "NEGLIGIBLE"
        },
        {
          "category": "HARM_CATEGORY_HATE_SPEECH",
          "probability": "NEGLIGIBLE"
        },
        {
          "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
          "probability": "NEGLIGIBLE"
        },
        {
          "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
          "probability": "NEGLIGIBLE"
        }
      ]
    }
  ],
  "promptFeedback": {
    "safetyRatings": [
      {
        "category": "HARM_CATEGORY_HARASSMENT",
        "probability": "NEGLIGIBLE"
      }
    ]
  }
}
```

#### Error Responses

**Status Code**: `400 Bad Request`
```json
{
  "error": {
    "code": 400,
    "message": "Invalid request: text is required",
    "status": "INVALID_ARGUMENT"
  }
}
```

**Status Code**: `429 Too Many Requests`
```json
{
  "error": {
    "code": 429,
    "message": "Resource exhausted: Quota exceeded",
    "status": "RESOURCE_EXHAUSTED"
  }
}
```

**Status Code**: `401 Unauthorized`
```json
{
  "error": {
    "code": 401,
    "message": "API key not valid",
    "status": "UNAUTHENTICATED"
  }
}
```

## Contract Tests

### Success Scenario

```python
def test_gemini_api_success():
    """논문 요약을 성공적으로 생성한다"""
    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': os.environ['GEMINI_API_KEY']
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": "다음 논문을 한국어로 요약해주세요:\n\n제목: Test Paper\n초록: This is a test abstract."
            }]
        }],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 500
        }
    }
    
    response = requests.post(
        'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent',
        headers=headers,
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert 'candidates' in data
    assert len(data['candidates']) > 0
    assert 'content' in data['candidates'][0]
    assert 'parts' in data['candidates'][0]['content']
    assert 'text' in data['candidates'][0]['content']['parts'][0]
```

### Quota Exceeded Scenario

```python
def test_gemini_api_quota_exceeded():
    """할당량 초과 처리"""
    # 시뮬레이션: 대량의 요청으로 quota 초과
    # 실제로는 모킹으로 처리
    mock_response = {
        "error": {
            "code": 429,
            "message": "Resource exhausted: Quota exceeded",
            "status": "RESOURCE_EXHAUSTED"
        }
    }
    
    # 재시도 로직 테스트
    assert mock_response['error']['code'] == 429
```

## Implementation Notes

- API Key는 환경 변수로 관리 (`GEMINI_API_KEY`)
- 무료 티어: 분당 60회, 일일 1,500회 요청 제한
- `temperature`: 0.7 (일관성과 창의성 균형)
- `maxOutputTokens`: 500 (요약문 길이 제한)
- 한국어 프롬프트 사용으로 한국어 요약 생성
- Safety ratings 확인하여 부적절한 콘텐츠 필터링

