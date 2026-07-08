import time
from email.charset import add_codec
from pathlib import Path

import vlc
from mutagen.mp3 import MP3
from yt_dlp.aes import aes_gcm_decrypt_and_verify

PREVIEW_LENGTH = 5

class ThreadedVlcPlayer:
    player = None

    song_queue = []
    current_head_index = 0

    def queue_song_force_play(self, path):
        self.queue_song_next(path=path)
        self.play_head(advance=True if len(self.song_queue) > 1 else False)

    def queue_song_next(self, path):
        self.song_queue.insert(self.current_head_index + 1, path)

        print(f"Queued next, {self.song_queue}")

    def queue_song(self, path):
        self.song_queue.append(path)

        print(f"Queued to end, {self.song_queue}")

    def play_head(self, advance: bool = False):
        print(f"play_head called while pointing to element {self.current_head_index}")

        if self.current_head_index >= len(self.song_queue):
            return

        if advance:
            self.current_head_index += 1

        # self.stop()

        first_song = self.song_queue[self.current_head_index]
        self.player = vlc.MediaPlayer(first_song)
        self.player.play()

        print(f"Played {Path(first_song).stem} (Queue element {self.current_head_index})")

        events = self.player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, lambda event: self.play_head(advance=True))

    def play(self):
        if self.player is not None:
            self.player.play()

    def stop(self):
        if self.player is not None:
            self.player.stop()

    def preview(self, from_path, to_path):
        self.stop()

        self.queue_song_next(path=from_path)
        self.queue_song_next(path=to_path)

        self.play_head(advance=True if len(self.song_queue) > 2 else False)

        song_ending = MP3(from_path)
        song_ending_length = song_ending.info.length
        start_song_ending_at = max(0, song_ending_length - PREVIEW_LENGTH)
        self.player.set_time(int(start_song_ending_at * 1000))