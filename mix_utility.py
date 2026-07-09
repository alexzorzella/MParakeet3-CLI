from collections import defaultdict
from pathlib import Path
from typing import Callable

from PySide6.QtWidgets import QListWidget
from mutagen.mp3 import MP3

from baklava import is_null_or_whitespace
from load_file_action import FileLoadAction
from sconfig import parse_config_with_fallbacks
from vlc_handler import ThreadedVlcPlayer

DEFAULT_MUSIC_DIR: Path = Path(__file__).resolve().parent / "Music"
DEFAULT_MIX_DIR: Path = Path(__file__).resolve().parent / "Mixes"

class MixUtility:
    list_widget: QListWidget | None = None
    add_song_file_load_action: FileLoadAction | None = None

    search_path: Path
    mix_path: Path

    music_library: defaultdict[str, MP3]
    player = ThreadedVlcPlayer()

    show_status_bar_message: Callable

    def __init__(self, show_status_bar_message: Callable):
        self.music_library = defaultdict()
        self.show_status_bar_message = show_status_bar_message
        self.parse_config_file()
        self.load_music()

    def parse_config_file(self):
        params = parse_config_with_fallbacks(config_path="config.ini", section="mix", params=[("search", str, ""), ("mixes", str, "")])

        self.search_path = Path(params["search"]) if not is_null_or_whitespace(params["search"]) else DEFAULT_MUSIC_DIR
        self.mix_path = Path(params["mixes"]) if not is_null_or_whitespace(params["mixes"]) else DEFAULT_MIX_DIR

        if not self.search_path.is_dir():
            self.search_path.mkdir(parents=True, exist_ok=False)

        if not self.mix_path.is_dir():
            self.mix_path.mkdir(parents=True, exist_ok=False)

    def load_music(self):
        files = list(self.search_path.rglob("*.mp3"))

        mp3s = [MP3(file) for file in files]

        for mp3 in mp3s:
            track_name = mp3.get('Title', Path(mp3.filename).stem)
            self.music_library[track_name] = mp3

        self.show_status_bar_message(f"Loaded {len(self.music_library)} mp3(s) from {self.search_path}", 8000)