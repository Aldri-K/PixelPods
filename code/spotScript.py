import os
import base64
import requests
import json
import time

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/callback"
SCOPE = "user-read-currently-playing"
AUTHORIZATION_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"

access_token = os.getenv("ACCESS_TOKEN")
refresh_token = os.getenv("REFRESH_TOKEN")


def get_authorization_request_url(client_id):
    query_params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    }
    authorization_request_url = f"{AUTHORIZATION_URL}?{'&'.join([f'{key}={value}' for key, value in query_params.items()])}"
    return authorization_request_url


def get_tokens(authorization_code):
    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()}",
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data["access_token"]
        refresh_token = response_data["refresh_token"]
        return access_token, refresh_token
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None, None


def refresh_access_token(refresh_token):
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()}",
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data["access_token"]
        return access_token
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def get_current_song(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{API_BASE_URL}/me/player/currently-playing", headers=headers)

    if response.status_code == 200:
        track_data = response.json()["item"]
        artists = [artist["name"] for artist in track_data["artists"]]
        album_name = track_data["album"]["name"]
        cur_song = {
            "track_id": track_data["id"],
            "track_name": track_data["name"],
            "artists": artists,
            "album_name": album_name,
        }
        print(f"You are currently playing: {cur_song['track_name']} by {', '.join(cur_song['artists'])} from the album {cur_song['album_name']}")
        return cur_song
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def get_cover_art(track_id, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{API_BASE_URL}/tracks/{track_id}", headers=headers)

    if response.status_code == 200:
        album_data = response.json()["album"]
        cover_art_url = album_data["images"][0]["url"]
        print(f"Album cover art for '{album_data['name']}' by {', '.join([artist['name'] for artist in album_data['artists']])}: {cover_art_url}")
        return cover_art_url
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def save_tokens(access_token, refresh_token):
    with open(".env", "a") as file:
        file.write(f"ACCESS_TOKEN={access_token}\n")
        file.write(f"REFRESH_TOKEN={refresh_token}\n")


def main():
    global access_token
    global refresh_token

    if access_token is None or refresh_token is None:
        authorization_request_url = get_authorization_request_url(CLIENT_ID)
        print(f"Please grant access to your Spotify account by visiting the following URL:\n{authorization_request_url}\n")
        authorization_code = input("Enter the authorization code provided by Spotify: ")

        access_token, refresh_token = get_tokens(authorization_code)
        if access_token is None or refresh_token is None:
            return

        save_tokens(access_token, refresh_token)

    song = None

    while True:
        current_song = get_current_song(access_token)

        if current_song != song:
            song = current_song
            if song:
                cover_art_url = get_cover_art(song["track_id"], access_token)
                # Perform any other actions with the song data or cover art URL here

        access_token = refresh_access_token(refresh_token)
        time.sleep(5)


if __name__ == "__main__":
    main()
