#!/usr/bin/env python3
import requests
import time
import os
from flask import Flask
from datetime import datetime, timedelta
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

last_sent_minute = None


# ---------------- WEBHOOK ----------------
def send_webhook(message):
    now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Wysyłam wiadomość...")

    try:
        response = requests.post(WEBHOOK_URL, json={"content": message}, timeout=15)
        print(f"[{now}] Status: {response.status_code}")
    except Exception as e:
        print(f"[{now}] Błąd: {e}")


# ---------------- TIME CALC ----------------
def get_next_run_time():
    now = datetime.now(TZ)
    candidates = []

    for t in SCHEDULE_TIMES:
        hour, minute = map(int, t.split(":"))
        run_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if run_time <= now:
            run_time += timedelta(days=1)

        candidates.append(run_time)

    return min(candidates)


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
    global last_sent_minute

    print("Scheduler uruchomiony")
    send_webhook(TEST_MESSAGE_TEXT)

    last_heartbeat = datetime.now(TZ)

    while True:
        now = datetime.now(TZ)
        next_run = get_next_run_time()
        seconds_left = (next_run - now).total_seconds()

        # Heartbeat co 60 sekund
        if (now - last_heartbeat).total_seconds() >= 60:
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Heartbeat | Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            last_heartbeat = now

        # Ochrona przed podwójną wysyłką
        current_minute = now.strftime("%Y-%m-%d %H:%M")

        if seconds_left <= 1 and last_sent_minute != current_minute:
            send_webhook(MESSAGE_TEXT)
            last_sent_minute = current_minute
            time.sleep(2)
            continue

        time.sleep(min(10, max(1, seconds_left)))


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
