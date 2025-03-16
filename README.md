# Subtitle Processing Toolkit

## Overview

This project provides a set of tools for working with subtitles, including:
- Adjusting subtitle timings in `.vtt` files.
- Combining multiple subtitle files while preserving timing accuracy.
- Embedding subtitles directly into videos using `FFmpeg`.

## Features

- **Adjust VTT Timings**: Shift subtitles forward or backward in time.
- **Merge Subtitles**: Combine subtitles from multiple episodes while maintaining synchronization.
- **Hardcode Subtitles**: Embed subtitles into a video file using `FFmpeg`, supporting batch processing.
- **Time Offset Handling**: Adjust subtitle delays for better synchronization.

## Installation

### Prerequisites

- Python 3.8+
- `ffmpeg` (Ensure it's installed and accessible in your system path)
- Required Python libraries:
  ```sh
  pip install webvtt-py
  ```

## Usage

### Adjust Subtitle Timings
Shift all subtitle timings in a `.vtt` file:

```sh
python vtt_adjuster.py shift input.vtt output.vtt 2.5
```

(Shifts the subtitles forward by 2.5 seconds.)

### Combine Two Subtitle Files
```sh
python vtt_adjuster.py combine episode1.vtt episode2.vtt output.vtt 1800
```
(Combines `episode2.vtt` after `episode1.vtt`, assuming `episode1` is 1800 seconds long.)

### Embed Subtitles into a Video
For a single video:
```sh
python subtitle_script.py video.mp4 subtitles.vtt output.mp4
```

For batch processing (matching videos and subtitles by episode number):
```sh
python subtitle_script.py video_folder/ subtitles_folder/ output_folder/
```

Use `--offset` to fine-tune synchronization.

---

## Roadmap

### Short-Term Goals
✅ Improve subtitle parsing efficiency  
✅ Add subtitle time offsets for better sync control  

### Mid-Term Goals
🔲 **AI-powered Translations**: Integrate OpenAI’s API or Google Translate to automatically translate existing `.vtt` files.  
🔲 **Auto VTT Generation**: Convert AI-generated translations into `.vtt` format with precise timestamps.  
🔲 **Multi-Language Support**: Provide language selection in the command-line tool.  

### Long-Term Goals
🚀 **Web UI for Subtitle Processing**: A user-friendly interface to:
   - Upload videos and subtitles
   - Adjust timings with visual previews
   - Translate and generate subtitles with AI

🚀 **AI-Enhanced Translations**: Instead of simple translations, implement context-aware subtitle adaptation.

🚀 **Real-Time Sync Adjustments**: A UI with a timeline editor for fine-tuning subtitle positions.  

🚀 **Subtitle Styling**: Add dynamic font styling and positioning based on speaker identification.  

🚀 **Automatic Speaker Detection**: Identify speakers and color-code their subtitles.  

---

## Contributing
Contributions are welcome! Please open issues or pull requests for bug fixes or new features.

## License
MIT License

