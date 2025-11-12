"""Subtitle generation and manipulation service."""

from pathlib import Path
from typing import Optional

from videotranslator.logger import logger
from videotranslator.models import TranscriptionResult


class SubtitleService:
    """Service for subtitle file operations."""

    @staticmethod
    def save_srt(transcription: TranscriptionResult, output_path: Path) -> None:
        """
        Save transcription as SRT file.

        Args:
            transcription: Transcription result to save
            output_path: Path to save the SRT file
        """
        transcription.save_srt(output_path)
        logger.info(f"SRT file saved: {output_path}")

    @staticmethod
    def convert_srt_to_vtt(srt_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Convert SRT to WebVTT format.

        Args:
            srt_path: Path to SRT file
            output_path: Optional output path for VTT file

        Returns:
            Path to the VTT file
        """
        if not srt_path.exists():
            raise FileNotFoundError(f"SRT file not found: {srt_path}")

        if output_path is None:
            output_path = srt_path.with_suffix(".vtt")

        # Read SRT content
        srt_content = srt_path.read_text(encoding="utf-8")

        # Convert to VTT (simple conversion)
        vtt_content = "WEBVTT\n\n" + srt_content.replace(",", ".")

        # Save VTT file
        output_path.write_text(vtt_content, encoding="utf-8")
        logger.info(f"VTT file saved: {output_path}")

        return output_path
