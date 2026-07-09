from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QTabWidget

from baklava import set_tooltip
from load_file_action import FileLoadAction
from mix_utility import MixUtility


class MixWindow(QMainWindow):
    mix_util: MixUtility

    def __init__(self):
        super().__init__()

        self.mix_util = MixUtility(self.show_status_bar_message)

        self.create_window()

    def create_window(self):
        self.setWindowTitle("Parakeet")
        self.resize(880, 660)

        self.populate_menu_bar()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        horizontal_layout = QHBoxLayout(central_widget)

        self.mix_tabs = QTabWidget()
        horizontal_layout.addWidget(self.mix_tabs)

        self.create_list_widget(parent_tab_widget=self.mix_tabs)

        self.mix_util.player.populate_gui(parent=horizontal_layout)

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

    def new_mix(self):
        pass

    # def load_mix(self):
    #     # files = list(self.search_path.glob("*.txt"))
    #     paths = self.add_song_file_load_action.load_files(parent=self, caption="Select track(s)", directory=self.search_path.as_posix(), file_filter="File (*.mp3);;")

    def show_status_bar_message(self, message, time=8000):
        self.statusBar().showMessage(message, time)

def main():
    app = QApplication()
    window = MixWindow()
    window.show()
    app.exec()

if __name__ == '__main__':
    main()