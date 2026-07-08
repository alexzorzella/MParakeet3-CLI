import queue
import threading
from pathlib import Path
from time import sleep

import vlc
from mutagen.mp3 import MP3

PREVIEW_LENGTH = 5

class ThreadedVlcPlayer:
    vlc_instance = None
    player = None

    song_queue = []
    current_head_index = -1

    thread = None

    commands = None

    def __init__(self):
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

        events = self.player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, lambda event: self._on_end())

        self.commands = queue.Queue()

        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        while True:
            func, args = self.commands.get()
            func(*args)

    def _on_end(self):
        self.commands.put((self.play_head, (True,)))

    def play(self):
        if self.player is not None:
            self.player.play()

    def stop(self):
        if self.player is not None:
            self.player.stop()

    def queue_song_force_play(self, path):
        self.queue_song_next(path=path)
        self.play_head(advance=True)

    def debug_print_queue(self, paths):
        return f"{[Path(path).stem for path in paths]}"

    def queue_song_next(self, path):
        if len(self.song_queue) > 0:
            self.song_queue.insert(self.current_head_index + 1, path)
            print(f"Queued {Path(path).stem} next, current queue: {self.debug_print_queue(paths=self.song_queue)}")
        else:
            self.queue_song(path=path)

    def queue_song(self, path):
        self.song_queue.append(path)

        print(f"Queued {Path(path).stem} to end, current queue: {self.debug_print_queue(paths=self.song_queue)}")

    def play_head(self, advance: bool = False):
        if advance:
            self.current_head_index += 1

        print(f"play_head called while pointing to track {self.current_head_index}")

        if self.current_head_index >= len(self.song_queue):
            print(f"Queue exhausted")
            return

        try:
            current_song = self.song_queue[self.current_head_index]

            print(f"Current song now: {Path(current_song).stem}, attempting to play it")

            media = self.vlc_instance.media_new(current_song)
            self.player.set_media(media)
            self.player.play()

            print(f"Played {Path(current_song).stem} (Queue track {self.current_head_index})")
        except Exception as e:
            print(f"Error while attempting to play next song: {e}")

    def preview(self, from_path, to_path):
        self.stop()

        self.queue_song_next(path=to_path)
        self.queue_song_next(path=from_path)

        self.play_head(advance=True)

        song_ending = MP3(from_path)
        song_ending_length = song_ending.info.length
        start_song_ending_at = max(0, song_ending_length - PREVIEW_LENGTH)
        self.player.set_time(int(start_song_ending_at * 1000))