"""Static site generator for podcast website with paper viewer."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from src.models.podcast import Podcast
from src.utils.logger import logger


class StaticSiteGenerator:
    """Generates static website for podcast with enhanced paper viewing."""
    
    def __init__(self, output_dir: str = "static-site"):
        """Initialize the static site generator.
        
        Args:
            output_dir: Output directory for generated site
        """
        self.output_dir = Path(output_dir)
        self.logger = logger
        
    def generate_site(self, podcasts: List[Podcast]) -> None:
        """Generate complete static site with all episodes.
        
        Args:
            podcasts: List of podcast episodes to generate site for
        """
        self.logger.info("Generating static site...")
        
        # Create output directories
        self._create_directories()
        
        # Generate index page
        self._generate_index_page(podcasts)
        
        # Generate individual episode pages
        for podcast in podcasts:
            self._generate_episode_page(podcast)
        
        # Generate podcast index JSON
        self._generate_podcast_index(podcasts)
        
        # Copy/generate CSS and JS files
        self._generate_styles()
        self._generate_scripts()
        
        self.logger.info(f"Static site generated at {self.output_dir}")
    
    def _create_directories(self) -> None:
        """Create necessary directories for static site."""
        directories = [
            self.output_dir,
            self.output_dir / "episodes",
            self.output_dir / "podcasts",
            self.output_dir / "assets",
            self.output_dir / "assets" / "css",
            self.output_dir / "assets" / "js",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _generate_index_page(self, podcasts: List[Podcast]) -> None:
        """Generate main index.html page.
        
        Args:
            podcasts: List of all podcasts
        """
        # Sort podcasts by date (newest first)
        sorted_podcasts = sorted(podcasts, key=lambda p: p.created_at, reverse=True)
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PaperCast - AI 논문 팟캐스트</title>
    <meta name="description" content="매일 Hugging Face 트렌딩 논문을 음성으로 듣는 팟캐스트">
    <link rel="stylesheet" href="assets/css/styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <h1 class="site-title">🎧 PaperCast</h1>
            <p class="site-subtitle">매일 아침, AI 논문을 음성으로</p>
        </div>
    </header>

    <main class="container">
        <section class="episodes-section">
            <h2 class="section-title">최신 에피소드</h2>
            <div class="episodes-grid">
                {self._generate_episode_cards(sorted_podcasts)}
            </div>
        </section>
    </main>

    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2025 PaperCast. Powered by Hugging Face, Gemini Pro, and Google TTS.</p>
        </div>
    </footer>

    <script src="assets/js/script.js"></script>
</body>
</html>"""
        
        output_path = self.output_dir / "index.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated index page: {output_path}")
    
    def _generate_episode_cards(self, podcasts: List[Podcast]) -> str:
        """Generate HTML for episode cards.
        
        Args:
            podcasts: List of podcasts
            
        Returns:
            HTML string for episode cards
        """
        cards_html = []
        
        for podcast in podcasts:
            # Format date
            date_obj = podcast.created_at
            formatted_date = date_obj.strftime("%Y년 %m월 %d일")
            
            # Calculate duration in minutes
            duration_minutes = podcast.audio_duration // 60
            
            card_html = f"""
                <article class="episode-card">
                    <div class="episode-header">
                        <h3 class="episode-title">{podcast.title}</h3>
                        <div class="episode-meta">
                            <span class="episode-date">📅 {formatted_date}</span>
                            <span class="episode-duration">⏱️ {duration_minutes}분</span>
                        </div>
                    </div>
                    
                    <p class="episode-description">{podcast.description}</p>
                    
                    <div class="paper-preview">
                        <h4 class="paper-preview-title">이번 에피소드의 논문들</h4>
                        <ul class="paper-preview-list">
                            {self._generate_paper_preview_items(podcast.papers)}
                        </ul>
                    </div>
                    
                    <div class="episode-actions">
                        <a href="episodes/{podcast.id}.html" class="btn btn-primary">
                            ▶️ 듣기 & 논문 보기
                        </a>
                        <a href="{podcast.audio_file_path}" download class="btn btn-secondary">
                            📥 다운로드
                        </a>
                    </div>
                </article>
            """
            cards_html.append(card_html)
        
        return "\n".join(cards_html)
    
    def _generate_paper_preview_items(self, papers: List) -> str:
        """Generate paper preview list items.
        
        Args:
            papers: List of papers
            
        Returns:
            HTML string for paper preview items
        """
        items = []
        for i, paper in enumerate(papers, 1):
            item_html = f"""
                <li class="paper-preview-item">
                    <span class="paper-number">{i}</span>
                    <span class="paper-title-preview">{paper.title}</span>
                </li>
            """
            items.append(item_html)
        
        return "\n".join(items)
    
    def _generate_episode_page(self, podcast: Podcast) -> None:
        """Generate individual episode page with paper viewer.
        
        Args:
            podcast: Podcast episode
        """
        date_obj = podcast.created_at
        formatted_date = date_obj.strftime("%Y년 %m월 %d일")
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{podcast.title} - PaperCast</title>
    <meta name="description" content="{podcast.description}">
    <link rel="stylesheet" href="../assets/css/styles.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
