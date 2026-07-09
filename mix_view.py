from collections import defaultdict
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QListWidget, QWidget
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QAbstractItemView, QListView, QListWidgetItem, QTabWidget

from baklava import create_button, create_line_edit, BaklavaLineEdit
from mix_utility import MixUtility
from song_entry import SongEntry

HEADER_FONT_SIZE: int = 20
DEFAULT_MIX_NAME = "New Mix"

class MixView:
    name: str
    mix_util: MixUtility

    current_tracklist: defaultdict[QWidget, SongEntry]
    mix_name_line_edit: BaklavaLineEdit

    tab_index = -1

    def __init__(self, mix_util, mix_path: Path | None = None):
        self.name = DEFAULT_MIX_NAME
        self.current_tracklist = defaultdict()
        self.mix_util = mix_util
        self.initialize_gui()

    def initialize_gui(self):
        parent_widget = QWidget()
        vertical_layout = QVBoxLayout(parent_widget)
        self.mix_util.parent_tab_widget.addTab(parent_widget, self.name)
        self.tab_index = self.mix_util.parent_tab_widget.count() - 1

        self.mix_name_line_edit = create_line_edit(
                                    container=vertical_layout,
                                    placeholder_text="Title",
                                    default_value=self.name,
                                    height=40,
                                    font_size=HEADER_FONT_SIZE,
                                    connect_to_method=self.update_name)

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

        vertical_layout.addWidget(list_widget)

        hotbar = QHBoxLayout()
        height = 30

        create_button(container=hotbar,
                      text="Add Song(s)",
                      height=height,
                      tooltip="Add one or more audio files",
                      connect_to_method=lambda: self.add_song_to_mix())
        create_button(container=hotbar,
                      text="Add Break",
                      height=height,
                      tooltip="Add a break (good for cassettes, CDs)",
                      connect_to_method=self.add_break)

        vertical_layout.addLayout(hotbar)

    def update_name(self, new_name):
        self.name = new_name

        if self.tab_index >= 0:
            self.mix_util.parent_tab_widget.setTabText(self.tab_index, new_name)

    def add_song_to_mix(self, passed_path=None):
        if passed_path is None:
            paths = self.mix_util.add_song_file_load_action.load_files(parent=self.mix_util.parent_window, caption="Select track(s)", directory=self.mix_util.search_path.as_posix(), file_filter="File (*.mp3);;")
        else:
            paths = [passed_path]

        if paths is None or len(paths) <= 0:
            return

        for path in paths:
            song_entry = SongEntry(filepath=Path(path), player=self.mix_util.player, generic_func=self.call_generic_player_command, preview_transition_func=self.preview_transition_from, delete_item=self.delete_list_widget_item)
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

    def get_track_by_list_widget_item(self, list_widget_item: QListWidgetItem):
        widget = self.list_widget.itemWidget(list_widget_item)

        if self.current_tracklist.__contains__(widget):
            song_entry = self.current_tracklist[widget]
        else:
            return None

        return song_entry

    def get_track_by_index(self, index):
        list_widget_item = self.list_widget.item(index)
        return self.get_track_by_list_widget_item(list_widget_item)

    def update_cumulative_times(self):
        current_runtime: int = 0

        for i in range(self.list_widget.count()):
            song_entry = self.get_track_by_index(i)

            if song_entry is None:
                continue

            current_runtime += song_entry.length()
            song_entry.update_time_label(time=current_runtime)

    def queue_player_command(self, function, args):
        self.mix_util.player.commands.put((function, args))

    def call_generic_player_command(self, function, list_widget_item: QListWidgetItem):
        song_entry = self.get_track_by_list_widget_item(list_widget_item)

        if song_entry is None:
            return

        path = song_entry.filepath

        if not Path(path).exists():
            self.mix_util.show_status_bar_message(f"{path} doesn't exist")

        self.queue_player_command(function=function, args=(path,))

    def preview_transition_from(self, list_widget_item: QListWidgetItem):
        index = self.list_widget.row(list_widget_item)

        from_track = self.get_track_by_index(index - 1) if index > 0 else None
        to_track = self.get_track_by_list_widget_item(list_widget_item)

        if from_track is None:
            return

        from_path = from_track.filepath
        to_path = to_track.filepath

        if not Path(from_path).exists():
            self.mix_util.show_status_bar_message(f"{from_path} doesn't exist")
        elif not Path(to_path).exists():
            self.mix_util.show_status_bar_message(f"{to_path} doesn't exist")

        self.queue_player_command(self.mix_util.player.preview, (from_path, to_path,))

    def delete_list_widget_item(self, list_widget_item):
        widget = self.list_widget.itemWidget(list_widget_item)
        self.current_tracklist.__delitem__(widget)
        row = self.list_widget.row(list_widget_item)
        self.list_widget.takeItem(row)
        # print(f"Deleted item at index {row} with widget {widget}, removed from tracklist, Current tracklist -> (length {len(self.current_tracklist)}), tracks: {", ".join([Path(song_entry.filepath).stem for widget, song_entry in self.current_tracklist.items()])}")

    def save(self):
        pass