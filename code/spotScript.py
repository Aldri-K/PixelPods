from dotenv import load_dotenv
import os
import base64
import requests
import json
import time
from urllib import request
import subprocess


def get_authorization_request_url(client_id):
    authorization_url = "https://accounts.spotify.com/authorize"
    query_params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": "http://localhost:8000/callback",
        "scope": "user-read-currently-playing"
    }
    authorization_request_url = f"{authorization_url}?{'&'.join([f'{key}={value}' for key, value in query_params.items()])}"
    print(f"Please grant access to your Spotify account by visiting the following URL:\n{authorization_request_url}\n")

    return authorization_request_url


def exchange_authorization_code_for_token(client_id, client_secret, authorization_code):
    token_url = "https://accounts.spotify.com/api/token"
    auth_header = f"{client_id}:{client_secret}"
    auth_header_b64 = base64.b64encode(auth_header.encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": "http://localhost:8000/callback"
    }
    response = requests.post(token_url, headers=headers, data=data)

    # Extract access token and refresh token from response
    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data["access_token"]
        refresh_token = response_data["refresh_token"]
        print("Access token obtained successfully.")
        return access_token, refresh_token
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None, None


def refresh_access_token(refresh_token, client_id, client_secret):
    token_url = "https://accounts.spotify.com/api/token"
    auth_header = f"{client_id}:{client_secret}"
    auth_header_b64 = base64.b64encode(auth_header.encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header_b64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    response = requests.post(token_url, headers=headers, data=data)

    # Extract refreshed access token from response
    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data["access_token"]
        print("Access token refreshed successfully.")
        return access_token
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def get_current_song(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)

    # Extract information about user's current playing song from response
    if response.status_code == 200:
        track_id = response.json()["item"]["id"]
        track_name = response.json()["item"]["name"]
        artists = [artist["name"] for artist in response.json()["item"]["artists"]]
        album_name = response.json()["item"]["album"]["name"]
        cur_song = {
            "track_id": track_id,
            "track_name": track_name,
            "artists": artists,
            "album_name": album_name
        }
        print(f"You are currently playing: {track_name} by {', '.join(artists)} from the album {album_name}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        cur_song = None

    return cur_song


def get_cover_art(track_id, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers)

    # Extract cover art URL from track information
    if response.status_code == 200:
        cover_art_url = response.json()["album"]["images"][0]["url"]
        print(f"Album cover art URL: {cover_art_url}")
        return cover_art_url
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def display_cover_art(cover_art_url):
    if not cover_art_url:
        return

    image_file = "/tmp/cover.jpg"

    # Download the cover art image
    response = requests.get(cover_art_url)
    if response.status_code == 200:
        with open(image_file, "wb") as file:
            file.write(response.content)
    else:
        print(f"Error: {response.status_code} - Failed to download cover art")
        return

    # Display the image using fbi
    subprocess.run(["fbi", "-noverbose", "-a", image_file])


def create_dotenv_file(client_id, client_secret, access_token, refresh_token):
    with open(".env", "w") as file:
        file.write(f"CLIENT_ID={client_id}\n")
        file.write(f"CLIENT_SECRET={client_secret}\n")
        file.write(f"ACCESS_TOKEN={access_token}\n")
        file.write(f"REFRESH_TOKEN={refresh_token}\n")


def load_dotenv_file():
    if not os.path.exists(".env"):
        return False

    load_dotenv(".env")
    return True


def main():
    client_id = "YOUR_CLIENT_ID"
    client_secret = "YOUR_CLIENT_SECRET"

    # Load tokens from .env file if it exists
    dotenv_loaded = load_dotenv_file()

    if dotenv_loaded:
        access_token = os.getenv("ACCESS_TOKEN")
        refresh_token = os.getenv("REFRESH_TOKEN")
        print("Tokens loaded from .env file.")
    else:
        # No .env file found, prompt for authorization
        auth_request_url = get_authorization_request_url(client_id)
        authorization_code = input("Enter the authorization code provided by Spotify: ")
        access_token, refresh_token = exchange_authorization_code_for_token(client_id, client_secret, authorization_code)

        # Store tokens in .env file
        create_dotenv_file(client_id, client_secret, access_token, refresh_token)

    # Track the current song and cover art URL
    song = None
    cover_art_url = None

    while True:
        current_song = get_current_song(access_token)

        if current_song != song:
            song = current_song
            if song:
                new_cover_art_url = get_cover_art(song["track_id"], access_token)
                if new_cover_art_url != cover_art_url:
                    # Close the existing image display
                    subprocess.run(["killall", "fbi"])

                    # Display the new cover art
                    display_cover_art(new_cover_art_url)
                    cover_art_url = new_cover_art_url

        # Wait for some time before checking the current song again
        time.sleep(5)


if __name__ == "__main__":
    main()
