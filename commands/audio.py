import typer
from lib.ffmpeg.extract_wav_from_video import extract_wav_from_video
from rich import print


app = typer.Typer()

@app.command("extract-audio")
def extract_audio(input: str, output: str):
    """Extract audio from video and save to output file"""
    try:
      wav_file = extract_wav_from_video(input, output)
      print("[bold green]Extract Audio: [/bold green] 🥳 🎉", wav_file)   
    except Exception as e:
        print("[bold red] ❌ extract_audio error: [/bold red]", e)
        raise typer.Exit(code=1)    