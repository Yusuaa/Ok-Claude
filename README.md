<div align="center">

# 🎙️ Claude Overlay

**Voice assistant for Linux integrating Claude AI**

*Minimalist interface, hybrid voice recognition (Vosk + Whisper) and system control*

![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Linux-green.svg)
![Claude](https://img.shields.io/badge/AI-Claude-orange.svg)

<img src="./logo.png" alt="Claude Overlay" width="200"/>

</div>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖼️ **Overlay Interface** | Transparent and non-intrusive window (PyQt6) |
| 🎤 **Local Wake Word** | Offline detection of "Claude" keyword (Vosk) |
| 📝 **Transcription** | Uses Whisper for accurate understanding |
| 🧠 **Intelligence** | Connected to Claude API for responses and complex commands |
| 🚀 **Control** | Launch applications and web navigation |

---

## 📦 Installation

### Prerequisites

- Linux (tested on Hyprland/Wayland)
- Python 3.10+
- `ffmpeg`
- `portaudio`
- `claude` CLI ([Install Claude CLI](https://docs.anthropic.com/en/docs/claude-cli))

### Quick Start

```bash
# 1. Clone the project
git clone https://github.com/your-user/claude-overlay.git
cd claude-overlay

# 2. Run the installer
chmod +x install.sh
./install.sh

# 3. Login to Claude
claude login
```

---

## 🚀 Usage

```bash
source venv/bin/activate
python main.py
```

### Voice Commands

| Action | Say |
|--------|-----|
| 🟢 **Activate** | "Claude" |
| 💬 **Command** | Ask your question or give an order |
| ✅ **Finish** | "End Claude" or "Send" or "Done" |
| ❌ **Cancel** | "Thanks" or "Stop" |

---

## ⚙️ Configuration

- **Hyprland**: Window rules are automatically injected via `main.py`
- **Models**:
  - Vosk (Wake word): `models/fr`
  - Whisper (Transcription): Configurable in `worker.py`

---

## 📁 Project Structure

```
claude-overlay/
├── main.py          # Entry point & Hyprland config
├── gui.py           # PyQt6 overlay interface
├── worker.py        # Audio processing & Claude integration
├── install.sh       # Installation script
├── requirements.txt # Python dependencies
└── models/          # Vosk voice models
```

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## ⚠️ Disclaimer

> **This project is not affiliated with or endorsed by Anthropic.**
> Claude is a trademark of Anthropic, PBC.

---

<div align="center">

Made with ❤️ for the Linux community

</div>
