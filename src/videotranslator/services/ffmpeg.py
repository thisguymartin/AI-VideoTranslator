"""FFmpeg service for audio/video processing with modern pathlib support."""

import subprocess
from pathlib import Path
from typing import Optional

import ffmpeg

from videotranslator.config import settings
from videotranslator.logger import logger

# ISO 639-1 (2-letter) to ISO 639-2 (3-letter) mapping for FFmpeg language tags
_ISO_639_1_TO_2: dict[str, str] = {
    "en": "eng", "es": "spa", "fr": "fra", "de": "deu", "it": "ita",
    "pt": "por", "zh": "zho", "ja": "jpn", "ko": "kor", "ar": "ara",
    "ru": "rus", "nl": "nld", "pl": "pol", "sv": "swe", "da": "dan",
    "fi": "fin", "no": "nor", "tr": "tur", "uk": "ukr", "cs": "ces",
    "hu": "hun", "ro": "ron", "bg": "bul", "hr": "hrv", "sk": "slk",
    "sl": "slv", "el": "ell", "he": "heb", "id": "ind", "ms": "msa",
    "th": "tha", "vi": "vie", "hi": "hin", "bn": "ben", "fa": "fas",
}


def _to_iso639_2(code: str) -> str:
    """Convert ISO 639-1 (2-letter) to ISO 639-2 (3-letter) language code."""
    return _ISO_639_1_TO_2.get(code.lower(), code)


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
        burn_in: bool = False,
    ) -> Path:
        """
        Add subtitles to a video file.

        Args:
            video_path: Path to the input video file
            subtitle_path: Path to the SRT subtitle file
            output_path: Optional output path for the video with subtitles
            burn_in: If True, burn subtitles into video (always visible).
                    If False, embed as separate stream (selectable in player).

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

        logger.info(
            f"Adding subtitles to {video_path.name} "
            f"(mode: {'burn-in' if burn_in else 'embedded stream'})"
        )

        try:
            if burn_in:
                # Burn subtitles into video (hardcoded, always visible)
                # This requires re-encoding the video
                # Convert Windows paths for FFmpeg's subtitles filter
                subtitle_path_str = str(subtitle_path).replace('\\', '/').replace(':', '\\:')

                cmd = [
                    "ffmpeg",
                    "-i",
                    str(video_path),
                    "-vf",
                    f"subtitles={subtitle_path_str}",
                    "-c:v",
                    settings.video_codec,  # Re-encode video
                    "-c:a",
                    "copy",  # Copy audio codec
                    "-y",  # Overwrite output file
                    str(output_path),
                ]
            else:
                # Embed subtitles as separate stream (soft subs, selectable in player)
                # Mark subtitle as default and forced for better compatibility
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
                    "-disposition:s:0",
                    "default",  # Mark subtitle stream as default
                    "-metadata:s:s:0",
                    f"language={settings.language}",
                    "-metadata:s:s:0",
                    "title=English",  # Add title for better player support
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
    def add_multi_subtitles(
        video_path: Path,
        subtitle_tracks: list[tuple[Path, str]],
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        Add multiple subtitle tracks to a video file in a single FFmpeg pass.

        Args:
            video_path: Path to the input video file
            subtitle_tracks: List of (srt_path, language_code) tuples
            output_path: Optional output path for the video with subtitles

        Returns:
            Path to the output video file

        Raises:
            FileNotFoundError: If video or any subtitle file doesn't exist
            subprocess.CalledProcessError: If FFmpeg fails
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        for srt_path, _ in subtitle_tracks:
            if not srt_path.exists():
                raise FileNotFoundError(f"Subtitle file not found: {srt_path}")

        if output_path is None:
            output_path = video_path.parent / f"{video_path.stem}_subtitled{video_path.suffix}"

        logger.info(f"Adding {len(subtitle_tracks)} subtitle track(s) to {video_path.name}")

        try:
            cmd = ["ffmpeg", "-i", str(video_path)]
            for srt_path, _ in subtitle_tracks:
                cmd += ["-i", str(srt_path)]

            cmd += ["-c:v", "copy", "-c:a", "copy"]

            for i, (_, lang_code) in enumerate(subtitle_tracks):
                iso3 = _to_iso639_2(lang_code)
                cmd += [
                    f"-c:s:{i}", settings.subtitle_codec,
                    f"-metadata:s:s:{i}", f"language={iso3}",
                ]

            cmd += ["-y", str(output_path)]

            subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"Multi-track subtitles added successfully: {output_path}")
            return output_path

        except subprocess.CalledProcessError as e:
            logger.error(f"FFmpeg error during multi-track subtitle addition: {e.stderr}")
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
