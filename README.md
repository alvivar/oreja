# Oreja means "ear" in Spanish

A simple command-line Python script for transcribing audio files using OpenAI's Whisper model.

I have a group of friends who send me long audio messages from time to time, and sometimes it's easier for me to read them.

## Really?

Yes, really. A repo for 25 lines of code, but I want to add more features later on.

-   Maybe call an LLM model to post-process the text.
-   Maybe call a text-to-speech model to read it out loud.

## Usage

```bash
python oreja.py audio.wav
> [text]
```

I usually use `> text.txt` to save the transcription to a file from the terminal.

```bash
python oreja.py audio.wav > text.txt
```

## Requirements

```bash
pip install openai
```

Remember to set your OpenAI API key as an environment variable.

```bash
export OPENAI_API_KEY="sk-proj-..."
```
