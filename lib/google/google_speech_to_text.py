# https://pypi.org/project/google-cloud-speech/

import json
from google.cloud import speech_v1p1beta1 as speech

def google_speech_to_text(inputFile: str):
  client = speech.SpeechClient()
  speech_file = inputFile
  
  first_lang = "en-US"
  second_lang = "es"

  with open(speech_file, "rb") as audio_file:
      content = audio_file.read()

  audio = speech.RecognitionAudio(content=content)

  config = speech.RecognitionConfig(
      encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
      sample_rate_hertz=44100,
      audio_channel_count=2,
      language_code=first_lang,
      alternative_language_codes=[second_lang],
  )

  print("Waiting for operation to complete...")
  response = client.recognize(config=config, audio=audio)
  print("Operation complete", response)
  data = json.loads(response)
  with open('transcripts.json', 'w') as file:
    file.write(response)
    print("[green] Transcripts saved to transcripts.json [/green]")



  print(response)
  return response.results


def generate_srt(transcript_text, output_srt_file):
    # Split the transcript into sentences or segments as needed
    transcript_segments = transcript_text.split("\n")  # Assuming each line is a segment

    with open(output_srt_file, "w") as srt_file:
        sequence_number = 1  # Initialize sequence number

        # Iterate through transcript segments
        for segment in transcript_segments:
            if segment.strip():  # Check if the segment is not empty
                # Define timestamp range (in SRT format)
                timestamp_range = f"{sequence_number}\n00:00:00,000 --> 00:00:10,000"  # You can adjust the time range as needed

                # Write sequence number, timestamp, and segment text to SRT file
                srt_file.write(timestamp_range + "\n")
                srt_file.write(segment.strip() + "\n\n")

                sequence_number += 1  # Increment sequence number

# Example usage:
transcript_text = """
This is the first segment.
This is the second segment.
This is the third segment.
"""

output_srt_file = "output.srt"

generate_srt(transcript_text, output_srt_file)