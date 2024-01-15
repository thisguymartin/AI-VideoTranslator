import typer
from commands import video
from commands import audio

app = typer.Typer()

# Add the subcommands from the other files to the main app.
app.add_typer(video.app, name="video")
app.add_typer(audio.app, name="audio")

if __name__ == "__main__":
    app()