"""Match video files to subtitle files by episode number."""

import glob
import os
import re
from typing import List, Optional, Tuple

# Tokens that contain digits but never identify an episode.
_NOISE_PATTERN = re.compile(
    r"(\d{3,4}p|[xh]\.?26[45]|\d+\s?bits?|v\d+)",
    re.IGNORECASE,
)
_YEAR_PATTERN = re.compile(r"^(19|20)\d{2}$")

VIDEO_EXTENSIONS = (".mp4", ".mkv", ".avi", ".mov", ".webm")
SUBTITLE_EXTENSIONS = (".vtt", ".srt", ".ass")


def extract_episode_number(filename: str) -> Optional[int]:
    """Extract an episode number from a filename, or None if there isn't one.

    Tries SxxEyy and "ep/episode N" forms first, then falls back to the last
    number remaining after stripping resolution/codec tokens and years.
    """
    stem = os.path.splitext(os.path.basename(filename))[0]

    match = re.search(r"[sS]\d+[\s._-]*[eE](\d+)", stem)
    if match:
        return int(match.group(1))

    match = re.search(r"(?:\bep|episode)[\s._-]*(\d+)", stem, re.IGNORECASE)
    if match:
        return int(match.group(1))

    cleaned = _NOISE_PATTERN.sub("", stem)
    numbers = re.findall(r"\d+", cleaned)
    if not numbers:
        return None

    non_years = [n for n in numbers if not _YEAR_PATTERN.match(n)]
    candidates = non_years or numbers
    return int(candidates[-1])


def _collect(directory: str, extensions: Tuple[str, ...]) -> List[str]:
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(directory, f"*{ext}")))
    return sorted(files)


def find_matching_pairs(
    video_path: str,
    subtitle_path: str,
) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Pair videos with subtitles.

    In single-file mode (both paths are files) returns that one pair. In
    directory mode, pairs files whose extracted episode numbers match.

    Returns (pairs, unmatched_videos).
    """
    if os.path.isfile(video_path) and os.path.isfile(subtitle_path):
        return [(video_path, subtitle_path)], []

    if not (os.path.isdir(video_path) and os.path.isdir(subtitle_path)):
        raise ValueError(
            "video_path and subtitle_path must both be files or both be directories"
        )

    video_files = _collect(video_path, VIDEO_EXTENSIONS)
    subtitle_files = _collect(subtitle_path, SUBTITLE_EXTENSIONS)

    subs_by_episode = {}
    for sub in subtitle_files:
        episode = extract_episode_number(sub)
        if episode is not None:
            subs_by_episode.setdefault(episode, sub)

    pairs = []
    unmatched = []
    for video in video_files:
        episode = extract_episode_number(video)
        sub = subs_by_episode.get(episode) if episode is not None else None
        if sub:
            pairs.append((video, sub))
        else:
            unmatched.append(video)

    pairs.sort(key=lambda pair: extract_episode_number(pair[0]) or 0)
    return pairs, unmatched
