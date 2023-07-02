from dotenv import load_dotenv, set_key
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
        access_token = response.json()["access_token"]
        refresh_token = response.json()["refresh_token"]
        print("Access token obtained successfully.")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        access_token = None
        refresh_token = None

    return access_token, refresh_token


def create_dotenv_file(client_id, client_secret, access_token, refresh_token):
    dotenv_data = f"CLIENT_ID={client_id}\nCLIENT_SECRET={client_secret}\nACCESS_TOKEN={access_token}\nREFRESH_TOKEN={refresh_token}"
    with open(".env", "w") as file:
        file.write(dotenv_data)


def load_dotenv_file():
    if os.path.exists(".env"):
        load_dotenv(".env")
        return True
    return False


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
        print(f"You are currently playing: {track_name} by {', '.join(artists)} from the album {album_name} ID: {track_id}")
        cur_song = {
            "track_id": track_id,
            "track_name": track_name,
            "artists": artists,
            "album_name": album_name
        }
    else:
        print(f"Error: {response.status_code} - {response.text}")
        cur_song = None

    return cur_song


def get_cover_art(track_id, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers)

    # Extract cover art URL from response
    if response.status_code == 200:
        album_id = response.json()["album"]["id"]
        album_response = requests.get(f"https://api.spotify.com/v1/albums/{album_id}", headers=headers)
        if album_response.status_code == 200:
            cover_art_url = album_response.json()["images"][0]["url"]
            return cover_art_url
        else:
            print(f"Error: {album_response.status_code} - {album_response.text}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

    return None


def is_token_expired():
    if "TOKEN_EXPIRATION" in os.environ:
        expiration_time = int(os.environ["TOKEN_EXPIRATION"])
        current_time = int(time.time())
        return expiration_time <= current_time
    return True


def refresh_access_token(client_id, client_secret, refresh_token):
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

    # Extract new access token from response
    if response.status_code == 200:
        access_token = response.json()["access_token"]
        refresh_token = response.json().get("refresh_token", refresh_token)
        token_expiration = int(time.time()) + response.json()["expires_in"]
        set_key(".env", "ACCESS_TOKEN", access_token)
        set_key(".env", "REFRESH_TOKEN", refresh_token)
        set_key(".env", "TOKEN_EXPIRATION", str(token_expiration))
        print("Access token refreshed successfully.")
        return access_token
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def display_cover_art(image_url):
    # Close the existing fbi process if it's running
    subprocess.run(["sudo", "pkill", "-f", "fbi"])

    # Display the cover art using fbi
    subprocess.run(["sudo", "fbi", "-d", "/dev/fb0", "-T", "1", image_url])


def main():
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    refresh_token = os.getenv("REFRESH_TOKEN")

    if not client_id or not client_secret or not access_token or not refresh_token:
        # No tokens found, perform authorization
        client_id = input("Enter your Spotify client ID: ")
        auth_request_url = get_authorization_request_url(client_id)
        authorization_code = input("Enter the authorization code provided by Spotify: ")
        access_token, refresh_token = exchange_authorization_code_for_token(client_id, client_secret, authorization_code)
        create_dotenv_file(client_id, client_secret, access_token, refresh_token)
    elif is_token_expired():
        # Access token has expired, refresh it
        access_token = refresh_access_token(client_id, client_secret, refresh_token)

    song = None
    cover_art_url = None

    while True:
        current_song = get_current_song(access_token)

        if current_song != song:
            song = current_song
            if song:
                cover_art_url = get_cover_art(song["track_id"], access_token)
                if cover_art_url:
                    display_cover_art(cover_art_url)


if __name__ == "__main__":
    main()