"""Contract tests for Google Gemini Pro API.

These tests verify that the Gemini API responses match our expectations.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.models.paper import Paper
from src.services.summarizer import Summarizer


class TestGeminiAPIContract:
    """Contract tests for Gemini Pro API."""
    
    @pytest.fixture
    def summarizer(self):
        """Create a Summarizer instance."""
        with patch('src.services.summarizer.genai.configure'):
            with patch('src.services.summarizer.genai.GenerativeModel'):
                return Summarizer(api_key="test_key")
    
    @pytest.fixture
    def sample_paper(self):
        """Create a sample paper."""
        return Paper(
            id="2401.12345",
            title="Test Paper",
            authors=["Author1"],
            abstract="This is a test abstract for validation.",
            url="https://huggingface.co/papers/2401.12345",
            collected_at=datetime.utcnow()
        )
    
    @pytest.mark.contract
    @pytest.mark.skipif(
        "not config.getoption('--run-contract-tests')",
        reason="Contract tests require --run-contract-tests flag"
    )
    def test_generate_content_response_structure(self, summarizer, sample_paper):
        """Test that Gemini API returns expected response structure.
        
        Contract: GenerativeModel.generate_content()
        Expected Response:
        {
            "text": "Generated summary text...",
            "prompt_feedback": {...},
            "candidates": [...]
        }
        """
        # Mock API response based on contract
        mock_response = Mock()
        mock_response.text = "이것은 생성된 요약입니다. 논문의 주요 내용을 포함합니다. 적절한 길이를 유지합니다."
        
        with patch.object(summarizer, 'model') as mock_model:
            mock_model.generate_content.return_value = mock_response
            
            summary = summarizer.generate_summary(sample_paper)
        
        # Verify response structure
        assert isinstance(summary, str)
        assert len(summary) >= 50  # Minimum length validation
        assert len(summary) <= 1000  # Maximum length validation
    
    @pytest.mark.contract
    def test_api_quota_exceeded_error(self, summarizer, sample_paper):
        """Test handling of quota exceeded error per contract."""
        with patch.object(summarizer, 'model') as mock_model:
            error = Exception("Resource exhausted (quota exceeded)")
            error.code = 429
            mock_model.generate_content.side_effect = error
            
            with pytest.raises(Exception) as exc_info:
                summarizer.generate_summary(sample_paper)
            
            assert "quota" in str(exc_info.value).lower() or "exhausted" in str(exc_info.value).lower()
    
    @pytest.mark.contract
    def test_api_invalid_request_error(self, summarizer, sample_paper):
        """Test handling of invalid request error."""
        with patch.object(summarizer, 'model') as mock_model:
            error = Exception("Invalid request: prompt too long")
            error.code = 400
            mock_model.generate_content.side_effect = error
            
            with pytest.raises(Exception):
                summarizer.generate_summary(sample_paper)
    
    @pytest.mark.contract
    def test_generation_config_compliance(self, summarizer, sample_paper):
        """Test that generation config follows API specifications."""
        mock_response = Mock()
        mock_response.text = "생성된 요약 텍스트입니다. 충분한 길이를 가지고 있습니다. 논문의 핵심 내용을 담고 있습니다."
        
        with patch.object(summarizer, 'model') as mock_model:
            mock_model.generate_content.return_value = mock_response
            
            summarizer.generate_summary(sample_paper)
            
            # Verify generation_config is passed
            call_args = mock_model.generate_content.call_args
            assert call_args is not None
            
            # Check that generation config exists
            assert summarizer.generation_config is not None
            assert 'temperature' in summarizer.generation_config
            assert 'max_output_tokens' in summarizer.generation_config
    
    @pytest.mark.contract
    def test_prompt_format_compliance(self, summarizer, sample_paper):
        """Test that prompts follow expected format."""
        prompt = summarizer._create_prompt(sample_paper, language="ko")
        
        # Verify prompt contains required elements
        assert sample_paper.title in prompt
        assert sample_paper.abstract in prompt
        assert "요약" in prompt  # Korean prompt should contain "요약"
        
        # Verify prompt structure
        assert len(prompt) > 0
        assert len(prompt) < 10000  # Within API limits
    
    @pytest.mark.contract
    def test_summary_validation_contract(self, summarizer):
        """Test that summary validation follows contract rules."""
        # Test minimum length
        short_summary = "짧음"
        assert not summarizer._validate_summary(short_summary)
        
        # Test maximum length
        long_summary = "a" * 1500
        assert not summarizer._validate_summary(long_summary)
        
        # Test valid length
        valid_summary = "적절한 길이의 요약입니다. " * 10
        assert summarizer._validate_summary(valid_summary)
        
        # Test empty
        assert not summarizer._validate_summary("")
        assert not summarizer._validate_summary(None)


