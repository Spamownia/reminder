import requests
import schedule
import time
from datetime import datetime
import pytz
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from threading import Thread
from flask import Flask
import os

app = Flask(__name__)

WEBHOOK_URL = "https://discord.com/api/webhooks/1439986012964126731/b05t-zKqJMCnmU3VWACytid2dsw2DG3bk-TQxVfG6MJI_6qglipuHIuWGURl5nutHwKu"
tz = pytz.timezone("Europe/Warsaw")
MESSAGE_TEXT = "⚠️ Serwer zostanie zrestartowany za 10 minut! ⚠️"
TEST_MESSAGE_TEXT = "✅ Test po starcie: webhook działa!"

def create_image(message):
    width, height = 800, 200
    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # Gradient tła (ciemnoczerwony -> czarny)
    for y in range(height):
        r = int(30 + (225 - 30) * (y / height))
        g = int(0 + (30 - 0) * (y / height))
        b = int(0 + (30 - 0) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()

    # Ikona zegara (prostokątne kółko po lewej)
    draw.ellipse((20, 60, 100, 140), fill=(255, 215, 0))

    # Wymiary tekstu
    try:
        bbox = draw.textbbox((0, 0), message, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        text_width, text_height = font.getsize(message)

    x = (width - text_width) / 2 + 30  # przesunięcie na prawo od ikony
    y = (height - text_height) / 2
    draw.text((x, y), message, font=font, fill=(255, 255, 255))

    return img

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
            print(f"Błąd połączenia: {e}")

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
