from yt_dlp import YoutubeDL

YDL_OPTS = {
    "extract-flat": True,
    "quiet": True
}

def get_song_names(playlist_url):
    with YoutubeDL(YDL_OPTS) as ydl:
        playlist = ydl.extract_info(playlist_url, download=False)

    result = [ song["title"] for song in playlist["entries"] ]
    return result