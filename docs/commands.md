# Command Reference

## Global options

| Flag | Description |
|------|-------------|
| `--version`, `-v` | Show version and exit |
| `--help` | Show help for any command |

---

## `transcribe`

Transcribe a video and optionally translate and embed subtitles.

```bash
videotranslator transcribe <video> [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | same dir as video | Output directory |
| `--language` | `-l` | auto-detect | Source language code |
| `--model` | `-m` | `base` | Whisper model size |
| `--add-to-video` | `-a` | off | Embed subtitles into the video |
| `--burn-in` | `-b` | off | Burn subtitles into video frames |
| `--keep-audio` | `-k` | off | Keep the extracted WAV file |
| `--translate-to` | | | Target language code(s), repeatable |
| `--translate-host` | | `http://localhost:5000` | LibreTranslate URL |
| `--translate-api-key` | | none | LibreTranslate API key |
| `--multi-track` | | off | Embed source + all translations as separate tracks |

**Examples:**

```bash
# Basic transcription
videotranslator transcribe lecture.mp4

# Transcribe + embed English subtitles
videotranslator transcribe lecture.mp4 --add-to-video

# Transcribe and translate to Spanish (one-shot pipeline)
videotranslator transcribe lecture.mp4 --translate-to es --add-to-video

# Multi-language: generate SRTs and embed all as selectable tracks
videotranslator transcribe lecture.mp4 \
  --translate-to es --translate-to fr --translate-to de \
  --add-to-video --multi-track
```

---

## `translate`

Translate an existing SRT file to one or more languages.

```bash
videotranslator translate <srt_file> --target <lang> [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--target` | `-t` | **required** | Target language code(s), repeatable |
| `--source` | `-s` | `auto` | Source language code |
| `--output` | `-o` | same dir as SRT | Output directory |
| `--host` | | `http://localhost:5000` | LibreTranslate URL |
| `--api-key` | | none | LibreTranslate API key |

**Examples:**

```bash
# Translate to Spanish
videotranslator translate subtitles.srt --target es

# Translate to multiple languages
videotranslator translate subtitles.srt --target es --target fr --target de

# Specify source language and output directory
videotranslator translate subtitles.srt --source en --target ja -o ./output
```

---

## `languages`

List all languages supported by the LibreTranslate server.

```bash
videotranslator languages [OPTIONS]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `http://localhost:5000` | LibreTranslate URL |
| `--api-key` | none | LibreTranslate API key |

**Example:**

```bash
videotranslator languages
videotranslator languages --host http://my-translate-server:5000
```

---

## `extract-audio`

Extract audio from a video file.

```bash
videotranslator extract-audio <video> [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | same name as video | Output audio file path |
| `--format` | `-f` | `wav` | Audio format (`wav`, `mp3`) |

---

## `add-subtitles`

Add an existing SRT file to a video.

```bash
videotranslator add-subtitles <video> <srt_file> [OPTIONS]
```

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | `<video>_subtitled.mp4` | Output video path |
| `--burn-in` | `-b` | off | Burn subtitles into frames |

---

## `models`

Show available Whisper models and their specifications.

```bash
videotranslator models
```

---

## `config`

Display the current configuration values.

```bash
videotranslator config
```
