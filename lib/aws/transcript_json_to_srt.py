def convert_to_srt(transcript_data):
    """Convert AWS Transcribe JSON to SRT format."""
    srt_string = ''
    counter = 1

    for item in transcript_data['results']['items']:
        if item['type'] == 'pronunciation':
            start_time = float(item['start_time'])
            end_time = float(item['end_time'])
            content = item['alternatives'][0]['content']

            # Format the timestamps
            start_timestamp = '{:02}:{:02}:{:02},{:03}'.format(
                int(start_time // 3600), int(start_time % 3600 // 60),
                int(start_time % 60), int(start_time % 1 * 1000))
            end_timestamp = '{:02}:{:02}:{:02},{:03}'.format(
                int(end_time // 3600), int(end_time % 3600 // 60),
                int(end_time % 60), int(end_time % 1 * 1000))

            # Append to the SRT string
            srt_string += f'{counter}\n{start_timestamp} --> {end_timestamp}\n{content}\n\n'
            counter += 1

    return srt_string
