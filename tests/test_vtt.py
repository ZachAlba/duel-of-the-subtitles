import textwrap

import pytest

from subtitle_toolkit.vtt import combine_vtt, format_timestamp, parse_timestamp, shift_vtt

SAMPLE = textwrap.dedent("""\
    WEBVTT

    00:00:01.500 --> 00:00:03.250
    First line

    00:00:05.000 --> 00:00:07.750
    Second line
    with a second row
""")


@pytest.fixture
def sample_vtt(tmp_path):
    path = tmp_path / "sample.vtt"
    path.write_text(SAMPLE, encoding="utf-8")
    return path


def test_parse_timestamp_full_and_short_forms():
    assert parse_timestamp("01:02:03.500") == 3723.5
    assert parse_timestamp("02:03.500") == 123.5
    assert parse_timestamp("00:00:00.001") == 0.001


def test_format_timestamp_roundtrip():
    for value in [0, 0.001, 1.5, 59.999, 61.25, 3723.5, 7325.042]:
        assert parse_timestamp(format_timestamp(value)) == pytest.approx(value, abs=0.0005)


def test_format_timestamp_clamps_negative():
    assert format_timestamp(-3.2) == "00:00:00.000"


def test_shift_forward(tmp_path, sample_vtt):
    out = tmp_path / "shifted.vtt"
    count = shift_vtt(str(sample_vtt), str(out), 2.5)
    assert count == 2
    content = out.read_text(encoding="utf-8")
    assert "00:00:04.000 --> 00:00:05.750" in content
    assert "00:00:07.500 --> 00:00:10.250" in content
    assert "with a second row" in content


def test_shift_backward_drops_cues_before_zero(tmp_path, sample_vtt):
    out = tmp_path / "shifted.vtt"
    count = shift_vtt(str(sample_vtt), str(out), -4)
    content = out.read_text(encoding="utf-8")
    # First cue (1.5-3.25s) would end before 0 and is dropped;
    # second cue (5-7.75s) survives at 1-3.75s.
    assert count == 1
    assert "First line" not in content
    assert "00:00:01.000 --> 00:00:03.750" in content


def test_combine_offsets_second_file(tmp_path, sample_vtt):
    out = tmp_path / "combined.vtt"
    count = combine_vtt(str(sample_vtt), str(sample_vtt), str(out), 1800)
    assert count == 4
    content = out.read_text(encoding="utf-8")
    # Original timings preserved for file 1
    assert "00:00:01.500 --> 00:00:03.250" in content
    # File 2 shifted by 1800s = 30min
    assert "00:30:01.500 --> 00:30:03.250" in content
    assert "00:30:05.000 --> 00:30:07.750" in content
