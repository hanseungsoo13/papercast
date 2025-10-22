"""Main pipeline orchestration for PaperCast."""

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.paper import Paper
from src.models.podcast import Podcast
from src.models.processing_log import ProcessingLog
from src.services.collector import PaperCollector
from src.services.summarizer import Summarizer
from src.services.tts import TTSConverter
from src.services.uploader import GCSUploader
from src.utils.config import config
from src.utils.logger import setup_logger


class PodcastPipeline:
    """Orchestrates the podcast generation pipeline."""
    
    def __init__(self):
        """Initialize the pipeline with all services."""
        self.logger = setup_logger(
            level=config.log_level,
            log_file=str(config.logs_dir / f"pipeline_{datetime.now().strftime('%Y%m%d')}.log")
        )
        
        # Validate configuration
        if not config.validate():
            self.logger.error("Configuration validation failed")
            sys.exit(1)
        
        # Initialize services
        self.collector = PaperCollector()
        self.summarizer = Summarizer(api_key=config.gemini_api_key)
        self.tts = TTSConverter(credentials_path=config.google_credentials_path)
        self.uploader = GCSUploader(
            bucket_name=config.gcs_bucket_name,
            credentials_path=config.google_credentials_path
        )
        
        self.podcast_id = datetime.now().strftime("%Y-%m-%d")
        self.logs: list[ProcessingLog] = []
    
    def run(self) -> Optional[Podcast]:
        """Run the complete podcast generation pipeline.
        
        Returns:
            Generated Podcast object, or None if failed
        """
        self.logger.info("=" * 80)
        self.logger.info(f"Starting PaperCast pipeline for {self.podcast_id}")
        self.logger.info("=" * 80)
        
        try:
            # Step 1: Collect papers
            papers = self._collect_papers()
            if not papers:
                self.logger.error("No papers collected, aborting pipeline")
                return None
            
            # Step 2: Generate summaries
            papers_with_summaries = self._generate_summaries(papers)
            if not papers_with_summaries:
                self.logger.error("No summaries generated, aborting pipeline")
                return None
            
            # Step 3: Convert to speech
            audio_path = self._convert_to_speech(papers_with_summaries)
            if not audio_path:
                self.logger.error("Audio generation failed, aborting pipeline")
                return None
            
            # Step 4: Upload to GCS
            audio_url = self._upload_to_gcs(audio_path, papers_with_summaries)
            if not audio_url:
                self.logger.error("Upload to GCS failed, aborting pipeline")
                return None
            
            # Step 5: Create podcast metadata
            podcast = self._create_podcast(papers_with_summaries, audio_path, audio_url)
            
            # Save logs
            self._save_logs()
            
            self.logger.info("=" * 80)
            self.logger.info(f"Pipeline completed successfully! Podcast: {self.podcast_id}")
            self.logger.info(f"Audio URL: {audio_url}")
            self.logger.info("=" * 80)
            
            return podcast
            
        except Exception as e:
            self.logger.error(f"Pipeline failed with error: {e}", exc_info=True)
            return None
    
    def _collect_papers(self) -> list[Paper]:
        """Collect papers from Hugging Face."""
        log = ProcessingLog(
            podcast_id=self.podcast_id,
            step="collect",
            status="started",
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            self.logger.info("Step 1/5: Collecting papers from Hugging Face...")
            papers = self.collector.fetch_papers(count=config.papers_to_fetch)
            
            log.mark_completed()
            log.metadata = {"papers_count": len(papers)}
            self.logs.append(log)
            
            self.logger.info(f"✓ Collected {len(papers)} papers")
            return papers
            
        except Exception as e:
            log.mark_failed(str(e))
            self.logs.append(log)
            raise
    
    def _generate_summaries(self, papers: list[Paper]) -> list[Paper]:
        """Generate summaries for papers."""
        log = ProcessingLog(
            podcast_id=self.podcast_id,
            step="summarize",
            status="started",
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            self.logger.info("Step 2/5: Generating summaries with Gemini Pro...")
            
            papers_with_summaries = []
            for i, paper in enumerate(papers, 1):
                self.logger.info(f"  Summarizing paper {i}/{len(papers)}: {paper.title}")
                summary = self.summarizer.generate_summary(paper, language="ko")
                paper.summary = summary
                papers_with_summaries.append(paper)
            
            log.mark_completed()
            log.metadata = {"summaries_generated": len(papers_with_summaries)}
            self.logs.append(log)
            
            self.logger.info(f"✓ Generated {len(papers_with_summaries)} summaries")
            return papers_with_summaries
            
        except Exception as e:
            log.mark_failed(str(e))
            self.logs.append(log)
            raise
    
    def _convert_to_speech(self, papers: list[Paper]) -> Optional[str]:
        """Convert summaries to speech."""
        log = ProcessingLog(
            podcast_id=self.podcast_id,
            step="tts",
            status="started",
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            self.logger.info("Step 3/5: Converting to speech with Google TTS...")
            
            # Create script
            script = self._create_podcast_script(papers)
            self.logger.info(f"  Script length: {len(script)} characters")
            
            # Convert to audio
            audio_filename = f"episode_{self.podcast_id}.mp3"
            audio_path = str(config.data_dir / "temp" / audio_filename)
            Path(audio_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.tts.convert_to_speech(script, audio_path)
            
            # Get audio metadata
            duration = self.tts.get_audio_duration(audio_path)
            size = self.tts.get_audio_size(audio_path)
            
            log.mark_completed()
            log.metadata = {
                "script_length": len(script),
                "audio_duration": duration,
                "audio_size": size
            }
            self.logs.append(log)
            
            self.logger.info(f"✓ Generated audio: {duration}s, {size} bytes")
            return audio_path
            
        except Exception as e:
            log.mark_failed(str(e))
            self.logs.append(log)
            raise
    
    def _upload_to_gcs(self, audio_path: str, papers: list[Paper]) -> Optional[str]:
        """Upload audio and metadata to GCS."""
        log = ProcessingLog(
            podcast_id=self.podcast_id,
            step="upload",
            status="started",
            started_at=datetime.now(timezone.utc)
        )
        
        try:
            self.logger.info("Step 4/5: Uploading to Google Cloud Storage...")
            
            # Upload audio file
            destination_audio = f"{self.podcast_id}/episode.mp3"
            audio_url = self.uploader.upload_file(audio_path, destination_audio)
            self.logger.info(f"  Audio uploaded: {audio_url}")
            
            # Upload metadata
            metadata = {
                "id": self.podcast_id,
                "title": f"{config.podcast_title_prefix} - {self.podcast_id}",
                "papers": [paper.to_dict() for paper in papers],
                "audio_url": audio_url,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            destination_meta = f"{self.podcast_id}/metadata.json"
            meta_url = self.uploader.upload_json(metadata, destination_meta)
            self.logger.info(f"  Metadata uploaded: {meta_url}")
            
            log.mark_completed()
            log.metadata = {
                "audio_url": audio_url,
                "metadata_url": meta_url
            }
            self.logs.append(log)
            
            self.logger.info(f"✓ Upload completed")
            return audio_url
            
        except Exception as e:
            log.mark_failed(str(e))
            self.logs.append(log)
            raise
    
    def _create_podcast(
        self,
        papers: list[Paper],
        audio_path: str,
        audio_url: str
    ) -> Podcast:
        """Create podcast object."""
        duration = self.tts.get_audio_duration(audio_path)
        size = self.tts.get_audio_size(audio_path)
        
        podcast = Podcast(
            id=self.podcast_id,
            title=f"{config.podcast_title_prefix} - {self.podcast_id}",
            description=f"오늘의 Hugging Face 트렌딩 논문 Top {len(papers)}",
            created_at=datetime.now(timezone.utc),
            papers=papers,
            audio_file_path=audio_url,
            audio_duration=duration,
            audio_size=size,
            status="completed"
        )
        
        # Save podcast metadata locally
        podcast_file = config.podcasts_dir / f"{self.podcast_id}.json"
        with open(podcast_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(podcast.to_dict(), f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Podcast metadata saved to {podcast_file}")
        
        return podcast
    
    #[TODO]: 이 부분도 gemini가 각 논문의 스크립트를 읽고 인트로와 아웃트로 팟캐스트 멘트를 짜도록 변경
    def _create_podcast_script(self, papers: list[Paper]) -> str:
        """Create podcast script from papers."""
        intro = f"안녕하세요. {config.podcast_title_prefix}입니다. "
        intro += f"{datetime.now().strftime('%Y년 %m월 %d일')} "
        intro += f"Hugging Face 트렌딩 논문 Top {len(papers)}를 소개합니다. "
        
        script_parts = [intro]
        
        for i, paper in enumerate(papers, 1):
            part = f"\n\n{i}번째 논문입니다. "
            part += f"제목은 {paper.title}입니다. "
            part += f"저자는 {', '.join(paper.authors[:3])}입니다. "
            if len(paper.authors) > 3:
                part += f"외 {len(paper.authors) - 3}명입니다. "
            part += f"\n\n{paper.summary}"
            script_parts.append(part)
        
        outro = "\n\n오늘의 논문 소개를 마치겠습니다. 감사합니다."
        script_parts.append(outro)
        
        return "".join(script_parts)
    
    def _save_logs(self):
        """Save processing logs."""
        import json
        log_file = config.logs_dir / f"{self.podcast_id}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            logs_data = [log.to_dict() for log in self.logs]
            json.dump(logs_data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Processing logs saved to {log_file}")


def main():
    """Main entry point."""
    pipeline = PodcastPipeline()
    podcast = pipeline.run()
    
    if podcast:
        print(f"\n✓ Podcast generated successfully: {podcast.id}")
        print(f"  Audio URL: {podcast.audio_file_path}")
        print(f"  Duration: {podcast.audio_duration}s")
        print(f"  Size: {podcast.audio_size} bytes")
        sys.exit(0)
    else:
        print("\n✗ Podcast generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

