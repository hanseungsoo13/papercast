"""Text-to-Speech service using Google Cloud TTS."""

import os
from pathlib import Path
from typing import Optional

from google.cloud import texttospeech

from src.utils.logger import logger
from src.utils.retry import retry_on_failure


class TTSConverter:
    """Converts text to speech using Google Cloud TTS."""
    
    MAX_TEXT_LENGTH = 8000  # Google TTS limit
    
    def __init__(self, credentials_path: Optional[str] = None):
        """Initialize the TTS converter.
        
        Args:
            credentials_path: Path to Google Cloud credentials JSON
        """
        self.logger = logger
        
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
        self.client = texttospeech.TextToSpeechClient()
    
    @retry_on_failure(max_attempts=3, exceptions=(Exception,))
    def convert_to_speech(
        self,
        text: str,
        output_path: str,
        language_code: str = "ko-KR",
        voice_name: str = "ko-KR-Chirp3-HD-Iapetus"
    ) -> str:
        """Convert text to speech and save as MP3.
        
        Args:
            text: Text to convert
            output_path: Output file path for MP3
            language_code: Language code (default: ko-KR)
            voice_name: Voice name (default: ko-KR-Wavenet-A)
            
        Returns:
            Path to generated MP3 file
            
        Raises:
            ValueError: If text is empty or too long
            Exception: If TTS conversion fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        if len(text) > self.MAX_TEXT_LENGTH:
            raise ValueError(f"Text exceeds maximum length of {self.MAX_TEXT_LENGTH} characters")
        
        self.logger.info(f"Converting {len(text)} characters to speech...")
        
        try:
            # Check byte length (TTS API has 5000 byte limit)
            text_bytes = text.encode('utf-8')
            MAX_BYTES = 4500  # Leave some margin for safety
            
            if len(text_bytes) > MAX_BYTES:
                # Split text and process in chunks
                self.logger.warning(f"Text is {len(text_bytes)} bytes (exceeds 5000 limit), splitting into chunks...")
                return self._convert_long_text(text, output_path, language_code, voice_name, MAX_BYTES)
            
            # Set up synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Configure voice
            voice = self._get_voice_params(language_code, voice_name)
            
            # Configure audio
            audio_config = self._get_audio_config()
            
            # Perform text-to-speech
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            # Write audio to file
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as out:
                out.write(response.audio_content)
            
            file_size = output_path_obj.stat().st_size
            self.logger.info(f"Audio saved to {output_path} ({file_size} bytes)")
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"Failed to convert text to speech: {e}")
            raise
    
    def _get_voice_params(
        self,
        language_code: str = "ko-KR",
        voice_name: str = "ko-KR-Wavenet-A"
    ) -> texttospeech.VoiceSelectionParams:
        """Get voice selection parameters.
        
        Args:
            language_code: Language code
            voice_name: Voice name
            
        Returns:
            VoiceSelectionParams object
        """
        return texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
    
    def _get_audio_config(self) -> texttospeech.AudioConfig:
        """Get audio configuration.
        
        Returns:
            AudioConfig object
        """
        return texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0,
            volume_gain_db=0.0,
            sample_rate_hertz=24000
        )
    
    def _convert_long_text(
        self,
        text: str,
        output_path: str,
        language_code: str,
        voice_name: str,
        max_bytes: int = 4500
    ) -> str:
        """Convert long text by splitting into chunks and merging audio.
        
        Args:
            text: Text to convert
            output_path: Output MP3 file path
            language_code: Language code
            voice_name: Voice name
            max_bytes: Maximum bytes per chunk
            
        Returns:
            Path to generated MP3 file
        """
        # Split text into byte-safe chunks
        chunks = self._split_text_by_bytes(text, max_bytes)
        self.logger.info(f"Split text into {len(chunks)} chunks")
        
        # Convert each chunk to audio
        audio_parts = []
        temp_dir = Path(output_path).parent / "temp_chunks"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            for i, chunk in enumerate(chunks):
                chunk_path = str(temp_dir / f"chunk_{i}.mp3")
                self.logger.info(f"Converting chunk {i+1}/{len(chunks)} ({len(chunk.encode('utf-8'))} bytes)...")
                
                # Convert chunk to speech
                synthesis_input = texttospeech.SynthesisInput(text=chunk)
                voice = self._get_voice_params(language_code, voice_name)
                audio_config = self._get_audio_config()
                
                response = self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                # Save chunk
                with open(chunk_path, 'wb') as out:
                    out.write(response.audio_content)
                
                audio_parts.append(chunk_path)
            
            # Merge audio files
            self.logger.info(f"Merging {len(audio_parts)} audio chunks...")
            self._merge_audio_files(audio_parts, output_path)
            
            file_size = Path(output_path).stat().st_size
            self.logger.info(f"Audio saved to {output_path} ({file_size} bytes)")
            
            return output_path
            
        finally:
            # Clean up temporary files
            import shutil
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
    
    def _split_text_by_bytes(self, text: str, max_bytes: int) -> list[str]:
        """Split text into chunks by byte size.
        
        Args:
            text: Text to split
            max_bytes: Maximum bytes per chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        
        # Split by sentences first
        sentences = text.replace('。', '. ').split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Add period back
            sentence_with_period = sentence + ". "
            test_chunk = current_chunk + sentence_with_period
            
            # Check byte length
            if len(test_chunk.encode('utf-8')) <= max_bytes:
                current_chunk = test_chunk
            else:
                # Current chunk is full
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence_with_period
                
                # If single sentence is too long, split by characters
                if len(current_chunk.encode('utf-8')) > max_bytes:
                    char_chunks = self._split_by_characters(current_chunk, max_bytes)
                    chunks.extend(char_chunks[:-1])
                    current_chunk = char_chunks[-1] if char_chunks else ""
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_by_characters(self, text: str, max_bytes: int) -> list[str]:
        """Split text by characters when sentence is too long.
        
        Args:
            text: Text to split
            max_bytes: Maximum bytes per chunk
            
        Returns:
            List of text chunks
        """
        chunks = []
        current = ""
        
        for char in text:
            test = current + char
            if len(test.encode('utf-8')) <= max_bytes:
                current = test
            else:
                if current:
                    chunks.append(current)
                current = char
        
        if current:
            chunks.append(current)
        
        return chunks
    
    def _merge_audio_files(self, audio_files: list[str], output_path: str) -> None:
        """Merge multiple MP3 files into one.
        
        Args:
            audio_files: List of audio file paths
            output_path: Output merged file path
        """
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        # Simple concatenation of MP3 files
        with open(output_path, 'wb') as outfile:
            for audio_file in audio_files:
                with open(audio_file, 'rb') as infile:
                    outfile.write(infile.read())
    
    def _split_text(self, text: str, max_length: int = 4000) -> list[str]:
        """Split long text into chunks.
        
        Args:
            text: Text to split
            max_length: Maximum length per chunk
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 2 <= max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_audio_duration(self, audio_path: str) -> int:
        """Get duration of audio file in seconds.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds (rounded up)
        """
        try:
            from mutagen.mp3 import MP3
            audio = MP3(audio_path)
            return int(audio.info.length) + 1  # Round up
        except:
            # Fallback: estimate based on file size
            # Rough estimate: 1 second ≈ 16 KB for 128kbps MP3
            file_size = Path(audio_path).stat().st_size
            estimated_duration = file_size // (16 * 1024)
            return max(estimated_duration, 1)
    
    def get_audio_size(self, audio_path: str) -> int:
        """Get size of audio file in bytes.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            File size in bytes
        """
        return Path(audio_path).stat().st_size


