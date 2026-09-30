import speech_recognition as sr
import os
import argparse
import requests
from pydub import AudioSegment

# --- Configuration ---
# A public domain, clear speech WAV file for the demo
DEMO_AUDIO_URL = "https://www.nasa.gov/wp-content/uploads/2015/01/147609main_skylab_descent.wav"
DEMO_FILENAME = "nasa_skylab.wav"

def download_sample_audio(url, filename):
    """Downloads a sample audio file for the demo if it doesn't exist."""
    if os.path.exists(filename):
        print(f"Sample audio '{filename}' already exists.")
        return
    
    print(f"Downloading sample audio for demo: {filename}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading sample audio: {e}")
        exit()

def convert_mp3_to_wav(mp3_path):
    """Converts an MP3 file to a temporary WAV file for processing."""
    try:
        wav_path = mp3_path + ".wav"
        print(f"Converting {mp3_path} to {wav_path}...")
        sound = AudioSegment.from_mp3(mp3_path)
        sound.export(wav_path, format="wav")
        return wav_path, True
    except Exception as e:
        print(f"\nError converting MP3: {e}")
        print("Please ensure FFmpeg is installed and accessible in your system's PATH.")
        return None, False

def transcribe_audio(audio_path):
    """Transcribes a given audio file using the PocketSphinx offline engine."""
    print(f"\nProcessing file: {audio_path}")
    recognizer = sr.Recognizer()
    is_temp_wav = False

    # Handle MP3 conversion
    if audio_path.lower().endswith(".mp3"):
        audio_path, is_temp_wav = convert_mp3_to_wav(audio_path)
        if not audio_path:
            return None

    if not audio_path.lower().endswith(".wav"):
        print(f"Error: Unsupported file format for '{audio_path}'. Please use WAV or MP3.")
        return None

    with sr.AudioFile(audio_path) as source:
        # Listen for the data (load audio to memory)
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Reading audio data...")
        audio_data = recognizer.record(source)

    # Recognize speech using Sphinx (offline)
    transcript = ""
    try:
        print("Transcribing using PocketSphinx (offline)...")
        transcript = recognizer.recognize_sphinx(audio_data)
        print("Transcription successful.")
    except sr.UnknownValueError:
        print("PocketSphinx could not understand the audio.")
        transcript = "[Transcription failed: audio could not be understood]"
    except sr.RequestError as e:
        print(f"Could not request results from PocketSphinx service; {e}")
        transcript = f"[Transcription failed: {e}]"
    finally:
        # Clean up temporary WAV file if one was created
        if is_temp_wav:
            os.remove(audio_path)

    return transcript

def export_to_text_file(transcript, original_path):
    """Saves the transcript to a text file."""
    base_name = os.path.splitext(original_path)[0]
    output_filename = base_name + ".txt"
    print(f"Saving transcript to: {output_filename}")
    with open(output_filename, 'w') as f:
        f.write(transcript)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio files using offline speech recognition.")
    parser.add_argument("files", nargs='*', help="Path(s) to audio files (WAV or MP3) to transcribe.")
    parser.add_argument("--demo", action="store_true", help="Run a demo with a sample NASA audio file.")
    args = parser.parse_args()

    if args.demo:
        download_sample_audio(DEMO_AUDIO_URL, DEMO_FILENAME)
        files_to_process = [DEMO_FILENAME]
    elif args.files:
        files_to_process = args.files
    else:
        parser.print_help()
        exit()

    for file_path in files_to_process:
        if not os.path.exists(file_path):
            print(f"Error: File not found at '{file_path}'. Skipping.")
            continue
        
        transcribed_text = transcribe_audio(file_path)
        if transcribed_text:
            export_to_text_file(transcribed_text, file_path)
    
    print("\n--- Process Complete ---")
