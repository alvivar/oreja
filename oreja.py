import sys
from openai import OpenAI
import argparse
import os


def transcribe(path):
    client = OpenAI()

    with open(path, "rb") as audio:
        config = {"model": "whisper-1", "file": audio}
        transcription = client.audio.transcriptions.create(**config)

    return transcription.text


def tts(text, path, voice="nova"):
    client = OpenAI()

    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )

    with open(path, "wb") as file:
        for chunk in response.iter_bytes():
            file.write(chunk)


def try_tts(text, output_path, voice):
    if output_path is None:
        raise ValueError("Output file path is required for text-to-speech")

    tts(text, output_path, voice)
    print(f"Speech generated and saved to {output_path}")


if __name__ == "__main__":
    description = "Transcribe audio files or generate speech from text using OpenAI."
    input = "Audio file path for transcription, or text content for text-to-speech"
    output = "Path to save the generated audio file (required for text-to-speech)"
    voice = "Voice model for text-to-speech (default: nova)"

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "input",
        type=str,
        help=input,
    )
    parser.add_argument(
        "--output",
        type=str,
        help=output,
        default=None,
    )
    parser.add_argument(
        "--voice",
        type=str,
        choices=["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        default="nova",
        help=voice,
    )
    args = parser.parse_args()

    # Determine if the input is a file or direct text.
    # If it's a file, check if it's text or audio.
    # If it's not a text file, assume it's an audio file.
    # Use direct text input for TTS if not a file.

    try:
        if os.path.isfile(args.input):
            try:
                with open(args.input, "r", encoding="utf-8") as file:
                    content = file.read()
                try_tts(content, args.output, args.voice)
            except UnicodeDecodeError:
                print(transcribe(args.input))
        else:
            try_tts(args.input, args.output, args.voice)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
