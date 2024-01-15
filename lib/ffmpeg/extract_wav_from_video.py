import os
import ffmpeg
from rich import print

def extract_wav_from_video(input: str, output: str):
  try:
    """
    Extract audio with best quality from video and save to output file
    """
    print("Extracting audio with best quality from video...")
    
    input_filename = os.path.basename(input)
    output_filename = os.path.splitext(input_filename)[0] + ".wav"
    output_path = os.path.join(output, output_filename)

    stream = ffmpeg.input(input)
    stream = ffmpeg.output(stream, output_path, audio_bitrate=0, map='a')
    ffmpeg.run(stream)
    
    return output_path
  except ffmpeg.Error as e:
    print("[bold red]extract_wav_from_video error: [/bold red]", e.stderr)
    raise e