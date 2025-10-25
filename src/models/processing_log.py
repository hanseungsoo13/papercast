"""ProcessingLog model for tracking pipeline execution."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ProcessingLog(BaseModel):
    """Represents a processing log entry for pipeline steps.
    
    Attributes:
        id: Log unique identifier (UUID)
        podcast_id: Related podcast ID
        step: Processing step name
        status: Step status
        started_at: Step start timestamp
        completed_at: Step completion timestamp
        duration: Execution time in seconds
        error_message: Error message if failed
        retry_count: Number of retries
        metadata: Additional metadata (JSON)
    """
    
    id: UUID = Field(default_factory=uuid4, description="Log unique identifier (UUID)")
    podcast_id: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Related podcast ID (YYYY-MM-DD)"
    )
    step: str = Field(
        ...,
        pattern="^(collect|summarize|tts|upload|deploy|generate_site)$",
        description="Processing step"
    )
    status: str = Field(
        ...,
        pattern="^(started|completed|failed|retrying)$",
        description="Step status"
    )
    started_at: datetime = Field(..., description="Step start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Step completion timestamp")
    duration: Optional[int] = Field(None, ge=0, description="Execution time in seconds")
    error_message: Optional[str] = Field(None, max_length=1000, description="Error message")
    retry_count: int = Field(0, ge=0, le=3, description="Number of retries")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    
    def to_dict(self) -> dict:
        """Convert model to dictionary.
        
        Returns:
            Dictionary representation of the log
        """
        return self.model_dump(mode='json')
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProcessingLog":
        """Create ProcessingLog from dictionary.
        
        Args:
            data: Dictionary containing log data
            
        Returns:
            ProcessingLog instance
        """
        return cls(**data)
    
    def mark_completed(self) -> None:
        """Mark the log entry as completed and calculate duration."""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)
        if self.completed_at and self.started_at:
            # Ensure both datetimes are timezone-aware
            started = self.started_at if self.started_at.tzinfo else self.started_at.replace(tzinfo=timezone.utc)
            completed = self.completed_at if self.completed_at.tzinfo else self.completed_at.replace(tzinfo=timezone.utc)
            self.duration = int((completed - started).total_seconds())
    
    def mark_failed(self, error: str) -> None:
        """Mark the log entry as failed with error message.
        
        Args:
            error: Error message
        """
        self.status = "failed"
        self.completed_at = datetime.now(timezone.utc)
        self.error_message = error[:1000]  # Truncate to max length
        if self.completed_at and self.started_at:
            # Ensure both datetimes are timezone-aware
            started = self.started_at if self.started_at.tzinfo else self.started_at.replace(tzinfo=timezone.utc)
            completed = self.completed_at if self.completed_at.tzinfo else self.completed_at.replace(tzinfo=timezone.utc)
            self.duration = int((completed - started).total_seconds())

