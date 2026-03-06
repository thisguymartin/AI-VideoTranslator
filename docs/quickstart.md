# Quickstart Guide

Get up and running with AI VideoTranslator in 5 steps.

## Step 1: Clone

```bash
git clone https://github.com/thisguymartin/AI-VideoTranslator.git
cd AI-VideoTranslator
```

## Step 2: Install

```bash
# Create virtual environment and install
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

Verify the installation:

```bash
videotranslator --version
```

## Step 3: Start LibreTranslate (for translation)

```bash
docker-compose up -d

# Wait ~1 minute for the first startup, then verify:
curl http://localhost:5000/health
```

## Step 4: Transcribe a video

```bash
# Generate an SRT subtitle file from a video
videotranslator transcribe video.mp4

# Transcribe and embed subtitles into the video
videotranslator transcribe video.mp4 --add-to-video

# Use a better model for higher accuracy
videotranslator transcribe video.mp4 -m medium --add-to-video
```

## Step 5: Translate subtitles

```bash
# Translate an existing SRT to Spanish
videotranslator translate video.srt --target es

# Or transcribe and translate in one command
videotranslator transcribe video.mp4 --translate-to es --add-to-video

# Multi-language, all tracks embedded in one video
videotranslator transcribe video.mp4 --translate-to es --translate-to fr --add-to-video --multi-track
```

## Next steps

- See [commands.md](commands.md) for the full command reference.
- Run `videotranslator languages` to list all supported translation languages.
- Run `videotranslator models` to compare Whisper model sizes.
