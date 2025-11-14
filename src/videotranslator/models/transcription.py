"""Data models for transcription results."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class SubtitleSegment:
    """A single subtitle segment with timing information."""

    index: int
    start_time: float
    end_time: float
    text: str

    def to_srt_format(self) -> str:
        """
        Convert this segment to SRT format.

        Returns:
            SRT formatted string
        """
        start = self._format_timestamp(self.start_time)
        end = self._format_timestamp(self.end_time)
        return f"{self.index}\n{start} --> {end}\n{self.text}\n"

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """
        Format seconds to SRT timestamp format (HH:MM:SS,mmm).

        Args:
            seconds: Time in seconds

        Returns:
            Formatted timestamp string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


@dataclass
class TranscriptionResult:
    """Result of a transcription operation."""

    segments: list[SubtitleSegment]
    language: str
    source_file: Path

    def to_srt(self) -> str:
        """
        Convert all segments to SRT format.

        Returns:
            Complete SRT file content
        """
        return "\n".join(segment.to_srt_format() for segment in self.segments)

    def save_srt(self, output_path: Path) -> None:
        """
        Save the transcription as an SRT file.

        Args:
            output_path: Path to save the SRT file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.to_srt(), encoding="utf-8")
