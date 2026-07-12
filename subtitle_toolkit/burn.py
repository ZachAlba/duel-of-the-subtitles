"""Embed subtitles into videos with FFmpeg: hardcode (re-encode) or mux (no re-encode)."""

import os
import subprocess
import tempfile
from typing import Callable, List, Optional

from subtitle_toolkit.ass import vtt_to_ass
from subtitle_toolkit.ffmpeg import find_ffmpeg

ProgressCallback = Callable[[str], None]


def escape_filter_path(path: str) -> str:
    """Escape a filesystem path for use inside an FFmpeg filter argument.

    FFmpeg filter syntax treats ':' and '\\' specially, so Windows paths like
    C:\\temp\\subs.ass must become C\\:/temp/subs.ass.
    """
    return path.replace("\\", "/").replace(":", "\\:")


def build_burn_command(
    ffmpeg: str,
    video_path: str,
    ass_path: str,
    output_path: str,
    limit_seconds: Optional[float] = None,
) -> List[str]:
    """Build the FFmpeg command that burns an ASS file into a video."""
    command = [
        ffmpeg,
        "-i", video_path,
        "-vf", f"ass={escape_filter_path(ass_path)}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-c:a", "copy",
        "-movflags", "+faststart",
    ]
    if limit_seconds is not None:
        command.extend(["-t", str(limit_seconds)])
    command.extend(["-y", output_path])
    return command


def build_mux_command(
    ffmpeg: str,
    video_path: str,
    subtitle_path: str,
    output_path: str,
    language: str = "eng",
) -> List[str]:
    """Build the FFmpeg command that muxes subtitles as a soft track (no re-encode)."""
    ext = os.path.splitext(output_path)[1].lower()
    if ext == ".mp4":
        subtitle_codec = "mov_text"
    elif ext == ".mkv":
        subtitle_codec = "srt"
    else:
        raise ValueError(f"Soft-sub muxing supports .mp4 and .mkv outputs, got {ext!r}")

    return [
        ffmpeg,
        "-i", video_path,
        "-i", subtitle_path,
        "-map", "0",
        "-map", "1:0",
        "-c", "copy",
        "-c:s", subtitle_codec,
        "-metadata:s:s:0", f"language={language}",
        "-y", output_path,
    ]


def _run_ffmpeg(command: List[str], progress: Optional[ProgressCallback] = None) -> None:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        encoding="utf-8",
        errors="replace",
    )
    stderr_lines: List[str] = []
    assert process.stderr is not None
    for line in process.stderr:
        line = line.strip()
        if line:
            stderr_lines.append(line)
            if progress and "frame=" in line:
                progress(line)
    process.wait()
    if process.returncode != 0:
        tail = "\n".join(stderr_lines[-10:])
        raise RuntimeError(f"FFmpeg failed (exit code {process.returncode}):\n{tail}")


def burn_subtitles(
    video_path: str,
    subtitle_path: str,
    output_path: str,
    time_offset: float = 0,
    position: str = "top",
    limit_seconds: Optional[float] = None,
    progress: Optional[ProgressCallback] = None,
    ffmpeg_path: Optional[str] = None,
) -> None:
    """Hardcode a VTT subtitle file into a video (re-encodes the video stream)."""
    ffmpeg = ffmpeg_path or find_ffmpeg()
    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)

    fd, temp_ass = tempfile.mkstemp(suffix=".ass", prefix="subtitle_toolkit_")
    os.close(fd)
    try:
        vtt_to_ass(subtitle_path, temp_ass, time_offset=time_offset, position=position)
        command = build_burn_command(ffmpeg, video_path, temp_ass, output_path, limit_seconds)
        _run_ffmpeg(command, progress)
    finally:
        if os.path.exists(temp_ass):
            os.remove(temp_ass)


def mux_subtitles(
    video_path: str,
    subtitle_path: str,
    output_path: str,
    language: str = "eng",
    progress: Optional[ProgressCallback] = None,
    ffmpeg_path: Optional[str] = None,
) -> None:
    """Add subtitles as a selectable soft track without re-encoding (fast)."""
    ffmpeg = ffmpeg_path or find_ffmpeg()
    out_dir = os.path.dirname(os.path.abspath(output_path))
    os.makedirs(out_dir, exist_ok=True)

    command = build_mux_command(ffmpeg, video_path, subtitle_path, output_path, language)
    _run_ffmpeg(command, progress)
