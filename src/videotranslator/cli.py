"""Modern CLI interface for AI VideoTranslator."""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

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


def _translate_srt(
    srt_path: Path,
    output_path: Path,
    source: str,
    target: str,
    host: str,
    api_key: Optional[str] = None,
) -> Path:
    """Translate an SRT file and write the result to output_path."""
    from videotranslator.services.translator import LibreTranslateClient, TranslationError

    client = LibreTranslateClient(host=host, api_key=api_key)
    content = srt_path.read_text(encoding="utf-8")
    blocks = content.strip().split("\n\n")
    translated_blocks = []

    for block in blocks:
        lines = block.split("\n")
        if len(lines) >= 3:
            number = lines[0]
            timestamp = lines[1]
            text = "\n".join(lines[2:])
            try:
                translated_text = client.translate_sync(text, source, target)
                translated_blocks.append(f"{number}\n{timestamp}\n{translated_text}")
            except TranslationError:
                translated_blocks.append(block)
        else:
            translated_blocks.append(block)

    output_path.write_text("\n\n".join(translated_blocks), encoding="utf-8")
    return output_path


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
    burn_in_subtitles: bool = typer.Option(
        False,
        "--burn-in",
        "-b",
        help="Burn subtitles into video (always visible, requires re-encoding)",
    ),
    keep_audio: bool = typer.Option(
        False,
        "--keep-audio",
        "-k",
        help="Keep extracted audio file",
    ),
    translate_to: Optional[List[str]] = typer.Option(
        None,
        "--translate-to",
        help="Translate subtitles to language code(s). Can be specified multiple times.",
    ),
    translate_host: str = typer.Option(
        "http://localhost:5000",
        "--translate-host",
        help="LibreTranslate server URL",
    ),
    translate_api_key: Optional[str] = typer.Option(
        None,
        "--translate-api-key",
        help="LibreTranslate API key if required",
    ),
    multi_track: bool = typer.Option(
        False,
        "--multi-track",
        help="Embed all subtitle languages as separate selectable tracks (requires --add-to-video)",
    ),
):
    """
    Transcribe a video file and generate subtitles using Whisper (open-source).

    This command:
    1. Extracts audio from the video
    2. Transcribes audio using Whisper AI
    3. Generates SRT subtitle file
    4. Optionally translates to one or more languages (--translate-to)
    5. Optionally adds subtitles to the video (--add-to-video)
    """
    try:
        from videotranslator.services import FFmpegService, WhisperService

        if output_dir is None:
            output_dir = video_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        progress_manager.info(f"Processing video: {video_path.name}")

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

        # Step 2.5: Translate to target languages
        translated_srts: list[tuple[Path, str]] = []
        if translate_to:
            source_lang = language or transcription.language or "auto"
            progress_manager.info(f"Translating subtitles to: {', '.join(translate_to)}")
            for target_lang in translate_to:
                translated_path = output_dir / f"{video_path.stem}_{target_lang}.srt"
                _translate_srt(
                    srt_path, translated_path, source_lang, target_lang,
                    translate_host, translate_api_key,
                )
                translated_srts.append((translated_path, target_lang))
                progress_manager.success(f"Translated to {target_lang}: {translated_path.name}")

        # Step 3: Add subtitles to video if requested
        output_video: Optional[Path] = None
        if add_to_video:
            progress_manager.info("Step 3/3: Adding subtitles to video...")
            output_video = output_dir / f"{video_path.stem}_subtitled{video_path.suffix}"

            if translated_srts and (multi_track or len(translated_srts) > 1):
                # Multi-track: embed source + all translations as separate tracks
                tracks = [(srt_path, transcription.language or "en")] + translated_srts
                output_video = ffmpeg_service.add_multi_subtitles(video_path, tracks, output_video)
            elif translated_srts:
                # Single translation, no multi-track: embed the translated SRT
                output_video = ffmpeg_service.add_subtitles(
                    video_path, translated_srts[0][0], output_video,
                    burn_in=burn_in_subtitles,
                )
            else:
                # No translation: embed source SRT
                output_video = ffmpeg_service.add_subtitles(
                    video_path, srt_path, output_video, burn_in=burn_in_subtitles
                )
            progress_manager.success(f"Video with subtitles: {output_video.name}")
        else:
            progress_manager.success("Skipping video subtitle addition")

        # Clean up audio file if not keeping it
        if not keep_audio and audio_path.exists():
            audio_path.unlink()
            logger.info(f"Removed temporary audio file: {audio_path}")

        # Final summary
        summary: dict[str, str] = {"Subtitle File": str(srt_path)}
        for path, lang in translated_srts:
            summary[f"Subtitle ({lang})"] = str(path)
        summary["Video with Subtitles"] = str(output_video) if output_video else "Not created"
        summary["Audio File"] = str(audio_path) if keep_audio else "Removed"
        progress_manager.status_table("Output Files", summary)

        progress_manager.success("All done!")

    except Exception as e:
        progress_manager.error(f"Error: {e}")
        logger.exception("Transcription failed")
        raise typer.Exit(code=1)


