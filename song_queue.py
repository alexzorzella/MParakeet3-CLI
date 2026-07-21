from mutagen.mp3 import MP3

from mix_utility import MixUtility
from mix_view import MixView
from threaded_vlc_player import PREVIEW_LENGTH, ThreadedVlcPlayer

class SongQueue():
    mix_util: MixUtility
    mix_view: MixView

    current_head_index: int = -1

    def __init__(self, mix_view: MixView):
        self.mix_view = mix_view
        self.mix_util = mix_view.mix_util

    def update_current_head_index(self, new_index):
        self.current_head_index = new_index

    def queue_song_force_play(self, path):
        print(f"Queueing {path.stem} and playing")
        self.queue_song_next(path=path)
        # self.mix_util.queue_player_command(self.mix_util.player.play_head, (True,))

    def queue_song_next(self, path):
        index = self.current_head_index + 1
        print(f"Queuing {path.stem} to {index}")
        self.mix_view.add_song_to_mix(passed_path=path, index=index)

    def queue_song(self, path):
        print(f"Queuing {path.stem}")
        self.mix_view.add_song_to_mix(passed_path=path)

    def preview(self, from_path, to_path):
        print(f"Previewing from {from_path.stem} to {to_path.stem}")

        # self.mix_util.queue_player_command(self.mix_util.player.stop, ())

        self.queue_song_next(path=to_path)
        self.queue_song_next(path=from_path)

        # self.mix_util.queue_player_command(self.mix_util.player.play_head, (True,))

        song_ending = MP3(from_path)
        song_ending_length = song_ending.info.length
        start_song_ending_at = max(0, song_ending_length - PREVIEW_LENGTH)

        time = int(start_song_ending_at * 1000)

        # self.mix_util.queue_player_command(self.mix_util.player.set_time, (time,))