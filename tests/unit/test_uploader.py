"""Unit tests for GCS uploader service."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.services.uploader import GCSUploader


class TestGCSUploader:
    """Test cases for GCSUploader."""
    
    @pytest.fixture
    def uploader(self):
        """Create a GCSUploader instance for testing."""
        with patch('src.services.uploader.storage.Client'):
            return GCSUploader(bucket_name="test-bucket")
    
    @pytest.mark.unit
    def test_upload_file_success(self, uploader):
        """Test successful file upload."""
        local_path = "/tmp/test.mp3"
        destination_path = "2025-01-27/episode.mp3"
        
        # Mock file existence
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024
                
                with patch.object(uploader, 'bucket') as mock_bucket:
                    mock_blob = Mock()
                    mock_blob.public_url = f"https://storage.googleapis.com/test-bucket/{destination_path}"
                    mock_bucket.blob.return_value = mock_blob
                    
                    public_url = uploader.upload_file(local_path, destination_path)
                    
                    assert destination_path in public_url
                    mock_blob.upload_from_filename.assert_called_once_with(
                        local_path,
                        content_type='audio/mpeg'
                    )
                    mock_blob.make_public.assert_called_once()
    
    @pytest.mark.unit
    def test_upload_file_not_found(self, uploader):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError):
            uploader.upload_file("/nonexistent/file.mp3", "test.mp3")
    
    @pytest.mark.unit
    def test_upload_json_success(self, uploader):
        """Test successful JSON upload."""
        data = {"key": "value", "items": [1, 2, 3]}
        destination_path = "2025-01-27/metadata.json"
        
        with patch.object(uploader, 'bucket') as mock_bucket:
            mock_blob = Mock()
            mock_blob.public_url = f"https://storage.googleapis.com/test-bucket/{destination_path}"
            mock_bucket.blob.return_value = mock_blob
            
            public_url = uploader.upload_json(data, destination_path)
            
            assert destination_path in public_url
            mock_blob.upload_from_string.assert_called_once()
            mock_blob.make_public.assert_called_once()
    
    @pytest.mark.unit
    def test_upload_api_error(self, uploader):
        """Test handling of upload API errors."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024
                
                with patch.object(uploader, 'bucket') as mock_bucket:
                    mock_blob = Mock()
                    mock_blob.upload_from_filename.side_effect = Exception("Upload failed")
                    mock_bucket.blob.return_value = mock_blob
                    
                    with pytest.raises(Exception):
                        uploader.upload_file("/tmp/test.mp3", "test.mp3")
    
    @pytest.mark.unit
    def test_delete_file_success(self, uploader):
        """Test successful file deletion."""
        file_path = "2025-01-27/episode.mp3"
        
        with patch.object(uploader, 'bucket') as mock_bucket:
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob
            
            uploader.delete_file(file_path)
            
            mock_blob.delete.assert_called_once()
    
    @pytest.mark.unit
    def test_file_exists(self, uploader):
        """Test checking if file exists in GCS."""
        file_path = "2025-01-27/episode.mp3"
        
        with patch.object(uploader, 'bucket') as mock_bucket:
            mock_blob = Mock()
            mock_blob.exists.return_value = True
            mock_bucket.blob.return_value = mock_blob
            
            exists = uploader.file_exists(file_path)
            
            assert exists is True
    
    @pytest.mark.unit
    def test_get_public_url(self, uploader):
        """Test getting public URL for uploaded file."""
        file_path = "2025-01-27/episode.mp3"
        expected_url = f"https://storage.googleapis.com/test-bucket/{file_path}"
        
        url = uploader.get_public_url(file_path)
        
        assert file_path in url
        assert "storage.googleapis.com" in url

