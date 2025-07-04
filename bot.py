import os
import re
import asyncio
import logging
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config import BOT_TOKEN, DOWNLOAD_DIR, ADMIN_USER_ID
from downloader import download_audio, download_video

# Ensure logs directory exists
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename=os.path.join(log_dir, 'bot.log')
)
logger = logging.getLogger(__name__)

# Dictionary to track active downloads
active_downloads = {}

# Set to store all user IDs
known_users = set()

# File to persist user IDs
USER_DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_db.txt')

# Load existing users
if os.path.exists(USER_DB_FILE):
    try:
        with open(USER_DB_FILE, 'r') as f:
            for line in f:
                if line.strip().isdigit():
                    known_users.add(int(line.strip()))
        logger.info(f"Loaded {len(known_users)} known users")
    except Exception as e:
        logger.error(f"Error loading user database: {e}")

def save_user(user_id: int):
    """Add user to known users and persist to file"""
    if user_id not in known_users:
        known_users.add(user_id)
        try:
            with open(USER_DB_FILE, 'a') as f:
                f.write(f"{user_id}\n")
            logger.info(f"Added new user: {user_id}")
        except Exception as e:
            logger.error(f"Error saving user: {e}")

# YouTube URL pattern
YOUTUBE_URL_PATTERN = re.compile(
    r'(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+'
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    save_user(user_id)
    
    welcome = (
                "👋 *Welcome to YouTube Downloader Bot!*\n\n"
        "With this bot, you can download:\n"
        "🎧 *Audio* — /audio <YouTube URL>\n"
        "🎥 *Video* — /video <YouTube URL>\n\n"
        "Example:\n"
        "/audio https://youtube.com/watch?v=abcd1234\n"
        "/video https://youtube.com/watch?v=abcd1234\n\n"
        "ℹ️ *Supported formats:*\n"
        "- MP3 (audio)\n"
        "- MP4 (video)\n\n"
        "Need help or want to contribute?\n"
        "📬 [Contact the developer](https://t.me/Thewarrior2003)"
    )
    await update.message.reply_text(welcome)

async def audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /audio command"""
    user_id = update.effective_user.id
    save_user(user_id)
    
    if not context.args:
        await update.message.reply_text("Please provide a YouTube URL after /audio")
        return
    
    url = context.args[0]
    if not YOUTUBE_URL_PATTERN.match(url):
        await update.message.reply_text("Invalid YouTube URL")
        return
    
    cancel_event = threading.Event()
    active_downloads[user_id] = cancel_event
    
    try:
        await update.message.reply_text("⏳ Downloading audio...")
        
        loop = asyncio.get_event_loop()
        filename, title, elapsed = await loop.run_in_executor(
            None,
            lambda: download_audio(url, cancel_event)
        )
        
        if cancel_event.is_set():
            await update.message.reply_text("❌ Download cancelled")
            return
            
        await update.message.reply_audio(
            audio=open(filename, 'rb'),
            title=title,
            performer="YouTube"
        )
        os.remove(filename)
        
    except Exception as e:
        logger.error(f"Audio download failed: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
    finally:
        if user_id in active_downloads:
            del active_downloads[user_id]

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /video command"""
    user_id = update.effective_user.id
    save_user(user_id)
    
    if not context.args:
        await update.message.reply_text("Please provide a YouTube URL after /video")
        return
    
    url = context.args[0]
    if not YOUTUBE_URL_PATTERN.match(url):
        await update.message.reply_text("Invalid YouTube URL")
        return
    
    cancel_event = threading.Event()
    active_downloads[user_id] = cancel_event
    
    try:
        await update.message.reply_text("⏳ Downloading video...")
        
        loop = asyncio.get_event_loop()
        filename, title, elapsed = await loop.run_in_executor(
            None,
            lambda: download_video(url, cancel_event))
        
        if cancel_event.is_set():
            await update.message.reply_text("❌ Download cancelled")
            return
            
        file_size = os.path.getsize(filename)
        if file_size > 50 * 1024 * 1024:  # 50MB
            await update.message.reply_text("⚠️ Video too large for Telegram (max 50MB)")
            return
            
        await update.message.reply_video(
            video=open(filename, 'rb'),
            caption=title
        )
        os.remove(filename)
        
    except Exception as e:
        logger.error(f"Video download failed: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")
    finally:
        if user_id in active_downloads:
            del active_downloads[user_id]

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command"""
    user_id = update.effective_user.id
    save_user(user_id)
    
    if user_id in active_downloads:
        active_downloads[user_id].set()
        await update.message.reply_text("🛑 Stopping download...")
    else:
        await update.message.reply_text("ℹ️ No active downloads")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user_id = update.effective_user.id
    save_user(user_id)
    
    help_text = (
        "📚 YouTube Downloader Bot Help:\n\n"
        "/audio <url> - Download audio\n"
        "/video <url> - Download video\n"
        "/stop - Cancel current download\n"
        "/help - Show this message\n\n"
        "Just send a YouTube link to download audio!"
    )
    await update.message.reply_text(help_text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    text = update.message.text
    user_id = update.effective_user.id
    save_user(user_id)
    
    if YOUTUBE_URL_PATTERN.match(text):
        await audio(update, context)
    else:
        await update.message.reply_text(
            "Send a YouTube URL or use /help for commands"
        )

def create_bot_app():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    
    bot_app = ApplicationBuilder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("audio", audio))
    bot_app.add_handler(CommandHandler("video", video))
    bot_app.add_handler(CommandHandler("stop", stop))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    return bot_app

if __name__ == '__main__':
    bot_app = create_bot_app()
    print("✅ Bot is running...")
    try:
        bot_app.run_polling()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user.")