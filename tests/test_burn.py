import pytest

from subtitle_toolkit.burn import build_burn_command, build_mux_command, escape_filter_path


def test_escape_filter_path_windows():
    assert escape_filter_path(r"C:\temp\subs.ass") == "C\\:/temp/subs.ass"


def test_escape_filter_path_posix():
    assert escape_filter_path("/tmp/subs.ass") == "/tmp/subs.ass"


def test_build_burn_command():
    cmd = build_burn_command("ffmpeg", "in.mp4", r"C:\t\s.ass", "out.mp4")
    assert cmd[0] == "ffmpeg"
    assert "-vf" in cmd
    assert cmd[cmd.index("-vf") + 1] == "ass=C\\:/t/s.ass"
    assert "-t" not in cmd
    assert cmd[-1] == "out.mp4"
    assert cmd[-2] == "-y"


def test_build_burn_command_with_limit():
    cmd = build_burn_command("ffmpeg", "in.mp4", "s.ass", "out.mp4", limit_seconds=60)
    assert cmd[cmd.index("-t") + 1] == "60"


def test_build_mux_command_mp4_uses_mov_text():
    cmd = build_mux_command("ffmpeg", "in.mp4", "subs.vtt", "out.mp4", language="jpn")
    assert cmd[cmd.index("-c:s") + 1] == "mov_text"
    assert "language=jpn" in cmd


def test_build_mux_command_mkv_uses_srt():
    cmd = build_mux_command("ffmpeg", "in.mkv", "subs.vtt", "out.mkv")
    assert cmd[cmd.index("-c:s") + 1] == "srt"


def test_build_mux_command_rejects_unknown_container():
    with pytest.raises(ValueError):
        build_mux_command("ffmpeg", "in.mp4", "subs.vtt", "out.avi")
