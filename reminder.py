#!/usr/bin/env python3
import requests
import time
import os
from flask import Flask
from datetime import datetime, timedelta
import pytz

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
    "📌 Przygotujcie się na chwilową przerwę.\n"
)

TEST_MESSAGE_TEXT = "✅ Test po starcie: webhook działa!"

app = Flask(__name__)


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

        run_time = now.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0
        )

        if run_time <= now:
            run_time += timedelta(days=1)

        candidates.append(run_time)

    next_run = min(candidates)
    return next_run


# ---------------- MAIN LOOP ----------------
def scheduler_loop():
    print("Scheduler uruchomiony")

    send_webhook(TEST_MESSAGE_TEXT)

    last_heartbeat = datetime.now(TZ)

    while True:
        now = datetime.now(TZ)
        next_run = get_next_run_time()
        seconds_left = (next_run - now).total_seconds()

        # Heartbeat co 60 sekund (Render lubi aktywność)
        if (now - last_heartbeat).total_seconds() >= 60:
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Heartbeat | Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            last_heartbeat = now

        # Jeśli czas wysyłki nadszedł
        if seconds_left <= 1:
            send_webhook(MESSAGE_TEXT)
            time.sleep(2)  # zabezpieczenie przed podwójną wysyłką
            continue

        # Uśpij maksymalnie na 10 sekund, żeby Render nie ubijał
        sleep_time = min(10, seconds_left)
        if sleep_time > 0:
            time.sleep(sleep_time)


# ---------------- FLASK ----------------
@app.route("/")
def home():
    return "Discord Restart Reminder działa."


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    print(f"Uruchamiam Flask na porcie {port}")

    import threading
    scheduler_thread = threading.Thread(target=scheduler_loop)
    scheduler_thread.start()

    app.run(host="0.0.0.0", port=port)
