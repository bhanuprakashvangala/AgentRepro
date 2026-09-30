# Audio Transcription Tool

This is a command-line tool that transcribes speech from audio files into text. It uses the `speech_recognition` library with the `PocketSphinx` engine to perform transcription entirely offline.

## Features

- **Offline Transcription**: No internet connection or API keys are required.
- **Noise Filtering**: Includes a simple step to adjust for ambient noise in the audio file.
- **File Support**: Natively supports `.wav` files. Can also handle `.mp3` files if `ffmpeg` is installed.
- **Bulk Processing**: Can process multiple audio files in a single command.
- **Reproducible Demo**: A `--demo` flag automatically downloads and transcribes a sample NASA audio file to verify functionality.

## ⚠️ Important Installation Notes

This tool is designed to be as self-contained as possible, but has two potential system-level dependencies:

1.  **PocketSphinx**: On some systems (especially Linux and macOS), you may need to install development tools for the `pocketsphinx` Python package to compile correctly. This might include `swig` or other audio libraries. On Windows, it typically installs without issue.
    - Example on Debian/Ubuntu: `sudo apt-get install -y swig libpulse-dev`

2.  **MP3 Support (Optional)**: To transcribe `.mp3` files, this tool uses the `pydub` library, which requires **`ffmpeg`**. You must install `ffmpeg` separately and ensure it is available in your system's PATH.

## Usage

1.  **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **(Recommended) Run the Demo:**
    This command will download a sample `.wav` file and transcribe it. It's the best way to confirm your setup is working.
    ```bash
    python transcriber.py --demo
    ```

4.  **Transcribe Your Own Files:**
    Provide the path to one or more audio files.
    ```bash
    # Transcribe a single WAV file
    python transcriber.py my_audio.wav

    # Transcribe multiple files at once
    python transcriber.py recording1.wav recording2.mp3
    ```

## Output

For each audio file processed (e.g., `my_audio.wav`), a corresponding text file (`my_audio.txt`) will be created in the same directory containing the transcribed text.
