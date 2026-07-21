import queue
from pathlib import Path

import vlc
from PySide6.QtCore import QThread
from PySide6.QtWidgets import QListWidgetItem

from tracklist import Tracklist

PREVIEW_LENGTH = 5

class ThreadedVlcPlayer(QThread):
    vlc_instance = None
    player = None

    tracklist: Tracklist | None = None
    current_head_widget: QListWidgetItem | None = None

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

    def update_tracklist(self, new_tracklist: Tracklist):
        self.tracklist = new_tracklist
        print(f"Updated tracklist to {self.tracklist}")

    def play(self, media):
        if self.player is not None:
            self.player.set_media(media)
            self.player.play()

    def stop(self):
        if self.player is not None:
            self.player.stop()

    def advance_head(self):
        if self.current_head_widget is None:
            self.current_head_widget = self.tracklist.get_widget_at_index(0)
        else:
            self.current_head_widget = self.tracklist.get_widget_after(self.current_head_widget)

    def play_song_at_head(self):
        if self.current_head_widget is None:
            print(f"Queue exhausted")
            return

        print(f"play_head called while pointing to track {self.tracklist.get_index_of_widget(self.current_head_widget)}")

        try:
            current_song_entry = self.tracklist.get_song_entry_by_list_widget_item(self.current_head_widget)
            current_song = current_song_entry.filepath

            print(f"Current song now: {Path(current_song).stem}, attempting to play it")

            media = self.vlc_instance.media_new(current_song)
            self.play(media)

            print(f"Played {Path(current_song).stem} (Queue track {self.tracklist.get_index_of_widget(self.current_head_widget)})")
        except Exception as e:
            print(f"Error while attempting to play next song: {e}")

    def play_head(self, advance: bool = False):
        if advance:
            self.advance_head()

        self.play_song_at_head()

    def skip_forward(self):
        self.advance_head()
        self.stop()
        self.play_song_at_head()

    def queue_command(self, function, args):
        self.commands.put((function, args))