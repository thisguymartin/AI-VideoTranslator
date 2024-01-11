import ffmpeg

def extract_wav_from_video(input: str, output: str):
  try:
    print("Extracting audio with best quality from video...")
    stream = ffmpeg.input(input)
    stream = ffmpeg.output(stream, output, audio_bitrate=0, map='a')
    ffmpeg.run(stream)
    print("Done extracting audio with best quality from video.")
  except ffmpeg.Error as e:
    print("extract_wav_from_video error: ", e.stderr)
    raise e