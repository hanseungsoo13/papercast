# Contract: Hugging Face Papers API

**Service**: Hugging Face Papers API  
**Purpose**: Hugging Face 트렌딩 논문 수집  
**Version**: 1.0

## Endpoint

### List Trending Papers

**Method**: `GET`  
**URL**: `https://huggingface.co/api/daily_papers`

#### Request

**Headers**:
```
Accept: application/json
```

**Query Parameters**:
- None (기본적으로 trending papers 반환)

#### Response

**Status Code**: `200 OK`

**Response Body**:
```json
[
  {
    "id": "2401.12345",
    "title": "Efficient Transformers with Dynamic Attention",
    "authors": [
      {
        "name": "John Doe",
        "url": "https://huggingface.co/johndoe"
      }
    ],
    "abstract": "We propose a novel approach to improve transformer efficiency...",
    "publishedAt": "2025-01-27T00:00:00.000Z",
    "upvotes": 142,
    "url": "https://huggingface.co/papers/2401.12345"
  },
  {
    "id": "2401.12346",
    "title": "Multimodal Learning for Visual Question Answering",
    "authors": [
      {
        "name": "Jane Smith",
        "url": "https://huggingface.co/janesmith"
      }
    ],
    "abstract": "This paper presents a multimodal approach...",
    "publishedAt": "2025-01-27T00:00:00.000Z",
    "upvotes": 98,
    "url": "https://huggingface.co/papers/2401.12346"
  }
]
```

#### Error Responses

**Status Code**: `429 Too Many Requests`
```json
{
  "error": "Rate limit exceeded",
  "message": "Please try again later"
}
```

**Status Code**: `500 Internal Server Error`
```json
{
  "error": "Internal server error",
  "message": "An error occurred while fetching papers"
}
```

## Contract Tests

### Success Scenario

```python
def test_huggingface_api_success():
    """트렌딩 논문을 성공적으로 가져온다"""
    response = requests.get('https://huggingface.co/api/daily_papers')
    
    assert response.status_code == 200
    papers = response.json()
    assert isinstance(papers, list)
    assert len(papers) >= 3
    
    # 첫 번째 논문 검증
    paper = papers[0]
    assert 'id' in paper
    assert 'title' in paper
    assert 'authors' in paper
    assert 'abstract' in paper
    assert 'url' in paper
```

### Rate Limit Scenario

```python
def test_huggingface_api_rate_limit():
    """Rate limit 처리"""
    # Rate limit을 초과하는 요청 시뮬레이션
    for _ in range(100):
        response = requests.get('https://huggingface.co/api/daily_papers')
        if response.status_code == 429:
            assert 'error' in response.json()
            break
```

## Implementation Notes

- API는 인증이 필요하지 않음 (공개 API)
- Rate limiting: 분당 60회 요청 제한 (추정)
- 논문은 upvotes 순으로 정렬됨
- 매일 새로운 trending papers가 업데이트됨

