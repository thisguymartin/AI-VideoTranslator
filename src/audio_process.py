from moviepy.editor import *


def audio_process(video_path, audio_path):
    # Load your video file
    video = VideoFileClip(video_path)

    # Extract the audio
    audio = video.audio

    # Write the audio to a file (e.g., mp3)
    audio.write_audiofile(audio_path)
