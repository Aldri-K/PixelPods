import qrcode
from dotenv import load_dotenv
import os
import socket

load_dotenv()
wifi = os.getenv('wifi_ssid', '')
wifi_pass = os.getenv('wifi_password', '')

def get_ip_address():
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Connect to a dummy address
        s.connect(("8.8.8.8", 80))
        
        # Get the local IP address
        ip_address = s.getsockname()[0]
        
        # Close the socket
        s.close()
        
        return ip_address
    except socket.error:
        return "Could not retrieve IP address"

# Test the function
# print("IP Address:", get_ip_address())


def qr_gen():
    ip_address = get_ip_address()
    img = qrcode.make(f'''
    To connect to device:
    Turn on Hotspot 
    or
    Change your hotspot to:
    SSID/WIFI name: {wifi}
    Password: {wifi_pass}
    For Configuration Open Browser to:
    {ip_address}:5000
    ''')

    type(img)  # qrcode.image.pil.PilImage
    img.save(os.path.dirname(os.path.realpath(__file__))+"//qr.png")

qr_gen()