"""Unit tests for summarizer service."""

import pytest
from unittest.mock import Mock, patch

from src.models.paper import Paper
from src.services.summarizer import Summarizer


class TestSummarizer:
    """Test cases for Summarizer."""
    
    @pytest.fixture
    def summarizer(self):
        """Create a Summarizer instance for testing."""
        with patch('src.services.summarizer.genai.configure'):
            with patch('src.services.summarizer.genai.GenerativeModel'):
                return Summarizer(api_key="test_api_key")
    
    @pytest.fixture
    def sample_paper(self):
        """Create a sample paper for testing."""
        from datetime import datetime
        return Paper(
            id="2401.12345",
            title="Efficient Transformers with Dynamic Attention",
            authors=["John Doe", "Jane Smith"],
            abstract="We propose a novel approach to improve transformer efficiency using dynamic attention mechanisms...",
            url="https://huggingface.co/papers/2401.12345",
            upvotes=142,
            collected_at=datetime.utcnow()
        )
    
    @pytest.mark.unit
    def test_generate_summary_success(self, summarizer, sample_paper):
        """Test successful summary generation."""
        # Make sure summary is long enough (>50 chars)
        mock_summary = "이 논문은 동적 어텐션 메커니즘을 사용하여 트랜스포머의 효율성을 개선하는 새로운 방법을 제안합니다. 실험 결과 기존 방법보다 30% 빠른 처리 속도를 보였습니다."
        
        with patch.object(summarizer, 'model') as mock_model:
            mock_response = Mock()
            mock_response.text = mock_summary
            mock_model.generate_content.return_value = mock_response
            
            summary = summarizer.generate_summary(sample_paper)
            
            assert summary == mock_summary
            assert len(summary) >= 50
            mock_model.generate_content.assert_called_once()
    
    @pytest.mark.unit
    def test_generate_summary_with_custom_prompt(self, summarizer, sample_paper):
        """Test summary generation with custom prompt."""
        mock_summary = "This is a custom summary of the paper that is long enough to pass validation. It describes the paper's main contributions and findings."
        
        with patch.object(summarizer, 'model') as mock_model:
            mock_response = Mock()
            mock_response.text = mock_summary
            mock_model.generate_content.return_value = mock_response
            
            summary = summarizer.generate_summary(sample_paper, language="en")
            
            assert summary == mock_summary
            assert len(summary) >= 50
    
    @pytest.mark.unit
    def test_generate_summary_api_error(self, summarizer, sample_paper):
        """Test handling of API errors."""
        with patch.object(summarizer, 'model') as mock_model:
            mock_model.generate_content.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                summarizer.generate_summary(sample_paper)
    
    @pytest.mark.unit
    def test_generate_summary_quota_exceeded(self, summarizer, sample_paper):
        """Test handling of quota exceeded error."""
        with patch.object(summarizer, 'model') as mock_model:
            error = Exception("Quota exceeded")
            error.code = 429
            mock_model.generate_content.side_effect = error
            
            with pytest.raises(Exception):
                summarizer.generate_summary(sample_paper)
    
    @pytest.mark.unit
    def test_create_prompt(self, summarizer, sample_paper):
        """Test prompt creation."""
        prompt = summarizer._create_prompt(sample_paper)
        
        assert sample_paper.title in prompt
        assert sample_paper.abstract in prompt
        assert "요약" in prompt or "summarize" in prompt.lower()
    
    @pytest.mark.unit
    def test_validate_summary_length(self, summarizer):
        """Test summary length validation."""
        short_summary = "짧은 요약"
        long_summary = "a" * 1500
        valid_summary = "적절한 길이의 요약입니다. " * 10
        
        assert not summarizer._validate_summary(short_summary)
        assert not summarizer._validate_summary(long_summary)
        assert summarizer._validate_summary(valid_summary)

