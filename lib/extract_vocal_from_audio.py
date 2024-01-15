import subprocess

# https://github.com/deezer/spleeter

def extract_vocal_from_audio(output: str):
    command = "spleeter separate -p spleeter:2stems -o output {0}".format(output)
    subprocess.run(command, shell=True)
