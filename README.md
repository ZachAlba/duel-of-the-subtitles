# Subtitle Toolkit

Tools for **dual subtitles**: overlay a second language on videos that already have one. Shift and combine `.vtt` files, then embed subtitles into videos — either burned in (top- or bottom-positioned) or as a fast soft track.

## Project layout

```
subtitle_toolkit/     # core library
  vtt.py              #   shift / combine VTT files
  ass.py              #   VTT -> styled ASS conversion (top/bottom positioning)
  burn.py             #   FFmpeg burn-in (re-encode) and soft-sub mux (no re-encode)
  matching.py         #   episode-number matching for batch mode
  ffmpeg.py           #   FFmpeg discovery
  cli.py              #   unified command-line interface
  gui.py              #   Tkinter desktop GUI
tests/                # pytest suite (no FFmpeg required)
```

## Installation

Requires Python 3.9+ and, for video operations, [FFmpeg](https://ffmpeg.org/download.html) (on `PATH`, or set `SUBTITLE_TOOLKIT_FFMPEG` to the executable's full path).

```sh
pip install -e .          # installs the `subtitle-toolkit` command
# or just install the one dependency and run from the repo:
pip install webvtt-py
```

## Usage

All commands work as `subtitle-toolkit <cmd>` (if installed) or `python -m subtitle_toolkit <cmd>` (from the repo).

### Desktop GUI

```sh
python -m subtitle_toolkit.gui
```

### Shift subtitle timings

```sh
python -m subtitle_toolkit shift input.vtt output.vtt 2.5
```

### Combine two subtitle files

```sh
python -m subtitle_toolkit combine episode1.vtt episode2.vtt output.vtt 1800
```

(Appends `episode2.vtt` after `episode1.vtt`, where episode 1 is 1800 seconds long.)

### Burn subtitles into a video (re-encodes)

```sh
python -m subtitle_toolkit burn video.mp4 subtitles.vtt output.mp4 --offset 1.5 --position top
```

`--position top` (default) places subtitles at the top of the frame so they coexist with subs already burned into the bottom.

### Mux subtitles as a soft track (fast, no re-encode)

```sh
python -m subtitle_toolkit mux video.mp4 subtitles.vtt output.mp4 --language jpn
```

### Batch mode

Pass directories instead of files; videos and subtitles are matched by episode number (`S01E05`, `ep5`, trailing numbers — resolution tokens like `1080p` are ignored):

```sh
python -m subtitle_toolkit burn videos/ subs/ output/ --debug
```

`--debug` processes only the first minute of each video.

The legacy entry points (`subtitle_script.py`, `vtt_adjuster.py`, `subtitle_gui.py`) still work and forward to the new CLI.

## Development

```sh
pip install -e .[dev]
python -m pytest
```

---

## Roadmap

### Done
✅ Core library refactor (`subtitle_toolkit` package) with tests
✅ Soft-subtitle muxing (no re-encode)
✅ Desktop GUI (threaded, direct library calls)

### Next: Web studio
🔲 Browser-based dual-subtitle editor: open a local video (no upload), preview two subtitle tracks live, adjust offsets with instant feedback, export VTT/SRT/ASS
🔲 Subtitle search: OpenSubtitles API (hash-based matching), Jimaku for anime
🔲 yt-dlp integration for platforms that expose subtitle tracks

### Later
🚀 Tauri desktop app wrapping the web studio, bundling FFmpeg for local burn-in
🚀 Whisper transcription for content with no existing subtitles
🚀 AI translation of subtitle tracks
🚀 Timeline editor with waveform-based sync alignment

## Contributing

Contributions are welcome! Please open issues or pull requests.

## License

MIT License
