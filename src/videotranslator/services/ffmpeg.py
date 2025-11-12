"""FFmpeg service for audio/video processing with modern pathlib support."""

import subprocess
from pathlib import Path
from typing import Optional

import ffmpeg

from videotranslator.config import settings
from videotranslator.logger import logger


class FFmpegService:
    """Service for FFmpeg operations with improved error handling and security."""

    @staticmethod
    def extract_audio(
        video_path: Path,
        output_path: Optional[Path] = None,
        audio_format: str = "wav",
    ) -> Path:
        """
        Extract audio from a video file.

        Args:
            video_path: Path to the input video file
            output_path: Optional output path for the audio file
            audio_format: Audio format (wav, mp3, etc.)

        Returns:
            Path to the extracted audio file

        Raises:
            FileNotFoundError: If video file doesn't exist
            subprocess.CalledProcessError: If FFmpeg fails
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Generate output path if not provided
        if output_path is None:
            output_path = video_path.with_suffix(f".{audio_format}")

        logger.info(f"Extracting audio from {video_path.name} to {output_path.name}")

        try:
            # Use ffmpeg-python for safe command construction
            stream = ffmpeg.input(str(video_path))
            stream = ffmpeg.output(
                stream,
                str(output_path),
                acodec="pcm_s16le" if audio_format == "wav" else "libmp3lame",
                audio_bitrate=settings.audio_bitrate,
                ar="16000",  # 16kHz for Whisper
                ac=1,  # Mono audio
            )

            # Overwrite output file if it exists
            stream = ffmpeg.overwrite_output(stream)

            # Run the FFmpeg command
            ffmpeg.run(stream, quiet=True, capture_stdout=True, capture_stderr=True)

            logger.info(f"Audio extraction complete: {output_path}")
            return output_path

        except ffmpeg.Error as e:
            error_message = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"FFmpeg error during audio extraction: {error_message}")
            raise

    @staticmethod
    def add_subtitles(
        video_path: Path,
        subtitle_path: Path,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Add subtitles to a video file.

        Args:
            video_path: Path to the input video file
            subtitle_path: Path to the SRT subtitle file
            output_path: Optional output path for the video with subtitles

        Returns:
            Path to the output video file

        Raises:
            FileNotFoundError: If video or subtitle file doesn't exist
            subprocess.CalledProcessError: If FFmpeg fails
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        if not subtitle_path.exists():
            raise FileNotFoundError(f"Subtitle file not found: {subtitle_path}")

        # Generate output path if not provided
        if output_path is None:
            output_path = video_path.parent / f"{video_path.stem}_subtitled{video_path.suffix}"

        logger.info(f"Adding subtitles to {video_path.name}")

        try:
            # Use list-based subprocess call for security (no shell injection)
            # This is safer than shell=True
            cmd = [
                "ffmpeg",
                "-i",
                str(video_path),
                "-i",
                str(subtitle_path),
                "-c:v",
                "copy",  # Copy video codec (no re-encoding)
                "-c:a",
                "copy",  # Copy audio codec
                "-c:s",
                settings.subtitle_codec,
                "-metadata:s:s:0",
                f"language={settings.language}",
                "-y",  # Overwrite output file
                str(output_path),
            ]

            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info(f"Subtitles added successfully: {output_path}")
            return output_path

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error during subtitle addition: {e.stderr}")
            raise

    @staticmethod
    def get_video_info(video_path: Path) -> dict:
        """
        Get information about a video file.

        Args:
            video_path: Path to the video file

        Returns:
            Dictionary with video information

        Raises:
            FileNotFoundError: If video file doesn't exist
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            probe = ffmpeg.probe(str(video_path))
            video_info = next(
                (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
            )
            audio_info = next(
                (stream for stream in probe["streams"] if stream["codec_type"] == "audio"), None
            )

            return {
                "duration": float(probe["format"].get("duration", 0)),
                "size": int(probe["format"].get("size", 0)),
                "bitrate": int(probe["format"].get("bit_rate", 0)),
                "video_codec": video_info.get("codec_name") if video_info else None,
                "audio_codec": audio_info.get("codec_name") if audio_info else None,
                "width": video_info.get("width") if video_info else None,
                "height": video_info.get("height") if video_info else None,
            }

        except ffmpeg.Error as e:
            logger.error(f"Error probing video file: {e}")
            raise
