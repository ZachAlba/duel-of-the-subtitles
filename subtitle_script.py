import webvtt
import subprocess
import os
from datetime import timedelta
import glob
import re

# FFmpeg paths
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

def create_ass_header():
    """Create ASS subtitle file header with styling for top-positioned English subtitles"""
    return """[Script Info]
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TopSubs,Arial,45,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,2,1,8,10,10,25,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def timedelta_to_ass_time(td):
    """Convert timedelta to ASS format time"""
    total_seconds = td.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    centiseconds = int((total_seconds * 100) % 100)
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"

def convert_vtt_to_ass(vtt_path: str, output_ass_path: str, time_offset: float = 0):
    """Convert VTT subtitles to ASS format with top positioning"""
    print(f"Converting {vtt_path} to ASS format...")
    print(f"Applying time offset of {time_offset} seconds")
    
    vtt = webvtt.read(vtt_path)
    
    with open(output_ass_path, 'w', encoding='utf-8') as f:
        f.write(create_ass_header())
        
        for caption in vtt:
            start = timedelta(seconds=caption.start_in_seconds + time_offset)
            end = timedelta(seconds=caption.end_in_seconds + time_offset)
            
            start_str = timedelta_to_ass_time(start)
            end_str = timedelta_to_ass_time(end)
            
            text = caption.text.replace('\n', '\\N')
            f.write(f"Dialogue: 0,{start_str},{end_str},TopSubs,,0,0,0,,{text}\n")

def process_video(video_path: str, vtt_path: str, output_path: str, debug=False, time_offset=0):
    """Process a single video file"""
    try:
        print(f"\nProcessing video: {video_path}")
        print(f"With subtitles: {vtt_path}")
        print(f"Output to: {output_path}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create temporary ASS file
        temp_ass = f"temp_subtitles_{os.path.basename(video_path)}.ass"
        convert_vtt_to_ass(vtt_path, temp_ass, time_offset)
        
        combine_cmd = [
            FFMPEG_PATH,
            '-i', video_path,
            '-vf', f"ass={temp_ass}",
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-crf', '23',
            '-c:a', 'copy',
            '-movflags', '+faststart',
            '-threads', 'auto'
        ]
        
        if debug:
            print("Debug mode: Processing first minute only")
            combine_cmd.extend(['-t', '60'])
            output_path = output_path.replace('.mp4', '_debug.mp4')
        
        combine_cmd.extend(['-y', output_path])
        
        print("Running FFmpeg command...")
        
        process = subprocess.Popen(
            combine_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            if output and 'frame=' in output:
                print(output.strip())
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, combine_cmd)
        
        if os.path.exists(temp_ass):
            os.remove(temp_ass)
        
        print(f"Successfully processed: {output_path}\n")
        return True
        
    except Exception as e:
        print(f"Error processing {video_path}: {str(e)}")
        if os.path.exists(temp_ass):
            os.remove(temp_ass)
        return False

def extract_episode_number(filename):
    """Extract episode number from filename"""
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else 0

def find_matching_files(video_path, sub_path):
    """Find matching video and subtitle files"""
    # Handle both file and directory inputs
    if os.path.isfile(video_path) and os.path.isfile(sub_path):
        # Single file mode
        return [(video_path, sub_path)]
    
    # Directory mode
    video_files = glob.glob(os.path.join(video_path, "*.mp4"))
    sub_files = glob.glob(os.path.join(sub_path, "*.vtt"))
    
    video_files.sort(key=lambda x: extract_episode_number(os.path.basename(x)))
    sub_files.sort(key=lambda x: extract_episode_number(os.path.basename(x)))
    
    matches = []
    for video in video_files:
        video_num = extract_episode_number(os.path.basename(video))
        matching_sub = next(
            (sub for sub in sub_files 
             if extract_episode_number(os.path.basename(sub)) == video_num),
            None
        )
        if matching_sub:
            matches.append((video, matching_sub))
        else:
            print(f"Warning: No matching subtitle found for {video}")
    
    return matches

def process_files(video_path, sub_path, output_path, debug=False, time_offset=0):
    """Process video and subtitle files"""
    # Find all matching pairs of files
    file_pairs = find_matching_files(video_path, sub_path)
    
    if not file_pairs:
        print("No matching video and subtitle pairs found!")
        return
    
    print(f"Found {len(file_pairs)} video/subtitle pairs to process")
    
    successful = 0
    failed = 0
    
    for video, sub in file_pairs:
        # Determine output filename
        if os.path.isfile(output_path) and len(file_pairs) == 1:
            # Single file mode - use output_path as is
            out_file = output_path
        else:
            # Batch mode - create numbered output files
            episode_num = extract_episode_number(os.path.basename(video))
            out_file = os.path.join(output_path, f"ep{episode_num}.mp4")
        
        if process_video(video, sub, out_file, debug, time_offset):
            successful += 1
        else:
            failed += 1
    
    print(f"\nProcessing complete!")
    print(f"Successfully processed: {successful}")
    print(f"Failed: {failed}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Add English subtitles to video(s)')
    parser.add_argument('video_path', help='Video file or directory')
    parser.add_argument('sub_path', help='Subtitle file or directory')
    parser.add_argument('output_path', help='Output file or directory')
    parser.add_argument('--debug', action='store_true', help='Process only first minute for testing')
    parser.add_argument('--offset', type=float, default=0, help='Time offset for subtitles in seconds')
    
    args = parser.parse_args()
    
    try:
        process_files(args.video_path, args.sub_path, args.output_path, args.debug, args.offset)
    except Exception as e:
        print(f"Error: {e}")
        import sys
        sys.exit(1)