import os
import time
import spotipy
import requests
from spotipy.oauth2 import SpotifyOAuth
from bs4 import BeautifulSoup
from flask import Flask, render_template, Response
import base64

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
downloads_dir = "./downloads"
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)

update_display = False
last_track_id = None

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


def play_video(video_path):
    # Implement video playback here using HTML5 video tags
    # Replace this with actual video playback logic
    return f"""
    <video width="640" height="360" controls>
        <source src="{video_path}" type="video/mp4">
        Your browser does not support the video tag.
    </video>
    """
@app.route('/')
def index():
    global update_display, last_track_id

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
                    update_display = video_path  # Trigger an update to display video
                else:
                    image_url = get_best_image(album["images"])
                    download_path = os.path.join(downloads_dir, track_id + ".jpg")
                    download_image(image_url, download_path)
                    update_display = download_path  # Trigger an update to display image

    except Exception as e:
        print(f"An error occurred: {e}")
    
    # Set update_display to False if no valid update is found
    if not update_display:
        update_display = False

    if update_display:
        if update_display.endswith(".jpg"):
            # Display the image
            with open(update_display, 'rb') as image_file:
                image_data = image_file.read()
            return f'<img src="data:image/jpeg;base64,{base64.b64encode(image_data).decode()}" alt="Image">'
        else:
            # Render the video template
            return render_template('video.html', video_path=update_display)
    
    # Return a default response if update_display is still False
    return "No valid content to display."

if __name__ == '__main__':
    app.run(debug=True)
