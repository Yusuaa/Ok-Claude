# Claude Overlay

Voice assistant for Linux integrating Claude AI.
Minimalist interface, hybrid voice recognition (Vosk + Whisper) and system control.

![Claude Overlay](claude_logo.png)

## Features

*   **Overlay Interface**: Transparent and non-intrusive window (PyQt6).
*   **Local Wake Word**: Offline detection of the "Claude" keyword (Vosk).
*   **Transcription**: Uses Whisper for accurate understanding.
*   **Intelligence**: Connected to Claude API for responses and complex commands.
*   **Control**: Launch applications and web navigation.

## Installation

Prerequisites: Linux, Python 3.10+, `ffmpeg`, `portaudio`, `claude` CLI.

1.  **Clone the project**
    ```bash
    git clone https://github.com/your-user/claude-overlay.git
    cd claude-overlay
    ```

2.  **Install**
    The `install.sh` script configures the virtual environment and downloads the necessary models.
    ```bash
    chmod +x install.sh
    ./install.sh
    ```

3.  **Claude Login**
    ```bash
    claude login
    ```

## Usage

Launch the assistant:
```bash
source venv/bin/activate
python main.py
```

*   **Activate**: Say "Claude".
*   **Command**: Ask your question or give an order.
*   **Finish**: Say "End Claude" or "Send".
*   **Cancel**: Say "Thanks" or "Stop".

## Configuration

*   **Hyprland**: Window rules included in `main.py`.
*   **Models**:
    *   Vosk (Wake word): `models/fr`
    *   Whisper (Transcription): Configurable in `worker.py`.

## Disclaimer

> This project is not affiliated with or endorsed by Anthropic.
> Claude is a trademark of Anthropic, PBC.
