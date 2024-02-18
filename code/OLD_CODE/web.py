import os
import time
import spotipy
import requests
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
from flask import Flask, render_template, send_file, Response
import base64
from selenium import webdriver

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("REDIRECT_URI")

app = Flask(__name__)
app.static_folder = 'downloads'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="user-read-playback-state"))

# Ensure the downloads directory exists
downloads_dir = "C:/Users/RDK/Downloads/New folder (2)/PixelPods/code/downloads"

if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)

update_display = False
last_track_id = None

script_directory = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to chromedriver
chromedriver_path = os.path.join(script_directory, 'chromedriver')

# Initialize WebDriver using the absolute path
driver = webdriver.Chrome(executable_path=chromedriver_path)

# Open a URL in Chrome
url_to_open = 'http://127.0.0.1:5000/'  # Replace with your desired URL
time.sleep(5)


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

def get_best_image(images):
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

def play_video(video_path):

    driver.maximize_window()  # Maximize the browser window for fullscreen
    driver.get('file://' + video_path.replace("\\", "/"))  # Load the local video file

    time.sleep(1)  # Give some time for the video to load
    video = driver.find_element_by_tag_name('video')
    video.play()  # Autoplay the video
    return driver.page_source

@app.route('/downloads/<path:filename>')
def download_file(filename):
    video_path = os.path.join(downloads_dir, filename)
    return send_file(video_path, as_attachment=True)

@app.route('/')
def index():
    global update_display, last_track_id
    driver.get(url_to_open)
    try:
        currently_playing = sp.current_playback()
        if currently_playing:
            track = currently_playing["item"]
            track_id = track["id"]
            if track_id != last_track_id:
                clear_directory(downloads_dir)
                last_track_id = track_id
                album = track["album"]
                track_link = track["external_urls"]["spotify"]
                print(f"Listening to: {track['name']} - {track_link}")
                video_path = download_canvas_video(track["name"], track_link)
                if video_path:
                    update_display = video_path
                else:
                    image_url = get_best_image(album["images"])
                    download_path = os.path.join(downloads_dir, track_id + ".jpg")
                    download_image(image_url, download_path)
                    update_display = download_path

    except Exception as e:
        print(f"An error occurred: {e}")

    if not update_display:
        update_display = False

    if update_display:
        if update_display.endswith(".jpg"):
            with open(update_display, 'rb') as image_file:
                image_data = image_file.read()
            return f'<img src="data:image/jpeg;base64,{base64.b64encode(image_data).decode()}" alt="Image">'
        else:
            return play_video(update_display)

    return "No valid content to display."

if __name__ == '__main__':
    app.run(debug=True)
    driver.get(url_to_open)