</head>
<body>
    <header class="site-header episode-header">
        <div class="container">
            <nav class="breadcrumb">
                <a href="../index.html">🏠 홈</a> / <span>에피소드</span>
            </nav>
            <h1 class="episode-title">{podcast.title}</h1>
            <p class="episode-date">{formatted_date}</p>
        </div>
    </header>

    <main class="episode-main">
        <div class="audio-player-section">
            <div class="container">
                <div class="audio-player-enhanced">
                    <audio id="podcast-audio" controls preload="metadata">
                        <source src="{podcast.audio_file_path}" type="audio/mpeg">
                        죄송합니다. 브라우저가 오디오를 지원하지 않습니다.
                    </audio>
                </div>
                
                <div class="episode-info">
                    <p class="episode-description">{podcast.description}</p>
                </div>
            </div>
        </div>

        <div class="papers-section">
            <div class="container">
                <div class="section-header">
                    <h2 class="section-title">논문 상세 정보</h2>
                    <button id="split-view-toggle" class="btn btn-secondary" aria-label="Split View 토글">
                        🔄 Split View
                    </button>
                </div>
                
                <div class="papers-grid" id="papers-grid">
                    {self._generate_paper_cards(podcast.papers)}
                </div>
            </div>
        </div>

        <!-- Split View Container -->
        <div id="split-view-container" class="split-view-container" data-active="false" aria-hidden="true">
            <div class="split-view-left">
                <div class="player-section-compact">
                    <h3>오디오 플레이어</h3>
                    <div id="audio-player-placeholder" class="audio-player-placeholder">
                        <p>Split View 모드에서는 위의 오디오 플레이어가 이곳으로 이동합니다.</p>
                    </div>
                </div>
            </div>
            
            <div class="split-view-divider" role="separator" aria-orientation="vertical">
                <div class="divider-handle"></div>
            </div>
            
            <div class="split-view-right">
                <div class="paper-viewer-section">
                    <div class="paper-viewer-header">
                        <h3 id="current-paper-title" class="current-paper-title"></h3>
                        <button id="close-split-view" class="close-button" aria-label="Split View 닫기">✕</button>
                    </div>
                    <div class="paper-viewer-content">
                        <iframe id="paper-embed" class="paper-embed" frameborder="0"></iframe>
                        <div id="pdf-viewer-container" class="pdf-viewer-container" style="display: none;">
                            <iframe id="pdf-viewer" class="pdf-viewer" frameborder="0"></iframe>
                        </div>
                        <div id="paper-fallback" class="paper-fallback" style="display: none;">
                            <div class="fallback-content">
                                <svg class="fallback-icon" viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                    <polyline points="14 2 14 8 20 8"></polyline>
                                    <line x1="12" y1="18" x2="12" y2="12"></line>
                                    <line x1="9" y1="15" x2="15" y2="15"></line>
                                </svg>
                                <p>PDF 뷰어를 사용할 수 없습니다.</p>
                                <p class="fallback-description">브라우저에서 직접 PDF를 열어보세요.</p>
                                <a id="fallback-link" href="#" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
                                    <svg class="btn-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                                        <polyline points="15 3 21 3 21 9"></polyline>
                                        <line x1="10" y1="14" x2="21" y2="3"></line>
                                    </svg>
                                    새 탭에서 PDF 열기
                                </a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <footer class="site-footer">
        <div class="container">
            <p>&copy; 2025 PaperCast. Powered by Hugging Face, Gemini Pro, and Google TTS.</p>
        </div>
    </footer>

    <script>
        const papersData = {json.dumps([{
            'id': p.id,
            'title': p.title,
            'authors': p.authors,
            'abstract': p.abstract,
            'url': str(p.url),
            'published_date': p.published_date,
            'upvotes': p.upvotes,
            'summary': p.summary,
            'collected_at': p.collected_at.isoformat() if p.collected_at else None,
            'arxiv_id': p.arxiv_id,
            'categories': p.categories,
            'thumbnail_url': p.thumbnail_url,
            'embed_supported': p.embed_supported,
            'view_count': p.view_count
        } for p in podcast.papers], ensure_ascii=False, indent=2)};
    </script>
    <script src="../assets/js/script.js"></script>
