# Keylogger
This project is a stealthy Python-based keylogger designed for Windows systems. It captures a wide range of user interactions and stores them locally for later analysis. Ideal for educational, monitoring, or security research purposes.
🛠️ Stealth Keylogger for Windows (Python)
This project is a stealthy Python-based keylogger designed for Windows systems. It captures a wide range of user interactions and stores them locally for later analysis. Ideal for educational, monitoring, or security research purposes.

🔍 Features
Keystroke Logging: Captures all pressed keys in real-time.

Window Change Detection: Logs active window titles to track application context.

Clipboard Monitoring: Logs copied text and saves copied images as PNG files.

Screenshot Capture: Takes screenshots when the active window changes.

Session Management: Automatically creates a new folder for each session, organized by date and time.

Runs in Background: Executes silently without console window.

Optional Audio Recording: (Planned) capture ambient sound via microphone.

Extensible Architecture: Easy to add exfiltration modules (e.g., webhook, email, etc.).

⚠️ Disclaimer: This project is intended strictly for educational purposes and lawful usage (e.g. parental control, self-monitoring, penetration testing on your own systems). Unauthorized use on devices without consent is illegal.

📁 Output Structure
Captured data is stored in:

/keylogger/
  └── YYYY-MM-DD/
        ├── session_HH-MM/
        │     ├── keystrokes.log
        │     ├── clipboard.txt
        │     ├── screenshots/
        │     └── images/
🧠 Tech Stack
pynput – Keyboard event listening

PIL (Pillow) – Image capturing

win32gui, win32clipboard – Windows API access

threading, datetime, ctypes, etc.

