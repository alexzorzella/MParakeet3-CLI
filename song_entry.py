from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from mutagen.mp3 import MP3
from baklava import create_label, create_button

AQtAlignCenterLeft = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
AQtAlignCenterRight = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight

def track_length_to_str(total_seconds: int) -> str:
    hours: int = int((total_seconds - (total_seconds % 60 * 24)) / (60 * 24))
    minutes: int = int((total_seconds - (total_seconds % 60)) / 60)
    seconds: int = total_seconds % 60

    if hours > 0:
        time = f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        time = f"{minutes}:{seconds:02d}"

    return time

class SongEntry:
    filepath: Path
    mp3: MP3
    list_widget_item: QListWidgetItem
    widget: QWidget
    time_label: QLabel

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.mp3 = MP3(filepath)

        list_widget_item = QListWidgetItem()

        parent_widget = QWidget()
        vertical_layout = QVBoxLayout(parent_widget)
        horizontal_layout = QHBoxLayout()

        vertical_layout.addLayout(horizontal_layout)

        create_label(container=horizontal_layout, text=self.name(), alignment=AQtAlignCenterLeft)

        song_utility_layout = QHBoxLayout()
        horizontal_layout.addLayout(song_utility_layout)

        create_label(container=song_utility_layout, text=track_length_to_str(self.length()), img_width=30, alignment=AQtAlignCenterRight)
        create_button(container=song_utility_layout, height=35, width=120, text="Preview Transition")
        create_button(container=song_utility_layout, height=35, width=50, text="Delete")
        create_button(container=song_utility_layout, height=35, width=35, text="↑")
        create_button(container=song_utility_layout, height=35, width=35, text="↓")

        self.time_label = create_label(container=song_utility_layout, text="00:00:00", alignment=Qt.AlignCenter)
        self.time_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        list_widget_item.setSizeHint(parent_widget.sizeHint())

        self.widget = parent_widget
        self.list_widget_item = list_widget_item

    def update_time_label(self, time: int):
        self.time_label.setText(track_length_to_str(total_seconds=time))

    def name(self) -> str:
        result = self.mp3.get('Title', self.filepath.stem)
        return result

    def length(self) -> int:
        result = self.mp3.info.length
        return int(result)