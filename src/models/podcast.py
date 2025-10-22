"""Podcast model for representing generated podcast episodes."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl

from .paper import Paper


class Podcast(BaseModel):
    """Represents a generated podcast episode.
    
    Attributes:
        id: Podcast unique identifier (YYYY-MM-DD format)
        title: Episode title
        description: Episode description
        created_at: Creation timestamp
        papers: List of papers included in this episode
        audio_file_path: MP3 file URL (GCS)
        audio_duration: Audio length in seconds
        audio_size: File size in bytes
        status: Processing status
        error_message: Error message if failed
    """
    
    id: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Podcast ID (YYYY-MM-DD)")
    title: str = Field(..., max_length=200, description="Episode title")
    description: str = Field(..., max_length=1000, description="Episode description")
    created_at: datetime = Field(..., description="Creation timestamp")
    papers: List[Paper] = Field(..., min_length=3, max_length=3, description="Included papers")
    audio_file_path: HttpUrl = Field(..., description="MP3 file URL (GCS)")
    audio_duration: int = Field(..., gt=0, description="Audio length in seconds")
    audio_size: int = Field(..., gt=0, description="File size in bytes")
    status: str = Field(
        ...,
        pattern="^(pending|processing|completed|failed)$",
        description="Processing status"
    )
    error_message: Optional[str] = Field(None, max_length=500, description="Error message")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v)
        }
    
    def to_dict(self) -> dict:
        """Convert model to dictionary.
        
        Returns:
            Dictionary representation of the podcast
        """
        return self.model_dump(mode='json')
    
    @classmethod
    def from_dict(cls, data: dict) -> "Podcast":
        """Create Podcast from dictionary.
        
        Args:
            data: Dictionary containing podcast data
            
        Returns:
            Podcast instance
        """
        return cls(**data)


