import webvtt
from datetime import timedelta
from decimal import Decimal

def adjust_vtt_times(input_vtt: str, output_vtt: str, shift_seconds: float):
    """Shift all timestamps in a VTT file by a given number of seconds"""
    vtt = webvtt.read(input_vtt)
    
    # Create new VTT file
    with open(output_vtt, 'w', encoding='utf-8') as f:
        f.write('WEBVTT\n\n')
        
        for caption in vtt:
            # Adjust start and end times
            new_start = caption.start_in_seconds + shift_seconds
            new_end = caption.end_in_seconds + shift_seconds
            
            # Convert to VTT format (HH:MM:SS.mmm)
            start_time = format_timestamp(new_start)
            end_time = format_timestamp(new_end)
            
            # Write adjusted caption
            f.write(f'{start_time} --> {end_time}\n')
            f.write(f'{caption.text}\n\n')
    
    print(f"Created adjusted VTT file: {output_vtt}")



def format_timestamp(seconds: float) -> str:
    """Convert seconds to VTT timestamp format while ensuring precision"""
    seconds = Decimal(str(seconds))  # Preserve precision
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)  # Extract exact milliseconds
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

def parse_vtt_time(vtt_timestamp: str) -> float:
    """Convert VTT timestamp (HH:MM:SS.mmm) to precise float seconds."""
    hours, minutes, seconds = vtt_timestamp.split(":")
    secs, millis = seconds.split(".")
    return int(hours) * 3600 + int(minutes) * 60 + int(secs) + int(millis) / 1000

def combine_vtt_files(vtt1_path: str, vtt2_path: str, output_path: str, ep1_duration: float):
    """Combine two VTT files, manually preserving timestamp precision."""
    vtt1 = webvtt.read(vtt1_path)
    vtt2 = webvtt.read(vtt2_path)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('WEBVTT\n\n')

        # Write first episode subtitles
        for caption in vtt1:
            f.write(f'{caption.start} --> {caption.end}\n')
            f.write(f'{caption.text}\n\n')

        # Write second episode subtitles with adjusted times
        for caption in vtt2:
            # Parse original timestamps to precise float values
            original_start = parse_vtt_time(caption.start)
            original_end = parse_vtt_time(caption.end)

            # Apply time shift while preserving milliseconds
            new_start = original_start + ep1_duration
            new_end = original_end + ep1_duration

            # Convert back to VTT timestamp format
            start_time = format_timestamp(new_start)
            end_time = format_timestamp(new_end)

            f.write(f'{start_time} --> {end_time}\n')
            f.write(f'{caption.text}\n\n')

    print(f"Created combined VTT file: {output_path}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Adjust VTT subtitle timings')
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Parser for shifting times
    shift_parser = subparsers.add_parser('shift', help='Shift subtitle times')
    shift_parser.add_argument('input_vtt', help='Input VTT file')
    shift_parser.add_argument('output_vtt', help='Output VTT file')
    shift_parser.add_argument('shift_seconds', type=float, 
                            help='Seconds to shift timestamps (positive to delay, negative to advance)')
    
    # Parser for combining files
    combine_parser = subparsers.add_parser('combine', help='Combine two VTT files')
    combine_parser.add_argument('vtt1', help='First VTT file')
    combine_parser.add_argument('vtt2', help='Second VTT file')
    combine_parser.add_argument('output_vtt', help='Output VTT file')
    combine_parser.add_argument('ep1_duration', type=float, 
                              help='Duration of first episode in seconds')
    
    args = parser.parse_args()
    
    if args.command == 'shift':
        adjust_vtt_times(args.input_vtt, args.output_vtt, args.shift_seconds)
    elif args.command == 'combine':
        combine_vtt_files(args.vtt1, args.vtt2, args.output_vtt, args.ep1_duration)
    else:
        parser.print_help()