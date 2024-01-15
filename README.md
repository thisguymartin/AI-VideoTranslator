# AI-VideoTranslator

## Objective
Develop a versatile tool for automatic subtitle generation from video audio, translating these subtitles into multiple languages, and embedding them back into the video. This user-friendly tool will leverage AI for accurate transcription and translation.

## Installation

To get started with this project, clone the repository and install the required packages.

### Cloning the Repository
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### Setting Up the Environment with PIP
It's recommended to use a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Installing Dependencies
Install the required packages using:
```bash
pip install -r requirements.txt
```

### Setting Up a Conda Environment Conda
Create and activate a Conda environment:
```bash
conda create --name myenv python=3.8
conda activate myenv
```
Replace `myenv` with your desired environment name and adjust the Python version as needed.

### Installing Dependencies
Install the required packages defined in [`environment.yml`](command:_github.copilot.openRelativePath?%5B%22environment.yml%22%5D "environment.yml"):
```bash
conda env update --file environment.yml
```

### Installing FFmpeg
FFmpeg is a free and open-source software project consisting of a large suite of libraries and programs for handling video, audio, and other multimedia files and streams. This project uses FFmpeg for audio extraction and video processing.

You can install FFmpeg on your system using the following commands:

#### For Ubuntu:
```bash
sudo apt update
sudo apt install ffmpeg
```

#### For MacOS:
```bash
brew install ffmpeg
```

#### For Windows:
You can download FFmpeg from the [official FFmpeg website](https://ffmpeg.org/download.html). Extract the downloaded zip file. Add the bin folder from the extracted file to the System Environment Variable PATH.

## Usage

Run the application using:
```bash
python main.py
```

### CLI Commands
- **Extract Audio from Video and Upload to AWS for Transcription**:
  ```bash
  python main.py video extract-audio-aws --input INPUT_PATH --output OUTPUT_PATH --s3 S3_BUCKET_NAME
  ```
  Replace `INPUT_PATH` and `OUTPUT_PATH` with your video and desired output file paths. Replace `S3_BUCKET_NAME` with the name of your S3 bucket.

  For example:
  ```bash
  python main.py video extract-audio-aws --input ~/Downloads/output.mp4 --output ~/Downloads/ --s3 anakin.test.1171
  ```