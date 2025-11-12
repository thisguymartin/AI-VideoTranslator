
![DALL·E 2024-01-15 19 42 01 - Modify the first banner image previously generated, representing the conversion from audio to subtitles for _AI-VideoTranslator_, by removing any text](https://github.com/thisguymartin/AI-VideoTranslator/assets/13192083/f922781b-518b-461e-9a5a-6257fcba55fb)

# AI VideoTranslator 🎥 → 📝

Modern CLI tool for video transcription and subtitle generation using **open-source AI**.

## ✨ Features

- 🆓 **100% Open Source** - Uses OpenAI's Whisper model (no API keys or cloud costs!)
- 🚀 **Fast & Modern** - Built with modern Python tooling (`uv`, `typer`, `rich`)
- 🎯 **Simple CLI** - Easy-to-use command-line interface with progress bars
- 🌍 **Multilingual** - Supports 99+ languages with auto-detection
- 🎬 **Complete Workflow** - Extract audio, transcribe, and add subtitles in one command
- 🔒 **Secure** - No shell injection vulnerabilities, proper error handling
- ⚙️ **Configurable** - Environment variables for all settings

## 🆚 Open Source vs Cloud

| Feature | Open Source (Whisper) | Cloud (AWS/Google) |
|---------|----------------------|-------------------|
| **Cost** | Free | Pay per minute |
| **Privacy** | 100% local | Data sent to cloud |
| **API Keys** | None required | Required |
| **Internet** | Not required | Required |
| **Speed** | Depends on hardware | Usually fast |
| **Accuracy** | Excellent | Excellent |

## 📋 Requirements

- Python 3.10+
- FFmpeg (for video processing)
- `uv` (modern Python package manager)

### Install FFmpeg

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (using Chocolatey)
choco install ffmpeg
```

### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/thisguymartin/AI-VideoTranslator.git
cd AI-VideoTranslator
```

### 2. Set up the environment with uv

```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode
uv pip install -e .
```

### 3. Configure (Optional)

```bash
# Copy example configuration
cp .env.example .env

# Edit settings (optional - defaults work well)
# nano .env
```

### 4. Run your first transcription!

```bash
# Basic usage - transcribe a video
videotranslator transcribe video.mp4

# Transcribe and add subtitles to video
videotranslator transcribe video.mp4 --add-to-video

# Specify output directory and language
videotranslator transcribe video.mp4 -o ./output -l es

# Use a larger model for better accuracy
videotranslator transcribe video.mp4 -m medium
```

## 📖 Usage

### Main Commands

#### Transcribe a Video

```bash
# Basic transcription (generates SRT file)
videotranslator transcribe video.mp4

# Full workflow (extract, transcribe, add subtitles)
videotranslator transcribe video.mp4 --add-to-video

# Specify output directory
videotranslator transcribe video.mp4 -o ./output

# Keep extracted audio file
videotranslator transcribe video.mp4 --keep-audio

# Use specific language (skip auto-detection)
videotranslator transcribe video.mp4 -l en

# Use different Whisper model
videotranslator transcribe video.mp4 -m large
```

#### Extract Audio Only

```bash
# Extract audio as WAV
videotranslator extract-audio video.mp4

# Extract as MP3
videotranslator extract-audio video.mp4 -f mp3 -o audio.mp3
```

#### Add Subtitles to Video

```bash
# Add existing SRT file to video
videotranslator add-subtitles video.mp4 subtitles.srt

# Specify output path
videotranslator add-subtitles video.mp4 subtitles.srt -o output.mp4
```

#### List Available Models

```bash
# Show all Whisper models and their specs
videotranslator models
```

#### Show Configuration

```bash
# Display current settings
videotranslator config
```

### Whisper Model Selection

Choose based on your needs:

| Model | Speed | Accuracy | VRAM | Best For |
|-------|-------|----------|------|----------|
| `tiny` | 🚀 Fastest | ⭐ Basic | ~1GB | Quick drafts |
| `base` | ⚡ Fast | ⭐⭐ Good | ~1GB | **Recommended default** |
| `small` | 🏃 Medium | ⭐⭐⭐ Better | ~2GB | Balanced |
| `medium` | 🚶 Slow | ⭐⭐⭐⭐ Great | ~5GB | High accuracy |
| `large` | 🐌 Slowest | ⭐⭐⭐⭐⭐ Best | ~10GB | Maximum accuracy |

## ⚙️ Configuration

Configuration can be set via:
1. Environment variables (`.env` file)
2. Command-line options
3. Default values

### Environment Variables

```bash
# Whisper model size
VIDEOTRANSLATOR_WHISPER_MODEL=base  # tiny, base, small, medium, large

# Language (ISO 639-1 code, empty for auto-detect)
VIDEOTRANSLATOR_LANGUAGE=en

# Device (cpu or cuda for GPU)
VIDEOTRANSLATOR_DEVICE=cpu

# Audio settings
VIDEOTRANSLATOR_AUDIO_BITRATE=192k

# Video encoding
VIDEOTRANSLATOR_VIDEO_CODEC=libx264
VIDEOTRANSLATOR_SUBTITLE_CODEC=mov_text

# Logging level
VIDEOTRANSLATOR_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

## 🎯 Examples

### Example 1: Quick Transcription

```bash
# Transcribe a video with default settings
videotranslator transcribe my_video.mp4
```

**Output:**
- `my_video.srt` - Subtitle file

### Example 2: Complete Workflow

```bash
# Transcribe and add subtitles to video
videotranslator transcribe interview.mp4 --add-to-video -o ./output
```

**Output:**
- `output/interview.srt` - Subtitle file
- `output/interview_subtitled.mp4` - Video with subtitles

### Example 3: High-Quality Transcription

```bash
# Use large model for best accuracy
videotranslator transcribe lecture.mp4 -m large --add-to-video
```

### Example 4: Foreign Language Video

```bash
# Spanish video transcription
videotranslator transcribe video_es.mp4 -l es --add-to-video
```

### Example 5: Batch Processing

```bash
# Process multiple videos
for video in *.mp4; do
    videotranslator transcribe "$video" --add-to-video -o ./processed
done
```

## 🛠️ Development

### Install Development Dependencies

```bash
# Install with dev extras
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality

```bash
# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/

# Run tests
pytest
```

## 🏗️ Architecture

```
src/videotranslator/
├── cli.py              # Main CLI interface
├── config.py           # Configuration management
├── logger.py           # Logging setup
├── models/             # Data models
│   └── transcription.py
├── services/           # Core services
│   ├── whisper.py      # Whisper AI integration
│   ├── ffmpeg.py       # Video/audio processing
│   └── subtitle.py     # Subtitle generation
└── ui/                 # Terminal UI
    └── progress.py     # Progress bars & status
```

## 🔄 Migrating from Old Version

The old version used AWS Transcribe or Google Cloud Speech-to-Text (cloud services with API costs). The new version uses:

- ✅ **Whisper** (open-source, local, free)
- ✅ Modern Python tooling (`uv`, `pyproject.toml`)
- ✅ Type hints and better error handling
- ✅ Improved CLI with progress bars
- ✅ Security fixes (no shell injection)

### Old Command → New Command

```bash
# Old
python main.py video extract-audio-aws ~/video.mp4 ~/output/ my-bucket

# New (no AWS needed!)
videotranslator transcribe ~/video.mp4 -o ~/output --add-to-video
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) - Open-source speech recognition
- [FFmpeg](https://ffmpeg.org/) - Video processing
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/thisguymartin/AI-VideoTranslator/issues)
- 📖 **Documentation**: This README
- 💬 **Discussions**: [GitHub Discussions](https://github.com/thisguymartin/AI-VideoTranslator/discussions)

---

Made with ❤️ using open-source AI
