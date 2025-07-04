import os
import time
import random
import logging
from yt_dlp import YoutubeDL
from yt_dlp.utils import ExtractorError
from config import DOWNLOAD_DIR

# Path to cookies file
COOKIES_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')

# List of user agents for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
]

# Critical extractor arguments to handle YouTube changes
EXTRACTOR_ARGS = {
    'youtube': {
        'player_client': ['android_embedded', 'web'],  # Prefer Android client
        'skip': ['hls', 'dash'],  # Avoid problematic formats
        'formats': 'missing_pot'  # Skip formats requiring special tokens
    }
}

def download_audio(url: str, cancel_flag=None, proxy: str = None):
    def progress_hook(d):
        if cancel_flag and cancel_flag.is_set():
            raise Exception("Download cancelled by user.")
    
    user_agent = random.choice(USER_AGENTS)
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'noplaylist': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'http_headers': {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Mode': 'navigate',
        },
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'verbose': True,
        'force-ipv4': True,
        'ratelimit': 1000000,
        'progress_hooks': [progress_hook],
        'extractor_args': EXTRACTOR_ARGS,
        'compat_opts': ['no-youtube-unavailable-videos'],
    }
    
    # Add cookies if file exists
    if os.path.exists(COOKIES_FILE_PATH):
        ydl_opts['cookiefile'] = COOKIES_FILE_PATH
    else:
        logging.warning(f"Cookies file not found at {COOKIES_FILE_PATH}. If you encounter 'Sign in to confirm you’re not a bot' errors, please export your YouTube cookies.")
    
    # Add proxy if provided
    if proxy:
        ydl_opts['proxy'] = proxy

    retry_count = 0
    max_retries = 2
    
    while retry_count < max_retries:
        try:
            with YoutubeDL(ydl_opts) as ydl:
                start_time = time.time()
                info = ydl.extract_info(url, download=True)
                elapsed_time = time.time() - start_time
                title = info.get('title', 'audio')
                
                # FIXED: Correct filename handling
                base_filename = os.path.splitext(ydl.prepare_filename(info))[0]
                filename = base_filename + '.mp3'
                
                return filename, title, elapsed_time
                
        except ExtractorError as e:
            if 'signature' in str(e).lower() or 'decrypt' in str(e).lower():
                retry_count += 1
                logging.warning(f"Signature extraction failed, retry {retry_count}/{max_retries}")
                # Simplify options for retry
                ydl_opts['format'] = 'bestaudio'
                ydl_opts['extractor_args']['youtube']['player_client'] = ['android']
                continue
            raise
        except Exception as e:
            raise

    # Final fallback if retries fail
    ydl_opts['format'] = 'bestaudio'
    ydl_opts['extractor_args']['youtube']['player_client'] = ['android']
    with YoutubeDL(ydl_opts) as ydl:
        start_time = time.time()
        info = ydl.extract_info(url, download=True)
        elapsed_time = time.time() - start_time
        title = info.get('title', 'audio')
        
        # FIXED: Correct filename handling
        base_filename = os.path.splitext(ydl.prepare_filename(info))[0]
        filename = base_filename + '.mp3'
        
        return filename, title, elapsed_time

def download_video(url: str, cancel_flag=None, proxy: str = None):
    def progress_hook(d):
        if cancel_flag and cancel_flag.is_set():
            raise Exception("Download cancelled by user.")
    
    user_agent = random.choice(USER_AGENTS)
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'http_headers': {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Sec-Fetch-Mode': 'navigate',
        },
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'verbose': True,
        'force-ipv4': True,
        'ratelimit': 1000000,
        'progress_hooks': [progress_hook],
        'extractor_args': EXTRACTOR_ARGS,
        'compat_opts': ['no-youtube-unavailable-videos'],
    }
    
    # Add cookies if file exists
    if os.path.exists(COOKIES_FILE_PATH):
        ydl_opts['cookiefile'] = COOKIES_FILE_PATH
    
    # Add proxy if provided
    if proxy:
        ydl_opts['proxy'] = proxy

    retry_count = 0
    max_retries = 2
    
    while retry_count < max_retries:
        try:
            with YoutubeDL(ydl_opts) as ydl:
                start_time = time.time()
                info = ydl.extract_info(url, download=True)
                elapsed_time = time.time() - start_time
                title = info.get('title', 'video')
                
                # FIXED: Correct filename handling
                base_filename = os.path.splitext(ydl.prepare_filename(info))[0]
                filename = base_filename + '.mp4'
                
                # Handle temporary files
                if not os.path.exists(filename):
                    temp_filename = base_filename + '.temp.mp4'
                    if os.path.exists(temp_filename):
                        for _ in range(10):
                            time.sleep(0.5)
                            if os.path.exists(filename):
                                break
                        else:
                            try:
                                os.rename(temp_filename, filename)
                            except Exception:
                                pass
                return filename, title, elapsed_time
                
        except ExtractorError as e:
            if 'signature' in str(e).lower() or 'decrypt' in str(e).lower():
                retry_count += 1
                logging.warning(f"Signature extraction failed, retry {retry_count}/{max_retries}")
                # Simplify options for retry
                ydl_opts['format'] = 'best[height<=720]'
                ydl_opts['extractor_args']['youtube']['player_client'] = ['android']
                continue
            raise
        except Exception as e:
            raise

    # Final fallback if retries fail
    ydl_opts['format'] = 'best[height<=480]'
    ydl_opts['extractor_args']['youtube']['player_client'] = ['android']
    with YoutubeDL(ydl_opts) as ydl:
        start_time = time.time()
        info = ydl.extract_info(url, download=True)
        elapsed_time = time.time() - start_time
        title = info.get('title', 'video')
        
        # FIXED: Correct filename handling
        base_filename = os.path.splitext(ydl.prepare_filename(info))[0]
        filename = base_filename + '.mp4'
        
        return filename, title, elapsed_time