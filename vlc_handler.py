import time

import vlc
from mutagen.mp3 import MP3

PREVIEW_LENGTH = 5

class ThreadedVlcPlayer:
    def __init__(self):
        self.player = None

    def preview(self, from_path, to_path):
        song_ending = MP3(from_path)
        song_ending_length = song_ending.info.length

        start_song_ending_at = max(0, song_ending_length - PREVIEW_LENGTH)

        song_ending_player = vlc.MediaPlayer(from_path)
        song_starting_player = vlc.MediaPlayer(to_path)

        song_ending_player.play()

        time.sleep(0.1)
        song_ending_player.set_time(int(start_song_ending_at * 1000))
        time.sleep(PREVIEW_LENGTH + 0.1)
        song_starting_player.play()
        time.sleep(PREVIEW_LENGTH)
        song_starting_player.stop()