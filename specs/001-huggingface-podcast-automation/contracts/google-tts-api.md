# Contract: Google Cloud Text-to-Speech API

**Service**: Google Cloud Text-to-Speech  
**Purpose**: 텍스트를 MP3 음성 파일로 변환  
**Version**: v1

## Endpoint

### Synthesize Speech

**Method**: `POST`  
**URL**: `https://texttospeech.googleapis.com/v1/text:synthesize`

#### Request

**Headers**:
```
Content-Type: application/json
Authorization: Bearer {ACCESS_TOKEN}
```

**Request Body**:
```json
{
  "input": {
    "text": "안녕하세요. 오늘의 Hugging Face 트렌딩 논문을 소개합니다. 첫 번째 논문은 '동적 어텐션을 활용한 효율적인 트랜스포머'입니다..."
  },
  "voice": {
    "languageCode": "ko-KR",
    "name": "ko-KR-Wavenet-A",
    "ssmlGender": "NEUTRAL"
  },
  "audioConfig": {
    "audioEncoding": "MP3",
    "speakingRate": 1.0,
    "pitch": 0.0,
    "volumeGainDb": 0.0,
    "sampleRateHertz": 24000
  }
}
```

#### Response

**Status Code**: `200 OK`

**Response Body**:
```json
{
  "audioContent": "//NExAASCCIIAAhEuUAAASDg4OEhQo...(base64 encoded MP3 data)..."
}
```

#### Error Responses

**Status Code**: `400 Bad Request`
```json
{
  "error": {
    "code": 400,
    "message": "Invalid input: text is empty",
    "status": "INVALID_ARGUMENT"
  }
}
```

**Status Code**: `401 Unauthorized`
```json
{
  "error": {
    "code": 401,
    "message": "Request is missing required authentication credential",
    "status": "UNAUTHENTICATED"
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

**Status Code**: `503 Service Unavailable`
```json
{
  "error": {
    "code": 503,
    "message": "Service temporarily unavailable",
    "status": "UNAVAILABLE"
  }
}
```

## Contract Tests

### Success Scenario

```python
def test_google_tts_success():
    """텍스트를 MP3로 성공적으로 변환한다"""
    from google.cloud import texttospeech
    
    client = texttospeech.TextToSpeechClient()
    
    synthesis_input = texttospeech.SynthesisInput(
        text="안녕하세요. 테스트 음성입니다."
    )
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name="ko-KR-Wavenet-A",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
        pitch=0.0,
        sample_rate_hertz=24000
    )
    
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    assert response.audio_content is not None
    assert len(response.audio_content) > 0
    assert response.audio_content[:3] == b'ID3'  # MP3 magic bytes
```

### SSML Support Scenario

```python
def test_google_tts_with_ssml():
    """SSML을 사용한 음성 변환"""
    from google.cloud import texttospeech
    
    client = texttospeech.TextToSpeechClient()
    
    ssml_text = """
    <speak>
        <prosody rate="medium" pitch="+0st">
            안녕하세요. <break time="500ms"/>
            오늘의 논문을 소개합니다.
        </prosody>
    </speak>
    """
    
    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
    
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        name="ko-KR-Wavenet-A"
    )
    
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )
    
    assert response.audio_content is not None
```

### Text Length Limit Scenario

```python
def test_google_tts_text_length_limit():
    """텍스트 길이 제한 처리"""
    # Google TTS는 단일 요청당 최대 5,000자 제한
    long_text = "테스트 " * 1000  # 5,000자 초과
    
    # 텍스트를 청크로 분할
    max_chars = 4000
    chunks = [long_text[i:i+max_chars] for i in range(0, len(long_text), max_chars)]
    
    assert len(chunks) > 1
    assert all(len(chunk) <= max_chars for chunk in chunks)
```

## Voice Options

### Available Korean Voices

| Voice Name | Gender | Type | Quality |
|------------|--------|------|---------|
| ko-KR-Wavenet-A | Female | Wavenet | High |
| ko-KR-Wavenet-B | Female | Wavenet | High |
| ko-KR-Wavenet-C | Male | Wavenet | High |
| ko-KR-Wavenet-D | Male | Wavenet | High |
| ko-KR-Standard-A | Female | Standard | Medium |
| ko-KR-Standard-B | Female | Standard | Medium |

**Recommended**: `ko-KR-Wavenet-A` (자연스러운 여성 음성, 고품질)

## Audio Configuration

### Recommended Settings

- **audioEncoding**: `MP3` (웹 호환성 및 파일 크기)
- **speakingRate**: `1.0` (표준 속도, 0.25 ~ 4.0 범위)
- **pitch**: `0.0` (자연스러운 음높이, -20.0 ~ 20.0 범위)
- **sampleRateHertz**: `24000` (고품질, 8000/16000/24000 지원)
- **volumeGainDb**: `0.0` (표준 볼륨, -96.0 ~ 16.0 범위)

## Implementation Notes

- 인증: Service Account JSON 키 또는 Application Default Credentials
- 텍스트 길이 제한: 단일 요청당 최대 5,000자
- SSML 지원으로 발음, 속도, 휴지 조정 가능
- 요금: 100만 문자당 $4 (Wavenet), $16 (WaveNet HD)
- 무료 티어: 월 100만 문자까지 Standard voices 무료
- MP3 파일은 base64 인코딩되어 반환됨 (디코딩 필요)

