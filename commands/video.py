# users.py
import typer
from moviepy.editor import *
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer()

@app.command("extract-audio")
def create_user(input: str, output: str):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Processing...")
        video = VideoFileClip(input, verbose=False)
        audio = video.audio
        
        file_name = os.path.basename(output)

        audio.write_audiofile(file_name, verbose=False)
        print("Done extracting audio from video.")


