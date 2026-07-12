"""Subtitle Toolkit: shift, combine, convert, and embed subtitles into videos."""

__version__ = "0.2.0"

from subtitle_toolkit.vtt import shift_vtt, combine_vtt
from subtitle_toolkit.ass import vtt_to_ass
from subtitle_toolkit.burn import burn_subtitles, mux_subtitles
from subtitle_toolkit.matching import find_matching_pairs

__all__ = [
    "shift_vtt",
    "combine_vtt",
    "vtt_to_ass",
    "burn_subtitles",
    "mux_subtitles",
    "find_matching_pairs",
]
