import json

def load_json(file_path):
    """Load the JSON file from the specified path."""
    with open(file_path, 'r') as file:
        return json.load(file)

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

def save_srt(srt_content, output_path):
    """Save the SRT content to a file."""
    with open(output_path, 'w') as file:
        file.write(srt_content)

def main():
    # Path to your JSON transcript file
    json_file_path = 'transcripts.json'

    # Path where the SRT file will be saved
    output_srt_path = 'output_file.srt'

    # Load the JSON transcript
    transcript = load_json(json_file_path)

    # Convert the transcript to SRT format
    srt_content = convert_to_srt(transcript)

    # Save the SRT content to a file
    save_srt(srt_content, output_srt_path)
    print(f'SRT file saved to {output_srt_path}')

if __name__ == '__main__':
    main()
