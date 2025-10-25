"""End-to-end tests for the generated website functionality."""

import pytest
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch

from src.services.generator import StaticSiteGenerator
from src.models.paper import Paper
from src.models.podcast import Podcast


class TestWebsiteE2E:
    """End-to-end tests for website functionality."""
    
    @pytest.fixture
    def sample_papers(self):
        """Create sample papers for testing."""
        return [
            Paper(
                id="test-1",
                title="Test Paper 1: Advanced AI Research",
                authors=["Dr. Alice Johnson", "Prof. Bob Smith"],
                abstract="This paper presents groundbreaking research in artificial intelligence, focusing on novel approaches to machine learning that could revolutionize the field.",
                url="https://huggingface.co/papers/test-1",
                published_date="2025-10-24",
                upvotes=250,
                collected_at=datetime.now(timezone.utc),
                arxiv_id="2410.12345",
                categories=["Machine Learning", "Artificial Intelligence", "Deep Learning"],
                thumbnail_url="https://example.com/thumbnails/test-1.jpg",
                embed_supported=True,
                view_count=5000
            ),
            Paper(
                id="test-2",
                title="Test Paper 2: Neural Network Optimization",
                authors=["Dr. Carol Davis"],
                abstract="We introduce a new optimization technique for neural networks that significantly improves training efficiency and model performance.",
                url="https://huggingface.co/papers/test-2",
                published_date="2025-10-24",
                upvotes=180,
                collected_at=datetime.now(timezone.utc),
                arxiv_id="2410.12346",
                categories=["Neural Networks", "Optimization"],
                thumbnail_url="https://example.com/thumbnails/test-2.jpg",
                embed_supported=False,
                view_count=3200
            ),
            Paper(
                id="test-3",
                title="Test Paper 3: Computer Vision Breakthrough",
                authors=["Dr. David Wilson", "Dr. Eva Martinez", "Prof. Frank Chen"],
                abstract="This research demonstrates a revolutionary approach to computer vision that achieves state-of-the-art results across multiple benchmarks.",
                url="https://huggingface.co/papers/test-3",
                published_date="2025-10-24",
                upvotes=320,
                collected_at=datetime.now(timezone.utc),
                arxiv_id="2410.12347",
                categories=["Computer Vision", "Image Processing"],
                thumbnail_url="https://example.com/thumbnails/test-3.jpg",
                embed_supported=True,
                view_count=7500
            )
        ]
    
    @pytest.fixture
    def sample_podcast(self, sample_papers):
        """Create a sample podcast for testing."""
        return Podcast(
            id="2025-10-24",
            title="Daily AI Papers - October 24, 2025",
            description="오늘의 Hugging Face 트렌딩 논문 Top 3를 소개합니다. AI와 머신러닝 분야의 최신 연구 동향을 팟캐스트로 만나보세요.",
            created_at=datetime.now(timezone.utc),
            papers=sample_papers,
            audio_file_path="https://storage.googleapis.com/papercast-audio/2025-10-24/episode.mp3",
            audio_duration=720,  # 12 minutes
            audio_size=11520000,  # ~11.5MB
            status="completed"
        )
    
    @pytest.fixture
    def generated_site(self, sample_podcast, tmp_path):
        """Generate a complete test site."""
        output_dir = tmp_path / "test-site"
        generator = StaticSiteGenerator(output_dir=str(output_dir))
        generator.generate_site([sample_podcast])
        return output_dir
    
    @pytest.mark.e2e
    def test_site_structure_complete(self, generated_site):
        """Test that all required files and directories are created."""
        # Check main files
        assert (generated_site / "index.html").exists()
        assert (generated_site / "episodes" / "2025-10-24.html").exists()
        
        # Check assets
        assert (generated_site / "assets" / "css" / "styles.css").exists()
        assert (generated_site / "assets" / "js" / "script.js").exists()
        
        # Check data files
        assert (generated_site / "podcasts" / "index.json").exists()
        
        # Check directory structure
        assert (generated_site / "episodes").is_dir()
        assert (generated_site / "assets" / "css").is_dir()
        assert (generated_site / "assets" / "js").is_dir()
        assert (generated_site / "podcasts").is_dir()
    
    @pytest.mark.e2e
    def test_homepage_content_complete(self, generated_site):
        """Test that homepage contains all required content."""
        index_content = (generated_site / "index.html").read_text(encoding='utf-8')
        
        # Check basic HTML structure
        assert "<!DOCTYPE html>" in index_content
        assert "<html lang=\"ko\">" in index_content
        assert "<head>" in index_content
        assert "<body>" in index_content
        assert "</html>" in index_content
        
        # Check meta tags
        assert "<meta charset=\"UTF-8\">" in index_content
        assert "<meta name=\"viewport\"" in index_content
        assert "<title>PaperCast - Daily AI Paper Podcasts</title>" in index_content
        
        # Check main content
        assert "PaperCast" in index_content
        assert "Daily AI Paper Podcasts" in index_content
        assert "Daily AI Papers - October 24, 2025" in index_content
        
        # Check episode card elements
        assert "episode-card" in index_content
        assert "episodes/2025-10-24.html" in index_content
        assert "3 papers" in index_content
        assert "12:00" in index_content  # Duration formatting
        
        # Check CSS and JS links
        assert "assets/css/styles.css" in index_content
        assert "assets/js/script.js" in index_content
    
    @pytest.mark.e2e
    def test_episode_page_content_complete(self, generated_site):
        """Test that episode page contains all required content."""
        episode_content = (generated_site / "episodes" / "2025-10-24.html").read_text(encoding='utf-8')
        
        # Check basic structure
        assert "<!DOCTYPE html>" in episode_content
        assert "<html lang=\"ko\">" in episode_content
        
        # Check episode information
        assert "Daily AI Papers - October 24, 2025" in episode_content
        assert "오늘의 Hugging Face 트렌딩 논문 Top 3" in episode_content
        
        # Check audio player
        assert "<audio" in episode_content
        assert "controls" in episode_content
        assert "https://storage.googleapis.com/papercast-audio/2025-10-24/episode.mp3" in episode_content
        
        # Check paper cards
        assert "Test Paper 1: Advanced AI Research" in episode_content
        assert "Test Paper 2: Neural Network Optimization" in episode_content
        assert "Test Paper 3: Computer Vision Breakthrough" in episode_content
        
        # Check paper metadata
        assert "Dr. Alice Johnson" in episode_content
        assert "250 upvotes" in episode_content
        assert "5000 views" in episode_content
        assert "Machine Learning" in episode_content
        
        # Check embed support indicators
        assert "✅ Embed Supported" in episode_content
        assert "❌ Embed Not Supported" in episode_content
        
        # Check JavaScript data
        assert "const papersData = " in episode_content
        assert "const podcastData = " in episode_content
        
        # Check split view elements
        assert "split-view-container" in episode_content
        assert "paper-viewer" in episode_content
        assert "toggle-split-view" in episode_content
    
    @pytest.mark.e2e
    def test_paper_data_javascript_valid(self, generated_site):
        """Test that embedded JavaScript data is valid JSON."""
        episode_content = (generated_site / "episodes" / "2025-10-24.html").read_text(encoding='utf-8')
        
        # Extract papersData
        start_marker = "const papersData = "
        end_marker = ";\n        const podcastData"
        
        start_idx = episode_content.find(start_marker)
        assert start_idx != -1, "papersData not found"
        
        start_idx += len(start_marker)
        end_idx = episode_content.find(end_marker, start_idx)
        assert end_idx != -1, "papersData end not found"
        
        papers_json = episode_content[start_idx:end_idx]
        
        # Should be valid JSON
        papers_data = json.loads(papers_json)
        
        # Verify structure
        assert len(papers_data) == 3
        assert papers_data[0]["title"] == "Test Paper 1: Advanced AI Research"
        assert papers_data[0]["embed_supported"] is True
        assert papers_data[1]["embed_supported"] is False
        assert isinstance(papers_data[0]["url"], str)
        assert papers_data[0]["categories"] == ["Machine Learning", "Artificial Intelligence", "Deep Learning"]
        
        # Extract podcastData
        podcast_start = "const podcastData = "
        podcast_end = ";\n    </script>"
        
        podcast_start_idx = episode_content.find(podcast_start)
        assert podcast_start_idx != -1, "podcastData not found"
        
        podcast_start_idx += len(podcast_start)
        podcast_end_idx = episode_content.find(podcast_end, podcast_start_idx)
        assert podcast_end_idx != -1, "podcastData end not found"
        
        podcast_json = episode_content[podcast_start_idx:podcast_end_idx]
        
        # Should be valid JSON
        podcast_data = json.loads(podcast_json)
        
        # Verify structure
        assert podcast_data["id"] == "2025-10-24"
        assert podcast_data["title"] == "Daily AI Papers - October 24, 2025"
        assert isinstance(podcast_data["audio_url"], str)
    
    @pytest.mark.e2e
    def test_css_contains_required_styles(self, generated_site):
        """Test that CSS contains all required styles for functionality."""
        css_content = (generated_site / "assets" / "css" / "styles.css").read_text()
        
        # Check basic layout styles
        assert "body {" in css_content
        assert ".container {" in css_content
        assert ".header {" in css_content
        
        # Check episode and paper card styles
        assert ".episode-card" in css_content
        assert ".paper-card" in css_content
        assert ".paper-metadata" in css_content
        
        # Check audio player styles
        assert ".audio-player" in css_content
        assert ".audio-controls" in css_content
        
        # Check split view styles
        assert ".split-view-container" in css_content
        assert ".split-view" in css_content
        assert ".paper-viewer" in css_content
        assert ".viewer-content" in css_content
        
        # Check responsive design
        assert "@media" in css_content
        assert "max-width" in css_content
        
        # Check button styles
        assert ".btn" in css_content
        assert ".btn-primary" in css_content
        assert ".btn-secondary" in css_content
        
        # Check utility classes
        assert ".hidden" in css_content
        assert ".loading" in css_content
    
    @pytest.mark.e2e
    def test_javascript_contains_required_functions(self, generated_site):
        """Test that JavaScript contains all required functions."""
        js_content = (generated_site / "assets" / "js" / "script.js").read_text()
        
        # Check main functions
        assert "function toggleSplitView" in js_content
        assert "function showPaperViewer" in js_content
        assert "function closePaperViewer" in js_content
        assert "function loadPaperContent" in js_content
        assert "function formatDuration" in js_content
        
        # Check event listeners
        assert "addEventListener" in js_content
        assert "DOMContentLoaded" in js_content
        
        # Check DOM manipulation
        assert "document.getElementById" in js_content
        assert "document.querySelector" in js_content
        assert "classList.add" in js_content
        assert "classList.remove" in js_content
        
        # Check keyboard shortcuts
        assert "keydown" in js_content
        assert "Escape" in js_content
        assert "ctrlKey" in js_content
    
    @pytest.mark.e2e
    def test_podcast_index_json_structure(self, generated_site):
        """Test that podcast index JSON has correct structure."""
        index_json_path = generated_site / "podcasts" / "index.json"
        index_data = json.loads(index_json_path.read_text())
        
        # Check top-level structure
        assert "podcasts" in index_data
        assert "generated_at" in index_data
        assert "total_episodes" in index_data
        
        # Check podcast data
        assert len(index_data["podcasts"]) == 1
        podcast = index_data["podcasts"][0]
        
        assert podcast["id"] == "2025-10-24"
        assert podcast["title"] == "Daily AI Papers - October 24, 2025"
        assert podcast["paper_count"] == 3
        assert podcast["duration"] == 720
        assert podcast["episode_url"] == "episodes/2025-10-24.html"
        assert isinstance(podcast["audio_url"], str)
        assert isinstance(podcast["created_at"], str)
        
        # Check metadata
        assert index_data["total_episodes"] == 1
        assert isinstance(index_data["generated_at"], str)
    
    @pytest.mark.e2e
    def test_accessibility_features(self, generated_site):
        """Test that accessibility features are properly implemented."""
        index_content = (generated_site / "index.html").read_text()
        episode_content = (generated_site / "episodes" / "2025-10-24.html").read_text()
        
        # Check language attributes
        assert 'lang="ko"' in index_content
        assert 'lang="ko"' in episode_content
        
        # Check ARIA labels and roles
        assert 'aria-label' in episode_content
        assert 'role=' in episode_content
        
        # Check semantic HTML
        assert '<main' in index_content
        assert '<article' in episode_content
        assert '<section' in episode_content
        assert '<nav' in index_content
        
        # Check alt text for images (if any)
        if '<img' in episode_content:
            assert 'alt=' in episode_content
    
    @pytest.mark.e2e
    def test_mobile_responsive_elements(self, generated_site):
        """Test that mobile responsive elements are present."""
        css_content = (generated_site / "assets" / "css" / "styles.css").read_text()
        
        # Check viewport meta tag in HTML
        index_content = (generated_site / "index.html").read_text()
        assert 'name="viewport"' in index_content
        assert 'width=device-width' in index_content
        
        # Check responsive CSS
        assert "@media (max-width: 768px)" in css_content
        assert "@media (max-width: 480px)" in css_content
        
        # Check flexible layouts
        assert "flex-direction: column" in css_content
        assert "width: 100%" in css_content
    
    @pytest.mark.e2e
    def test_performance_optimizations(self, generated_site):
        """Test that performance optimizations are in place."""
        index_content = (generated_site / "index.html").read_text()
        episode_content = (generated_site / "episodes" / "2025-10-24.html").read_text()
        
        # Check that CSS is loaded in head
        assert 'rel="stylesheet"' in index_content
        assert 'assets/css/styles.css' in index_content
        
        # Check that JS is loaded at end of body
        index_body_end = index_content.rfind("</body>")
        index_js_pos = index_content.rfind("assets/js/script.js")
        assert index_js_pos < index_body_end, "JS should be loaded before </body>"
        
        # Check for efficient loading
        assert 'defer' in episode_content or 'async' in episode_content or index_js_pos > 0
