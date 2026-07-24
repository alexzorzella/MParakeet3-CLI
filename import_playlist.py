import re
from ytmusicapi import YTMusic

def extract_playlist_id(url: str) -> str:
    match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
    return match.group(1) if match else url

def get_song_names(playlist_url):
    playlist_id = extract_playlist_id(playlist_url)

    ytmusic = YTMusic()
    playlist_data = ytmusic.get_playlist(playlist_id)

    result = []

    for song in playlist_data["tracks"]:
        # artists = [ artist["name"] for artist in song["artists"] ]
        result.append(song["title"])

    return result