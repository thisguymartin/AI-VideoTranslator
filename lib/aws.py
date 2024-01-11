# https://docs.aws.amazon.com/transcribe/
import json
import boto3
import time
import urllib.parse
import os
from rich import print

def upload_file_to_s3(local_file_path: str, bucket_name: str, s3_file_name: str):
    s3_client = boto3.client('s3')
    file = s3_client.upload_file(local_file_path, bucket_name, s3_file_name)
    return f's3://{bucket_name}/{s3_file_name}'

def transcribe_audio(file_uri, transcribe_client):    
    job_name = "TranscriptionJob_" + str(int(time.time()))
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': file_uri},
        MediaFormat='wav', 
        LanguageCode='en-US'
    )

    while True:
        status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            break
        print("Not ready yet...")
        time.sleep(5)

    print("Transcription finished")
    return status['TranscriptionJob']['Transcript']['TranscriptFileUri']

def process_audio_file_with_aws(local_file_path: str, bucket_name: str):
    print("[yellow]Processing audio file with AWS...[/yellow]")
    print("[yellow]local_file_path: [/yellow]", local_file_path)
    print("[yellow]bucket_name: [/yellow]", bucket_name)
    
    s3_file_name = os.path.basename(local_file_path)  # Name for the file in S3

    # Upload the local file to S3
    s3_file_name_str = str(s3_file_name)
    bucket_name_str = str(bucket_name)
    file_uri = upload_file_to_s3(local_file_path, bucket_name_str, s3_file_name_str)
    print(f"[green]File uploaded to S3: {file_uri}[/green]")

    transcribe_client = boto3.client('transcribe')
    transcript_uri = transcribe_audio(file_uri, transcribe_client)
    
    # # Fetch and print the transcript
    transcript = urllib.request.urlopen(transcript_uri).read().decode('utf-8')
    print("[green]Transcript:", transcript)
    
    # Open the file with write permission
    data = json.loads(transcript)
    with open('transcripts.json', 'w') as file:
        file.write(json.dumps(data, indent=4))
        print("[green] Transcripts saved to transcripts.json [/green]")
