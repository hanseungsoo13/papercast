"""Paper collector service for fetching trending papers from Hugging Face."""

from datetime import datetime
from typing import List
import requests

from src.models.paper import Paper
from src.utils.logger import logger
from src.utils.retry import retry_on_failure


class PaperCollector:
    """Collects trending papers from Hugging Face."""
    
    HUGGINGFACE_API_URL = "https://huggingface.co/api/daily_papers"
    
    def __init__(self):
        """Initialize the paper collector."""
        self.logger = logger
    
    @retry_on_failure(max_attempts=3, exceptions=(requests.RequestException,))
    def fetch_papers(self, count: int = 3) -> List[Paper]:
        """Fetch top trending papers from Hugging Face.
        
        Args:
            count: Number of papers to fetch (default: 3)
            
        Returns:
            List of Paper objects
            
        Raises:
            ValueError: If no papers found
            Exception: If API request fails
        """
        self.logger.info(f"Fetching top {count} trending papers from Hugging Face...")
        
        try:
            response = requests.get(self.HUGGINGFACE_API_URL, timeout=30)
            
            if response.status_code == 429:
                raise Exception("Rate limit exceeded. Please try again later.")
            
            response.raise_for_status()
            papers_data = response.json()
            
            if not papers_data:
                raise ValueError("No papers found in Hugging Face response")
            
            self.logger.info(f"Found {len(papers_data)} papers")
            
            # Parse and convert to Paper objects
            papers = []
            for i, paper_data in enumerate(papers_data[:count]):
                try:
                    # Debug: Log the structure of first paper
                    if i == 0:
                        self.logger.debug(f"Sample paper structure: {list(paper_data.keys())}")
                    
                    paper = self._parse_paper(paper_data)
                    papers.append(paper)
                except Exception as e:
                    self.logger.warning(f"Failed to parse paper {paper_data.get('id', 'unknown')}: {e}")
                    self.logger.debug(f"Paper data keys: {list(paper_data.keys()) if isinstance(paper_data, dict) else type(paper_data)}")
                    continue
            
            if not papers:
                raise ValueError("No papers could be parsed successfully")
            
            self.logger.info(f"Successfully fetched {len(papers)} papers")
            return papers[:count]
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch papers from Hugging Face: {e}")
            raise
    
    def _parse_paper(self, data: dict) -> Paper:
        """Parse paper data from Hugging Face API response.
        
        Args:
            data: Raw paper data from API (contains 'paper' object)
            
        Returns:
            Paper object
        """
        # Extract paper object from response
        paper_obj = data.get("paper", {})
        
        # Extract author names
        authors = [author.get("name", "Unknown") for author in paper_obj.get("authors", [])]
        if not authors:
            authors = ["Unknown"]
        
        # Parse publication date
        published_date = None
        if "publishedAt" in data:
            try:
                pub_dt = datetime.fromisoformat(data["publishedAt"].replace("Z", "+00:00"))
                published_date = pub_dt.strftime("%Y-%m-%d")
            except:
                pass
        
        # Get paper ID
        paper_id = paper_obj.get("id", "unknown")
        
        # Build paper URL
        paper_url = f"https://huggingface.co/papers/{paper_id}"
        
        return Paper(
            id=paper_id,
            title=data.get("title", paper_obj.get("title", "Untitled")),
            authors=authors,
            abstract=data.get("summary", paper_obj.get("abstract", "")),
            url=paper_url,
            published_date=published_date,
            upvotes=data.get("numComments", 0),  # Using comment count as proxy for engagement
            collected_at=datetime.utcnow()
        )

