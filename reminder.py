import requests
import schedule
import time
from datetime import datetime
import pytz
from threading import Thread
from flask import Flask
import os

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1440029602603864094/aTvg3TEcY3_SYCBxNzCgTr1ppLoMZGgMqzaMlamN5qCm8aZJK4QKGbuyQfyCX5Y5Le8M"
tz = pytz.timezone("Europe/Warsaw")

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

def send_webhook(message):
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Wysyłam wiadomość: {message}")
    try:
        response = requests.post(
            WEBHOOK_URL,
            json={"content": message}
        )
        print(f"[{now}] Status: {response.status_code} {response.text}")
    except Exception as e:
        print(f"[{now}] Błąd połączenia: {e}")

def run_scheduler():
    schedule_times = ["03:50", "09:50", "15:50", "21:50"]
    for t in schedule_times:
        hour, minute = map(int, t.split(":"))
        now = datetime.now(tz)
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        utc_hour = target.astimezone(pytz.utc).hour
        utc_minute = target.astimezone(pytz.utc).minute
        schedule.every().day.at(f"{utc_hour:02d}:{utc_minute:02d}").do(lambda: send_webhook(MESSAGE_TEXT))
        print(f"Harmonogram ustawiony na {t} CET -> {utc_hour:02d}:{utc_minute:02d} UTC")

    while True:
        schedule.run_pending()
        time.sleep(10)

# Start scheduler w osobnym wątku
Thread(target=run_scheduler, daemon=True).start()

# Wyślij natychmiastową wiadomość testową w osobnym wątku
Thread(target=lambda: send_webhook(TEST_MESSAGE_TEXT)).start()

@app.route("/")
def home():
    return "Discord Restart Reminder działa! Harmonogram uruchomiony."

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Uruchamiam Flask na porcie {port}")
    app.run(host="0.0.0.0", port=port)
