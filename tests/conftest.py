"""Shared fixtures for the test suite."""

import pytest
from pathlib import Path

SAMPLE_SRT_CONTENT = """\
1
00:00:01,000 --> 00:00:03,000
Hello, world!

2
00:00:04,000 --> 00:00:06,000
This is a test subtitle.

3
00:00:07,000 --> 00:00:09,500
Goodbye!
"""


@pytest.fixture
def sample_srt_content() -> str:
    return SAMPLE_SRT_CONTENT


@pytest.fixture
def sample_srt_file(tmp_path: Path) -> Path:
    srt_path = tmp_path / "sample.srt"
    srt_path.write_text(SAMPLE_SRT_CONTENT, encoding="utf-8")
    return srt_path


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    out = tmp_path / "output"
    out.mkdir()
    return out
