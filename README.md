# Oreja means "ear" in Spanish

A simple command-line Python script for transcribing and converting text-to-speech files using OpenAI's Whisper model.

I have a group of friends who send me long audio messages from time to time, and sometimes it's easier for me to read them.

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

## How to use pyinstaller to create an executable

To create a standalone executable for Oreja using PyInstaller, follow these steps:

1. Install PyInstaller:

    ```
    pip install pyinstaller
    ```

2. Navigate to the directory containing your `oreja.py` script.

3. Run PyInstaller with the following command:

    ```
    pyinstaller --onefile --add-data "openai_api_key.credential:." oreja.py
    ```

    This command does the following:

    - `--onefile`: Creates a single executable file.
    - `--add-data "openai_api_key.credential:."`: Includes the API key file in the executable.

4. After the process completes, you'll find the executable in the `dist` directory.

5. You can now run the executable without needing Python installed:
    ```
    ./dist/oreja
    ```

Note: Ensure that your `openai_api_key.credential` file is in the same directory as `oreja.py` when creating the executable.

Remember to keep your API key secure and not share the executable containing your key.
