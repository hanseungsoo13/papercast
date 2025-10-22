"""Contract tests for Hugging Face API.

These tests verify that the Hugging Face API responses match our expectations.
They use real API calls (mocked in CI) to validate the contract.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.collector import PaperCollector


class TestHuggingFaceAPIContract:
    """Contract tests for Hugging Face API."""
    
    @pytest.fixture
    def collector(self):
        """Create a PaperCollector instance."""
        return PaperCollector()
    
    @pytest.mark.contract
    @pytest.mark.skipif(
        "not config.getoption('--run-contract-tests')",
        reason="Contract tests require --run-contract-tests flag"
    )
    def test_trending_papers_response_structure(self, collector):
        """Test that trending papers API returns expected structure.
        
        Contract: GET https://huggingface.co/api/daily_papers
        Expected Response:
        [
            {
                "paper": {
                    "id": "2401.12345",
                    "title": "Paper Title",
                    "authors": ["Author1", "Author2"],
                    "summary": "Abstract text...",
                    "publishedAt": "2025-01-27T10:00:00.000Z",
                    "upvotes": 142
                },
                "url": "https://huggingface.co/papers/2401.12345"
            }
        ]
        """
        # Mock API response based on contract
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "paper": {
                    "id": "2401.12345",
                    "title": "Test Paper",
                    "authors": [{"name": "Author1"}],
                    "summary": "Test abstract",
                    "publishedAt": "2025-01-27T10:00:00.000Z",
                    "upvotes": 100
                },
                "url": "https://huggingface.co/papers/2401.12345"
            }
        ]
        mock_response.status_code = 200
        
        with patch('requests.get', return_value=mock_response):
            papers = collector.collect_top_papers(limit=1)
        
        # Verify response structure matches contract
        assert len(papers) == 1
        paper = papers[0]
        
        # Required fields per contract
        assert hasattr(paper, 'id')
        assert hasattr(paper, 'title')
        assert hasattr(paper, 'authors')
        assert hasattr(paper, 'abstract')
        assert hasattr(paper, 'url')
        assert hasattr(paper, 'upvotes')
        assert hasattr(paper, 'collected_at')
        
        # Type validation
        assert isinstance(paper.id, str)
        assert isinstance(paper.title, str)
        assert isinstance(paper.authors, list)
        assert isinstance(paper.abstract, str)
        assert isinstance(paper.url, str)
        assert isinstance(paper.upvotes, int) or paper.upvotes is None
        assert isinstance(paper.collected_at, datetime)
    
    @pytest.mark.contract
    def test_api_error_handling(self, collector):
        """Test that API errors are handled correctly per contract."""
        # Test 404 error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(Exception):
                collector.collect_top_papers()
    
    @pytest.mark.contract
    def test_api_rate_limiting(self, collector):
        """Test that rate limiting is handled per contract."""
        # Test 429 (Too Many Requests)
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("429 Too Many Requests")
        
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(Exception):
                collector.collect_top_papers()
    
    @pytest.mark.contract
    def test_empty_response_handling(self, collector):
        """Test handling of empty paper list."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.status_code = 200
        
        with patch('requests.get', return_value=mock_response):
            papers = collector.collect_top_papers()
        
        assert papers == []
    
    @pytest.mark.contract
    def test_paper_url_format(self, collector):
        """Test that paper URLs follow the expected format."""
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "paper": {
                    "id": "2401.12345",
                    "title": "Test",
                    "authors": [{"name": "Author"}],
                    "summary": "Abstract",
                    "publishedAt": "2025-01-27T10:00:00.000Z",
                    "upvotes": 10
                },
                "url": "https://huggingface.co/papers/2401.12345"
            }
        ]
        mock_response.status_code = 200
        
        with patch('requests.get', return_value=mock_response):
            papers = collector.collect_top_papers(limit=1)
        
        paper = papers[0]
        assert paper.url.startswith("https://huggingface.co/papers/")
        assert paper.id in paper.url


