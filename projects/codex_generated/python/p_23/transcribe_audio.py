#!/usr/bin/env python3
"""Batch audio transcription tool using SpeechRecognition with noise filtering."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Iterable, List

import speech_recognition as sr
from pydub import AudioSegment

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".flac", ".aiff", ".aif", ".ogg", ".m4a"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transcribe audio files to text")
    parser.add_argument("--inputs", nargs="+", help="Audio files or directories to transcribe")
    parser.add_argument(
        "--output-dir",
        default="transcripts",
        help="Directory to store transcript text files",
    )
    parser.add_argument(
        "--language",
        default="en-US",
        help="Language code for recognition (default: en-US)",
    )
    parser.add_argument(
        "--ambient-duration",
        type=float,
        default=0.5,
        help="Seconds to sample for ambient noise adjustment (default: 0.5)",
    )
    parser.add_argument(
        "--energy-threshold",
        type=float,
        default=None,
        help="Manually set recognizer energy threshold (skips auto adjustment if provided)",
    )
    parser.add_argument(
        "--recognizer",
        choices=["google", "sphinx"],
        default="google",
        help="Recognition backend (google uses web API, sphinx is offline if installed)",
    )
    parser.add_argument(
        "--chunk-duration",
        type=int,
        default=None,
        help="Optional chunk duration in seconds for long audio (split transcription)",
    )
    return parser.parse_args()


def collect_audio_files(inputs: Iterable[str]) -> List[Path]:
    files: List[Path] = []
    for entry in inputs:
        path = Path(entry)
        if not path.exists():
            print(f"Warning: {path} not found", file=sys.stderr)
            continue
        if path.is_file():
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                files.append(path)
            else:
                print(f"Skipping unsupported file extension: {path}", file=sys.stderr)
        else:
            for child in path.rglob("*"):
                if child.is_file() and child.suffix.lower() in SUPPORTED_EXTENSIONS:
                    files.append(child)
    return sorted(files)


def convert_to_wav(source: Path) -> Path:
    if source.suffix.lower() == ".wav":
        return source
    audio = AudioSegment.from_file(source)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
        temp_path = Path(tmp_file.name)
    audio.export(temp_path, format="wav")
    return temp_path


def transcribe_file(
    path: Path,
    recognizer: sr.Recognizer,
    language: str,
    ambient_duration: float,
    chunk_duration: int | None,
) -> str:
    wav_path = convert_to_wav(path)
    transcripts: List[str] = []
    try:
        with sr.AudioFile(str(wav_path)) as source:
            if ambient_duration > 0:
                recognizer.adjust_for_ambient_noise(source, duration=ambient_duration)

            if chunk_duration and chunk_duration > 0:
                chunk_ms = chunk_duration * 1000
                audio_segment = AudioSegment.from_wav(str(wav_path))
                total_ms = len(audio_segment)
                for start in range(0, total_ms, chunk_ms):
                    end = min(start + chunk_ms, total_ms)
                    chunk = audio_segment[start:end]
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_chunk:
                        tmp_chunk_path = Path(tmp_chunk.name)
                    chunk.export(tmp_chunk_path, format="wav")
                    try:
                        with sr.AudioFile(str(tmp_chunk_path)) as chunk_source:
                            audio = recognizer.record(chunk_source)
                        transcripts.append(_recognize_audio(recognizer, audio, language))
                    finally:
                        tmp_chunk_path.unlink(missing_ok=True)
            else:
                audio = recognizer.record(source)
                transcripts.append(_recognize_audio(recognizer, audio, language))
    finally:
        if wav_path != path:
            wav_path.unlink(missing_ok=True)
    return "\n".join(filter(None, transcripts)).strip()


def _recognize_audio(recognizer: sr.Recognizer, audio: sr.AudioData, language: str) -> str:
    try:
        if getattr(recognizer, "_backend", "google") == "sphinx":
            return recognizer.recognize_sphinx(audio, language=language)
        return recognizer.recognize_google(audio, language=language)
    except sr.UnknownValueError:
        print("Warning: audio unintelligible", file=sys.stderr)
        return ""
    except sr.RequestError as exc:
        print(f"Error: recognition service failed ({exc})", file=sys.stderr)
        return ""


def main() -> None:
    args = parse_args()
    audio_files = collect_audio_files(args.inputs)
    if not audio_files:
        print("No audio files found to transcribe.")
        sys.exit(0)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    recognizer = sr.Recognizer()
    if args.energy_threshold is not None:
        recognizer.energy_threshold = args.energy_threshold
    if args.recognizer == "sphinx":
        recognizer._backend = "sphinx"  # type: ignore[attr-defined]
    else:
        recognizer._backend = "google"  # type: ignore[attr-defined]

    for audio_path in audio_files:
        print(f"Transcribing {audio_path}...")
        transcript = transcribe_file(
            audio_path,
            recognizer,
            language=args.language,
            ambient_duration=args.ambient_duration,
            chunk_duration=args.chunk_duration,
        )
        output_name = audio_path.stem + ".txt"
        output_path = output_dir / output_name
        output_path.write_text(transcript or "(No transcription)", encoding="utf-8")
        print(f"Saved transcript to {output_path}")


if __name__ == "__main__":
    main()
