import requests
import schedule
import time
from datetime import datetime
import pytz
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Webhook Discord
WEBHOOK_URL = "https://discord.com/api/webhooks/1439986012964126731/b05t-zKqJMCnmU3VWACytid2dsw2DG3bk-TQxVfG6MJI_6qglipuHIuWGURl5nutHwKu"

# Strefa czasowa Polska
tz = pytz.timezone("Europe/Warsaw")

# Treść wiadomości
MESSAGE_TEXT = "⚠️ Serwer zostanie zrestartowany za 10 minut! ⚠️"

# Funkcja tworząca obrazek z wiadomością
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
def send_webhook():
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Wysyłam powiadomienie...")

    img = create_image(MESSAGE_TEXT)
    with BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)
        try:
            response = requests.post(
                WEBHOOK_URL,
                files={"file": ("restart.png", image_binary, "image/png")}
            )
            if response.status_code in [200, 204]:
                print(f"[{now}] Wiadomość wysłana pomyślnie.")
            else:
                print(f"[{now}] Błąd wysyłki: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Błąd połączenia: {e}")

# Harmonogram w czasie polskim
schedule_times = ["03:50", "09:50", "15:50", "21:50"]
for t in schedule_times:
    schedule.every().day.at(t).do(send_webhook)

print("Skrypt graficznych przypomnień uruchomiony...")

# Pętla główna
while True:
    schedule.run_pending()
    time.sleep(30)
