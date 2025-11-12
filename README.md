# 🎥 REDLIX Streaming Tools

<div align="center">

![Version](https://img.shields.io/badge/version-Alpha%20v1.0-red?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/flask-3.0+-green?style=for-the-badge&logo=flask)
![License](https://img.shields.io/badge/license-MIT-purple?style=for-the-badge)

**Professional streaming overlay system with real-time controls and visual effects**

Features • Installation • Usage • Configuration • Documentation

</div>

---

## 📋 Overview

REDLIX Streaming Tools is a web-based streaming overlay system designed for OBS Studio and other streaming software. It provides a clean, modern control panel with real-time timers, countdowns, messages, and visual effects - all with integrated text-to-speech functionality.

### ✨ Key Features

- **🎛️ Modern Control Panel** - Clean, responsive web interface with real-time state updates
- **⏱️ Timer & Countdown** - Precise time tracking with visual progress bars
- **💬 Messages** - Display custom messages with emoji support and color customization
- **🎭 Visual Effects** - Confetti and glitch effects with customizable durations
- **🔊 Text-to-Speech** - Automatic multilingual TTS with French accent (oui oui!)
- **🎨 OBS Integration** - Chroma key ready (#00FF00) overlay display
- **📱 Responsive Design** - Works on desktop, tablet, and mobile devices

---

## 🚀 Features

### Timer & Countdown
- ⏯️ Start, stop, and reset controls
- 👁️ Toggle visibility for OBS scenes
- 📊 Real-time progress bars
- ⏰ Precise time tracking (HH:MM:SS format)

### Message System
- 📝 Custom text with emoji support
- 🎨 Color picker for message styling
- ⏲️ Configurable display duration (3s - 60s)
- ✨ Animated entrance with progress bar

### Visual Effects
- 🎉 **Confetti** - Colorful celebration effect
- ⚡ **Glitch** - Advanced CRT TV malfunction effect with:
  - TV color bars
  - RGB separation
  - Static noise
  - Scanlines
  - Vertical roll
  - Color bleeding
  - Signal loss effects

### Text-to-Speech
- 🗣️ Automatic language detection
- 🇫🇷 French accent for all languages
- 🧹 Emoji and special character cleaning
- 🎯 Async processing (non-blocking)

---

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- FFmpeg (for audio playback)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/redlix-streamingtools.git
cd redlix-streamingtools/StreamingTools
```

### Step 2: Install Dependencies

```bash
pip install flask gtts pydub langdetect
```

### Step 3: Install FFmpeg

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

---

## 🎮 Usage

### Starting the Server

```bash
python main.py
```

The server will start on `http://127.0.0.1:8765`

### Control Panel

Open your browser and navigate to:
```
http://127.0.0.1:8765/
```

The control panel provides access to all streaming tools:
- Timer controls (Start/Stop/Reset/Toggle)
- Countdown configuration
- Message composer with emoji picker
- Event triggers

### OBS Studio Setup

1. **Add Browser Source**
   - In OBS, click the `+` button under Sources
   - Select "Browser"
   - Name it "REDLIX Overlay"

2. **Configure Browser Source**
   ```
   URL: http://127.0.0.1:8765/display
   Width: 1920
   Height: 1080
   FPS: 60
   ```

3. **Enable Chroma Key**
   - Right-click the source → Filters
   - Add "Chroma Key" filter
   - Set Key Color Type to "Green" (#00FF00)
   - Adjust Similarity and Smoothness as needed

4. **Position & Scale**
   - Transform the source to fit your scene
   - Overlay works best in fullscreen mode

---

## ⚙️ Configuration

### File Structure

```
StreamingTools/
├── main.py              # Main application server
├── tts.py              # Text-to-speech module
├── media/              # Media assets
│   ├── headerlogo.png  # Control panel header logo
│   └── redlixlogo.svg  # Footer logo
└── __pycache__/        # Python cache files
```

### Customization

#### Changing Default Languages

Edit tts.py:

```python
class TTSManager:
    def __init__(self):
        self.default_language = 'en'  # Change default fallback language
        self.tld = 'com'              # Change accent (com=US, co.uk=UK, etc.)
```

#### Modifying Colors

Edit color variables in main.py CONTROL_HTML section:

```css
:root {
    --primary-red: rgb(128, 26, 48);
    --dark-gray: rgb(38, 38, 38);
    --burgundy: rgb(49, 18, 26);
}
```

#### Adjusting Port

Change the port in main.py:

```python
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)  # Changed from 8765
```

---

## 📡 API Reference

### Endpoints

#### Timer
- `POST /api/timer/start` - Start the timer
- `POST /api/timer/stop` - Stop the timer
- `POST /api/timer/reset` - Reset the timer

#### Countdown
- `POST /api/countdown/start` - Start countdown (requires `minutes` in JSON body)
- `POST /api/countdown/stop` - Stop countdown
- `POST /api/countdown/reset` - Reset countdown

#### Visibility
- `POST /api/visibility/timer` - Toggle timer visibility
- `POST /api/visibility/countdown` - Toggle countdown visibility

#### Messages
- `POST /api/message` - Show message (requires `text`, `color`, `duration` in JSON body)
- `POST /api/message/clear` - Clear current message

#### Events
- `POST /api/event` - Trigger visual effect (requires `type`, `duration` in JSON body)

#### State
- `GET /api/state` - Get current state of all components

---

## 📚 Documentation

### Timer Component

The timer tracks elapsed time and displays it in HH:MM:SS format. When running, a green progress bar is visible.

### Countdown Component

Set a specific duration (hours, minutes, seconds) and count down to zero. The progress bar depletes as time runs out.

### Message System

Messages appear centered on screen with:
- Custom text content
- Emoji support (⚠️ 🔴 📢 💡 🎮 ⭐)
- Color customization
- Animated progress bar showing time remaining
- Glow effects matching message color

### TTS Integration

Text-to-speech is automatically triggered when messages are shown:
- Language auto-detection using [`langdetect`](https://pypi.org/project/langdetect/)
- Emoji removal for clean speech
- French accent for all languages
- Async processing via queue

---

## 🛠️ Troubleshooting

### Common Issues

**Server won't start**
- Check if port 8765 is already in use
- Ensure all dependencies are installed: `pip list`

**TTS not working**
- Verify FFmpeg installation: `ffmpeg -version`
- Check for error messages in the console
- Ensure speakers/audio output is enabled

**OBS overlay not visible**
- Verify the browser source URL is correct
- Check browser source dimensions (1920x1080)
- Ensure chroma key is configured for green (#00FF00)

**Messages not appearing**
- Check message duration setting
- Verify network connectivity to `127.0.0.1:8765`
- Open browser console (F12) for JavaScript errors

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🔗 Links

- **Website:** [redlix.xyz](https://redlix.xyz/)
- **Documentation:** [redlix.xyz/streaming-tools](https://redlix.xyz/streaming-tools)
- **Issues:** [GitHub Issues](https://github.com/yourusername/redlix-streamingtools/issues)

---

<div align="center">

**Made with ❤️ by REDLIX**

*Professional streaming overlay system*

</div>