</body>
</html>"""
        
        output_path = self.output_dir / "episodes" / f"{podcast.id}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated episode page: {output_path}")
    
    def _generate_paper_cards(self, papers: List) -> str:
        """Generate HTML for paper cards with enhanced metadata.
        
        Args:
            papers: List of papers
            
        Returns:
            HTML string for paper cards
        """
        cards_html = []
        
        for i, paper in enumerate(papers):
            # Get thumbnail or use placeholder
            thumbnail = paper.thumbnail_url if hasattr(paper, 'thumbnail_url') and paper.thumbnail_url else "../assets/images/placeholder.png"
            
            # Get categories
            categories_html = ""
            if hasattr(paper, 'categories') and paper.categories:
                category_tags = [f'<span class="category-tag">{cat}</span>' for cat in paper.categories[:3]]
                categories_html = f'<div class="category-tags">{" ".join(category_tags)}</div>'
            
            # Get metrics
            upvotes = paper.upvotes if paper.upvotes else 0
            view_count_html = ""
            if hasattr(paper, 'view_count') and paper.view_count:
                view_count_html = f'<span class="view-count">👁️ {paper.view_count}</span>'
            
            # Authors string
            authors_str = ", ".join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors_str += f" 외 {len(paper.authors) - 3}명"
            
            card_html = f"""
                <article class="paper-card" data-paper-id="{paper.id}" data-paper-index="{i}">
                    <div class="paper-thumbnail">
                        <img src="{thumbnail}" alt="{paper.title} thumbnail" loading="lazy">
                        {categories_html}
                    </div>
                    
                    <div class="paper-content">
                        <h3 class="paper-title">{paper.title}</h3>
                        <p class="paper-authors">{authors_str}</p>
                        <p class="paper-abstract">{paper.abstract[:200]}...</p>
                        
                        <div class="paper-meta">
                            <span class="upvotes">👍 {upvotes}</span>
                            {view_count_html}
                            <span class="paper-date">📅 {paper.published_date if paper.published_date else 'N/A'}</span>
                        </div>
                    </div>
                    
                    <div class="paper-actions">
                        <button class="btn btn-primary view-paper-btn" 
                                data-paper-url="{paper.url}" 
                                data-arxiv-id="{paper.arxiv_id if paper.arxiv_id else ''}"
                                onclick="openPaperPDF('{paper.arxiv_id if paper.arxiv_id else ''}', '{paper.url}')">
                            📄 View PDF
                        </button>
                        <button class="btn btn-secondary split-view-btn" 
                                data-paper-id="{paper.id}" 
                                data-paper-index="{i}"
                                onclick="toggleSplitView({i})">
                            🔄 Split View
                        </button>
                    </div>
                </article>
            """
            cards_html.append(card_html)
        
        return "\n".join(cards_html)
    
    def _generate_podcast_index(self, podcasts: List[Podcast]) -> None:
        """Generate podcast index JSON file.
        
        Args:
            podcasts: List of all podcasts
        """
        # Sort by date (newest first)
        sorted_podcasts = sorted(podcasts, key=lambda p: p.created_at, reverse=True)
        
        index_data = {
            "podcasts": [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "created_at": p.created_at.isoformat(),
                    "audio_url": str(p.audio_file_path),  # Convert HttpUrl to string
                    "duration": p.audio_duration,
                    "paper_count": len(p.papers),
                    "episode_url": f"episodes/{p.id}.html"
                }
                for p in sorted_podcasts
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_episodes": len(podcasts)
        }
        
        output_path = self.output_dir / "podcasts" / "index.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Generated podcast index: {output_path}")
    
    def _generate_styles(self) -> None:
        """Generate CSS stylesheet."""
        css_content = """/* PaperCast Styles */

:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    --success-color: #10b981;
    --background-color: #f8fafc;
    --surface-color: #ffffff;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background-color: var(--background-color);
    color: var(--text-primary);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Header */
.site-header {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 3rem 0;
    text-align: center;
}

.site-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.site-subtitle {
    font-size: 1.125rem;
    opacity: 0.9;
}

/* Episodes Grid */
.episodes-section {
    padding: 3rem 0;
}

.section-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 2rem;
    color: var(--text-primary);
}

.episodes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 2rem;
}

.episode-card {
    background: var(--surface-color);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow-md);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.episode-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg);
}

.episode-header {
    margin-bottom: 1rem;
}

.episode-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.episode-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.875rem;
    color: var(--text-secondary);
}

.episode-description {
    color: var(--text-secondary);
    margin-bottom: 1rem;
}

.paper-preview {
    background: var(--background-color);
    border-radius: var(--radius-sm);
    padding: 1rem;
    margin-bottom: 1rem;
}

.paper-preview-title {
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.paper-preview-list {
    list-style: none;
}

.paper-preview-item {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
}

.paper-number {
    flex-shrink: 0;
    width: 1.5rem;
    height: 1.5rem;
    background: var(--primary-color);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
}

.paper-title-preview {
    color: var(--text-secondary);
}

/* Buttons */
.episode-actions {
    display: flex;
    gap: 0.5rem;
}

.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border-radius: var(--radius-sm);
    font-weight: 500;
    text-decoration: none;
    text-align: center;
    transition: all 0.2s ease;
    cursor: pointer;
    border: none;
    font-size: 0.875rem;
}

.btn-primary {
    background: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background: #4f46e5;
}

.btn-secondary {
    background: white;
    color: var(--primary-color);
    border: 1px solid var(--primary-color);
}

.btn-secondary:hover {
    background: var(--primary-color);
    color: white;
}

/* Paper Cards */
.papers-section {
    padding: 2rem 0;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.papers-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 2rem;
}

.paper-card {
    background: var(--surface-color);
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-md);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.paper-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.paper-thumbnail {
    position: relative;
    width: 100%;
    aspect-ratio: 16/9;
    overflow: hidden;
    background: var(--background-color);
}

.paper-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.category-tags {
    position: absolute;
    top: 0.5rem;
    left: 0.5rem;
    display: flex;
    gap: 0.25rem;
    flex-wrap: wrap;
}

.category-tag {
    background: rgba(99, 102, 241, 0.9);
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
}

.paper-content {
    padding: 1.5rem;
}

.paper-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    line-height: 1.4;
}

.paper-authors {
    color: var(--text-secondary);
    font-size: 0.875rem;
    margin-bottom: 0.75rem;
}

.paper-abstract {
    color: var(--text-secondary);
    font-size: 0.875rem;
    margin-bottom: 1rem;
    line-height: 1.6;
}

.paper-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-bottom: 1rem;
}

.paper-actions {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    padding: 0 1.5rem 1.5rem;
}

/* Audio Player */
.audio-player-section {
    background: var(--surface-color);
    padding: 2rem 0;
    border-bottom: 1px solid var(--border-color);
}

.audio-player-enhanced audio {
    width: 100%;
    margin-bottom: 1rem;
}

.episode-info {
    margin-top: 1rem;
}

/* Split View */
.split-view-container {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: var(--surface-color);
    z-index: 1000;
    display: none;
    grid-template-columns: 1fr 4px 1fr;
}

.split-view-container[data-active="true"] {
    display: grid;
}

.split-view-left,
.split-view-right {
    overflow-y: auto;
    padding: 2rem;
}

.split-view-divider {
    background: var(--border-color);
    cursor: col-resize;
    display: flex;
    align-items: center;
    justify-content: center;
}

.divider-handle {
    width: 4px;
    height: 50px;
    background: var(--primary-color);
    border-radius: 2px;
}

.paper-viewer-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border-color);
}

.close-button {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    border: none;
    background: var(--background-color);
    cursor: pointer;
    font-size: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: center;
}

.close-button:hover {
    background: var(--border-color);
}

.paper-embed {
    width: 100%;
    height: calc(100vh - 200px);
    border: none;
}

.pdf-viewer-container {
    width: 100%;
    height: calc(100vh - 200px);
}

.pdf-viewer {
    width: 100%;
    height: 100%;
    border: none;
}

