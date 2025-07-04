
# 🎧 YouTube Downloader Telegram Bot

A fast, simple, and user-friendly Telegram bot that allows anyone to download **YouTube videos or audio (MP4/MP3)** directly within Telegram — no third-party websites, no ads, no hassle.

> 🔗 Try it now on Telegram: [@your\_frind\_bot](https://t.me/your_frind_bot)

---
## 📸 Screenshots

<div align="center">
  <img src="https://i.postimg.cc/m2K2VFmS/photo-2025-07-04-16-36-13.jpg" width="300" alt="Audio Download Example">
  <img src="https://i.postimg.cc/Hk5WNsK1/photo-2025-07-04-16-36-10.jpg" width="300" alt="Video Download Example">  
  <img src="https://i.postimg.cc/KvhmMyj9/photo-2025-07-04-16-43-52.jpg" width="300" alt="Bot Commands">
</div>

## 🚀 What This Bot Can Do

* 🎵 Download **high-quality MP3** audio from any public YouTube video
* 🎥 Download **MP4 video** (standard quality) directly to your Telegram
* ⚡ Works with just a single command or link
* 🔄 Real-time feedback with download status and completion time
* 📂 Cleans up files automatically after sending
* 🧠 Smart detection of whether user wants audio or video

---

## ✅ Supported Formats

* Audio: `.mp3` (192 kbps)
* Video: `.mp4` (standard resolution)

---

## 💬 Example Usage

Just send any public YouTube link with the appropriate command:

```bash
/audio https://www.youtube.com/watch?v=abcd1234
/video https://youtu.be/abcd1234
```

The bot will download and send the requested format directly to you within seconds.

---

## 🧱 Project Structure

```
youtube_audio_bot/
├── bot.py                # Main Telegram bot logic
├── downloader.py         # Download handler using yt-dlp + FFmpeg
├── config.py             # Bot token and download directory config
├── requirements.txt      # Required Python packages
├── logs/                 # Download and error logs
└── downloads/            # Temporary downloaded files
```

---

## 🔧 How to Set Up Locally

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/youtube-audio-bot.git
cd youtube-audio-bot
```

### 2. Install required libraries

```bash
pip install -r requirements.txt
```

### 3. Configure your bot

Edit the `config.py`:

```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
DOWNLOAD_DIR = "downloads"
```

Create your bot using [@BotFather](https://t.me/BotFather) to get the token.

### 4. Run the bot

```bash
python bot.py
```

---

## 💬 Telegram Commands

| Command          | Description                                         |
| ---------------- | --------------------------------------------------- |
| `/start`         | Welcome message with instructions                   |
| `/audio <URL>`   | Download YouTube audio (MP3)                        |
| `/video <URL>`   | Download YouTube video (MP4)                        |
| `/stop`          | Cancel an active download                           |
| `/help`          | List available commands and instructions            |
| Send just a link | Bot detects and downloads audio/video automatically |

---

## 🔗 Technology Stack

* **Language:** Python 3.11+
* **Bot API:** `python-telegram-bot`
* **Downloader:** `yt-dlp` (advanced YouTube downloader)
* **Media Processing:** FFmpeg
* **Logging:** Python logging module

---

## 🤝 Contribution & Support

Built and maintained by [@Thewarrior2003](https://t.me/Thewarrior2003)
If you have suggestions, ideas, or issues — feel free to open an issue or reach out.

---

## 🧠 Ideal Use Cases

* Quickly grab background music for your projects
* Save motivational songs or lectures offline
* Help students, creators, and learners download content easily
* No YouTube Premium needed. No web ads. Just Telegram.

---

## 📌 Legal Notice

This project is intended **only for educational and personal use**. Please respect YouTube’s [Terms of Service](https://www.youtube.com/t/terms) and copyright laws. Do not use this bot to download copyrighted content without permission.
