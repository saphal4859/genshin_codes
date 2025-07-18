import requests
import os
from datetime import datetime

# === Configuration ===
API_URL = "https://hoyo-codes.seria.moe/codes?game=genshin"
SENT_FILE = "sent_codes.txt"
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

# === Telegram Sender ===
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.get(url, params={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        })
    except Exception as e:
        print(f"❌ Failed to send message to Telegram: {e}")

# === Fetch Codes from API ===
def fetch_genshin_codes():
    try:
        resp = requests.get(API_URL, timeout=10)
        if resp.status_code != 200:
            print("❌ Unable to fetch from API.")
            return []
        items = resp.json().get("codes", [])
        codes = [f"{it['code']} - {it['rewards'].capitalize()}" for it in items]
        return codes
    except Exception as e:
        print(f"⚠️ Error fetching codes: {e}")
        return []

# === File Helpers ===
def load_sent_codes():
    if os.path.exists(SENT_FILE):
        return set(open(SENT_FILE).read().splitlines())
    return set()

def save_new_codes(codes):
    with open(SENT_FILE, "a") as f:
        for c in codes:
            f.write(c + "\n")

# === Beautify Message ===
def format_codes_message(codes):
    timestamp = datetime.now().strftime("%b %d, %I:%M %p")
    header = f"🎮 *Genshin Impact New Codes* _(as of {timestamp})_\n\n"
    body = ""
    for idx, c in enumerate(codes, 1):
        if " - " in c:
            code, rewards = c.split(" - ", 1)
        else:
            code, rewards = c, ""
        line = f"{idx}️⃣ `{code.strip()}` – {rewards.strip()}"
        body += line + "\n\n"
    return header + body.strip()

def format_no_codes_message():
    timestamp = datetime.now().strftime("%b %d, %I:%M %p")
    return f"📭 No new Genshin codes found as of *{timestamp}*."

# === Main Execution ===
def main():
    print("🔍 Fetching Genshin Impact codes from API...")
    codes = fetch_genshin_codes()
    if not codes:
        print("❌ No codes returned.")
        send_telegram_message("⚠️ API returned no data.")
        return

    sent = load_sent_codes()
    new = [c for c in codes if c not in sent]

    if new:
        print("🎉 New codes found:")
        for c in new:
            print("✅", c)
        message = format_codes_message(new)
        send_telegram_message(message)
        save_new_codes(new)
    else:
        print("ℹ️ No new codes — sending status update.")
        send_telegram_message(format_no_codes_message())

if __name__ == "__main__":
    main()
