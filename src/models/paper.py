"""Paper model for representing Hugging Face papers."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Paper(BaseModel):
    """Represents a paper from Hugging Face with enhanced metadata.
    
    Attributes:
        id: Paper unique identifier (Hugging Face paper ID)
        title: Paper title
        authors: List of author names
        abstract: Paper abstract
        url: Paper URL on Hugging Face
        published_date: Publication date (ISO 8601 format)
        upvotes: Number of upvotes
        summary: AI-generated summary (Gemini Pro)
        collected_at: Collection timestamp (ISO 8601)
        arxiv_id: ArXiv paper ID (if available)
        categories: Paper categories/tags
        thumbnail_url: Paper thumbnail image URL
        embed_supported: Whether iframe embedding is supported
        view_count: View count on Hugging Face
    """
    
    id: str = Field(..., min_length=1, description="Paper unique identifier")
    title: str = Field(..., max_length=500, description="Paper title")
    authors: List[str] = Field(..., min_length=1, description="List of authors")
    abstract: str = Field(..., max_length=5000, description="Paper abstract")
    url: HttpUrl = Field(..., description="Paper URL on Hugging Face")
    published_date: Optional[str] = Field(None, description="Publication date (YYYY-MM-DD)")
    upvotes: Optional[int] = Field(None, ge=0, description="Number of upvotes")
    summary: Optional[str] = Field(None, max_length=5000, description="AI-generated summary")
    short_summary: Optional[str] = Field(None, max_length=1000, description="3-line summary for episode display")
    collected_at: datetime = Field(..., description="Collection timestamp")
    arxiv_id: Optional[str] = Field(None, description="ArXiv paper ID")
    categories: Optional[List[str]] = Field(None, description="Paper categories/tags")
    thumbnail_url: Optional[str] = Field(None, description="Paper thumbnail URL")
    embed_supported: Optional[bool] = Field(None, description="iframe embedding support")
    view_count: Optional[int] = Field(None, ge=0, description="View count on Hugging Face")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }
    
    def to_dict(self) -> dict:
        """Convert model to dictionary.
        
        Returns:
            Dictionary representation of the paper
        """
        data = self.model_dump(mode='json')
        # Ensure URL is a string
        if 'url' in data:
            data['url'] = str(data['url'])
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> "Paper":
        """Create Paper from dictionary.
        
        Args:
            data: Dictionary containing paper data
            
        Returns:
            Paper instance
        """
        return cls(**data)

