from pathlib import Path
from typing import Callable

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from mutagen.mp3 import MP3
from baklava import create_label, create_button, create_line_edit, time_int_to_str, BaklavaLineEdit, \
    time_int_str_to_int, resource_path
from vlc_handler import ThreadedVlcPlayer

AQtAlignCenterLeft = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
AQtAlignCenterRight = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight

class SongEntry:
    filepath: Path
    mp3: MP3

    list_widget_item: QListWidgetItem
    widget: QWidget

    time_label: QLabel

    is_break: bool = False
    break_duration: int = 75 * 60
    last_cached_cumulative_duration: int = 0
    duration_input: BaklavaLineEdit

    def __init__(self, filepath: Path | None, player: ThreadedVlcPlayer | None = None, generic_func: Callable | None = None, preview_transition_func: Callable | None = None, break_duration: int | None = None):
        if filepath is not None:
            self.filepath = filepath
            self.mp3 = MP3(filepath)

        list_widget_item = QListWidgetItem()

        parent_widget = QWidget()
        vertical_layout = QVBoxLayout(parent_widget)
        horizontal_layout = QHBoxLayout()

        vertical_layout.addLayout(horizontal_layout)

        if break_duration is not None:
            self.is_break = True
            self.break_duration = break_duration

        create_label(container=horizontal_layout, text=self.name() if not self.is_break else "Break", alignment=AQtAlignCenterLeft)

        song_utility_layout = QHBoxLayout()
        horizontal_layout.addLayout(song_utility_layout)

        length_as_string: str = time_int_to_str(self.absolute_length())

        if not self.is_break:
            create_label(container=song_utility_layout, text=length_as_string, img_width=30, alignment=AQtAlignCenterRight)
        else:
            create_label(container=song_utility_layout, text="Section Duration:", alignment=AQtAlignCenterRight)
            self.duration_input = create_line_edit(container=song_utility_layout,
                                                   placeholder_text="Length",
                                                   default_value=length_as_string,
                                                   width=70,
                                                   height=35,
                                                   alignment=Qt.AlignCenter,
                                                   connect_to_method=self.update_break_duration,
                                                   on_deselected=self.format_duration_input)

        icon_side_length = 35
        icon_size = QSize(28, 28)

        container = song_utility_layout
        length = icon_side_length
        color = "white"
        size = icon_size

        if not self.is_break:
            create_button(container=container, height=length, width=length, icon=resource_path("img/play.svg"), icon_color=color, icon_size=size, tooltip="Play",
                          connect_to_method=lambda: generic_func(player.queue_song_force_play, list_widget_item))
            create_button(container=container, height=length, width=length, icon=resource_path("img/list_end.svg"), icon_color=color, icon_size=size, tooltip="Queue Track",
                          connect_to_method=lambda: generic_func(player.queue_song, list_widget_item))
            create_button(container=container, height=length, width=length, icon=resource_path("img/list_start.svg"), icon_color=color, icon_size=size, tooltip="Play Next",
                          connect_to_method=lambda: generic_func(player.queue_song_next, list_widget_item))
            create_button(container=container, height=length, width=length, icon=resource_path("img/ear.svg"), icon_color=color, icon_size=size, tooltip="Play Transition",
                          connect_to_method=lambda: preview_transition_func(list_widget_item))

        create_button(container=container, height=length, width=length, icon=resource_path("img/delete.svg"), icon_color=color, icon_size=size, tooltip="Delete")
        # create_button(container=container, height=length, width=length, icon=resource_path("img/up_arrow.svg"), icon_color=color, icon_size=size, tooltip="Move Up")
        # create_button(container=container, height=length, width=length, icon=resource_path("img/down_arrow.svg"), icon_color=color, icon_size=size, tooltip="Move Down")

        self.time_label = create_label(container=container, text="00:00:00", alignment=Qt.AlignCenter)
        self.time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        list_widget_item.setSizeHint(parent_widget.sizeHint())

        self.widget = parent_widget
        self.list_widget_item = list_widget_item

    def update_break_duration(self, new_duration):
        self.break_duration = time_int_str_to_int(new_duration)
        self.update_time_label(time=self.last_cached_cumulative_duration)

    def format_duration_input(self):
        self.duration_input.setText(time_int_to_str(self.break_duration))

    def update_time_label(self, time: int):
        if not self.is_break:
            time_label_text = time_int_to_str(total_seconds=time)
        else:
            self.last_cached_cumulative_duration = time
            time_diff = self.break_duration - time

            time_label_text = ""

            color = "white"

            if time_diff > 0:
                color = "green"
                time_label_text += "-"
            elif time_diff < 0:
                color = "red"
                time_label_text += "+"

            time_label_text += time_int_to_str(abs(time_diff))

            self.time_label.setStyleSheet(f"color: {color};")

        self.time_label.setText(time_label_text)

    def name(self) -> str:
        result = self.mp3.get('Title', self.filepath.stem)
        return result

    def absolute_length(self):
        result = self.mp3.info.length if not self.is_break else self.break_duration
        return result

    def length(self) -> int:
        result = self.mp3.info.length if not self.is_break else 0
        return int(result)