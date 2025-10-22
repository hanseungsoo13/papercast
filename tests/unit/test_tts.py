"""Unit tests for TTS service."""

import pytest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from src.services.tts import TTSConverter


class TestTTSConverter:
    """Test cases for TTSConverter."""
    
    @pytest.fixture
    def tts_converter(self):
        """Create a TTSConverter instance for testing."""
        with patch('src.services.tts.texttospeech.TextToSpeechClient'):
            return TTSConverter()
    
    @pytest.mark.unit
    def test_convert_to_speech_success(self, tts_converter):
        """Test successful text-to-speech conversion."""
        text = "안녕하세요. 오늘의 논문을 소개합니다."
        output_path = "/tmp/test_audio.mp3"
        
        with patch.object(tts_converter, 'client') as mock_client:
            mock_response = Mock()
            mock_response.audio_content = b'fake_audio_data'
            mock_client.synthesize_speech.return_value = mock_response
            
            with patch('builtins.open', mock_open()):
                with patch('pathlib.Path.mkdir'):  # Mock mkdir to avoid file system operations
                    with patch('pathlib.Path.stat') as mock_stat:
                        mock_stat.return_value.st_size = 1024
                        result_path = tts_converter.convert_to_speech(text, output_path)
                        
                        assert result_path == output_path
                        mock_client.synthesize_speech.assert_called_once()
    
    @pytest.mark.unit
    def test_convert_to_speech_empty_text(self, tts_converter):
        """Test handling of empty text."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            tts_converter.convert_to_speech("", "/tmp/output.mp3")
    
    @pytest.mark.unit
    def test_convert_to_speech_text_too_long(self, tts_converter):
        """Test handling of text exceeding length limit."""
        long_text = "a" * 6000  # Exceeds 5000 char limit
        
        with pytest.raises(ValueError, match="Text exceeds maximum length"):
            tts_converter.convert_to_speech(long_text, "/tmp/output.mp3")
    
    @pytest.mark.unit
    def test_convert_to_speech_api_error(self, tts_converter):
        """Test handling of API errors."""
        text = "테스트 텍스트"
        
        with patch.object(tts_converter, 'client') as mock_client:
            mock_client.synthesize_speech.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                tts_converter.convert_to_speech(text, "/tmp/output.mp3")
    
    @pytest.mark.unit
    def test_split_text_into_chunks(self, tts_converter):
        """Test text splitting for long content."""
        # Use English text with ". " for proper splitting
        long_text = "This is a sentence. " * 300  # ~6000 chars
        
        chunks = tts_converter._split_text(long_text, max_length=4000)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 4000 for chunk in chunks)
    
    @pytest.mark.unit
    def test_get_audio_config(self, tts_converter):
        """Test audio configuration creation."""
        config = tts_converter._get_audio_config()
        
        assert config is not None
        # Verify config properties if accessible
    
    @pytest.mark.unit
    def test_get_voice_params(self, tts_converter):
        """Test voice parameters creation."""
        voice = tts_converter._get_voice_params(language_code="ko-KR")
        
        assert voice is not None
        # Verify voice properties if accessible
    
    @pytest.mark.unit
    def test_get_audio_duration(self, tts_converter):
        """Test audio duration calculation."""
        # Mock MP3 file with mutagen
        with patch('mutagen.mp3.MP3') as mock_mp3:
            mock_audio = Mock()
            mock_info = Mock()
            mock_info.length = 120.5  # 2 minutes
            mock_audio.info = mock_info
            mock_mp3.return_value = mock_audio
            
            duration = tts_converter.get_audio_duration("/tmp/test.mp3")
            
            assert duration == 121  # Rounded up

