from openai import OpenAI
import argparse
import os
import pyaudio
import pyperclip
import signal
import sys
import wave


# Pyinstaller compatibility: Ensure the correct path for OpenAI API key
if getattr(sys, "frozen", False):
    # Running as compiled by pyinstaller
    # Static file path in the executable directory
    bundle_dir = sys._MEIPASS
else:
    # Running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Set the OpenAI API key from the credential file
with open(os.path.join(bundle_dir, "openai_api_key.credential"), "r") as key_file:
    os.environ["OPENAI_API_KEY"] = key_file.read().strip()


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
        file.write(response.content)


def try_tts(text, output_path, voice):
    if output_path is None:
        raise ValueError("Output file path is required for text-to-speech")

    tts(text, output_path, voice)
    print(f"Speech generated and saved to {output_path}")


# Optimized for voice audio:
# - Sample rate set to 16000 Hz, which is sufficient for speech and reduces file size
# - Mono channel (1) is used as stereo is unnecessary for voice recording
# - Chunk size of 1024 provides a good balance between latency and processing overhead
def record_audio(output_path, sample_rate=16000, channels=1, chunk=1024):
    p = pyaudio.PyAudio()
    frames = []
    recording = True

    def signal_handler(sig, frame):
        nonlocal recording
        print("\nRecording stopped.")
        recording = False

    signal.signal(signal.SIGINT, signal_handler)

    stream = p.open(
        format=pyaudio.paInt16,  # 16-bit depth is standard for voice and provides good quality
        channels=channels,
        rate=sample_rate,
        input=True,
        frames_per_buffer=chunk,
    )

    print("Recording... Press Ctrl+C to stop.")
    try:
        while recording:
            frames.append(stream.read(chunk))
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop_stream()
        stream.close()

    save_audio(p, frames, output_path, channels, sample_rate)


def save_audio(p, frames, output_path, channels, sample_rate):
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(b"".join(frames))
    print(f"Audio saved to {output_path}")
    p.terminate()


def record_and_transcribe(output_path):
    record_audio(output_path)
    transcription = transcribe(output_path)
    return transcription


if __name__ == "__main__":
    description = "Transcribe audio files, generate speech from text, or record and transcribe audio using OpenAI's API."
    input = "Audio file path for transcription, text content for text-to-speech, or 'record' (or 'rec') to record and transcribe"
    output = "Path to save the generated audio file (required for text-to-speech and recording) or transcription file"
    voice = "Voice model for text-to-speech (choices: alloy, echo, fable, onyx, nova, shimmer; default: nova)"

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

    # Determine if the input is a file, a recording command, or direct text
    # If it's a file, check if it's text or audio
    # If it's not a text file, assume it's an audio file
    # Use direct text input for TTS if not a file or recording command

    try:
        if args.input.lower() in ["rec", "record", "recording"]:
            if args.output is None:
                raise ValueError("Output file path is required for recording")

            transcription = record_and_transcribe(args.output)
            print(f"\n{transcription}\n")

            transcription_file = os.path.splitext(args.output)[0] + "_transcription.txt"
            with open(transcription_file, "w", encoding="utf-8") as f:
                f.write(transcription)
            print(f"Transcription saved to {transcription_file}")

            pyperclip.copy(transcription)
            print("Transcription copied to clipboard")

        elif os.path.isfile(args.input):
            try:
                with open(args.input, "r", encoding="utf-8") as file:
                    content = file.read()

                try_tts(content, args.output, args.voice)
            except UnicodeDecodeError:
                transcription = transcribe(args.input)
                print(transcription)

                pyperclip.copy(transcription)
                print("Transcription copied to clipboard")
        else:
            try_tts(args.input, args.output, args.voice)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
