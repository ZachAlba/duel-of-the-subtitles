"""Locate the FFmpeg executable."""

import os
import shutil

ENV_VAR = "SUBTITLE_TOOLKIT_FFMPEG"

# Fallback for machines where ffmpeg was unpacked manually instead of added to PATH.
_LEGACY_WINDOWS_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"


def find_ffmpeg() -> str:
    """Return the path to ffmpeg, or raise FileNotFoundError with install guidance.

    Resolution order: SUBTITLE_TOOLKIT_FFMPEG env var, PATH, then the
    conventional C:\\ffmpeg\\bin location on Windows.
    """
    env_path = os.environ.get(ENV_VAR)
    if env_path:
        if os.path.isfile(env_path):
            return env_path
        raise FileNotFoundError(
            f"{ENV_VAR} is set to {env_path!r} but no file exists there."
        )

    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path

    if os.path.isfile(_LEGACY_WINDOWS_PATH):
        return _LEGACY_WINDOWS_PATH

    raise FileNotFoundError(
        "ffmpeg not found. Install it and add it to PATH, or set the "
        f"{ENV_VAR} environment variable to the full path of the executable."
    )
