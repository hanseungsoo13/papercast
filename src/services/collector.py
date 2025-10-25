"""Paper collector service for fetching trending papers from Hugging Face."""

from datetime import datetime, timedelta
from typing import List
import requests
from bs4 import BeautifulSoup

from src.models.paper import Paper
from src.utils.logger import logger
from src.utils.retry import retry_on_failure


class PaperCollector:
    """Collects trending papers from Hugging Face."""
    
    HUGGINGFACE_PAPERS_URL = "https://huggingface.co/papers"
    
    def __init__(self):
        """Initialize the paper collector."""
        self.logger = logger
    
    @retry_on_failure(max_attempts=3, exceptions=(requests.RequestException,))
    def fetch_papers(self, count: int = 3) -> List[Paper]:
        """Fetch top trending papers from Hugging Face's daily papers page.
        
        Args:
            count: Number of papers to fetch (default: 3)
            
        Returns:
            List of Paper objects
            
        Raises:
            ValueError: If no papers found
            Exception: If request fails
        """
        # 어제 날짜 계산
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
        
        # Hugging Face 날짜별 페이퍼 페이지 URL 생성
        url = f"{self.HUGGINGFACE_PAPERS_URL}?date={date_str}"
        
        self.logger.info(f"Fetching top {count} papers from {date_str} from Hugging Face...")
        
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            
            response.raise_for_status()
            
            # HTML 파싱
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 논문 정보 추출
            papers = []
            paper_articles = soup.find_all('article', limit=count)
            
            if not paper_articles:
                raise ValueError(f"No papers found for date {date_str}")
            
            self.logger.info(f"Found {len(paper_articles)} papers for {date_str}")
            
            for i, article in enumerate(paper_articles):
                try:
                    paper = self._parse_paper_from_html(article, date_str)
                    papers.append(paper)
                    self.logger.debug(f"Successfully parsed paper {i+1}: {paper.title[:50]}...")
                except Exception as e:
                    self.logger.warning(f"Failed to parse paper {i+1}: {e}")
                    continue
            
            if not papers:
                raise ValueError("No papers could be parsed successfully")
            
            self.logger.info(f"Successfully fetched {len(papers)} papers from {date_str}")
            return papers[:count]
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch papers from Hugging Face: {e}")
            raise
    
    def _parse_paper_from_html(self, article, date_str: str) -> Paper:
        """Parse paper data from HTML article element with enhanced metadata.
        
        Args:
            article: BeautifulSoup article element
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            Paper object with enhanced metadata
        """
        # 제목 추출
        title_elem = article.find('h3')
        title = title_elem.get_text(strip=True) if title_elem else "Untitled"
        
        # 논문 URL 추출
        link_elem = article.find('a', href=True)
        paper_url = ""
        paper_id = "unknown"
        
        if link_elem and 'href' in link_elem.attrs:
            href = link_elem['href']
            # 상대 경로를 절대 경로로 변환
            if href.startswith('/papers/'):
                paper_url = f"https://huggingface.co{href}"
                paper_id = href.split('/papers/')[-1]
            elif href.startswith('http'):
                paper_url = href
                if '/papers/' in href:
                    paper_id = href.split('/papers/')[-1]
        
        # 저자 추출
        authors = []
        authors_div = article.find('div', class_=lambda x: x and 'author' in x.lower()) if article else None
        if authors_div:
            author_links = authors_div.find_all('a')
            authors = [a.get_text(strip=True) for a in author_links if a.get_text(strip=True)]
        
        if not authors:
            authors = ["Unknown"]
        
        # 초록 추출
        abstract = ""
        abstract_elem = article.find('p', class_=lambda x: x and ('abstract' in x.lower() or 'description' in x.lower()))
        if abstract_elem:
            abstract = abstract_elem.get_text(strip=True)
        else:
            # 일반 p 태그에서 찾기
            p_elems = article.find_all('p')
            if p_elems:
                abstract = p_elems[0].get_text(strip=True)
        
        # 좋아요/댓글 수 추출
        upvotes = 0
        upvote_elem = article.find('span', class_=lambda x: x and ('upvote' in x.lower() or 'like' in x.lower()))
        if upvote_elem:
            try:
                upvote_text = upvote_elem.get_text(strip=True)
                upvotes = int(''.join(filter(str.isdigit, upvote_text)))
            except:
                pass
        
        # ArXiv ID 추출
        arxiv_id = None
        if paper_id and paper_id != "unknown":
            arxiv_id = paper_id  # Hugging Face paper ID often matches ArXiv ID
        
        # 카테고리/태그 추출
        categories = []
        tag_elements = article.find_all(['span', 'a'], class_=lambda x: x and ('tag' in x.lower() or 'category' in x.lower()))
        for tag in tag_elements:
            tag_text = tag.get_text(strip=True)
            if tag_text and len(tag_text) < 50:
                categories.append(tag_text)
        
        # 썸네일 URL 추출
        thumbnail_url = None
        img_elem = article.find('img')
        if img_elem and 'src' in img_elem.attrs:
            src = img_elem['src']
            if src.startswith('http'):
                thumbnail_url = src
            elif src.startswith('/'):
                thumbnail_url = f"https://huggingface.co{src}"
        
        # iframe 임베딩 지원 확인
        embed_supported = self._check_embed_support(paper_url) if paper_url else False
        
        # 조회수 추출 (있는 경우)
        view_count = None
        view_elem = article.find('span', class_=lambda x: x and ('view' in x.lower() or 'read' in x.lower()))
        if view_elem:
            try:
                view_text = view_elem.get_text(strip=True)
                view_count = int(''.join(filter(str.isdigit, view_text)))
            except:
                pass
        
        return Paper(
            id=paper_id,
            title=title,
            authors=authors,
            abstract=abstract,
            url=paper_url,
            published_date=date_str,
            upvotes=upvotes,
            collected_at=datetime.utcnow(),
            arxiv_id=arxiv_id,
            categories=categories if categories else None,
            thumbnail_url=thumbnail_url,
            embed_supported=embed_supported,
            view_count=view_count
        )
    
    def _check_embed_support(self, url: str) -> bool:
        """Check if a paper URL supports iframe embedding.
        
        Args:
            url: Paper URL to check
            
        Returns:
            True if embedding is supported, False otherwise
        """
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            x_frame_options = response.headers.get('X-Frame-Options', '').lower()
            
            # Check for embedding restrictions
            if x_frame_options in ['deny', 'sameorigin']:
                return False
            
            # Check Content-Security-Policy
            csp = response.headers.get('Content-Security-Policy', '')
            if 'frame-ancestors' in csp.lower() and "'none'" in csp.lower():
                return False
            
            return True
        except Exception as e:
            self.logger.debug(f"Could not check embed support for {url}: {e}")
            return False

