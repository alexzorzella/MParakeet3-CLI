import time

import vlc
from mutagen.mp3 import MP3

PREVIEW_LENGTH = 5

class ThreadedVlcPlayer:
    def __init__(self):
        self.song_starting_player = None
        self.song_ending_player = None

    def play(self, from_path):
        self.stop()

        self.song_starting_player = vlc.MediaPlayer(from_path)
        self.song_starting_player.play()

    def stop(self):
        if self.song_starting_player is not None:
            self.song_starting_player.stop()

        if self.song_ending_player is not None:
            self.song_ending_player.stop()

    def preview(self, from_path, to_path):
        self.stop()

        song_ending = MP3(from_path)
        song_ending_length = song_ending.info.length

        start_song_ending_at = max(0, song_ending_length - PREVIEW_LENGTH)

        self.song_ending_player = vlc.MediaPlayer(from_path)
        self.song_starting_player = vlc.MediaPlayer(to_path)

        self.song_ending_player.play()

        time.sleep(0.1)
        self.song_ending_player.set_time(int(start_song_ending_at * 1000))
        time.sleep(PREVIEW_LENGTH + 0.1)
        self.song_starting_player.play()
        time.sleep(PREVIEW_LENGTH)
        self.song_starting_player.stop()