import textwrap

import pytest

from subtitle_toolkit.ass import build_ass_header, seconds_to_ass_time, vtt_to_ass


@pytest.fixture
def sample_vtt(tmp_path):
    path = tmp_path / "sample.vtt"
    path.write_text(
        textwrap.dedent("""\
            WEBVTT

            00:00:01.500 --> 00:00:03.250
            Hello
            world
        """),
        encoding="utf-8",
    )
    return path


def test_seconds_to_ass_time():
    assert seconds_to_ass_time(0) == "0:00:00.00"
    assert seconds_to_ass_time(3723.5) == "1:02:03.50"
    assert seconds_to_ass_time(59.999) == "0:01:00.00"  # rounds to centiseconds
    assert seconds_to_ass_time(-5) == "0:00:00.00"


def test_header_positions():
    assert ",8,10,10,25,1" in build_ass_header(position="top")
    assert ",2,10,10,25,1" in build_ass_header(position="bottom")
    with pytest.raises(ValueError):
        build_ass_header(position="middle")


def test_vtt_to_ass_conversion(tmp_path, sample_vtt):
    out = tmp_path / "out.ass"
    count = vtt_to_ass(str(sample_vtt), str(out), time_offset=1.0)
    assert count == 1
    content = out.read_text(encoding="utf-8")
    assert "[Script Info]" in content
    # 1.5s + 1.0s offset = 2.5s; newline becomes \N
    assert "Dialogue: 0,0:00:02.50,0:00:04.25,Subs,,0,0,0,,Hello\\Nworld" in content
