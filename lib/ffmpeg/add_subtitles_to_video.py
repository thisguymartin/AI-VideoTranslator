import subprocess
import ffmpeg
from rich import print

def add_subtitles_to_video(input_video, input_subtitle, outputDir):
    try:
        output_video = outputDir + "video_subtitle.mp4" 
        command = f"ffmpeg -i {input_video} -i {input_subtitle} -c copy -scodec mov_text {output_video} -y"
        subprocess.run(command, shell=True, check=True)
        print("Subtitles added successfully.")
    except ffmpeg.Error as e:
        print("[bold red] ❌ add_subtitles_to_video error: [/bold red]", e)
