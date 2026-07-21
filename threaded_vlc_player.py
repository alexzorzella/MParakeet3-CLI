import queue
from pathlib import Path

import vlc
from PySide6.QtCore import QThread

PREVIEW_LENGTH = 5

class ThreadedVlcPlayer(QThread):
    vlc_instance = None
    player = None

    tracklist = []
    current_head_index = -1

    thread = None

    commands = None

    def __init__(self):
        super().__init__()

        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

        events = self.player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, lambda event: self.on_end())

        self.commands = queue.Queue()

        self.start()

    def run(self):
        while True:
            func, args = self.commands.get()
            print(f"Received {func}({args})")
            func(*args)

    def on_end(self):
        self.commands.put((self.play_head, (True,)))

    def update_tracklist(self, new_tracklist):
        self.tracklist = new_tracklist

    def play(self, media):
        if self.player is not None:
            self.player.set_media(media)
            self.player.play()

    def stop(self):
        if self.player is not None:
            self.player.stop()

    def play_head(self, advance: bool = False):
        if advance:
            self.current_head_index += 1

        print(f"play_head called while pointing to track {self.current_head_index}")

        if self.current_head_index >= len(self.tracklist):
            print(f"Queue exhausted")
            self.current_head_index -= 1
            return

        try:
            current_song_entry = self.tracklist[self.current_head_index]
            current_song = current_song_entry.filepath

            print(f"Current song now: {Path(current_song).stem}, attempting to play it")

            media = self.vlc_instance.media_new(current_song)
            self.play(media)

            print(f"Played {Path(current_song).stem} (Queue track {self.current_head_index})")
        except Exception as e:
            print(f"Error while attempting to play next song: {e}")

    def queue_command(self, function, args):
        self.commands.put((function, args))