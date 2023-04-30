from dotenv import load_dotenv
import os
import base64
import requests
import json
import time
from urllib import request


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

    # Extract access token from response
    if response.status_code == 200:
        access_token = response.json()["access_token"]
        print("Access token obtained successfully.")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        access_token = None
    print(access_token)
    return access_token


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
        cur_song = [track_id,track_name,artists,album_name]
        print(cur_song)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        cur_song = ""

    return cur_song


def get_cover_art(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)

    # Extract information about user's current playing song from response
    if response.status_code == 200:
        track_id = response.json()["item"]["id"]
        album_id = response.json()["item"]["album"]["id"]
        album_name = response.json()["item"]["album"]["name"]
        artists = [artist["name"] for artist in response.json()["item"]["artists"]]
        cur_song = f"You are currently playing: {track_id} by {', '.join(artists)} from the album {album_name}"
        
        # Get album details
        album_response = requests.get(f"https://api.spotify.com/v1/albums/{album_id}", headers=headers)
        if album_response.status_code == 200:
            cover_art_url = album_response.json()["images"][0]["url"]
            print(f"Album cover art for '{album_name}' by {', '.join(artists)}: {cover_art_url}")
        else:
            print(f"Error: {album_response.status_code} - {album_response.text}")
            cover_art_url = ""
    else:
        print(f"Error: {response.status_code} - {response.text}")
        cover_art_url = ""

    return cover_art_url

def get_video(id,newtoken):
    #using delitefully's api not stable or trusted source
    print("called get video")
    url = "https://api.delitefully.com/api/canvas/"+id
    vidurl = ""
    response = requests.get(url)

    # Extract information about user's current playing song from response
    if response.json()["success"] == "true":
        print("canvas found")
        vidurl = response.json()["canvas_url"]
        print(vidurl)
        return vidurl
    else:
        print("canvas not found")
        get_cover_art(newtoken)


    

def main():
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    song = []
    # token = get_token(client_id, client_secret)

    auth_request_url = get_authorization_request_url(client_id)
    authorization_code = input("Enter the authorization code provided by Spotify: ")
    newtoken=exchange_authorization_code_for_token(client_id, client_secret, authorization_code)
    while True:
        if song != get_current_song(newtoken):
            song = get_current_song(newtoken)
            get_video(song[0],newtoken)
            # get_cover_art(newtoken)
        time.sleep(5)

main()