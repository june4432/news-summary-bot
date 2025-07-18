import os
import json

from batch.common.config import recipients_email_file, recipients_telegram_file

# Load recipients from file or initialize empty list
def load_recipients():
    if os.path.exists(recipients_email_file):
        with open(recipients_email_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Save updated recipients list
def save_recipients(data):
    with open(recipients_email_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_recipients_telegram():
    try:
        with open(recipients_telegram_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_recipients_telegram(data):
    with open(recipients_telegram_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)