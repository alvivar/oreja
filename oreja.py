from openai import OpenAI
import argparse


def transcribe(path):
    client = OpenAI()
    with open(path, "rb") as audio:
        config = {"model": "whisper-1", "file": audio}
        transcription = client.audio.transcriptions.create(**config)
    return transcription.text


if __name__ == "__main__":
    description = "Transcribe audio files using OpenAI's Whisper model."
    help = "Path to the audio file to transcribe."

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("audio_file", type=str, help=help)
    args = parser.parse_args()

    try:
        result = transcribe(args.audio_file)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
