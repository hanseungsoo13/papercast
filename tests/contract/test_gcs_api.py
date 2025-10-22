"""Contract tests for Google Cloud Storage API.

These tests verify that the GCS API responses match our expectations.
"""

import pytest
from unittest.mock import Mock, patch
import json

from src.services.uploader import GCSUploader


class TestGCSAPIContract:
    """Contract tests for Google Cloud Storage API."""
    
    @pytest.fixture
    def uploader(self):
        """Create a GCSUploader instance."""
        with patch('src.services.uploader.storage.Client'):
            return GCSUploader(bucket_name="test-bucket")
    
    @pytest.mark.contract
    @pytest.mark.skipif(
        "not config.getoption('--run-contract-tests')",
        reason="Contract tests require --run-contract-tests flag"
    )
    def test_upload_from_filename_contract(self, uploader):
        """Test that upload_from_filename follows API contract.
        
        Contract: Blob.upload_from_filename(filename, content_type)
        Expected: File uploaded to specified path with correct content type
        """
        local_path = "/tmp/test.mp3"
        destination_path = "2025-01-27/episode.mp3"
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024
                
                with patch.object(uploader, 'bucket') as mock_bucket:
                    mock_blob = Mock()
                    mock_blob.public_url = f"https://storage.googleapis.com/test-bucket/{destination_path}"
                    mock_bucket.blob.return_value = mock_blob
                    
                    public_url = uploader.upload_file(local_path, destination_path)
        
        # Verify contract compliance
        mock_blob.upload_from_filename.assert_called_once_with(
            local_path,
            content_type='audio/mpeg'
        )
        mock_blob.make_public.assert_called_once()
        assert destination_path in public_url
        assert public_url.startswith("https://storage.googleapis.com/")
    
    @pytest.mark.contract
    def test_upload_from_string_contract(self, uploader):
        """Test that upload_from_string follows API contract.
        
        Contract: Blob.upload_from_string(data, content_type)
        Expected: JSON data uploaded with correct content type
        """
        data = {"key": "value", "timestamp": "2025-01-27T10:00:00Z"}
        destination_path = "2025-01-27/metadata.json"
        
        with patch.object(uploader, 'bucket') as mock_bucket:
            mock_blob = Mock()
            mock_blob.public_url = f"https://storage.googleapis.com/test-bucket/{destination_path}"
            mock_bucket.blob.return_value = mock_blob
            
            public_url = uploader.upload_json(data, destination_path)
        
        # Verify contract compliance
        assert mock_blob.upload_from_string.call_count == 1
        call_args = mock_blob.upload_from_string.call_args
        
        # Verify JSON string format
        uploaded_data = call_args[0][0]
        assert isinstance(uploaded_data, str)
        parsed_data = json.loads(uploaded_data)
        assert parsed_data == data
        
        # Verify content type
        assert call_args.kwargs['content_type'] == 'application/json'
        mock_blob.make_public.assert_called_once()
    
    @pytest.mark.contract
    def test_blob_exists_contract(self, uploader):
        """Test that blob.exists() follows API contract.
        
        Contract: Blob.exists() -> bool
        """
        file_path = "2025-01-27/episode.mp3"
        
        with patch.object(uploader, 'bucket') as mock_bucket:
            mock_blob = Mock()
            mock_blob.exists.return_value = True
            mock_bucket.blob.return_value = mock_blob
            
            exists = uploader.file_exists(file_path)
        
        assert exists is True
        mock_blob.exists.assert_called_once()
    
    @pytest.mark.contract
    def test_blob_delete_contract(self, uploader):
        """Test that blob.delete() follows API contract.
        
        Contract: Blob.delete() -> None
        """
        file_path = "2025-01-27/episode.mp3"
        
        with patch.object(uploader, 'bucket') as mock_bucket:
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob
            
            uploader.delete_file(file_path)
        
        mock_blob.delete.assert_called_once()
    
    @pytest.mark.contract
    def test_public_url_format_contract(self, uploader):
        """Test that public URLs follow expected format.
        
        Contract: https://storage.googleapis.com/{bucket}/{path}
        """
        file_path = "2025-01-27/episode.mp3"
        
        public_url = uploader.get_public_url(file_path)
        
        # Verify URL format per contract
        assert public_url == f"https://storage.googleapis.com/test-bucket/{file_path}"
        assert public_url.startswith("https://storage.googleapis.com/")
        assert uploader.bucket_name in public_url
        assert file_path in public_url
    
    @pytest.mark.contract
    def test_list_blobs_contract(self, uploader):
        """Test that list_blobs follows API contract.
        
        Contract: Bucket.list_blobs(prefix) -> Iterator[Blob]
        """
        prefix = "2025-01/"
        
        with patch.object(uploader, 'bucket') as mock_bucket:
            mock_blob1 = Mock()
            mock_blob1.name = "2025-01-27/episode.mp3"
            mock_blob2 = Mock()
            mock_blob2.name = "2025-01-27/metadata.json"
            
            mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]
            
            files = uploader.list_files(prefix=prefix)
        
        # Verify contract compliance
        mock_bucket.list_blobs.assert_called_once_with(prefix=prefix)
        assert len(files) == 2
        assert "2025-01-27/episode.mp3" in files
        assert "2025-01-27/metadata.json" in files
    
    @pytest.mark.contract
    def test_upload_error_handling_contract(self, uploader):
        """Test that API errors are handled correctly per contract."""
        local_path = "/tmp/test.mp3"
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024
                
                with patch.object(uploader, 'bucket') as mock_bucket:
                    mock_blob = Mock()
                    # Simulate 403 Forbidden error
                    mock_blob.upload_from_filename.side_effect = Exception("403 Forbidden")
                    mock_bucket.blob.return_value = mock_blob
                    
                    with pytest.raises(Exception) as exc_info:
                        uploader.upload_file(local_path, "test.mp3")
                    
                    assert "403" in str(exc_info.value) or "Forbidden" in str(exc_info.value)
    
    @pytest.mark.contract
    def test_content_type_validation_contract(self, uploader):
        """Test that content types are correctly set per contract."""
        # Test MP3 upload
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024
                
                with patch.object(uploader, 'bucket') as mock_bucket:
                    mock_blob = Mock()
                    mock_blob.public_url = "https://example.com/test.mp3"
                    mock_bucket.blob.return_value = mock_blob
                    
                    uploader.upload_file("/tmp/test.mp3", "test.mp3")
                    
                    call_args = mock_blob.upload_from_filename.call_args
                    assert call_args.kwargs['content_type'] == 'audio/mpeg'
        
        # Test JSON upload
        with patch.object(uploader, 'bucket') as mock_bucket:
            mock_blob = Mock()
            mock_blob.public_url = "https://example.com/test.json"
            mock_bucket.blob.return_value = mock_blob
            
            uploader.upload_json({"test": "data"}, "test.json")
            
            call_args = mock_blob.upload_from_string.call_args
            assert call_args.kwargs['content_type'] == 'application/json'
    
    @pytest.mark.contract
    def test_file_not_found_error_contract(self, uploader):
        """Test that FileNotFoundError is raised for non-existent files."""
        # Per contract, should raise FileNotFoundError for non-existent files
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(FileNotFoundError, match="File not found"):
                uploader.upload_file("/nonexistent/file.mp3", "test.mp3")


