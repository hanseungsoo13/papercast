"""Unit tests for ProcessingLog model."""

import pytest
from datetime import datetime, timezone
from uuid import UUID
from pydantic import ValidationError

from src.models.processing_log import ProcessingLog


class TestProcessingLog:
    """Test cases for ProcessingLog model."""
    
    @pytest.fixture
    def basic_log_data(self):
        """Basic log data for testing."""
        return {
            "podcast_id": "2025-10-24",
            "step": "collect",
            "status": "started",
            "started_at": datetime.now(timezone.utc)
        }
    
    @pytest.mark.unit
    def test_processing_log_creation(self, basic_log_data):
        """Test basic ProcessingLog creation."""
        log = ProcessingLog(**basic_log_data)
        
        assert log.podcast_id == "2025-10-24"
        assert log.step == "collect"
        assert log.status == "started"
        assert isinstance(log.id, UUID)
        assert log.started_at is not None
        assert log.completed_at is None
        assert log.duration is None
        assert log.retry_count == 0
    
    @pytest.mark.unit
    def test_all_valid_steps(self):
        """Test that all expected steps are valid."""
        valid_steps = ["collect", "summarize", "tts", "upload", "deploy", "generate_site"]
        
        for step in valid_steps:
            log = ProcessingLog(
                podcast_id="2025-10-24",
                step=step,
                status="started",
                started_at=datetime.now(timezone.utc)
            )
            assert log.step == step
    
    @pytest.mark.unit
    def test_invalid_step(self):
        """Test that invalid steps raise ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            ProcessingLog(
                podcast_id="2025-10-24",
                step="invalid_step",
                status="started",
                started_at=datetime.now(timezone.utc)
            )
        
        assert "string_pattern_mismatch" in str(exc_info.value)
    
    @pytest.mark.unit
    def test_all_valid_statuses(self):
        """Test that all expected statuses are valid."""
        valid_statuses = ["started", "completed", "failed", "retrying"]
        
        for status in valid_statuses:
            log = ProcessingLog(
                podcast_id="2025-10-24",
                step="collect",
                status=status,
                started_at=datetime.now(timezone.utc)
            )
            assert log.status == status
    
    @pytest.mark.unit
    def test_invalid_status(self):
        """Test that invalid statuses raise ValidationError."""
        with pytest.raises(ValidationError):
            ProcessingLog(
                podcast_id="2025-10-24",
                step="collect",
                status="invalid_status",
                started_at=datetime.now(timezone.utc)
            )
    
    @pytest.mark.unit
    def test_invalid_podcast_id_format(self):
        """Test that invalid podcast ID format raises ValidationError."""
        with pytest.raises(ValidationError):
            ProcessingLog(
                podcast_id="invalid-format",
                step="collect",
                status="started",
                started_at=datetime.now(timezone.utc)
            )
    
    @pytest.mark.unit
    def test_mark_completed(self, basic_log_data):
        """Test marking log as completed."""
        log = ProcessingLog(**basic_log_data)
        
        # Mark as completed
        log.mark_completed()
        
        assert log.status == "completed"
        assert log.completed_at is not None
        assert log.duration is not None
        assert log.duration >= 0
    
    @pytest.mark.unit
    def test_mark_failed(self, basic_log_data):
        """Test marking log as failed."""
        log = ProcessingLog(**basic_log_data)
        error_message = "Test error message"
        
        # Mark as failed
        log.mark_failed(error_message)
        
        assert log.status == "failed"
        assert log.completed_at is not None
        assert log.error_message == error_message
        assert log.duration is not None
        assert log.duration >= 0
    
    @pytest.mark.unit
    def test_mark_failed_with_long_message(self, basic_log_data):
        """Test marking log as failed with long error message."""
        log = ProcessingLog(**basic_log_data)
        long_error = "x" * 1500  # Longer than max length
        
        # Mark as failed
        log.mark_failed(long_error)
        
        assert log.status == "failed"
        assert len(log.error_message) == 1000  # Truncated to max length
        assert log.error_message == "x" * 1000
    
    @pytest.mark.unit
    def test_to_dict(self, basic_log_data):
        """Test converting log to dictionary."""
        log = ProcessingLog(**basic_log_data)
        log_dict = log.to_dict()
        
        assert isinstance(log_dict, dict)
        assert "id" in log_dict
        assert "podcast_id" in log_dict
        assert "step" in log_dict
        assert "status" in log_dict
        assert "started_at" in log_dict
        
        # Check that UUID and datetime are serialized as strings
        assert isinstance(log_dict["id"], str)
        assert isinstance(log_dict["started_at"], str)
    
    @pytest.mark.unit
    def test_from_dict(self, basic_log_data):
        """Test creating log from dictionary."""
        log = ProcessingLog(**basic_log_data)
        log_dict = log.to_dict()
        
        # Create new log from dict
        new_log = ProcessingLog.from_dict(log_dict)
        
        assert new_log.podcast_id == log.podcast_id
        assert new_log.step == log.step
        assert new_log.status == log.status
        assert str(new_log.id) == str(log.id)
    
    @pytest.mark.unit
    def test_generate_site_step_specifically(self):
        """Test that generate_site step works specifically."""
        log = ProcessingLog(
            podcast_id="2025-10-24",
            step="generate_site",
            status="started",
            started_at=datetime.now(timezone.utc)
        )
        
        assert log.step == "generate_site"
        assert log.status == "started"
        
        # Test completion
        log.mark_completed()
        assert log.status == "completed"
        assert log.completed_at is not None
    
    @pytest.mark.unit
    def test_retry_count_validation(self):
        """Test retry count validation."""
        # Valid retry count
        log = ProcessingLog(
            podcast_id="2025-10-24",
            step="collect",
            status="started",
            started_at=datetime.now(timezone.utc),
            retry_count=2
        )
        assert log.retry_count == 2
        
        # Invalid retry count (too high)
        with pytest.raises(ValidationError):
            ProcessingLog(
                podcast_id="2025-10-24",
                step="collect",
                status="started",
                started_at=datetime.now(timezone.utc),
                retry_count=5  # Max is 3
            )
        
        # Invalid retry count (negative)
        with pytest.raises(ValidationError):
            ProcessingLog(
                podcast_id="2025-10-24",
                step="collect",
                status="started",
                started_at=datetime.now(timezone.utc),
                retry_count=-1
            )
