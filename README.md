# AI-VideoTranslator

## Objective
The AI-VideoTranslator is a powerful command-line tool designed to automate the process of subtitle generation from video audio, translating these subtitles into multiple languages, and embedding them back into the video. This tool leverages the power of AI for accurate transcription and translation, making it an invaluable resource for content creators, translators, and anyone in need of automated subtitle generation and translation.

## Prerequisites
This tool uses [FFmpeg](https://ffmpeg.org/), a free and open-source software project consisting of a vast software suite of libraries and programs for handling video, audio, and other multimedia files and streams. Make sure you have FFmpeg installed on your system. You can download it from the [official FFmpeg website](https://ffmpeg.org/download.html).

## Installation

### Cloning the Repository
To get started with the AI-VideoTranslator, you first need to clone the repository to your local machine. You can do this by running the following command in your terminal:

```bash
git clone git@github.com:thisguymartin/AI-VideoTranslator.git
cd AI-VideoTranslator
```

### Setting Up the Environment with PIP
We recommend using a virtual environment to avoid any package conflicts. You can set up a virtual environment using the venv module in Python:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

This will create a new virtual environment in a folder named venv and activate it.

### Installing Dependencies
Once you have your virtual environment set up and activated, you can install the required packages using pip:

```bash
pip install -r requirements.txt
```

This command reads the requirements.txt file and installs all the necessary packages listed in it.

### Setting Up a Conda Environment
If you prefer using Conda, you can create and activate a Conda environment:

```bash
conda create --name myenv python=3.8
conda activate myenv
```

Replace `myenv` with your desired environment name and adjust the Python version as needed.

### Installing Dependencies with Conda
Install the required packages defined in `environment.yml`:

```bash
conda env update --file environment.yml
```

## Usage

### Using AWS Transcribe to Generate Subtitles
To use AWS Transcribe for generating subtitles, you can use the following command:

```bash
python main.py video extract-audio-aws ~/Downloads/output.mp4 ~/Downloads/ anakin.test.1171
```

In this command, `~/Downloads/output.mp4` is the path to your video file, `~/Downloads/` is the directory where you want to save the output, and `anakin.test.1171` is the name of the job that will be created in AWS Transcribe.

### Extracting Audio and Converting to WAV
If you only want to extract the audio from the video and convert it to a WAV file, you can use the following command:

```bash
python main.py video extract-audio ~/Downloads/output.mp4 ~/Downloads/
```

Again, `~/Downloads/output.mp4` is the path to your video file and `~/Downloads/` is the directory where you want to save the output.

## Note
The AI-VideoTranslator is still in active development. Currently, it only supports AWS Transcribe for generating subtitles. However, we are working on adding support for other transcription services in the future.
