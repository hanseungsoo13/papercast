"""Configuration management for PaperCast application."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class Config:
    """Application configuration from environment variables."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            env_file: Optional path to .env file
        """
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Google Cloud Configuration
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        self.gcs_bucket_name = os.getenv("GCS_BUCKET_NAME", "papercast-podcasts")
        
        # GitHub Configuration
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        
        # Application Configuration
        self.timezone = os.getenv("TZ", "Asia/Seoul")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.podcast_title_prefix = os.getenv("PODCAST_TITLE_PREFIX", "Daily AI Papers")
        self.papers_to_fetch = int(os.getenv("PAPERS_TO_FETCH", "3"))
        
        # Paths
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data"
        self.podcasts_dir = self.data_dir / "podcasts"
        self.logs_dir = self.data_dir / "logs"
        self.static_site_dir = self.project_root / "static-site"
        
        # Create directories if they don't exist
        self.podcasts_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.static_site_dir.mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> bool:
        """Validate required configuration.
        
        Returns:
            True if all required config is present, False otherwise
        """
        required_fields = [
            ("GEMINI_API_KEY", self.gemini_api_key),
            ("GOOGLE_APPLICATION_CREDENTIALS", self.google_credentials_path),
            ("GCS_BUCKET_NAME", self.gcs_bucket_name),
        ]
        
        missing = []
        for field_name, field_value in required_fields:
            if not field_value:
                missing.append(field_name)
        
        if missing:
            print(f"Missing required configuration: {', '.join(missing)}")
            return False
        
        # Check if credentials file exists
        if not Path(self.google_credentials_path).exists():
            print(f"Google credentials file not found: {self.google_credentials_path}")
            return False
        
        return True
    
    def __repr__(self) -> str:
        """String representation of config (without sensitive data)."""
        return (
            f"Config(gcs_bucket={self.gcs_bucket_name}, "
            f"timezone={self.timezone}, "
            f"papers_to_fetch={self.papers_to_fetch})"
        )


# Global config instance
config = Config()


