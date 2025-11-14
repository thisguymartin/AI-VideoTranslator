"""Configuration management using pydantic-settings."""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="VIDEOTRANSLATOR_",
        case_sensitive=False,
    )

    # Transcription settings
    whisper_model: Literal["tiny", "base", "small", "medium", "large"] = Field(
        default="base",
        description="Whisper model size (tiny, base, small, medium, large)",
    )

    language: str = Field(
        default="en",
        description="Language code for transcription (e.g., 'en', 'es', 'fr')",
    )

    device: Literal["cpu", "cuda"] = Field(
        default="cpu",
        description="Device to run Whisper on (cpu or cuda)",
    )

    # Video settings
    audio_bitrate: str = Field(
        default="192k",
        description="Audio bitrate for extraction",
    )

    video_codec: str = Field(
        default="libx264",
        description="Video codec for output",
    )

    subtitle_codec: str = Field(
        default="mov_text",
        description="Subtitle codec (mov_text for MP4, srt, ass)",
    )

    # AWS Settings (optional)
    aws_bucket: str | None = Field(
        default=None,
        description="AWS S3 bucket name for transcription",
    )

    aws_region: str = Field(
        default="us-east-1",
        description="AWS region",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )


# Global settings instance
settings = Settings()
