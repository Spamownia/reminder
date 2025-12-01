#!/usr/bin/env python3
import requests
import time
import os
from flask import Flask
from datetime import datetime
import pytz
import threading

# ---------------- CONFIG ----------------
WEBHOOK_URL = "https://discord.com/api/webhooks/1440029602603864094/aTvg3TEcY3_SYCBxNzCgTr1ppLoMZGgMqzaMlamN5qCm8aZJK4QKGbuyQfyCX5Y5Le8M"

TZ = pytz.timezone("Europe/Warsaw")

SCHEDULE_TIMES = ["03:50", "09:50", "15:50", "21:50"]

MESSAGE_TEXT = (
    "⏰ **Server Restart Reminder!**\n"
    "⚠️ Server will restart in 10 minutes! ⚠️\n"
    "📌 Prepare for a temporary downtime.\n"
    "=============================================\n"
    "⏰ **Przypomnienie o restarcie serwera!**\n"
    "⚠️ Serwer zostanie zrestartowany za 10 minut! ⚠️\n"
    "📌 Przygotujcie się na chwilową przerwę."
)

TEST_MESSAGE_TEXT = "✅ Test po starcie: webhook działa!"

app = Flask(__name__)

last_sent = None


# ---------------- WEBHOOK ----------------
def send_webhook(message):
    now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Wysyłam wiadomość...")

    try:
        response = requests.post(WEBHOOK_URL, json={"content": message}, timeout=15)
        print(f"[{now}] Status: {response.status_code}")
    except Exception as e:
        print(f"[{now}] Błąd: {e}")


# ---------------- SELF PING ----------------
def self_ping():
    while True:
        try:
            url = f"http://127.0.0.1:{os.environ.get('PORT', 10000)}/"
            requests.get(url, timeout=10)
            print(f"[{datetime.now(TZ).strftime('%H:%M:%S')}] Self-ping OK")
        except Exception as e:
            print(f"Self-ping error: {e}")

        time.sleep(300)  # co 5 minut


# ---------------- MAIN LOOP ----------------
def scheduler_loop():
    global last_sent

    print("Scheduler uruchomiony")
    send_webhook(TEST_MESSAGE_TEXT)

    last_heartbeat = datetime.now(TZ)

    while True:
        now = datetime.now(TZ)
        current_time = now.strftime("%H:%M")
        current_stamp = now.strftime("%Y-%m-%d %H:%M")

        # Heartbeat co 60 sekund
        if (now - last_heartbeat).total_seconds() >= 60:
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Heartbeat")
            last_heartbeat = now

        # Główna logika wyzwalania
        if current_time in SCHEDULE_TIMES and last_sent != current_stamp:
            send_webhook(MESSAGE_TEXT)
            last_sent = current_stamp

        time.sleep(1)


# ---------------- FLASK ----------------
@app.route("/")
def home():
    return "Discord Restart Reminder działa poprawnie."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Uruchamiam Flask na porcie {port}")

    threading.Thread(target=scheduler_loop, daemon=True).start()
    threading.Thread(target=self_ping, daemon=True).start()

    app.run(host="0.0.0.0", port=port)
