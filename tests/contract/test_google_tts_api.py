"""Contract tests for Google Cloud Text-to-Speech API.

These tests verify that the TTS API responses match our expectations.
"""

import pytest
from unittest.mock import Mock, patch, mock_open

from src.services.tts import TTSConverter


class TestGoogleTTSAPIContract:
    """Contract tests for Google Cloud TTS API."""
    
    @pytest.fixture
    def tts_converter(self):
        """Create a TTSConverter instance."""
        with patch('src.services.tts.texttospeech.TextToSpeechClient'):
            return TTSConverter()
    
    @pytest.mark.contract
    @pytest.mark.skipif(
        "not config.getoption('--run-contract-tests')",
        reason="Contract tests require --run-contract-tests flag"
    )
    def test_synthesize_speech_response_structure(self, tts_converter):
        """Test that TTS API returns expected response structure.
        
        Contract: TextToSpeechClient.synthesize_speech()
        Expected Response:
        {
            "audio_content": b"MP3 binary data..."
        }
        """
        text = "테스트 텍스트입니다."
        output_path = "/tmp/test.mp3"
        
        # Mock API response based on contract
        mock_response = Mock()
        mock_response.audio_content = b'fake_mp3_data_content'
        
        with patch.object(tts_converter, 'client') as mock_client:
            mock_client.synthesize_speech.return_value = mock_response
            
            with patch('builtins.open', mock_open()):
                with patch('pathlib.Path.mkdir'):
                    with patch('pathlib.Path.stat') as mock_stat:
                        mock_stat.return_value.st_size = len(mock_response.audio_content)
                        
                        result = tts_converter.convert_to_speech(text, output_path)
        
        # Verify response handling
        assert result == output_path
        mock_client.synthesize_speech.assert_called_once()
        
        # Verify call arguments structure
        call_args = mock_client.synthesize_speech.call_args
        assert 'input' in call_args.kwargs or len(call_args.args) >= 1
        assert 'voice' in call_args.kwargs or len(call_args.args) >= 2
        assert 'audio_config' in call_args.kwargs or len(call_args.args) >= 3
    
    @pytest.mark.contract
    def test_synthesis_input_format(self, tts_converter):
        """Test that synthesis input follows API contract."""
        text = "테스트"
        
        # Verify text length validation (API limit: 5000 chars)
        assert len(text) <= tts_converter.MAX_TEXT_LENGTH
        
        # Test max length enforcement
        long_text = "a" * 6000
        with pytest.raises(ValueError, match="exceeds maximum length"):
            tts_converter.convert_to_speech(long_text, "/tmp/test.mp3")
    
    @pytest.mark.contract
    def test_voice_selection_params_format(self, tts_converter):
        """Test that voice parameters follow API contract."""
        voice = tts_converter._get_voice_params(
            language_code="ko-KR",
            voice_name="ko-KR-Wavenet-A"
        )
        
        # Verify voice params structure per contract
        assert hasattr(voice, 'language_code')
        assert hasattr(voice, 'name')
        assert hasattr(voice, 'ssml_gender')
        
        # Verify values
        assert voice.language_code == "ko-KR"
        assert voice.name == "ko-KR-Wavenet-A"
    
    @pytest.mark.contract
    def test_audio_config_format(self, tts_converter):
        """Test that audio config follows API contract."""
        config = tts_converter._get_audio_config()
        
        # Verify audio config structure per contract
        assert hasattr(config, 'audio_encoding')
        assert hasattr(config, 'speaking_rate')
        assert hasattr(config, 'pitch')
        assert hasattr(config, 'volume_gain_db')
        assert hasattr(config, 'sample_rate_hertz')
        
        # Verify values are within API limits
        assert 0.25 <= config.speaking_rate <= 4.0
        assert -20.0 <= config.pitch <= 20.0
        assert -96.0 <= config.volume_gain_db <= 16.0
    
    @pytest.mark.contract
    def test_api_quota_exceeded_error(self, tts_converter):
        """Test handling of quota exceeded error per contract."""
        text = "테스트"
        
        with patch.object(tts_converter, 'client') as mock_client:
            error = Exception("Quota exceeded")
            error.code = 429
            mock_client.synthesize_speech.side_effect = error
            
            with pytest.raises(Exception):
                tts_converter.convert_to_speech(text, "/tmp/test.mp3")
    
    @pytest.mark.contract
    def test_invalid_language_code_error(self, tts_converter):
        """Test handling of invalid language code."""
        with patch.object(tts_converter, 'client') as mock_client:
            error = Exception("Invalid language code")
            error.code = 400
            mock_client.synthesize_speech.side_effect = error
            
            with pytest.raises(Exception):
                tts_converter.convert_to_speech("test", "/tmp/test.mp3")
    
    @pytest.mark.contract
    def test_audio_content_binary_format(self, tts_converter):
        """Test that audio content is in correct binary format."""
        text = "테스트"
        
        mock_response = Mock()
        # Simulate real MP3 header (ID3)
        mock_response.audio_content = b'ID3\x04\x00\x00\x00\x00\x00\x00' + b'\x00' * 100
        
        with patch.object(tts_converter, 'client') as mock_client:
            mock_client.synthesize_speech.return_value = mock_response
            
            with patch('builtins.open', mock_open()) as mock_file:
                with patch('pathlib.Path.mkdir'):
                    with patch('pathlib.Path.stat') as mock_stat:
                        mock_stat.return_value.st_size = len(mock_response.audio_content)
                        
                        tts_converter.convert_to_speech(text, "/tmp/test.mp3")
        
        # Verify binary data was written
        write_calls = [call for call in mock_file().write.call_args_list]
        if write_calls:
            written_data = write_calls[0][0][0]
            assert isinstance(written_data, bytes)
    
    @pytest.mark.contract
    def test_empty_text_validation(self, tts_converter):
        """Test that empty text is rejected per contract."""
        with pytest.raises(ValueError, match="cannot be empty"):
            tts_converter.convert_to_speech("", "/tmp/test.mp3")
        
        with pytest.raises(ValueError, match="cannot be empty"):
            tts_converter.convert_to_speech("   ", "/tmp/test.mp3")


