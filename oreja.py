import sys
from openai import OpenAI
import argparse
import os
import pyaudio
import wave
import signal


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


def record_audio(output_path, sample_rate=44100, channels=1, chunk=1024):
    p = pyaudio.PyAudio()

    stream = p.open(
        format=pyaudio.paInt16,
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk,
    )

    print("Recording... Press Ctrl+C to stop.")
    frames = []

    def signal_handler(sig, frame):
        nonlocal frames
        print("\nRecording stopped.")
        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(output_path, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(frames))
        wf.close()

        print(f"Audio saved to {output_path}")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        while True:
            data = stream.read(chunk)
            frames.append(data)
    except KeyboardInterrupt:
        pass


def record_and_transcribe(output_path):
    record_audio(output_path)
    transcription = transcribe(output_path)
    return transcription


if __name__ == "__main__":
    description = "Transcribe audio files, generate speech from text, or record and transcribe audio using OpenAI."
    input = "Audio file path for transcription, text content for text-to-speech, or 'record' to record and transcribe"
    output = "Path to save the generated audio file (required for text-to-speech and recording)"
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
        if args.input.lower() == "rec":
            if args.output is None:
                raise ValueError("Output file path is required for recording")
            transcription = record_and_transcribe(args.output)
            print(transcription)
        elif os.path.isfile(args.input):
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
