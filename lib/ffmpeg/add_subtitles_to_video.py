import ffmpeg

def add_subtitles_to_video(input_video, input_subtitle, output_video):
    try:
        input_stream = ffmpeg.input(input_video)
        subtitle_stream = ffmpeg.input(input_subtitle)
        
        # Overlay subtitles on the video
        output_stream = ffmpeg.output(input_stream, subtitle_stream, output_video, vcodec='copy', acodec='copy', format='mp4')
        
        ffmpeg.run(output_stream, overwrite_output=True)
        print("Subtitles added successfully.")
    except ffmpeg.Error as e:
        print(f"Error adding subtitles: {e.stderr}")
        