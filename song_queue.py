from PySide6.QtWidgets import QLabel
from mutagen.mp3 import MP3

from mix_view import MixView
from threaded_vlc_player import PREVIEW_LENGTH, ThreadedVlcPlayer

class SongQueue():
    player: ThreadedVlcPlayer
    mix_view: MixView

    current_head_index: int = -1

    currently_playing_label: QLabel

    def __init__(self, mix_view: MixView, player: ThreadedVlcPlayer, currently_playing_label):
        self.mix_view = mix_view
        self.player = player
        self.currently_playing_label = currently_playing_label

        self.player.song_changed.connect(self.on_song_changed)

    def on_song_changed(self, new_song):
        self.currently_playing_label.setText(new_song.name())

    def update_current_head_index(self, new_index):
        self.current_head_index = new_index

    def queue_song_force_play(self, path):
        print(f"Queueing {path.stem} and playing")
        self.queue_song_next(path=path)
        self.player.queue_command(self.player.play_head, (True,))

    def queue_song(self, path):
        print(f"Queuing {path.stem}")
        self.mix_view.add_song_to_mix(passed_path=path)
        self.update_player_tracklist()

    def queue_song_next(self, path):
        index = self.current_head_index + 1
        print(f"Queuing {path.stem} to {index}")
        self.mix_view.add_song_to_mix(passed_path=path, index=index)
        self.update_player_tracklist()

    def preview(self, from_path, to_path):
        print(f"Previewing from {from_path.stem} to {to_path.stem}")

        self.player.queue_command(self.player.stop, ())

        self.queue_song_next(path=to_path)
        self.queue_song_next(path=from_path)

        self.player.queue_command(self.player.play_head, (True,))

        song_ending = MP3(from_path)
        song_ending_length = song_ending.info.length
        start_song_ending_at = max(0, song_ending_length - PREVIEW_LENGTH)

        time = int(start_song_ending_at * 1000)

        self.player.queue_command(self.player.set_time, (time,))

    def update_player_tracklist(self):
        tracklist = self.mix_view.current_tracklist
        self.player.queue_command(self.player.update_tracklist, (tracklist,))