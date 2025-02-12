# Make Reel v2

## Description
Make Reel v2 is a Python script that utilizes the Groq API and `ffmpeg` to generate reels or process video content. The script integrates various Python libraries, including `requests`, `random`, `os`, `uuid4`, `subprocess`, and `time`, and leverages `rich` for enhanced console interactions.

## Requirements
Before running the script, ensure that the following dependencies are met:

- Python 3.x installed
- `ffmpeg` installed and added to your system path
- A valid Groq API key
- Required Python packages:
  - `requests`
  - `rich`
  - `groq`
  
You can install the required Python packages using:
```sh
pip install requests rich groq
```

## Installation
1. Clone this repository or download the `make_reelv2.py` script.
2. Install the required Python packages using the command mentioned above.
3. Ensure `ffmpeg` is installed and accessible via the command line.

## Usage
Run the script using the following command:
```sh
python make_reelv2.py
```

## Environment Variables
Make sure you have your Groq API key set up. You can either set it as an environment variable or include it in your script (not recommended for security reasons).

Set the API key in your terminal:
```sh
export GROQ_API_KEY="your_api_key_here"
```
Or on Windows:
```sh
set GROQ_API_KEY="your_api_key_here"
```

## License
This project is provided as-is with no warranty. You are free to modify and distribute it as needed.

## Contribution
Feel free to submit issues or contribute to the project via pull requests.

## Disclaimer
Ensure you comply with Groq API's terms of service when using this script.

