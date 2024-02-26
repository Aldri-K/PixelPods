import qrcode
from dotenv import load_dotenv
import os

load_dotenv()
wifi = os.getenv('wifi_ssid', '')
wifi_pass = os.getenv('wifi_password', '')
print(wifi,wifi_pass)
img = qrcode.make(f'''
To connect to device:
Turn on Hotspot 
or
Change your hotspot to:
SSID/WIFI name: {wifi}
Password: {wifi_pass}''')

type(img)  # qrcode.image.pil.PilImage
img.save("qr.png")