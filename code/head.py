import os
import time
import subprocess
from dotenv import load_dotenv



load_dotenv(dotenv_path = '/home/rdk/Downloads/PixelPods/.env')

print (os.path.dirname(os.path.abspath(__file__)))
SPOTIPY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("REDIRECT_URI")

print(SPOTIPY_CLIENT_ID)