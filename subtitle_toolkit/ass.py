"""Convert WebVTT subtitles to styled ASS, positioned to coexist with existing subs."""

import webvtt

from subtitle_toolkit.vtt import parse_timestamp

# ASS numpad alignment values.
_ALIGNMENT = {"top": 8, "bottom": 2}

_HEADER_TEMPLATE = """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: {style_name},{font},{size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,2,1,{alignment},10,10,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def build_ass_header(
    position: str = "top",
    font: str = "Arial",
    size: int = 45,
    margin_v: int = 25,
    style_name: str = "Subs",
) -> str:
    """Build the ASS file header with a single named style."""
    if position not in _ALIGNMENT:
        raise ValueError(f"position must be one of {sorted(_ALIGNMENT)}, got {position!r}")
    return _HEADER_TEMPLATE.format(
        style_name=style_name,
        font=font,
        size=size,
        alignment=_ALIGNMENT[position],
        margin_v=margin_v,
    )


def seconds_to_ass_time(seconds: float) -> str:
    """Convert float seconds to ASS time format (H:MM:SS.cc)."""
    if seconds < 0:
        seconds = 0.0
    total_centis = round(seconds * 100)
    hours, rem = divmod(total_centis, 360_000)
    minutes, rem = divmod(rem, 6_000)
    secs, centis = divmod(rem, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"


def vtt_to_ass(
    vtt_path: str,
    ass_path: str,
    time_offset: float = 0,
    position: str = "top",
    font: str = "Arial",
    size: int = 45,
) -> int:
    """Convert a VTT file to ASS with the given position and time offset.

    Returns the number of dialogue lines written.
    """
    style_name = "Subs"
    vtt = webvtt.read(vtt_path)
    written = 0

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(build_ass_header(position=position, font=font, size=size, style_name=style_name))
        for caption in vtt:
            start = seconds_to_ass_time(parse_timestamp(caption.start) + time_offset)
            end = seconds_to_ass_time(parse_timestamp(caption.end) + time_offset)
            text = caption.text.replace("\n", "\\N")
            f.write(f"Dialogue: 0,{start},{end},{style_name},,0,0,0,,{text}\n")
            written += 1

    return written
