# Contract: Google Cloud Storage API

**Service**: Google Cloud Storage  
**Purpose**: MP3 파일 및 메타데이터 업로드  
**Version**: v1

## Endpoint

### Upload Object

**Method**: `POST`  
**URL**: `https://storage.googleapis.com/upload/storage/v1/b/{bucket}/o?uploadType=media&name={objectName}`

#### Request

**Headers**:
```
Content-Type: audio/mpeg
Authorization: Bearer {ACCESS_TOKEN}
```

**Request Body**: Binary MP3 file data

#### Response

**Status Code**: `200 OK`

**Response Body**:
```json
{
  "kind": "storage#object",
  "id": "papercast-podcasts/2025-01-27/episode.mp3/1706342400000000",
  "selfLink": "https://www.googleapis.com/storage/v1/b/papercast-podcasts/o/2025-01-27%2Fepisode.mp3",
  "mediaLink": "https://storage.googleapis.com/download/storage/v1/b/papercast-podcasts/o/2025-01-27%2Fepisode.mp3?generation=1706342400000000&alt=media",
  "name": "2025-01-27/episode.mp3",
  "bucket": "papercast-podcasts",
  "generation": "1706342400000000",
  "metageneration": "1",
  "contentType": "audio/mpeg",
  "storageClass": "STANDARD",
  "size": "7680000",
  "md5Hash": "CY9rzUYh03PK3k6DJie09g==",
  "crc32c": "AAAAAA==",
  "etag": "COiPjezDy4QDEAE=",
  "timeCreated": "2025-01-27T06:00:00.000Z",
  "updated": "2025-01-27T06:00:00.000Z",
  "timeStorageClassUpdated": "2025-01-27T06:00:00.000Z"
}
```

### Make Object Public

**Method**: `PUT`  
**URL**: `https://storage.googleapis.com/storage/v1/b/{bucket}/o/{objectName}/acl`

#### Request

**Headers**:
```
Content-Type: application/json
Authorization: Bearer {ACCESS_TOKEN}
```

**Request Body**:
```json
{
  "entity": "allUsers",
  "role": "READER"
}
```

#### Response

**Status Code**: `200 OK`

**Response Body**:
```json
{
  "kind": "storage#objectAccessControl",
  "entity": "allUsers",
  "role": "READER",
  "etag": "CAE="
}
```

## Python Client Library Usage

### Upload File

```python
from google.cloud import storage

def upload_podcast(bucket_name: str, source_file: str, destination_blob: str) -> str:
    """MP3 파일을 GCS에 업로드하고 공개 URL을 반환"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    
    # 파일 업로드
    blob.upload_from_filename(
        source_file,
        content_type='audio/mpeg'
    )
    
    # 공개 접근 설정
    blob.make_public()
    
    # 공개 URL 반환
    return blob.public_url

# 사용 예시
public_url = upload_podcast(
    bucket_name='papercast-podcasts',
    source_file='/tmp/episode.mp3',
    destination_blob='2025-01-27/episode.mp3'
)
# 결과: https://storage.googleapis.com/papercast-podcasts/2025-01-27/episode.mp3
```

### Upload Metadata

```python
def upload_metadata(bucket_name: str, metadata: dict, destination_blob: str):
    """팟캐스트 메타데이터를 JSON으로 업로드"""
    import json
    from google.cloud import storage
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    
    # JSON 직접 업로드
    blob.upload_from_string(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        content_type='application/json'
    )
    
    blob.make_public()
    return blob.public_url
```

### Set Lifecycle Policy

```python
def set_lifecycle_policy(bucket_name: str):
    """30일 후 자동 삭제 정책 설정"""
    from google.cloud import storage
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    rule = storage.bucket.LifecycleRuleDelete(age=30)
    bucket.add_lifecycle_rule(rule)
    bucket.patch()
```

## Contract Tests

### Upload Success Scenario

```python
def test_gcs_upload_success():
    """파일 업로드 성공"""
    from google.cloud import storage
    import tempfile
    
    # 임시 MP3 파일 생성
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
        tmp.write(b'test audio data')
        tmp_path = tmp.name
    
    client = storage.Client()
    bucket = client.bucket('papercast-podcasts')
    blob = bucket.blob('test/test.mp3')
    
    # 업로드
    blob.upload_from_filename(tmp_path, content_type='audio/mpeg')
    
    # 검증
    assert blob.exists()
    assert blob.content_type == 'audio/mpeg'
    assert blob.size > 0
    
    # 정리
    blob.delete()
```

### Make Public Scenario

```python
def test_gcs_make_public():
    """파일 공개 설정"""
    from google.cloud import storage
    
    client = storage.Client()
    bucket = client.bucket('papercast-podcasts')
    blob = bucket.blob('test/test.mp3')
    
    # 공개 설정
    blob.make_public()
    
    # 공개 URL 검증
    public_url = blob.public_url
    assert public_url.startswith('https://storage.googleapis.com/')
    
    # HTTP 접근 가능 확인
    import requests
    response = requests.head(public_url)
    assert response.status_code == 200
```

### Lifecycle Policy Scenario

```python
def test_gcs_lifecycle_policy():
    """라이프사이클 정책 설정"""
    from google.cloud import storage
    
    client = storage.Client()
    bucket = client.bucket('papercast-podcasts')
    
    # 30일 후 삭제 규칙
    rule = storage.bucket.LifecycleRuleDelete(age=30)
    bucket.add_lifecycle_rule(rule)
    bucket.patch()
    
    # 검증
    rules = bucket.lifecycle_rules
    assert len(rules) > 0
    assert any(rule.get('action', {}).get('type') == 'Delete' for rule in rules)
```

## Bucket Configuration

### Recommended Settings

```yaml
Bucket Name: papercast-podcasts
Location: asia-northeast3 (Seoul)
Storage Class: STANDARD
Access Control: Uniform (bucket-level)
Public Access: Enabled for specific objects only
Versioning: Disabled
Lifecycle Rules:
  - Delete after 30 days
CORS: Enabled for web playback
  - origin: ["*"]
  - method: ["GET"]
  - responseHeader: ["Content-Type"]
  - maxAgeSeconds: 3600
```

## Error Responses

**Status Code**: `401 Unauthorized`
```json
{
  "error": {
    "code": 401,
    "message": "Invalid Credentials"
  }
}
```

**Status Code**: `403 Forbidden`
```json
{
  "error": {
    "code": 403,
    "message": "Insufficient Permission"
  }
}
```

**Status Code**: `404 Not Found`
```json
{
  "error": {
    "code": 404,
    "message": "Not Found"
  }
}
```

## Implementation Notes

- 인증: Service Account JSON 키 (`GOOGLE_APPLICATION_CREDENTIALS` 환경 변수)
- 버킷은 사전에 생성되어 있어야 함
- 객체 이름은 URL-safe 형식 권장
- 대용량 파일은 resumable upload 사용
- CDN 캐싱 활용 (Cloud CDN 또는 Cloudflare)
- 비용: 스토리지 $0.020/GB/월 (Standard, Seoul region)
- 무료 티어: 월 5GB 스토리지, 1GB 네트워크 egress (북미)

