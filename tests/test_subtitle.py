"""Tests for SubtitleService."""

import pytest
from pathlib import Path

from videotranslator.services.subtitle import SubtitleService


def test_convert_srt_to_vtt_adds_webvtt_header(sample_srt_file, tmp_path):
    vtt_path = tmp_path / "out.vtt"
    result = SubtitleService.convert_srt_to_vtt(sample_srt_file, vtt_path)
    content = result.read_text(encoding="utf-8")
    assert content.startswith("WEBVTT")


def test_convert_srt_to_vtt_converts_commas_to_dots(sample_srt_file, tmp_path):
    vtt_path = tmp_path / "out.vtt"
    result = SubtitleService.convert_srt_to_vtt(sample_srt_file, vtt_path)
    content = result.read_text(encoding="utf-8")
    # SRT uses commas in timestamps (00:00:01,000); VTT uses dots (00:00:01.000)
    assert "00:00:01.000" in content
    assert "00:00:01,000" not in content


def test_convert_srt_to_vtt_preserves_text(sample_srt_file, tmp_path):
    vtt_path = tmp_path / "out.vtt"
    result = SubtitleService.convert_srt_to_vtt(sample_srt_file, vtt_path)
    content = result.read_text(encoding="utf-8")
    assert "Hello, world!" in content
    assert "Goodbye!" in content


def test_convert_srt_to_vtt_default_output_path(sample_srt_file):
    result = SubtitleService.convert_srt_to_vtt(sample_srt_file)
    assert result.suffix == ".vtt"
    assert result.stem == sample_srt_file.stem
    result.unlink(missing_ok=True)


def test_convert_srt_to_vtt_raises_if_file_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        SubtitleService.convert_srt_to_vtt(tmp_path / "nonexistent.srt")
