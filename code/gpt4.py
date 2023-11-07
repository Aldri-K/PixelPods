import os
import time
import spotipy
import requests
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
import PySimpleGUI as sg
import vlc
from PIL import Image
from io import BytesIO
import platform


# Load environment variables
from dotenv import load_dotenv
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

update_display = False
last_track_id = None

def get_best_image(images):
    """
    Return the URL of the largest image from the list of images.
    """
    if not images:
        return None
    largest_image = sorted(images, key=lambda x: x['width'], reverse=True)[0]
    return largest_image['url']

def download_image(url, path):
    with requests.get(url, stream=True) as response:
        with open(path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

def download_canvas_video(track_name, track_link):
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

def create_window():
    layout = [
        [sg.Image(key='-IMAGE-')],
        [sg.Canvas(key='-VIDEO-')]
    ]
    return sg.Window('Spotify Viewer', layout, finalize=True)

def play_video(video_path):
    vlc_instance = vlc.Instance("--loop")  # Enable looping
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(video_path)
    player.set_media(media)
    player.play()

    # Check the current track and loop until it changes
    global last_track_id
    while True:
        time.sleep(1)  # Check every second
        currently_playing = sp.current_playback()
        if currently_playing is None or currently_playing["item"]["id"] != last_track_id:
            break  # Stop the loop if the song has changed

    player.stop()  # Stop the player once the song changes

def display_image_with_pygui(window, image_path):
    image = Image.open(image_path)
    bio = BytesIO()
    image.save(bio, format="PNG")
    window['-IMAGE-'].update(data=bio.getvalue())

# Define the window layout for images
layout = [
    [sg.Image(key='-IMAGE-')],
]

# Create the window for images
window = sg.Window('Spotify Image Viewer', layout, finalize=True)
while True:
    update_display = False  # Reset the flag at the beginning of the loop
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
                video_path = download_canvas_video(track["name"], track_link)
                if video_path:
                    window.Hide()  # Hide the image window
                    play_video(video_path)
                    window.UnHide()  # Show the image window again
                else:
                    image_url = get_best_image(album["images"])
                    download_path = os.path.join(downloads_dir, track_id + ".jpg")
                    download_image(image_url, download_path)
                    display_image_with_pygui(window, download_path)

        # Event handling for PySimpleGUI window
        event, values = window.read(timeout=100)  # Poll every 100 ms
        if event == sg.WIN_CLOSED:
            break
    except Exception as e:
        print(f"An error occurred: {e}")
    time.sleep(1)

window.close()