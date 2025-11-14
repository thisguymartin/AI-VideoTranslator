"""Whisper service for audio transcription using OpenAI's open-source model."""

from pathlib import Path
from typing import Optional

import whisper

from videotranslator.config import settings
from videotranslator.logger import logger
from videotranslator.models import SubtitleSegment, TranscriptionResult


class WhisperService:
    """
    Service for audio transcription using OpenAI's Whisper model.

    This is a fully open-source alternative to AWS Transcribe and Google Cloud Speech-to-Text.
    Whisper runs locally without requiring cloud services or API keys.
    """

    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize the Whisper service.

        Args:
            model_name: Whisper model to use (tiny, base, small, medium, large)
            device: Device to run on (cpu or cuda)
        """
        self.model_name = model_name or settings.whisper_model
        self.device = device or settings.device
        self._model = None
        logger.info(f"Initializing Whisper service with model: {self.model_name}")

    @property
    def model(self):
        """Lazy load the Whisper model."""
        if self._model is None:
            logger.info(f"Loading Whisper model '{self.model_name}' on {self.device}...")
            self._model = whisper.load_model(self.model_name, device=self.device)
            logger.info("Whisper model loaded successfully")
        return self._model

    def transcribe(
        self,
        audio_path: Path,
        language: Optional[str] = None,
        task: str = "transcribe",
    ) -> TranscriptionResult:
        """
        Transcribe an audio file using Whisper.

        Args:
            audio_path: Path to the audio file
            language: Language code (e.g., 'en', 'es', 'fr'). If None, auto-detect.
            task: Task type ('transcribe' or 'translate' to English)

        Returns:
            TranscriptionResult with segments and metadata

        Raises:
            FileNotFoundError: If audio file doesn't exist
        """
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        logger.info(f"Transcribing {audio_path.name} using Whisper...")

        # Transcribe with Whisper
        result = self.model.transcribe(
            str(audio_path),
            language=language or settings.language,
            task=task,
            verbose=False,
            word_timestamps=True,  # Enable word-level timestamps
        )

        logger.info(f"Transcription complete. Detected language: {result['language']}")

        # Convert Whisper segments to our SubtitleSegment format
        segments = []
        for idx, segment in enumerate(result["segments"], start=1):
            subtitle_segment = SubtitleSegment(
                index=idx,
                start_time=segment["start"],
                end_time=segment["end"],
                text=segment["text"].strip(),
            )
            segments.append(subtitle_segment)

        return TranscriptionResult(
            segments=segments,
            language=result["language"],
            source_file=audio_path,
        )

    def transcribe_and_save(
        self,
        audio_path: Path,
        output_path: Optional[Path] = None,
        language: Optional[str] = None,
    ) -> tuple[TranscriptionResult, Path]:
        """
        Transcribe an audio file and save as SRT.

        Args:
            audio_path: Path to the audio file
            output_path: Optional output path for SRT file
            language: Optional language code

        Returns:
            Tuple of (TranscriptionResult, Path to SRT file)
        """
        # Transcribe the audio
        result = self.transcribe(audio_path, language=language)

        # Generate output path if not provided
        if output_path is None:
            output_path = audio_path.with_suffix(".srt")

        # Save the SRT file
        result.save_srt(output_path)
        logger.info(f"Subtitles saved to: {output_path}")

        return result, output_path

    @staticmethod
    def get_available_models() -> list[str]:
        """
        Get list of available Whisper models.

        Returns:
            List of model names
        """
        return ["tiny", "base", "small", "medium", "large"]

    @staticmethod
    def get_model_info() -> dict[str, dict]:
        """
        Get information about Whisper models.

        Returns:
            Dictionary with model information
        """
        return {
            "tiny": {
                "parameters": "39M",
                "vram": "~1GB",
                "speed": "~32x realtime",
                "description": "Fastest, lowest accuracy",
            },
            "base": {
                "parameters": "74M",
                "vram": "~1GB",
                "speed": "~16x realtime",
                "description": "Good balance for most use cases",
            },
            "small": {
                "parameters": "244M",
                "vram": "~2GB",
                "speed": "~6x realtime",
                "description": "Better accuracy, still fast",
            },
            "medium": {
                "parameters": "769M",
                "vram": "~5GB",
                "speed": "~2x realtime",
                "description": "High accuracy",
            },
            "large": {
                "parameters": "1550M",
                "vram": "~10GB",
                "speed": "~1x realtime",
                "description": "Highest accuracy, slowest",
            },
        }
