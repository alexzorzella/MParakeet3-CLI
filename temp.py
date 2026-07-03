import os
from pathlib import Path

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QListWidget, QWidget, QApplication, QVBoxLayout,QAbstractItemView,QListWidgetItem
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QListView, QFileDialog, QHBoxLayout, QMainWindow

from baklava import create_label, create_button, set_tooltip

class MixWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Edit Mix")
        self.resize(400, 300)

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

        file_menu.setToolTipsVisible(True)
        export_menu.setToolTipsVisible(True)

        load_mix_action = file_menu.addAction("&Load Mix")
        export_mix_as_file = export_menu.addAction("As &File")
        export_mix_as_tracks = export_menu.addAction("As Ordered &Tracks")

        load_mix_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        export_mix_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        export_mix_as_tracks_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)

        set_tooltip(widget=load_mix_action, text="Load a mix from a .txt file (Ctrl+L)")
        set_tooltip(widget=export_mix_as_file, text="Export a mix from as a .txt file (Ctrl+S)")
        set_tooltip(widget=export_mix_as_tracks, text="Export a mix as ordered audio file (Ctrl+E)")

    def create_text_entry(self, text_content: str):
        list_widget_item = QListWidgetItem()

        parent_widget = QWidget()
        vertical_layout = QVBoxLayout(parent_widget)
        create_label(container=vertical_layout, text=text_content)

        list_widget_item.setSizeHint(parent_widget.sizeHint())

        return list_widget_item, parent_widget

    def create_list_widget(self, parent):
        listWidget = QListWidget()
        listWidget.setDragDropMode(QAbstractItemView.InternalMove)
        listWidget.setFlow(QListView.TopToBottom)
        listWidget.setWrapping(False)
        listWidget.setResizeMode(QListView.Adjust)
        listWidget.setMovement(QListView.Snap)
        listWidget.setIconSize(QSize(200,200))

        listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        folder = QFileDialog.getExistingDirectory(None, "Open Folder")
        files = os.listdir(folder)
        files = [f for f in files if os.path.isfile(os.path.join(folder,f))]

        for filepath in files:
            list_widget_item, parent_widget = self.create_text_entry(Path(filepath).name)
            listWidget.addItem(list_widget_item)
            listWidget.setItemWidget(list_widget_item, parent_widget)

        parent.addWidget(listWidget)

def main():
    app = QApplication()
    window = MixWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()