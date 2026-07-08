from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from mutagen.mp3 import MP3
from baklava import create_label, create_button, create_line_edit, time_int_to_str, BaklavaLineEdit, time_int_str_to_int

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

    def __init__(self, filepath: Path | None, break_duration: int | None = None):
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

        if not self.is_break:
            create_button(container=song_utility_layout, height=35, width=120, text="Preview Transition")

        create_button(container=song_utility_layout, height=35, width=50, text="Delete")
        create_button(container=song_utility_layout, height=35, width=35, text="↑")
        create_button(container=song_utility_layout, height=35, width=35, text="↓")

        self.time_label = create_label(container=song_utility_layout, text="00:00:00", alignment=Qt.AlignCenter)
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