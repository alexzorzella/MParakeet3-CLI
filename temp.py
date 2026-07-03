from pathlib import Path

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QListWidget, QWidget, QApplication, QVBoxLayout,QAbstractItemView,QListWidgetItem
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QListView, QFileDialog, QHBoxLayout, QMainWindow

from baklava import create_label, create_button, set_tooltip
from load_file_action import FileLoadAction

class MixWindow(QMainWindow):
    list_widget: QListWidget | None = None
    add_song_file_load_action: FileLoadAction | None = None

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Edit Mix")
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        vertical_layout = QVBoxLayout(central_widget)
        self.create_list_widget(parent=vertical_layout)

        self.populate_menu_bar()

        hotbar = QHBoxLayout()
        height = 30

        add_song = create_button(container=hotbar, text="Add Song(s)", height=height, tooltip="Add one or more audio files")
        add_break = create_button(container=hotbar, text="Add Break", height=height, tooltip="Add a break (good for cassettes, CDs)")

        vertical_layout.addLayout(hotbar)

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
        add_song_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        add_song_shortcut.activated.connect(self.add_song_to_mix)

        self.add_song_file_load_action = FileLoadAction(menu=mix_menu, name="&Recent", action=self.add_song_to_mix)

        set_tooltip(widget=load_mix_action, text="Load a mix from a .txt file (Ctrl+L)")
        set_tooltip(widget=export_mix_as_file, text="Export a mix from as a .txt file (Ctrl+S)")
        set_tooltip(widget=export_mix_as_tracks, text="Export a mix as ordered audio file (Ctrl+E)")
        set_tooltip(widget=add_song_action, text="Add one or more tracks to the mix (Ctrl++)")

    def create_text_entry(self, text_content: str):
        list_widget_item = QListWidgetItem()

        parent_widget = QWidget()
        vertical_layout = QVBoxLayout(parent_widget)
        create_label(container=vertical_layout, text=text_content)

        list_widget_item.setSizeHint(parent_widget.sizeHint())

        return list_widget_item, parent_widget

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

        parent.addWidget(list_widget)

    def add_song_to_mix(self):
        paths = self.add_song_file_load_action.load_files(parent=self, caption="Select track(s)", file_filter="File (*.mp3 *.wav *.ogg *.opus);;")

        if paths is None or len(paths) <= 0:
            return

        for path in paths:
            list_widget_item, parent_widget = self.create_text_entry(Path(path).name)
            self.list_widget.addItem(list_widget_item)
            self.list_widget.setItemWidget(list_widget_item, parent_widget)

def main():
    app = QApplication()
    window = MixWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()