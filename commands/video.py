import typer
from lib.aws import process_audio_file_with_aws
from lib.ffmpeg import extract_wav_from_video

app = typer.Typer()

@app.command("extract-audio")
def extract_audio(input: str, output: str):
    """Extract audio from video and save to output file"""
    try:
        extract_wav_from_video(input, output)
    except Exception as e:
        print("extract_audio error: ", e)
        raise typer.Exit(code=1)
         
@app.command("extract-audio-gcloud")
def extract_audio_gcloud(input: str, output: str):
    """Extract audio from video and upload to Google Cloud for transcription"""
    try:
        extract_wav_from_video(input, output)
        # missing google cloud code
    except Exception as e:
        print("extract_audio_gcloud error: ", e)
        raise typer.Exit(code=1)
     
@app.command("extract-audio-aws")
def extract_audio_aws(input: str, output: str, bucket: str):
    """Extract audio from video and upload to AWS for transcription"""
    try: 
        extract_wav_from_video(input, output)
        process_audio_file_with_aws(output, bucket)
    except Exception as e:
        print("extract_audio_aws error: ", e)
        raise typer.Exit(code=1)
  