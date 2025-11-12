"""Modern CLI interface for AI VideoTranslator."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from videotranslator import __version__
from videotranslator.config import settings
from videotranslator.logger import logger
from videotranslator.ui import ProgressManager

app = typer.Typer(
    name="videotranslator",
    help="Modern CLI tool for video transcription and subtitle generation using open-source AI",
    add_completion=False,
)

console = Console()
progress_manager = ProgressManager()


def version_callback(show_version: bool):
    """Show version and exit."""
    if show_version:
        console.print(f"AI VideoTranslator v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """AI VideoTranslator - Transcribe videos with open-source AI."""
    pass


@app.command("transcribe")
def transcribe(
    video_path: Path = typer.Argument(
        ...,
        help="Path to the video file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for generated files",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="Language code (e.g., 'en', 'es', 'fr'). Auto-detect if not specified.",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Whisper model size (tiny, base, small, medium, large)",
    ),
    add_to_video: bool = typer.Option(
        False,
        "--add-to-video",
        "-a",
        help="Add subtitles to video file",
    ),
    keep_audio: bool = typer.Option(
        False,
        "--keep-audio",
        "-k",
        help="Keep extracted audio file",
    ),
):
    """
    Transcribe a video file and generate subtitles using Whisper (open-source).

    This command:
    1. Extracts audio from the video
    2. Transcribes audio using Whisper AI
    3. Generates SRT subtitle file
    4. Optionally adds subtitles to the video
    """
    try:
        # Lazy imports for heavy dependencies
        from videotranslator.services import FFmpegService, WhisperService

        # Set up output directory
        if output_dir is None:
            output_dir = video_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # Show initial status
        progress_manager.info(f"Processing video: {video_path.name}")

        # Get video info
        ffmpeg_service = FFmpegService()
        video_info = ffmpeg_service.get_video_info(video_path)
        progress_manager.status_table(
            "Video Information",
            {
                "File": video_path.name,
                "Duration": f"{video_info['duration']:.2f}s",
                "Size": f"{video_info['size'] / (1024*1024):.2f} MB",
                "Video Codec": video_info["video_codec"],
                "Audio Codec": video_info["audio_codec"],
            },
        )

        # Step 1: Extract audio
        progress_manager.info("Step 1/3: Extracting audio...")
        audio_path = output_dir / f"{video_path.stem}.wav"
        audio_path = ffmpeg_service.extract_audio(video_path, audio_path)
        progress_manager.success(f"Audio extracted: {audio_path.name}")

        # Step 2: Transcribe with Whisper
        progress_manager.info("Step 2/3: Transcribing audio with Whisper...")
        whisper_service = WhisperService(model_name=model)
        srt_path = output_dir / f"{video_path.stem}.srt"
        transcription, srt_path = whisper_service.transcribe_and_save(
            audio_path,
            output_path=srt_path,
            language=language,
        )
        progress_manager.success(
            f"Transcription complete: {len(transcription.segments)} segments, "
            f"Language: {transcription.language}"
        )

        # Step 3: Add subtitles to video if requested
        if add_to_video:
            progress_manager.info("Step 3/3: Adding subtitles to video...")
            output_video = output_dir / f"{video_path.stem}_subtitled{video_path.suffix}"
            output_video = ffmpeg_service.add_subtitles(video_path, srt_path, output_video)
            progress_manager.success(f"Video with subtitles: {output_video.name}")
        else:
            progress_manager.success("Skipping video subtitle addition")

        # Clean up audio file if not keeping it
        if not keep_audio and audio_path.exists():
            audio_path.unlink()
            logger.info(f"Removed temporary audio file: {audio_path}")

        # Final summary
        progress_manager.status_table(
            "Output Files",
            {
                "Subtitle File": str(srt_path),
                "Video with Subtitles": str(output_video) if add_to_video else "Not created",
                "Audio File": str(audio_path) if keep_audio else "Removed",
            },
        )

        progress_manager.success("All done! 🎉")

    except Exception as e:
        progress_manager.error(f"Error: {e}")
        logger.exception("Transcription failed")
        raise typer.Exit(code=1)


@app.command("extract-audio")
def extract_audio(
    video_path: Path = typer.Argument(
        ...,
        help="Path to the video file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    output_path: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output path for audio file",
        dir_okay=False,
        resolve_path=True,
    ),
    format: str = typer.Option(
        "wav",
        "--format",
        "-f",
        help="Audio format (wav, mp3, etc.)",
    ),
):
    """Extract audio from a video file."""
    try:
        from videotranslator.services import FFmpegService

        progress_manager.info(f"Extracting audio from: {video_path.name}")

        ffmpeg_service = FFmpegService()
        audio_path = ffmpeg_service.extract_audio(video_path, output_path, format)

        progress_manager.success(f"Audio extracted: {audio_path}")

    except Exception as e:
        progress_manager.error(f"Error: {e}")
        logger.exception("Audio extraction failed")
        raise typer.Exit(code=1)


@app.command("add-subtitles")
def add_subtitles(
    video_path: Path = typer.Argument(
        ...,
        help="Path to the video file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    subtitle_path: Path = typer.Argument(
        ...,
        help="Path to the SRT subtitle file",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    output_path: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output path for video with subtitles",
        dir_okay=False,
        resolve_path=True,
    ),
):
    """Add subtitles to a video file."""
    try:
        from videotranslator.services import FFmpegService

        progress_manager.info(f"Adding subtitles to: {video_path.name}")

        ffmpeg_service = FFmpegService()
        output_video = ffmpeg_service.add_subtitles(video_path, subtitle_path, output_path)

        progress_manager.success(f"Video with subtitles: {output_video}")

    except Exception as e:
        progress_manager.error(f"Error: {e}")
        logger.exception("Subtitle addition failed")
        raise typer.Exit(code=1)


@app.command("models")
def list_models():
    """Show available Whisper models and their specifications."""
    from rich.table import Table
    from videotranslator.services import WhisperService

    table = Table(title="Available Whisper Models", show_header=True, header_style="bold magenta")
    table.add_column("Model", style="cyan", width=10)
    table.add_column("Parameters", style="green", width=12)
    table.add_column("VRAM", style="yellow", width=10)
    table.add_column("Speed", style="blue", width=15)
    table.add_column("Description", style="white", width=30)

    models_info = WhisperService.get_model_info()
    for model_name, info in models_info.items():
        table.add_row(
            model_name,
            info["parameters"],
            info["vram"],
            info["speed"],
            info["description"],
        )

    console.print(table)
    console.print(
        f"\n[bold]Current model:[/bold] {settings.whisper_model}",
        style="green",
    )


@app.command("config")
def show_config():
    """Show current configuration."""
    progress_manager.status_table(
        "Current Configuration",
        {
            "Whisper Model": settings.whisper_model,
            "Language": settings.language,
            "Device": settings.device,
            "Audio Bitrate": settings.audio_bitrate,
            "Video Codec": settings.video_codec,
            "Subtitle Codec": settings.subtitle_codec,
            "Log Level": settings.log_level,
        },
    )


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
