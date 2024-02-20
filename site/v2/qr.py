import qrcode
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path = '.env')
wifi = os.getenv('wifi_ssid', '')
wifi_pass = os.getenv('wifi_password', '')
print(wifi,wifi_pass)
img = qrcode.make(f'''
Turn on Hotspot 
or
Change your hotspot to:
SSID/WIFI name: {wifi}
Password: {wifi_pass}''')

type(img)  # qrcode.image.pil.PilImage
img.save("qr.png")