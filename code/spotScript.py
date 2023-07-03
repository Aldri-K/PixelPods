from dotenv import load_dotenv
import os
import base64
import requests
import json
import time
from urllib import request
import subprocess

def display_error_image():
    print(" display_error_image called")
    # Function to display an error image
    subprocess.run(["sudo", "fbi", "-T", "1", "-a", "--noverbose", "AKLogo.png"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(10)

def get_authorization_request_url(client_id):
    print("get_authorization_request_url called")
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
    print("exchange_authorization_code_for_token called")
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
    print("refresh_access_token called")
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
    print("get_current_song called")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)
    try:
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
            return cur_song
        elif response.status_code == 204:
            print("No song is currently playing.")
            return None
        if response.status_code == 401:
            print("Access token has expired. Refreshing token...")
            new_access_token = refresh_access_token(refresh_token, client_id, client_secret)

            if new_access_token is not None:
                # Update the access token
                access_token = new_access_token
                # Retry the API request with the new access token
                response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)
            else:
                print("Failed to refresh access token.")
                display_error_image()
                return None

        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    except:
        display_error_image()


def get_cover_art(track_id, access_token):
    print("get_cover_art called")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"https://api.spotify.com/v1/tracks/{track_id}", headers=headers)

    # Extract cover art URL from response
    if response.status_code == 200:
        cover_art_url = response.json()["album"]["images"][0]["url"]
        return cover_art_url
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


def display_cover_art(cover_art_url):
    print("display_cover_art called")
    subprocess.run(["wget", cover_art_url, "-O", "cover_art.jpg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["sudo", "fbi", "-T", "1", "-a", "--noverbose", "cover_art.jpg"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)



def load_dotenv_file():
    print("load_dotenv_file called")
    dotenv_path = ".env"
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        return True
    else:
        return False


def create_dotenv_file(client_id, client_secret, access_token, refresh_token):
    print("create_dotenv_file called")
    with open(".env", "w") as file:
        file.write(f"CLIENT_ID={client_id}\n")
        file.write(f"CLIENT_SECRET={client_secret}\n")
        file.write(f"ACCESS_TOKEN={access_token}\n")
        file.write(f"REFRESH_TOKEN={refresh_token}\n")
    print("Tokens stored in .env file.")

def validate_tokens(access_token, refresh_token):
    print("validate_tokens called")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)

    if response.status_code == 401:
        print("Access token has expired or is invalid.")
        return False
    elif response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return False

    return True


def authorize_spotify():
    print("authurize spotify called")
    client_id = input("Enter your Spotify client ID: ")
    client_secret = input("Enter your Spotify client secret: ")

    auth_request_url = get_authorization_request_url(client_id)
    authorization_code = input("Enter the authorization code provided by Spotify: ")
    access_token, refresh_token = exchange_authorization_code_for_token(client_id, client_secret, authorization_code)

    # Validate the obtained tokens
    while not validate_tokens(access_token, refresh_token):
        print("Failed to obtain valid access token. Please try again.")
        authorization_code = input("Enter the authorization code provided by Spotify: ")
        access_token, refresh_token = exchange_authorization_code_for_token(client_id, client_secret, authorization_code)

    # Store tokens in .env file
    create_dotenv_file(client_id, client_secret, access_token, refresh_token)

    return client_id, client_secret, access_token, refresh_token



def main():
    print("main called")
    client_id = "YOUR_CLIENT_ID"
    client_secret = "YOUR_CLIENT_SECRET"

    # Load tokens from .env file if it exists
    dotenv_loaded = load_dotenv_file()

    if dotenv_loaded:
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        access_token = os.getenv("ACCESS_TOKEN")
        refresh_token = os.getenv("REFRESH_TOKEN")
        print("Tokens loaded from .env file.")
    else:
        # No .env file found, authorize Spotify
        client_id, client_secret, access_token, refresh_token = authorize_spotify()

    # Track the current song and cover art URL
    current_song = None
    cover_art_url = None

    while True:
        if not validate_tokens(access_token, refresh_token):
            client_id, client_secret, access_token, refresh_token = authorize_spotify()

        new_song = get_current_song(access_token)

        if new_song is None:
            display_error_image()
            current_song = None
            cover_art_url = None
        elif new_song != current_song:
            current_song = new_song
            if current_song:
                new_cover_art_url = get_cover_art(current_song["track_id"], access_token)
                if new_cover_art_url != cover_art_url:
                    # Close the existing image display
                    subprocess.run(["sudo", "killall", "fbi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    # Display the new cover art or error image
                    if new_cover_art_url:
                        display_cover_art(new_cover_art_url)
                        cover_art_url = new_cover_art_url
                    else:
                        display_error_image()

        # Wait for some time before checking the current song again
        time.sleep(1)

if __name__ == "__main__":
    main()
