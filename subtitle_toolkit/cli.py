"""Unified command-line interface for the subtitle toolkit."""

import argparse
import os
import sys

from subtitle_toolkit import __version__
from subtitle_toolkit.burn import burn_subtitles, mux_subtitles
from subtitle_toolkit.matching import extract_episode_number, find_matching_pairs
from subtitle_toolkit.vtt import combine_vtt, shift_vtt


def _resolve_output(video: str, output_path: str, single: bool) -> str:
    """Decide the output file for one video in single or batch mode."""
    root, ext = os.path.splitext(output_path)
    if single and ext:
        return output_path
    episode = extract_episode_number(os.path.basename(video))
    name = f"ep{episode}.mp4" if episode is not None else os.path.basename(video)
    return os.path.join(output_path, name)


def _run_batch(args, action, verb: str) -> int:
    pairs, unmatched = find_matching_pairs(args.video_path, args.sub_path)
    for video in unmatched:
        print(f"Warning: no matching subtitle found for {video}")
    if not pairs:
        print("No matching video/subtitle pairs found.")
        return 1

    single = len(pairs) == 1
    print(f"{verb} {len(pairs)} video/subtitle pair(s)...")
    failed = 0
    for video, sub in pairs:
        out_file = _resolve_output(video, args.output_path, single)
        print(f"\n{video} + {sub} -> {out_file}")
        try:
            action(video, sub, out_file)
            print(f"Done: {out_file}")
        except Exception as exc:  # keep batch going; report at the end
            failed += 1
            print(f"Error processing {video}: {exc}", file=sys.stderr)

    print(f"\nFinished: {len(pairs) - failed} succeeded, {failed} failed.")
    return 1 if failed else 0


def _cmd_burn(args) -> int:
    def action(video, sub, out_file):
        burn_subtitles(
            video,
            sub,
            out_file,
            time_offset=args.offset,
            position=args.position,
            limit_seconds=60 if args.debug else None,
            progress=lambda line: print(line, end="\r"),
        )

    return _run_batch(args, action, "Hardcoding subtitles into")


def _cmd_mux(args) -> int:
    def action(video, sub, out_file):
        mux_subtitles(video, sub, out_file, language=args.language)

    return _run_batch(args, action, "Muxing soft subtitles into")


def _cmd_shift(args) -> int:
    count = shift_vtt(args.input_vtt, args.output_vtt, args.shift_seconds)
    print(f"Wrote {count} cues to {args.output_vtt}")
    return 0


def _cmd_combine(args) -> int:
    count = combine_vtt(args.vtt1, args.vtt2, args.output_vtt, args.ep1_duration)
    print(f"Wrote {count} cues to {args.output_vtt}")
    return 0


def _add_video_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("video_path", help="Video file or directory")
    parser.add_argument("sub_path", help="Subtitle file or directory")
    parser.add_argument("output_path", help="Output file or directory")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="subtitle-toolkit",
        description="Shift, combine, and embed subtitles into videos",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    burn = subparsers.add_parser("burn", help="Hardcode subtitles into video (re-encodes)")
    _add_video_args(burn)
    burn.add_argument("--offset", type=float, default=0, help="Subtitle time offset in seconds")
    burn.add_argument(
        "--position", choices=["top", "bottom"], default="top",
        help="Where to place the burned subtitles (default: top, for dual-subtitle setups)",
    )
    burn.add_argument("--debug", action="store_true", help="Process only the first minute")
    burn.set_defaults(func=_cmd_burn)

    mux = subparsers.add_parser("mux", help="Add subtitles as a soft track (fast, no re-encode)")
    _add_video_args(mux)
    mux.add_argument("--language", default="eng", help="ISO 639-2 language tag (default: eng)")
    mux.set_defaults(func=_cmd_mux)

    shift = subparsers.add_parser("shift", help="Shift all cue times in a VTT file")
    shift.add_argument("input_vtt", help="Input VTT file")
    shift.add_argument("output_vtt", help="Output VTT file")
    shift.add_argument(
        "shift_seconds", type=float,
        help="Seconds to shift (positive to delay, negative to advance)",
    )
    shift.set_defaults(func=_cmd_shift)

    combine = subparsers.add_parser("combine", help="Concatenate two VTT files")
    combine.add_argument("vtt1", help="First VTT file")
    combine.add_argument("vtt2", help="Second VTT file")
    combine.add_argument("output_vtt", help="Output VTT file")
    combine.add_argument("ep1_duration", type=float, help="Duration of the first video in seconds")
    combine.set_defaults(func=_cmd_combine)

    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
