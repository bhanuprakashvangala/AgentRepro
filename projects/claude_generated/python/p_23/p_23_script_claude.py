#!/usr/bin/env python3
"""
Audio Transcription Tool with Speech Recognition
Supports multiple audio formats with noise filtering
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import speech_recognition as sr
from pydub import AudioSegment
from pydub.effects import normalize
import noisereduce as nr
import numpy as np


class AudioTranscriber:
    """Audio transcription tool with noise filtering support"""

    def __init__(self, language='en-US'):
        self.recognizer = sr.Recognizer()
        self.language = language
        # Adjust recognizer settings for better accuracy
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8

    def convert_to_wav(self, audio_path):
        """Convert audio file to WAV format if needed"""
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # If already WAV, return the path
        if audio_path.suffix.lower() == '.wav':
            return str(audio_path)

        print(f"Converting {audio_path.name} to WAV format...")

        # Load audio file based on format
        try:
            if audio_path.suffix.lower() == '.mp3':
                audio = AudioSegment.from_mp3(str(audio_path))
            elif audio_path.suffix.lower() == '.ogg':
                audio = AudioSegment.from_ogg(str(audio_path))
            elif audio_path.suffix.lower() == '.flac':
                audio = AudioSegment.from_file(str(audio_path), "flac")
            elif audio_path.suffix.lower() in ['.m4a', '.aac']:
                audio = AudioSegment.from_file(str(audio_path), "m4a")
            else:
                # Try generic loader
                audio = AudioSegment.from_file(str(audio_path))
        except Exception as e:
            raise ValueError(f"Unsupported audio format or corrupted file: {e}")

        # Convert to WAV
        wav_path = audio_path.with_suffix('.wav')
        audio.export(str(wav_path), format='wav')
        print(f"Converted to: {wav_path.name}")

        return str(wav_path)

    def reduce_noise(self, audio_path, output_path=None):
        """Apply noise reduction to audio file"""
        print("Applying noise reduction...")

        # Load audio file
        audio = AudioSegment.from_wav(audio_path)

        # Normalize audio
        audio = normalize(audio)

        # Convert to numpy array for noise reduction
        samples = np.array(audio.get_array_of_samples())
        sample_rate = audio.frame_rate

        # Apply noise reduction
        reduced_noise = nr.reduce_noise(
            y=samples.astype(np.float32),
            sr=sample_rate,
            stationary=True,
            prop_decrease=0.8
        )

        # Convert back to AudioSegment
        reduced_audio = AudioSegment(
            reduced_noise.astype(np.int16).tobytes(),
            frame_rate=sample_rate,
            sample_width=audio.sample_width,
            channels=audio.channels
        )

        # Save processed audio
        if output_path is None:
            output_path = audio_path.replace('.wav', '_processed.wav')

        reduced_audio.export(output_path, format='wav')
        print(f"Noise-reduced audio saved to: {output_path}")

        return output_path

    def transcribe(self, audio_path, apply_noise_reduction=True):
        """Transcribe audio file to text"""
        print(f"\nTranscribing: {audio_path}")
        print("-" * 50)

        # Convert to WAV if needed
        wav_path = self.convert_to_wav(audio_path)

        # Apply noise reduction if requested
        if apply_noise_reduction:
            processed_path = self.reduce_noise(wav_path)
        else:
            processed_path = wav_path

        # Load audio file
        with sr.AudioFile(processed_path) as source:
            print("Loading audio data...")
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            audio_data = self.recognizer.record(source)

        # Perform transcription
        print(f"Transcribing audio (language: {self.language})...")
        transcript = ""

        try:
            # Try Google Speech Recognition (free)
            transcript = self.recognizer.recognize_google(
                audio_data,
                language=self.language,
                show_all=False
            )
            print("\n✓ Transcription successful!")

        except sr.UnknownValueError:
            print("\n✗ Could not understand audio")
            transcript = "[Could not transcribe audio - speech unintelligible]"

        except sr.RequestError as e:
            print(f"\n✗ API error: {e}")
            transcript = f"[Transcription failed: {e}]"

        # Clean up temporary processed file
        if apply_noise_reduction and processed_path != wav_path:
            try:
                os.remove(processed_path)
            except:
                pass

        return transcript

    def transcribe_long_audio(self, audio_path, chunk_length_ms=60000, apply_noise_reduction=True):
        """Transcribe long audio files by splitting into chunks"""
        print(f"\nTranscribing long audio: {audio_path}")
        print("-" * 50)

        # Convert to WAV if needed
        wav_path = self.convert_to_wav(audio_path)

        # Apply noise reduction if requested
        if apply_noise_reduction:
            processed_path = self.reduce_noise(wav_path)
        else:
            processed_path = wav_path

        # Load audio
        audio = AudioSegment.from_wav(processed_path)
        duration_ms = len(audio)

        print(f"Audio duration: {duration_ms / 1000:.2f} seconds")
        print(f"Splitting into {chunk_length_ms / 1000}s chunks...")

        # Split audio into chunks
        chunks = []
        for i in range(0, duration_ms, chunk_length_ms):
            chunk = audio[i:i + chunk_length_ms]
            chunks.append(chunk)

        print(f"Processing {len(chunks)} chunks...")

        # Transcribe each chunk
        full_transcript = []
        for idx, chunk in enumerate(chunks, 1):
            print(f"\nChunk {idx}/{len(chunks)}...")

            # Save chunk temporarily
            chunk_path = f"temp_chunk_{idx}.wav"
            chunk.export(chunk_path, format='wav')

            # Transcribe chunk
            with sr.AudioFile(chunk_path) as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)

            try:
                text = self.recognizer.recognize_google(
                    audio_data,
                    language=self.language
                )
                full_transcript.append(text)
                print(f"✓ Transcribed: {text[:50]}...")

            except sr.UnknownValueError:
                print("✗ Could not understand this chunk")
                full_transcript.append("[unintelligible]")

            except sr.RequestError as e:
                print(f"✗ API error: {e}")
                full_transcript.append(f"[error]")

            # Clean up chunk file
            try:
                os.remove(chunk_path)
            except:
                pass

        # Clean up processed file
        if apply_noise_reduction and processed_path != wav_path:
            try:
                os.remove(processed_path)
            except:
                pass

        return " ".join(full_transcript)

    def save_transcript(self, transcript, output_path=None, audio_path=None):
        """Save transcript to text file"""
        if output_path is None:
            if audio_path:
                audio_name = Path(audio_path).stem
                output_path = f"{audio_name}_transcript.txt"
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"transcript_{timestamp}.txt"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 50 + "\n")
            f.write("AUDIO TRANSCRIPTION\n")
            f.write("=" * 50 + "\n\n")

            if audio_path:
                f.write(f"Source: {audio_path}\n")

            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Language: {self.language}\n")
            f.write("\n" + "-" * 50 + "\n\n")
            f.write(transcript)
            f.write("\n\n" + "=" * 50 + "\n")

        print(f"\n✓ Transcript saved to: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(
        description='Audio Transcription Tool with Speech Recognition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s audio.wav
  %(prog)s audio.mp3 -o transcript.txt
  %(prog)s audio.wav --no-noise-reduction
  %(prog)s long_audio.mp3 --long --chunk-size 30
  %(prog)s audio.wav --language es-ES
        """
    )

    parser.add_argument(
        'audio_file',
        help='Path to audio file (WAV, MP3, OGG, FLAC, M4A)'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output text file path (default: auto-generated)',
        default=None
    )

    parser.add_argument(
        '--no-noise-reduction',
        action='store_true',
        help='Disable noise reduction processing'
    )

    parser.add_argument(
        '--long',
        action='store_true',
        help='Process long audio files (splits into chunks)'
    )

    parser.add_argument(
        '--chunk-size',
        type=int,
        default=60,
        help='Chunk size in seconds for long audio (default: 60)'
    )

    parser.add_argument(
        '--language',
        default='en-US',
        help='Language code (default: en-US, examples: es-ES, fr-FR, de-DE)'
    )

    args = parser.parse_args()

    # Validate audio file exists
    if not os.path.exists(args.audio_file):
        print(f"Error: Audio file not found: {args.audio_file}")
        sys.exit(1)

    # Create transcriber
    transcriber = AudioTranscriber(language=args.language)

    # Transcribe
    try:
        apply_noise_reduction = not args.no_noise_reduction

        if args.long:
            transcript = transcriber.transcribe_long_audio(
                args.audio_file,
                chunk_length_ms=args.chunk_size * 1000,
                apply_noise_reduction=apply_noise_reduction
            )
        else:
            transcript = transcriber.transcribe(
                args.audio_file,
                apply_noise_reduction=apply_noise_reduction
            )

        # Display transcript
        print("\n" + "=" * 50)
        print("TRANSCRIPT:")
        print("=" * 50)
        print(transcript)
        print("=" * 50)

        # Save to file
        output_path = transcriber.save_transcript(
            transcript,
            output_path=args.output,
            audio_path=args.audio_file
        )

    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