.paper-fallback {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    padding: 3rem;
}

.fallback-content {
    text-align: center;
    max-width: 400px;
}

.fallback-icon {
    color: var(--text-secondary);
    margin: 0 auto 1rem;
}

.fallback-description {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin: 0.5rem 0 1.5rem;
}

.btn-icon {
    margin-right: 0.5rem;
    vertical-align: middle;
}

.audio-player-placeholder {
    min-height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1rem;
    background: var(--background-color);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
}

/* Footer */
.site-footer {
    background: var(--text-primary);
    color: white;
    padding: 2rem 0;
    text-align: center;
    margin-top: 4rem;
}

/* Responsive Design */
@media (max-width: 768px) {
    .site-title {
        font-size: 2rem;
    }
    
    .episodes-grid,
    .papers-grid {
        grid-template-columns: 1fr;
    }
    
    .split-view-container[data-active="true"] {
        display: block;
    }
    
    .split-view-left,
    .split-view-right {
        width: 100%;
        height: auto;
    }
    
    .split-view-divider {
        display: none;
    }
    
    .paper-actions {
        gap: 0.75rem;
    }
    
    .btn {
        width: 100%;
        min-height: 44px;
    }
}

/* Screen Reader Only */
.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}
"""
        
        css_path = self.output_dir / "assets" / "css" / "styles.css"
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        self.logger.info(f"Generated CSS: {css_path}")
    
    def _generate_scripts(self) -> None:
        """Generate JavaScript file."""
        js_content = """// PaperCast JavaScript

// Global state
let splitViewActive = false;
let currentPaperIndex = -1;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
    setupEventListeners();
    setupAccessibility();
});

function initializePage() {
    console.log('PaperCast initialized');
    
    // Check if we're on an episode page
    if (typeof papersData !== 'undefined') {
        console.log(`Loaded ${papersData.length} papers`);
    }
}

