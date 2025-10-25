"""Unit tests for Paper model."""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from src.models.paper import Paper


class TestPaper:
    """Test cases for Paper model."""
    
    @pytest.fixture
    def basic_paper_data(self):
        """Basic paper data for testing."""
        return {
            "id": "2401.12345",
            "title": "Test Paper: Advanced AI Research",
            "authors": ["John Doe", "Jane Smith"],
            "abstract": "This is a test abstract for our paper model testing.",
            "url": "https://huggingface.co/papers/2401.12345",
            "collected_at": datetime.now(timezone.utc)
        }
    
    @pytest.fixture
    def enhanced_paper_data(self):
        """Enhanced paper data with all new fields."""
        return {
            "id": "2401.12345",
            "title": "Test Paper: Advanced AI Research",
            "authors": ["John Doe", "Jane Smith"],
            "abstract": "This is a test abstract for our paper model testing.",
            "url": "https://huggingface.co/papers/2401.12345",
            "published_date": "2025-10-24",
            "upvotes": 150,
            "collected_at": datetime.now(timezone.utc),
            "arxiv_id": "2401.12345",
            "categories": ["Machine Learning", "NLP", "AI"],
            "thumbnail_url": "https://example.com/thumbnail.jpg",
            "embed_supported": True,
            "view_count": 2500
        }
    
    @pytest.mark.unit
    def test_basic_paper_creation(self, basic_paper_data):
        """Test basic paper creation with required fields only."""
        paper = Paper(**basic_paper_data)
        
        assert paper.id == "2401.12345"
        assert paper.title == "Test Paper: Advanced AI Research"
        assert len(paper.authors) == 2
        assert "John Doe" in paper.authors
        assert str(paper.url) == "https://huggingface.co/papers/2401.12345"
        assert paper.collected_at is not None
        
        # Optional fields should be None
        assert paper.arxiv_id is None
        assert paper.categories is None
        assert paper.thumbnail_url is None
        assert paper.embed_supported is None
        assert paper.view_count is None
    
    @pytest.mark.unit
    def test_enhanced_paper_creation(self, enhanced_paper_data):
        """Test paper creation with all enhanced fields."""
        paper = Paper(**enhanced_paper_data)
        
        # Basic fields
        assert paper.id == "2401.12345"
        assert paper.title == "Test Paper: Advanced AI Research"
        assert len(paper.authors) == 2
        
        # Enhanced fields
        assert paper.arxiv_id == "2401.12345"
        assert paper.categories == ["Machine Learning", "NLP", "AI"]
        assert paper.thumbnail_url == "https://example.com/thumbnail.jpg"
        assert paper.embed_supported is True
        assert paper.view_count == 2500
    
    @pytest.mark.unit
    def test_paper_validation_errors(self):
        """Test paper validation with invalid data."""
        # Missing required fields
        with pytest.raises(ValidationError):
            Paper()
        
        # Invalid URL
        with pytest.raises(ValidationError):
            Paper(
                id="test",
                title="Test",
                authors=["Author"],
                abstract="Abstract",
                url="not-a-valid-url",
                collected_at=datetime.now(timezone.utc)
            )
        
        # Negative view count
        with pytest.raises(ValidationError):
            Paper(
                id="test",
                title="Test",
                authors=["Author"],
                abstract="Abstract",
                url="https://example.com",
                collected_at=datetime.now(timezone.utc),
                view_count=-100
            )
    
    @pytest.mark.unit
    def test_paper_serialization(self, enhanced_paper_data):
        """Test paper serialization to dictionary."""
        paper = Paper(**enhanced_paper_data)
        paper_dict = paper.to_dict()
        
        # Check that all fields are present
        assert "id" in paper_dict
        assert "title" in paper_dict
        assert "authors" in paper_dict
        assert "url" in paper_dict
        assert "arxiv_id" in paper_dict
        assert "categories" in paper_dict
        assert "thumbnail_url" in paper_dict
        assert "embed_supported" in paper_dict
        assert "view_count" in paper_dict
        
        # Check that URL is converted to string
        assert isinstance(paper_dict["url"], str)
        assert paper_dict["url"] == "https://huggingface.co/papers/2401.12345"
        
        # Check datetime serialization
        assert "collected_at" in paper_dict
        assert isinstance(paper_dict["collected_at"], str)
    
    @pytest.mark.unit
    def test_paper_model_dump(self, enhanced_paper_data):
        """Test Pydantic model_dump functionality."""
        paper = Paper(**enhanced_paper_data)
        dumped = paper.model_dump(mode='json')
        
        # URL should be converted to string in JSON mode
        assert isinstance(dumped["url"], str)
        
        # Datetime should be serialized properly
        assert isinstance(dumped["collected_at"], str)
    
    @pytest.mark.unit
    def test_paper_categories_validation(self):
        """Test categories field validation."""
        # Empty categories list should be valid
        paper = Paper(
            id="test",
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com",
            collected_at=datetime.now(timezone.utc),
            categories=[]
        )
        assert paper.categories == []
        
        # None categories should be valid
        paper = Paper(
            id="test",
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com",
            collected_at=datetime.now(timezone.utc),
            categories=None
        )
        assert paper.categories is None
    
    @pytest.mark.unit
    def test_paper_embed_support_boolean(self):
        """Test embed_supported field accepts boolean values."""
        # Test True
        paper = Paper(
            id="test",
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com",
            collected_at=datetime.now(timezone.utc),
            embed_supported=True
        )
        assert paper.embed_supported is True
        
        # Test False
        paper = Paper(
            id="test",
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com",
            collected_at=datetime.now(timezone.utc),
            embed_supported=False
        )
        assert paper.embed_supported is False
        
        # Test None
        paper = Paper(
            id="test",
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com",
            collected_at=datetime.now(timezone.utc),
            embed_supported=None
        )
        assert paper.embed_supported is None
    
    @pytest.mark.unit
    def test_paper_view_count_validation(self):
        """Test view_count field validation."""
        # Valid positive number
        paper = Paper(
            id="test",
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com",
            collected_at=datetime.now(timezone.utc),
            view_count=1000
        )
        assert paper.view_count == 1000
        
        # Zero should be valid
        paper = Paper(
            id="test",
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com",
            collected_at=datetime.now(timezone.utc),
            view_count=0
        )
        assert paper.view_count == 0
        
        # None should be valid
        paper = Paper(
            id="test",
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            url="https://example.com",
            collected_at=datetime.now(timezone.utc),
            view_count=None
        )
        assert paper.view_count is None
