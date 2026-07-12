"""Read, shift, and combine WebVTT subtitle files with millisecond precision."""

import webvtt


def parse_timestamp(timestamp: str) -> float:
    """Convert a VTT timestamp (HH:MM:SS.mmm or MM:SS.mmm) to float seconds."""
    parts = timestamp.split(":")
    if len(parts) == 2:
        parts = ["0"] + parts
    hours, minutes, seconds = parts
    secs, _, millis = seconds.partition(".")
    total = int(hours) * 3600 + int(minutes) * 60 + int(secs)
    if millis:
        total += int(millis.ljust(3, "0")) / 1000
    return total


def format_timestamp(seconds: float) -> str:
    """Convert float seconds to a VTT timestamp (HH:MM:SS.mmm)."""
    if seconds < 0:
        seconds = 0.0
    # Round to whole milliseconds first so 1.0005-style float error can't
    # produce a timestamp that disagrees with the parsed value.
    total_millis = round(seconds * 1000)
    hours, rem = divmod(total_millis, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def _write_cue(f, start: str, end: str, text: str) -> None:
    f.write(f"{start} --> {end}\n{text}\n\n")


def shift_vtt(input_path: str, output_path: str, shift_seconds: float) -> int:
    """Shift every cue in a VTT file by shift_seconds (negative to advance).

    Cues that would end at or before 0:00 are dropped; cues that would start
    before 0:00 are clamped to 0. Returns the number of cues written.
    """
    vtt = webvtt.read(input_path)
    written = 0

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for caption in vtt:
            new_start = parse_timestamp(caption.start) + shift_seconds
            new_end = parse_timestamp(caption.end) + shift_seconds
            if new_end <= 0:
                continue
            _write_cue(f, format_timestamp(new_start), format_timestamp(new_end), caption.text)
            written += 1

    return written


def combine_vtt(
    first_path: str,
    second_path: str,
    output_path: str,
    first_duration: float,
) -> int:
    """Concatenate two VTT files, offsetting the second by first_duration seconds.

    Returns the total number of cues written.
    """
    first = webvtt.read(first_path)
    second = webvtt.read(second_path)
    written = 0

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")

        for caption in first:
            _write_cue(f, caption.start, caption.end, caption.text)
            written += 1

        for caption in second:
            new_start = parse_timestamp(caption.start) + first_duration
            new_end = parse_timestamp(caption.end) + first_duration
            _write_cue(f, format_timestamp(new_start), format_timestamp(new_end), caption.text)
            written += 1

    return written
