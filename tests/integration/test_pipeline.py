"""Integration tests for the full podcast generation pipeline.

These tests verify that all components work together correctly.
"""

import pytest
import os
import json
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
from pathlib import Path

from src.models.paper import Paper
from src.models.podcast import Podcast
from src.services.collector import PaperCollector
from src.services.summarizer import Summarizer
from src.services.tts import TTSConverter
from src.services.uploader import GCSUploader


class TestPipelineIntegration:
    """Integration tests for the full pipeline."""
    
    @pytest.fixture
    def mock_papers(self):
        """Create mock papers for testing."""
        return [
            Paper(
                id="2401.12345",
                title="Efficient Transformers with Dynamic Attention",
                authors=["John Doe", "Jane Smith"],
                abstract="We propose a novel approach to improve transformer efficiency...",
                url="https://huggingface.co/papers/2401.12345",
                upvotes=142,
                collected_at=datetime.utcnow()
            ),
            Paper(
                id="2401.12346",
                title="Neural Architecture Search at Scale",
                authors=["Alice Johnson"],
                abstract="This paper presents a scalable approach to neural architecture search...",
                url="https://huggingface.co/papers/2401.12346",
                upvotes=98,
                collected_at=datetime.utcnow()
            ),
            Paper(
                id="2401.12347",
                title="Self-Supervised Learning for Vision",
                authors=["Bob Williams", "Carol Davis"],
                abstract="We introduce a new self-supervised learning method for computer vision...",
                url="https://huggingface.co/papers/2401.12347",
                upvotes=156,
                collected_at=datetime.utcnow()
            )
        ]
    
    @pytest.mark.integration
    def test_collect_to_summarize_flow(self, mock_papers):
        """Test the flow from collection to summarization."""
        # Setup collector
        collector = PaperCollector()
        
        # Mock collector response
        with patch.object(collector, 'fetch_papers', return_value=mock_papers):
            papers = collector.fetch_papers(count=3)
        
        # Verify collection
        assert len(papers) == 3
        assert all(isinstance(p, Paper) for p in papers)
        
        # Setup summarizer
        with patch('src.services.summarizer.genai.configure'):
            with patch('src.services.summarizer.genai.GenerativeModel'):
                summarizer = Summarizer(api_key="test_key")
        
        # Mock summarizer responses
        summaries = [
            "이 논문은 동적 어텐션 메커니즘을 사용하여 트랜스포머의 효율성을 개선하는 새로운 방법을 제안합니다. 실험 결과 기존 방법보다 30% 빠른 처리 속도를 보였습니다.",
            "이 연구는 대규모 신경망 아키텍처 탐색을 위한 확장 가능한 접근 방식을 제시합니다. 제안된 방법은 기존 방법보다 10배 빠르게 최적 아키텍처를 찾습니다.",
            "컴퓨터 비전을 위한 새로운 자기지도 학습 방법을 소개합니다. 이 방법은 라벨 없는 데이터만으로도 높은 정확도를 달성합니다."
        ]
        
        # Generate summaries
        for i, paper in enumerate(papers):
            with patch.object(summarizer, 'model') as mock_model:
                mock_response = Mock()
                mock_response.text = summaries[i]
                mock_model.generate_content.return_value = mock_response
                
                summary = summarizer.generate_summary(paper)
                paper.summary = summary
        
        # Verify summarization
        assert all(p.summary is not None for p in papers)
        assert all(len(p.summary) >= 50 for p in papers)
    
    @pytest.mark.integration
    def test_summarize_to_tts_flow(self, mock_papers):
        """Test the flow from summarization to TTS."""
        # Add summaries to papers
        for paper in mock_papers:
            paper.summary = "이것은 테스트 요약입니다. " * 10
        
        # Create combined script
        script = "\n\n".join([
            f"논문 {i+1}: {paper.title}. {paper.summary}"
            for i, paper in enumerate(mock_papers)
        ])
        
        # Setup TTS converter
        with patch('src.services.tts.texttospeech.TextToSpeechClient'):
            tts_converter = TTSConverter()
        
        # Mock TTS response
        output_path = "/tmp/test_podcast.mp3"
        mock_audio_data = b'fake_mp3_audio_data' * 1000
        
        with patch.object(tts_converter, 'client') as mock_client:
            mock_response = Mock()
            mock_response.audio_content = mock_audio_data
            mock_client.synthesize_speech.return_value = mock_response
            
            with patch('builtins.open', mock_open()):
                with patch('pathlib.Path.mkdir'):
                    with patch('pathlib.Path.stat') as mock_stat:
                        mock_stat.return_value.st_size = len(mock_audio_data)
                        
                        result_path = tts_converter.convert_to_speech(script, output_path)
        
        # Verify TTS conversion
        assert result_path == output_path
        mock_client.synthesize_speech.assert_called_once()
    
    @pytest.mark.integration
    def test_tts_to_upload_flow(self):
        """Test the flow from TTS to GCS upload."""
        # Setup uploader
        with patch('src.services.uploader.storage.Client'):
            uploader = GCSUploader(bucket_name="test-bucket")
        
        # Mock file upload
        local_path = "/tmp/test_podcast.mp3"
        destination_path = "2025-01-27/episode.mp3"
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 7680000  # 7.68 MB
                
                with patch.object(uploader, 'bucket') as mock_bucket:
                    mock_blob = Mock()
                    expected_url = f"https://storage.googleapis.com/test-bucket/{destination_path}"
                    mock_blob.public_url = expected_url
                    mock_bucket.blob.return_value = mock_blob
                    
                    public_url = uploader.upload_file(local_path, destination_path)
        
        # Verify upload
        assert destination_path in public_url
        assert public_url.startswith("https://storage.googleapis.com/")
        mock_blob.make_public.assert_called_once()
    
    @pytest.mark.integration
    def test_full_pipeline_end_to_end(self, mock_papers):
        """Test the complete pipeline from collection to upload."""
        # Step 1: Collection
        collector = PaperCollector()
        with patch.object(collector, 'fetch_papers', return_value=mock_papers):
            papers = collector.fetch_papers(count=3)
        
        assert len(papers) == 3
        
        # Step 2: Summarization
        with patch('src.services.summarizer.genai.configure'):
            with patch('src.services.summarizer.genai.GenerativeModel'):
                summarizer = Summarizer(api_key="test_key")
        
        for paper in papers:
            with patch.object(summarizer, 'model') as mock_model:
                mock_response = Mock()
                mock_response.text = f"이것은 {paper.title}에 대한 요약입니다. " * 5
                mock_model.generate_content.return_value = mock_response
                
                paper.summary = summarizer.generate_summary(paper)
        
        assert all(p.summary for p in papers)
        
        # Step 3: Create script
        script = "오늘의 AI 논문을 소개합니다.\n\n"
        for i, paper in enumerate(papers):
            script += f"논문 {i+1}: {paper.title}. {paper.summary}\n\n"
        
        # Step 4: TTS Conversion
        with patch('src.services.tts.texttospeech.TextToSpeechClient'):
            tts_converter = TTSConverter()
        
        audio_path = "/tmp/podcast_2025-01-27.mp3"
        
        with patch.object(tts_converter, 'client') as mock_client:
            mock_response = Mock()
            mock_response.audio_content = b'audio_data' * 10000
            mock_client.synthesize_speech.return_value = mock_response
            
            with patch('builtins.open', mock_open()):
                with patch('pathlib.Path.mkdir'):
                    with patch('pathlib.Path.stat') as mock_stat:
                        mock_stat.return_value.st_size = 100000
                        
                        result_path = tts_converter.convert_to_speech(script, audio_path)
        
        assert result_path == audio_path
        
        # Step 5: Upload to GCS
        with patch('src.services.uploader.storage.Client'):
            uploader = GCSUploader(bucket_name="papercast-podcasts")
        
        destination = "2025-01-27/episode.mp3"
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 100000
                
                with patch.object(uploader, 'bucket') as mock_bucket:
                    mock_blob = Mock()
                    mock_blob.public_url = f"https://storage.googleapis.com/papercast-podcasts/{destination}"
                    mock_bucket.blob.return_value = mock_blob
                    
                    audio_url = uploader.upload_file(audio_path, destination)
        
        # Step 6: Create Podcast model
        podcast = Podcast(
            id="2025-01-27",
            title="Daily AI Papers - January 27, 2025",
            description="오늘의 Hugging Face 트렌딩 논문 Top 3",
            created_at=datetime.utcnow(),
            papers=papers,
            audio_file_path=audio_url,
            audio_duration=480,
            audio_size=100000,
            status="completed"
        )
        
        # Verify final podcast
        assert podcast.id == "2025-01-27"
        assert len(podcast.papers) == 3
        assert podcast.status == "completed"
        assert "storage.googleapis.com" in str(podcast.audio_file_path)
        assert podcast.audio_duration > 0
        assert podcast.audio_size > 0
    
    @pytest.mark.integration
    def test_pipeline_error_handling(self, mock_papers):
        """Test error handling throughout the pipeline."""
        # Test collection failure
        collector = PaperCollector()
        with patch.object(collector, 'fetch_papers', side_effect=Exception("API Error")):
            with pytest.raises(Exception, match="API Error"):
                collector.fetch_papers()
        
        # Test summarization failure
        with patch('src.services.summarizer.genai.configure'):
            with patch('src.services.summarizer.genai.GenerativeModel'):
                summarizer = Summarizer(api_key="test_key")
        
        with patch.object(summarizer, 'model') as mock_model:
            mock_model.generate_content.side_effect = Exception("Quota exceeded")
            
            with pytest.raises(Exception, match="Quota exceeded"):
                summarizer.generate_summary(mock_papers[0])
        
        # Test TTS failure
        with patch('src.services.tts.texttospeech.TextToSpeechClient'):
            tts_converter = TTSConverter()
        
        with patch.object(tts_converter, 'client') as mock_client:
            mock_client.synthesize_speech.side_effect = Exception("TTS Error")
            
            with pytest.raises(Exception, match="TTS Error"):
                tts_converter.convert_to_speech("test", "/tmp/test.mp3")
        
        # Test upload failure
        with patch('src.services.uploader.storage.Client'):
            uploader = GCSUploader(bucket_name="test-bucket")
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024
                
                with patch.object(uploader, 'bucket') as mock_bucket:
                    mock_blob = Mock()
                    mock_blob.upload_from_filename.side_effect = Exception("Upload failed")
                    mock_bucket.blob.return_value = mock_blob
                    
                    with pytest.raises(Exception, match="Upload failed"):
                        uploader.upload_file("/tmp/test.mp3", "test.mp3")
    
    @pytest.mark.integration
    def test_metadata_persistence(self, mock_papers):
        """Test that podcast metadata is correctly persisted."""
        # Create podcast
        podcast = Podcast(
            id="2025-01-27",
            title="Test Podcast",
            description="Test Description",
            created_at=datetime.utcnow(),
            papers=mock_papers,
            audio_file_path="https://storage.googleapis.com/test-bucket/2025-01-27/episode.mp3",
            audio_duration=480,
            audio_size=7680000,
            status="completed"
        )
        
        # Convert to JSON
        podcast_dict = podcast.model_dump(mode='json')
        podcast_json = json.dumps(podcast_dict, ensure_ascii=False, indent=2)
        
        # Verify JSON structure
        parsed = json.loads(podcast_json)
        assert parsed['id'] == "2025-01-27"
        assert len(parsed['papers']) == 3
        assert parsed['status'] == "completed"
        
        # Simulate upload
        with patch('src.services.uploader.storage.Client'):
            uploader = GCSUploader(bucket_name="test-bucket")
        
        with patch.object(uploader, 'bucket') as mock_bucket:
            mock_blob = Mock()
            mock_blob.public_url = "https://storage.googleapis.com/test-bucket/2025-01-27/metadata.json"
            mock_bucket.blob.return_value = mock_blob
            
            metadata_url = uploader.upload_json(podcast_dict, "2025-01-27/metadata.json")
        
        # Verify metadata upload
        assert "metadata.json" in metadata_url
        mock_blob.upload_from_string.assert_called_once()