function setupEventListeners() {
    // Split View toggle button
    const splitViewToggle = document.getElementById('split-view-toggle');
    if (splitViewToggle) {
        splitViewToggle.addEventListener('click', () => toggleSplitView(0));
    }
    
    // Close Split View button
    const closeSplitView = document.getElementById('close-split-view');
    if (closeSplitView) {
        closeSplitView.addEventListener('click', closeSplitViewMode);
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

function setupAccessibility() {
    // Add ARIA labels dynamically
    const audioElements = document.querySelectorAll('audio');
    audioElements.forEach(audio => {
        if (!audio.getAttribute('aria-label')) {
            audio.setAttribute('aria-label', '팟캐스트 오디오 플레이어');
        }
    });
}

function handleKeyboardShortcuts(event) {
    // Escape: Close split view
    if (event.key === 'Escape' && splitViewActive) {
        closeSplitViewMode();
    }
    
    // Ctrl+S: Toggle split view
    if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        if (currentPaperIndex >= 0) {
            toggleSplitView(currentPaperIndex);
        } else {
            toggleSplitView(0);
        }
    }
}

function openPaperInNewTab(paperUrl) {
    if (paperUrl) {
        window.open(paperUrl, '_blank', 'noopener,noreferrer');
    }
}

function openPaperPDF(arxivId, fallbackUrl) {
    // Try to open ArXiv PDF if arxivId is available
    if (arxivId && arxivId.trim() !== '') {
        const pdfUrl = `https://arxiv.org/pdf/${arxivId}`;
        window.open(pdfUrl, '_blank', 'noopener,noreferrer');
    } else {
        // Fallback to original URL
        openPaperInNewTab(fallbackUrl);
    }
}

function toggleSplitView(paperIndex) {
    if (typeof papersData === 'undefined' || !papersData[paperIndex]) {
        console.error('Paper data not available');
        return;
    }
    
    const paper = papersData[paperIndex];
    const container = document.getElementById('split-view-container');
    
    if (!container) {
        console.error('Split view container not found');
        return;
    }
    
    if (splitViewActive && currentPaperIndex === paperIndex) {
        // Close if same paper
        closeSplitViewMode();
    } else {
        // Open or switch to new paper
        openSplitViewMode(paper, paperIndex);
    }
}

function openSplitViewMode(paper, paperIndex) {
    const container = document.getElementById('split-view-container');
    const paperTitle = document.getElementById('current-paper-title');
    const paperEmbed = document.getElementById('paper-embed');
    const pdfViewerContainer = document.getElementById('pdf-viewer-container');
    const pdfViewer = document.getElementById('pdf-viewer');
    const paperFallback = document.getElementById('paper-fallback');
    const fallbackLink = document.getElementById('fallback-link');
    
    // Update state
    splitViewActive = true;
    currentPaperIndex = paperIndex;
    
    // Show container
    container.setAttribute('data-active', 'true');
    container.setAttribute('aria-hidden', 'false');
    
    // Update title
    paperTitle.textContent = paper.title;
    
    // Move audio player to split view (instead of duplicating)
    moveAudioPlayerToSplitView();
    
    // Hide all viewers initially
    paperEmbed.style.display = 'none';
    pdfViewerContainer.style.display = 'none';
    paperFallback.style.display = 'none';
    
    // Determine how to display the paper
    const arxivId = paper.arxiv_id;
    
    if (arxivId && arxivId.trim() !== '') {
        // Use PDF viewer for ArXiv papers
        const pdfUrl = `https://arxiv.org/pdf/${arxivId}`;
        pdfViewer.src = pdfUrl;
        pdfViewerContainer.style.display = 'block';
    } else if (paper.embed_supported) {
        // Try iframe embedding
        paperEmbed.src = paper.url;
        paperEmbed.style.display = 'block';
    } else {
        // Show fallback with PDF link
        paperFallback.style.display = 'block';
        const fallbackPdfUrl = arxivId ? `https://arxiv.org/pdf/${arxivId}` : paper.url;
        fallbackLink.href = fallbackPdfUrl;
    }
    
    // Update button state
    updateSplitViewButtons();
    
    // Focus management
    document.getElementById('close-split-view').focus();
}

function moveAudioPlayerToSplitView() {
    const mainAudio = document.getElementById('podcast-audio');
    const placeholder = document.getElementById('audio-player-placeholder');
    const audioSection = document.querySelector('.audio-player-section');
    
    if (mainAudio && placeholder && audioSection) {
        // Move the entire audio player to split view
        const audioPlayerEnhanced = audioSection.querySelector('.audio-player-enhanced');
        if (audioPlayerEnhanced) {
            placeholder.innerHTML = '';
            placeholder.appendChild(audioPlayerEnhanced);
        }
    }
}

function returnAudioPlayerToMain() {
    const placeholder = document.getElementById('audio-player-placeholder');
    const audioSection = document.querySelector('.audio-player-section');
    
    if (placeholder && audioSection) {
        const audioPlayerEnhanced = placeholder.querySelector('.audio-player-enhanced');
        if (audioPlayerEnhanced) {
            audioSection.insertBefore(audioPlayerEnhanced, audioSection.querySelector('.episode-info'));
            placeholder.innerHTML = '<p>Split View 모드에서는 위의 오디오 플레이어가 이곳으로 이동합니다.</p>';
        }
    }
}

function closeSplitViewMode() {
    const container = document.getElementById('split-view-container');
    
    // Update state
    splitViewActive = false;
    
    // Hide container
    container.setAttribute('data-active', 'false');
    container.setAttribute('aria-hidden', 'true');
    
    // Return audio player to main section
    returnAudioPlayerToMain();
    
    // Clear all viewers
    const paperEmbed = document.getElementById('paper-embed');
    const pdfViewer = document.getElementById('pdf-viewer');
    if (paperEmbed) {
        paperEmbed.src = '';
    }
    if (pdfViewer) {
        pdfViewer.src = '';
    }
    
    // Update button state
    updateSplitViewButtons();
}

// Audio sync is no longer needed since we move the player instead of duplicating it

function updateSplitViewButtons() {
    const buttons = document.querySelectorAll('.split-view-btn');
    buttons.forEach((button, index) => {
        if (splitViewActive && index === currentPaperIndex) {
            button.textContent = '❌ Split View 닫기';
            button.setAttribute('aria-pressed', 'true');
        } else {
            button.textContent = '🔄 Split View';
            button.setAttribute('aria-pressed', 'false');
        }
    });
}

// Utility functions
function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for global access
window.openPaperInNewTab = openPaperInNewTab;
window.openPaperPDF = openPaperPDF;
window.toggleSplitView = toggleSplitView;
window.closeSplitViewMode = closeSplitViewMode;
"""
        
        js_path = self.output_dir / "assets" / "js" / "script.js"
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        self.logger.info(f"Generated JavaScript: {js_path}")

