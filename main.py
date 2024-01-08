import typer
from commands import video

app = typer.Typer()

# Add the subcommands from the other files to the main app.
app.add_typer(video.app, name="video")

if __name__ == "__main__":
    app()