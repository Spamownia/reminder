import requests
import schedule
import time
from datetime import datetime, timedelta
import pytz
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from threading import Thread
from flask import Flask
import os

app = Flask(__name__)

# Webhook Discord
WEBHOOK_URL = "https://discord.com/api/webhooks/1439986012964126731/b05t-zKqJMCnmU3VWACytid2dsw2DG3bk-TQxVfG6MJI_6qglipuHIuWGURl5nutHwKu"

# Strefa Polska
tz = pytz.timezone("Europe/Warsaw")
MESSAGE_TEXT = "⚠️ Serwer zostanie zrestartowany za 10 minut! ⚠️"
TEST_MESSAGE_TEXT = "✅ Test po starcie: webhook działa!"

# Funkcja tworząca obrazek
def create_image(message):
    width, height = 800, 200
    img = Image.new("RGB", (width, height), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()
    text_width, text_height = draw.textsize(message, font=font)
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    draw.text((x, y), message, font=font, fill=(255, 50, 50))
    return img

# Funkcja wysyłająca webhook z obrazkiem
def send_webhook(message):
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Wysyłam wiadomość: {message}")

    img = create_image(message)
    with BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)
        try:
            response = requests.post(
                WEBHOOK_URL,
                files={"file": ("restart.png", image_binary, "image/png")}
            )
            print(f"[{now}] Status: {response.status_code} {response.text}")
        except Exception as e:
            print(f"[{now}] Błąd połączenia: {e}")

# Harmonogram w UTC przeliczony z CET
def run_scheduler():
    schedule_times = ["03:50", "09:50", "15:50", "21:50"]
    for t in schedule_times:
        hour, minute = map(int, t.split(":"))
        # przelicz CET na UTC
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

# Endpoint testowy
@app.route("/")
def home():
    return "Discord Restart Reminder działa! Harmonogram uruchomiony."

# Wiadomość testowa po starcie
@app.before_first_request
def startup_message():
    Thread(target=lambda: send_webhook(TEST_MESSAGE_TEXT)).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"Uruchamiam Flask na porcie {port}")
    app.run(host="0.0.0.0", port=port)
