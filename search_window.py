import math

from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout

from baklava import create_line_edit, BaklavaLineEdit, create_label, resource_path
from mix_utility import MixUtility

class SearchWindow(QDialog):
    search_field: BaklavaLineEdit
    mix_view = None
    mix_util: MixUtility

    def __init__(self, mix_util: MixUtility):
        super().__init__()

        self.setWindowTitle("Search")

        parent_layout = QVBoxLayout(self)

        search_bar_layout = QHBoxLayout()
        parent_layout.addLayout(search_bar_layout)

        create_label(container=search_bar_layout, img_path=resource_path("img/search.svg"), img_color="white")
        self.search_field = create_line_edit(container=search_bar_layout, placeholder_text="Search and/or filter songs", connect_to_method=self.on_search)

        self.mix_util = mix_util
        self.mix_view = MixView(mix_util=mix_util, parent=parent_layout)

        for _, mp3 in self.mix_util.music_library.items():
            self.mix_view.add_song_to_mix(mp3.filename)

    def on_search(self, new_search):
        search_tokens = new_search.split(" ")
        search_terms = []

        max_duration = math.inf

        for token in search_tokens:
            if "max_duration:" in token:
                try:
                    max_duration = int(token.split("max_duration:")[1])
                except:
                    pass
            else:
                search_terms.append(token)

        self.mix_view.filter(search_terms, max_duration)