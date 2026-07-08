from collections import defaultdict
from pathlib import Path

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QListWidget, QWidget, QApplication, QVBoxLayout,QAbstractItemView
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QListView, QHBoxLayout, QMainWindow

from baklava import create_button, set_tooltip, is_null_or_whitespace
from load_file_action import FileLoadAction
from sconfig import parse_config_with_fallbacks

from mutagen.mp3 import MP3

from song_entry import SongEntry

DEFAULT_MUSIC_DIR: Path = Path(__file__).resolve().parent / "Music"
DEFAULT_OUTPUT_DIR: Path = Path(__file__).resolve().parent / "Mixes"

class MixWindow(QMainWindow):
    list_widget: QListWidget | None = None
    add_song_file_load_action: FileLoadAction | None = None

    search_path: Path
    output_path: Path

    music: defaultdict[str, MP3] = defaultdict()

    current_tracklist: defaultdict[QWidget, SongEntry] = defaultdict()

    def __init__(self):
        super().__init__()
        self.parse_config_file()
        self.load_music()
        self.create_window()

    def create_window(self):
        self.setWindowTitle("Edit Mix")
        self.resize(880, 660)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        vertical_layout = QVBoxLayout(central_widget)
        self.create_list_widget(parent=vertical_layout)

        self.populate_menu_bar()

        hotbar = QHBoxLayout()
        height = 30

        create_button(container=hotbar,
                      text="Add Song(s)",
                      height=height,
                      tooltip="Add one or more audio files",
                      connect_to_method=self.add_song_to_mix)
        create_button(container=hotbar,
                      text="Add Break",
                      height=height,
                      tooltip="Add a break (good for cassettes, CDs)",
                      connect_to_method=self.add_break)

        vertical_layout.addLayout(hotbar)

    def parse_config_file(self):
        params = parse_config_with_fallbacks(config_path="config.ini", section="mix",
                                             params=[("search", str, ""), ("output", str, "")])

        self.search_path = Path(params["search"]) if not is_null_or_whitespace(params["search"]) else DEFAULT_MUSIC_DIR
        self.output_path = Path(params["output"]) if not is_null_or_whitespace(params["output"]) else DEFAULT_OUTPUT_DIR

        if not self.search_path.is_dir():
            self.search_path.mkdir(parents=True, exist_ok=False)

        if not self.output_path.is_dir():
            self.output_path.mkdir(parents=True, exist_ok=False)

    def populate_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        export_menu = menu_bar.addMenu("Export")
        mix_menu = menu_bar.addMenu("Mix")

        file_menu.setToolTipsVisible(True)
        export_menu.setToolTipsVisible(True)
        mix_menu.setToolTipsVisible(True)

        load_mix_action = file_menu.addAction("&Load Mix")
        export_mix_as_file = export_menu.addAction("As &File")
        export_mix_as_tracks = export_menu.addAction("As Ordered &Tracks")

        add_song_action = mix_menu.addAction("&Add Song(s)")
        add_song_action.triggered.connect(self.add_song_to_mix)

        load_mix_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        export_mix_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        export_mix_as_tracks_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        add_song_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        add_song_shortcut.activated.connect(self.add_song_to_mix)

        self.add_song_file_load_action = FileLoadAction(menu=mix_menu, name="&Recent", action=self.add_song_to_mix)

        set_tooltip(widget=load_mix_action, text="Load a mix from a .txt file (Ctrl+L)")
        set_tooltip(widget=export_mix_as_file, text="Export a mix from as a .txt file (Ctrl+S)")
        set_tooltip(widget=export_mix_as_tracks, text="Export a mix as ordered audio file (Ctrl+E)")
        set_tooltip(widget=add_song_action, text="Add one or more tracks to the mix (Ctrl+=)")

    def create_list_widget(self, parent):
        list_widget = QListWidget()
        list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        list_widget.setFlow(QListView.TopToBottom)
        list_widget.setWrapping(False)
        list_widget.setResizeMode(QListView.Adjust)
        list_widget.setMovement(QListView.Snap)
        list_widget.setIconSize(QSize(200,200))
        list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_widget = list_widget

        list_model = self.list_widget.model()

        list_model.rowsMoved.connect(self.update_cumulative_times)

        parent.addWidget(list_widget)

    def add_song_to_mix(self):
        paths = self.add_song_file_load_action.load_files(parent=self, caption="Select track(s)", directory=self.search_path.as_posix(), file_filter="File (*.mp3);;")

        if paths is None or len(paths) <= 0:
            return

        for path in paths:
            song_entry = SongEntry(filepath=Path(path))
            self.current_tracklist[song_entry.widget] = song_entry
            self.list_widget.addItem(song_entry.list_widget_item)
            self.list_widget.setItemWidget(song_entry.list_widget_item, song_entry.widget)

        self.update_cumulative_times()

    def add_break(self):
        song_entry = SongEntry(filepath=None, break_duration=45 * 60)
        self.current_tracklist[song_entry.widget] = song_entry
        self.list_widget.addItem(song_entry.list_widget_item)
        self.list_widget.setItemWidget(song_entry.list_widget_item, song_entry.widget)

        self.update_cumulative_times()

    def update_cumulative_times(self):
        print("Updating cumulative times")

        current_runtime: int = 0

        for i in range(self.list_widget.count()):
            list_widget_item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(list_widget_item)

            song_entry = self.current_tracklist[widget]

            current_runtime += song_entry.length()
            song_entry.update_time_label(time=current_runtime)

    def load_music(self):
        files = list(self.search_path.rglob("*.mp3"))

        mp3s = [MP3(file) for file in files]

        for mp3 in mp3s:
            track_name = mp3.get('Title', Path(mp3.filename).stem)
            self.music[track_name] = mp3

        self.statusBar().showMessage(f"Loaded {len(self.music)} mp3(s) from {self.search_path}", 8000)

def main():
    app = QApplication()
    window = MixWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()