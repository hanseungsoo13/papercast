"""Unit tests for paper collector service."""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup

from src.models.paper import Paper
from src.services.collector import PaperCollector


class TestPaperCollector:
    """Test cases for PaperCollector."""
    
    @pytest.fixture
    def collector(self):
        """Create a PaperCollector instance for testing."""
        return PaperCollector()
    
    @pytest.fixture
    def mock_html_content(self):
        """Mock HTML content from Hugging Face papers page."""
        return """
        <html>
        <body>
            <article class="paper-card">
                <h3><a href="/papers/2401.12345">Efficient Transformers with Dynamic Attention</a></h3>
                <div class="authors"><a href="/user1">John Doe</a>, <a href="/user2">Jane Smith</a></div>
                <p class="abstract">We propose a novel approach to transformer efficiency...</p>
                <span class="upvotes">142 upvotes</span>
                <img src="/thumbnails/2401.12345.jpg" alt="thumbnail">
                <span class="tag">Machine Learning</span>
                <span class="tag">NLP</span>
            </article>
            <article class="paper-card">
                <h3><a href="/papers/2401.12346">Multimodal Learning for VQA</a></h3>
                <div class="authors"><a href="/user3">Bob Wilson</a></div>
                <p class="abstract">This paper presents a comprehensive study...</p>
                <div class="upvotes">98 upvotes</div>
                <img src="/thumbnails/2401.12346.jpg" alt="thumbnail">
                <span class="tag">Computer Vision</span>
            </article>
            <article class="paper-card">
                <h3><a href="/papers/2401.12347">Zero-Shot Classification</a></h3>
                <div class="authors"><a href="/user4">Alice Johnson</a></div>
                <p class="abstract">We introduce a novel zero-shot approach...</p>
                <div class="upvotes">75 upvotes</div>
                <img src="/thumbnails/2401.12347.jpg" alt="thumbnail">
                <span class="tag">Deep Learning</span>
            </article>
        </body>
        </html>
        """
    
    @pytest.fixture
    def mock_paper_data(self):
        """Mock paper data for backward compatibility."""
        return [
            {
                "id": "2401.12345",
                "title": "Efficient Transformers with Dynamic Attention",
                "authors": ["John Doe", "Jane Smith"],
                "abstract": "We propose a novel approach to transformer efficiency...",
                "url": "https://huggingface.co/papers/2401.12345",
                "upvotes": 142,
                "categories": ["Machine Learning", "NLP"],
                "thumbnail_url": "https://huggingface.co/thumbnails/2401.12345.jpg"
            },
            {
                "id": "2401.12346", 
                "title": "Multimodal Learning for VQA",
                "authors": ["Bob Wilson"],
                "abstract": "This paper presents a comprehensive study...",
                "url": "https://huggingface.co/papers/2401.12346",
                "upvotes": 98,
                "categories": ["Computer Vision"],
                "thumbnail_url": "https://huggingface.co/thumbnails/2401.12346.jpg"
            },
            {
                "id": "2401.12347",
                "title": "Zero-Shot Classification", 
                "authors": ["Alice Johnson"],
                "abstract": "We introduce a novel zero-shot approach...",
                "url": "https://huggingface.co/papers/2401.12347",
                "upvotes": 75,
                "categories": ["Deep Learning"],
                "thumbnail_url": "https://huggingface.co/thumbnails/2401.12347.jpg"
            }
        ]
    
    @pytest.mark.unit
    def test_fetch_papers_success(self, collector, mock_html_content):
        """Test successful paper fetching with web scraping."""
        with patch('src.services.collector.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_html_content
            mock_get.return_value = mock_response
            
            papers = collector.fetch_papers(count=3)
            
            assert len(papers) == 3
            assert all(isinstance(paper, Paper) for paper in papers)
            assert papers[0].id == "2401.12345"
            assert papers[0].title == "Efficient Transformers with Dynamic Attention"
            assert "We propose a novel approach" in papers[0].abstract
            assert papers[0].upvotes == 142
            assert papers[0].categories == ["Machine Learning", "NLP"]
            assert papers[0].thumbnail_url == "https://huggingface.co/thumbnails/2401.12345.jpg"
    
    @pytest.mark.unit
    def test_fetch_papers_empty_response(self, collector):
        """Test handling of empty HTML response."""
        with patch('src.services.collector.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html><body></body></html>"
            mock_get.return_value = mock_response
            
            with pytest.raises(ValueError, match="No papers found"):
                collector.fetch_papers(count=3)
    
    @pytest.mark.unit
    def test_fetch_papers_http_error(self, collector):
        """Test handling of HTTP errors."""
        with patch('src.services.collector.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = Exception("404 Not Found")
            mock_get.return_value = mock_response
            
            with pytest.raises(Exception):
                collector.fetch_papers(count=3)
    
    @pytest.mark.unit
    def test_fetch_papers_network_error(self, collector):
        """Test handling of network errors."""
        with patch('src.services.collector.requests.get') as mock_get:
            mock_get.side_effect = Exception("Network Error")
            
            with pytest.raises(Exception):
                collector.fetch_papers(count=3)
    
    @pytest.mark.unit
    def test_parse_paper_from_html(self, collector, mock_html_content):
        """Test paper data parsing from HTML."""
        soup = BeautifulSoup(mock_html_content, 'html.parser')
        articles = soup.find_all('article')
        
        # Mock the _fetch_paper_details method to return expected authors
        with patch.object(collector, '_fetch_paper_details', return_value=(["John Doe", "Jane Smith"], "2025-10-24")):
            paper = collector._parse_paper_from_html(articles[0], "2025-10-24")
        
        assert isinstance(paper, Paper)
        assert paper.id == "2401.12345"
        assert paper.title == "Efficient Transformers with Dynamic Attention"
        assert "John Doe" in paper.authors
        assert "Jane Smith" in paper.authors
        assert "We propose a novel approach" in paper.abstract
        assert paper.upvotes == 142
        assert paper.categories == ["Machine Learning", "NLP"]
        assert paper.thumbnail_url == "https://huggingface.co/thumbnails/2401.12345.jpg"
        assert paper.published_date == "2025-10-24"
    
    @pytest.mark.unit
    def test_check_embed_support(self, collector):
        """Test iframe embed support checking."""
        # Test with headers that allow embedding
        with patch('src.services.collector.requests.head') as mock_head:
            mock_response = Mock()
            mock_response.headers = {}
            mock_head.return_value = mock_response
            
            result = collector._check_embed_support("https://example.com")
            assert result is True
        
        # Test with headers that deny embedding
        with patch('src.services.collector.requests.head') as mock_head:
            mock_response = Mock()
            mock_response.headers = {'X-Frame-Options': 'DENY'}
            mock_head.return_value = mock_response
            
            result = collector._check_embed_support("https://example.com")
            assert result is False
    
    @pytest.mark.unit
    def test_get_previous_day_url(self, collector):
        """Test URL generation for previous day."""
        from datetime import date, timedelta
        
        # Mock datetime.now() instead of date module
        with patch('src.services.collector.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 10, 25, 12, 0, 0)
            mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
            
            # Test the actual URL generation logic in fetch_papers
            with patch('src.services.collector.requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = "<html><body></body></html>"
                mock_get.return_value = mock_response
                
                # This should generate the correct URL internally
                try:
                    collector.fetch_papers(count=1)
                except ValueError:
                    pass  # Expected since we return empty HTML
                
                # Check that the URL was called with the correct date
                mock_get.assert_called_once()
                call_args = mock_get.call_args[0][0]
                assert "date=2025-10-24" in call_args
    
    @pytest.mark.unit
    def test_enhanced_paper_fields(self, collector, mock_html_content):
        """Test that enhanced paper fields are properly extracted."""
        with patch('src.services.collector.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_html_content
            mock_get.return_value = mock_response
            
            # Mock embed support check
            with patch.object(collector, '_check_embed_support', return_value=True):
                papers = collector.fetch_papers(count=1)
                
                paper = papers[0]
                assert paper.arxiv_id == "2401.12345"  # Should match paper ID
                assert paper.categories is not None
                assert len(paper.categories) > 0
                assert paper.thumbnail_url is not None
                assert paper.embed_supported is True