@app.command("translate")
def translate_subtitles(
    srt_path: Path = typer.Argument(
        ...,
        help="Path to the SRT subtitle file to translate",
        exists=True,
        file_okay=True,
        dir_okay=False,
        resolve_path=True,
    ),
    target: List[str] = typer.Option(
        ...,
        "--target",
        "-t",
        help="Target language code(s). Can be specified multiple times.",
    ),
    source: str = typer.Option(
        "auto",
        "--source",
        "-s",
        help="Source language code (default: auto-detect)",
    ),
    output_dir: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory for translated SRT files (default: same as input)",
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    host: str = typer.Option(
        "http://localhost:5000",
        "--host",
        help="LibreTranslate server URL",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        help="LibreTranslate API key if required",
    ),
):
    """
    Translate an SRT subtitle file to one or more languages.

    Examples:

        videotranslator translate subtitles.srt --target es

        videotranslator translate subtitles.srt --target es --target fr --target de

        videotranslator translate subtitles.srt --source en --target fr -o output/
    """
    try:
        from videotranslator.services.translator import LibreTranslateClient

        out_dir = output_dir or srt_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        client = LibreTranslateClient(host=host, api_key=api_key)
        if not client.health_check():
            progress_manager.error(
                f"LibreTranslate server not reachable at {host}. "
                "Start it with: docker-compose up -d"
            )
            raise typer.Exit(code=1)

        progress_manager.info(f"Translating: {srt_path.name} -> {', '.join(target)}")

        output_files: list[tuple[str, Path]] = []
        for target_lang in target:
            output_path = out_dir / f"{srt_path.stem}_{target_lang}.srt"
            progress_manager.info(f"Translating to {target_lang}...")
            _translate_srt(srt_path, output_path, source, target_lang, host, api_key)
            output_files.append((target_lang, output_path))
            progress_manager.success(f"Saved: {output_path.name}")

        progress_manager.status_table(
            "Translation Results",
            {lang: str(path) for lang, path in output_files},
        )
        progress_manager.success("Translation complete!")

    except typer.Exit:
        raise
    except Exception as e:
        progress_manager.error(f"Error: {e}")
        logger.exception("Translation failed")
        raise typer.Exit(code=1)


@app.command("languages")
def list_languages(
    host: str = typer.Option(
        "http://localhost:5000",
        "--host",
        help="LibreTranslate server URL",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        help="LibreTranslate API key if required",
    ),
):
    """Show all languages supported by the LibreTranslate server."""
    try:
        from videotranslator.services.translator import LibreTranslateClient

        client = LibreTranslateClient(host=host, api_key=api_key)
        progress_manager.info(f"Fetching languages from {host}...")
        languages = client.get_languages()

        table = Table(
            title=f"Supported Languages ({host})",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Code", style="cyan", width=8)
        table.add_column("Language", style="white", width=30)

        for lang in sorted(languages, key=lambda x: x.get("name", "")):
            table.add_row(lang.get("code", ""), lang.get("name", ""))

        console.print(table)
        console.print(f"\n[bold green]Total:[/bold green] {len(languages)} languages")

    except Exception as e:
        progress_manager.error(f"Error: {e}")
        progress_manager.error("Make sure LibreTranslate is running: docker-compose up -d")
        logger.exception("Failed to fetch languages")
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
    burn_in: bool = typer.Option(
        False,
        "--burn-in",
        "-b",
        help="Burn subtitles into video (always visible, requires re-encoding)",
    ),
):
    """
    Add subtitles to a video file.

    Two modes:
    - Default: Embed subtitles as separate stream (selectable in player, fast)
    - --burn-in: Burn subtitles into video frames (always visible, slower)
    """
    try:
        from videotranslator.services import FFmpegService

        mode = "burn-in" if burn_in else "embedded stream"
        progress_manager.info(f"Adding subtitles to: {video_path.name} (mode: {mode})")

        ffmpeg_service = FFmpegService()
        output_video = ffmpeg_service.add_subtitles(
            video_path, subtitle_path, output_path, burn_in=burn_in
        )

        progress_manager.success(f"Video with subtitles: {output_video}")

    except Exception as e:
        progress_manager.error(f"Error: {e}")
        logger.exception("Subtitle addition failed")
        raise typer.Exit(code=1)


@app.command("models")
def list_models():
    """Show available Whisper models and their specifications."""
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
