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
Install the required packages defined in `environment.yml`:
```bash
conda env update --file environment.yml
```


## Usage

Run the application using:
```bash
python main.py
```

### CLI Commands
- **Extract Audio from Video**:
  ```bash
  python main.py video extract-audio --input INPUT_PATH --output OUTPUT_PATH
  ```
  Replace `INPUT_PATH` and `OUTPUT_PATH` with your video and desired output file paths.
