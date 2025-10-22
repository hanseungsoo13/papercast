"""Unit tests for paper collector service."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.models.paper import Paper
from src.services.collector import PaperCollector


class TestPaperCollector:
    """Test cases for PaperCollector."""
    
    @pytest.fixture
    def collector(self):
        """Create a PaperCollector instance for testing."""
        return PaperCollector()
    
    @pytest.fixture
    def mock_paper_data(self):
        """Mock paper data from Hugging Face API.
        
        Matches actual API structure with 'paper' object nested inside.
        """
        return [
            {
                "paper": {
                    "id": "2401.12345",
                    "authors": [{"name": "John Doe"}]
                },
                "title": "Efficient Transformers with Dynamic Attention",
                "summary": "We propose a novel approach...",
                "publishedAt": "2025-01-27T00:00:00.000Z",
                "numComments": 142
            },
            {
                "paper": {
                    "id": "2401.12346",
                    "authors": [{"name": "Jane Smith"}]
                },
                "title": "Multimodal Learning for VQA",
                "summary": "This paper presents...",
                "publishedAt": "2025-01-27T00:00:00.000Z",
                "numComments": 98
            },
            {
                "paper": {
                    "id": "2401.12347",
                    "authors": [{"name": "Bob Wilson"}]
                },
                "title": "Zero-Shot Classification",
                "summary": "We introduce...",
                "publishedAt": "2025-01-27T00:00:00.000Z",
                "numComments": 75
            }
        ]
    
    @pytest.mark.unit
    def test_fetch_papers_success(self, collector, mock_paper_data):
        """Test successful paper fetching."""
        with patch('src.services.collector.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_paper_data
            mock_get.return_value = mock_response
            
            papers = collector.fetch_papers(count=3)
            
            assert len(papers) == 3
            assert all(isinstance(paper, Paper) for paper in papers)
            assert papers[0].id == "2401.12345"
            assert papers[0].title == "Efficient Transformers with Dynamic Attention"
            assert papers[0].abstract == "We propose a novel approach..."
            assert papers[0].upvotes == 142
    
    @pytest.mark.unit
    def test_fetch_papers_empty_response(self, collector):
        """Test handling of empty response."""
        with patch('src.services.collector.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response
            
            with pytest.raises(ValueError, match="No papers found"):
                collector.fetch_papers(count=3)
    
    @pytest.mark.unit
    def test_fetch_papers_api_error(self, collector):
        """Test handling of API errors."""
        with patch('src.services.collector.requests.get') as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            with pytest.raises(Exception):
                collector.fetch_papers(count=3)
    
    @pytest.mark.unit
    def test_fetch_papers_rate_limit(self, collector):
        """Test handling of rate limiting."""
        with patch('src.services.collector.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.json.return_value = {"error": "Rate limit exceeded"}
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception, match="Rate limit"):
                collector.fetch_papers(count=3)
    
    @pytest.mark.unit
    def test_parse_paper_data(self, collector, mock_paper_data):
        """Test paper data parsing."""
        paper = collector._parse_paper(mock_paper_data[0])
        
        assert isinstance(paper, Paper)
        assert paper.id == "2401.12345"
        assert paper.title == "Efficient Transformers with Dynamic Attention"
        assert "John Doe" in paper.authors
        assert paper.abstract == "We propose a novel approach..."
        assert paper.upvotes == 142
    
    @pytest.mark.unit
    def test_get_top_papers(self, collector, mock_paper_data):
        """Test getting top N papers."""
        with patch('src.services.collector.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_paper_data
            mock_get.return_value = mock_response
            
            papers = collector.fetch_papers(count=2)
            
            assert len(papers) == 2
            assert papers[0].upvotes >= papers[1].upvotes

