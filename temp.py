from pathlib import Path

from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QTabWidget

from baklava import set_tooltip
from load_file_action import FileLoadAction
from mix_utility import MixUtility
from mix_view import MixView

class MixWindow(QMainWindow):
    mix_util: MixUtility

    def __init__(self):
        super().__init__()

        self.mix_util = MixUtility(parent_window=self, show_status_bar_message=self.show_status_bar_message)

        self.create_window()

    def create_window(self):
        self.setWindowTitle("Parakeet")
        self.resize(880, 660)

        self.populate_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        horizontal_layout = QHBoxLayout(central_widget)

        self.mix_util.parent_tab_widget = QTabWidget()
        horizontal_layout.addWidget(self.mix_util.parent_tab_widget)
        self.mix_util.parent_tab_widget.currentChanged.connect(self.on_tab_changed)

        self.mix_util.player.populate_gui(parent=horizontal_layout)

        self.create_new_mix()

    def populate_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("File")
        export_menu = menu_bar.addMenu("Export")
        mix_menu = menu_bar.addMenu("Mix")

        file_menu.setToolTipsVisible(True)
        export_menu.setToolTipsVisible(True)
        mix_menu.setToolTipsVisible(True)

        new_mix_action = file_menu.addAction("&New Mix")
        new_mix_action.triggered.connect(self.create_new_mix)
        load_mix_action = file_menu.addAction("&Load Mix")
        load_mix_action.triggered.connect(self.load_mix)
        export_mix_as_file = export_menu.addAction("As &File")
        export_mix_as_tracks = export_menu.addAction("As Ordered &Tracks")

        add_song_action = mix_menu.addAction("&Add Song(s)")
        add_song_action.triggered.connect(self.add_song_to_currently_selected_mix)

        load_mix_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        load_mix_shortcut.activated.connect(self.load_mix)
        export_mix_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        export_mix_shortcut.activated.connect(self.save_currently_selected_mix)
        export_mix_as_tracks_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        add_song_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
        add_song_shortcut.activated.connect(self.add_song_to_currently_selected_mix)

        self.mix_util.add_song_file_load_action = FileLoadAction(menu=mix_menu, name="&Recent", action=self.add_song_to_currently_selected_mix)

        set_tooltip(widget=load_mix_action, text="Load a mix from a .txt file (Ctrl+L)")
        set_tooltip(widget=export_mix_as_file, text="Export a mix from as a .txt file (Ctrl+S)")
        set_tooltip(widget=export_mix_as_tracks, text="Export a mix as ordered audio file (Ctrl+E)")
        set_tooltip(widget=add_song_action, text="Add one or more tracks to the mix (Ctrl+=)")

    def currently_selected_mix(self):
        return self.mix_util.mix_tab_views[self.mix_util.currently_selected_tab]

    def on_tab_changed(self, new_index):
        self.mix_util.currently_selected_tab = new_index
        print(f"Switched view to {new_index}")

    def add_song_to_currently_selected_mix(self):
        self.currently_selected_mix().add_song_to_mix()

    def save_currently_selected_mix(self):
        self.currently_selected_mix().save()

    def create_new_mix(self, path: Path | None = None):
        mix_view = MixView(mix_util=self.mix_util, mix_path=path)
        self.mix_util.mix_tab_views.append(mix_view)

    def load_mix(self):
        path = self.mix_util.add_song_file_load_action.load_file(parent=self, caption="Select mix", directory=self.mix_util.mix_path.as_posix(), file_filter="File (*.txt);;")

        if path is not None and len(path) > 0:
            mix_path = path[0]
            print(f"Loading mix from {mix_path}")
            self.create_new_mix(path=mix_path)

    def show_status_bar_message(self, message, time=8000):
        self.statusBar().showMessage(message, time)

def main():
    app = QApplication()
    window = MixWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()