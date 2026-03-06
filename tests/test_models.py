"""Unit tests for transcription data models."""

from pathlib import Path

from videotranslator.models.transcription import SubtitleSegment, TranscriptionResult


def test_format_timestamp_zero():
    assert SubtitleSegment._format_timestamp(0.0) == "00:00:00,000"


def test_format_timestamp_minutes():
    assert SubtitleSegment._format_timestamp(90.0) == "00:01:30,000"


def test_format_timestamp_hours():
    assert SubtitleSegment._format_timestamp(3661.5) == "01:01:01,500"


def test_format_timestamp_millis():
    assert SubtitleSegment._format_timestamp(1.123) == "00:00:01,123"


def test_subtitle_segment_to_srt_format():
    seg = SubtitleSegment(index=1, start_time=1.0, end_time=3.0, text="Hello, world!")
    result = seg.to_srt_format()
    assert result == "1\n00:00:01,000 --> 00:00:03,000\nHello, world!\n"


def test_subtitle_segment_multiline_text():
    seg = SubtitleSegment(index=2, start_time=0.0, end_time=2.0, text="Line one\nLine two")
    result = seg.to_srt_format()
    assert "Line one\nLine two" in result


def test_transcription_result_to_srt():
    segs = [
        SubtitleSegment(1, 0.0, 1.0, "Hello"),
        SubtitleSegment(2, 1.0, 2.0, "World"),
    ]
    result = TranscriptionResult(segments=segs, language="en", source_file=Path("test.mp4"))
    srt = result.to_srt()
    assert "Hello" in srt
    assert "World" in srt
    assert "1\n" in srt
    assert "2\n" in srt


def test_transcription_result_to_srt_joins_with_newline():
    segs = [
        SubtitleSegment(1, 0.0, 1.0, "A"),
        SubtitleSegment(2, 1.0, 2.0, "B"),
    ]
    result = TranscriptionResult(segments=segs, language="en", source_file=Path("x.mp4"))
    srt = result.to_srt()
    # Segments are joined by a single newline (between the trailing \n of each block)
    assert srt.count("-->") == 2


def test_save_srt_writes_file(tmp_path):
    segs = [SubtitleSegment(1, 0.0, 1.5, "Test subtitle")]
    result = TranscriptionResult(segments=segs, language="en", source_file=Path("v.mp4"))
    output = tmp_path / "out.srt"
    result.save_srt(output)
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "Test subtitle" in content


def test_save_srt_creates_parent_dirs(tmp_path):
    segs = [SubtitleSegment(1, 0.0, 1.0, "Hi")]
    result = TranscriptionResult(segments=segs, language="en", source_file=Path("v.mp4"))
    output = tmp_path / "nested" / "dir" / "out.srt"
    result.save_srt(output)
    assert output.exists()


def test_save_srt_utf8_encoding(tmp_path):
    segs = [SubtitleSegment(1, 0.0, 1.0, "Hola, \u00bfc\u00f3mo est\u00e1s?")]
    result = TranscriptionResult(segments=segs, language="es", source_file=Path("v.mp4"))
    output = tmp_path / "out.srt"
    result.save_srt(output)
    content = output.read_text(encoding="utf-8")
    assert "\u00bfc\u00f3mo est\u00e1s?" in content
