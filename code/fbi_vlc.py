import os
import time
import subprocess
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("REDIRECT_URI")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="user-read-playback-state"))

# Ensure the downloads directory exists
downloads_dir = "./downloads"
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)

# Helper function to clear directory
def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

# Clear the downloads directory at the start
clear_directory(downloads_dir)

def get_best_image(images):
    """ Return the URL of the largest image from a list of images. """
    if not images:
        return None
    return max(images, key=lambda x: x['width'])['url']

def download_image(url, path):
    with requests.get(url, stream=True) as response:
        with open(path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

def download_canvas_video(track_name, track_link):
    """ Download the canvas video for a Spotify track (not used in this version). """
    canvas_link = f"https://www.canvasdownloader.com/canvas?link={track_link}"
    response = requests.get(canvas_link)
    soup = BeautifulSoup(response.text, 'html.parser')
    video_tag = soup.find("video")
    if video_tag:
        mp4_link = video_tag.find("source")["src"]
        download_path = os.path.join(downloads_dir, f"{track_name}.mp4")
        with requests.get(mp4_link, stream=True) as r:
            with open(download_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return download_path
    else:
        return None

def display_image_with_fbi(image_path):
    subprocess.run(['sudo','fbi', '-T', '10', '-d', '/dev/fb0', '--noverbose', '--autozoom', image_path])

last_track_id = None
while True:
    try:
        currently_playing = sp.current_playback()
        if currently_playing:
            track = currently_playing["item"]
            track_id = track["id"]
            if track_id != last_track_id:
                clear_directory(downloads_dir)  # Clear the downloads directory for a new track
                last_track_id = track_id
                album = track["album"]
                track_link = track["external_urls"]["spotify"]
                print(f"Listening to: {track['name']} - {track_link}")
                image_url = get_best_image(album["images"])
                download_path = os.path.join(downloads_dir, track_id + ".jpg")
                download_image(image_url, download_path)
                display_image_with_fbi(download_path)

        time.sleep(1)
    except Exception as e:
        print(f"An error occurred: {e}")



