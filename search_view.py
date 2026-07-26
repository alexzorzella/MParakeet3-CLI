import math

from PySide6.QtWidgets import QWidget

from baklava import BaklavaLineEdit, time_int_str_to_int
from mix_utility import MixUtility

class SearchView():
    search_field: BaklavaLineEdit
    mix_view = None
    mix_util: MixUtility

    def __init__(self, mix_view, mix_util: MixUtility, parent_layout, search_field):
        super().__init__()

        parent_widget = QWidget()
        parent_widget.setLayout(parent_layout)

        self.mix_util = mix_util
        self.mix_view = mix_view
        self.search_field = search_field

        self.mix_util.queue_search_tabs.addTab(parent_widget, "Search")

        self.search_field.textChanged.connect(self.on_search)

        for _, mp3 in self.mix_util.music_library.items():
            self.mix_view.add_song_to_mix(mp3.filename)

    def on_search(self, new_search):
        search_tokens = new_search.split(" ")
        search_terms = []

        max_duration = math.inf

        for token in search_tokens:
            if "max_duration:" in token:
                try:
                    max_duration = time_int_str_to_int(token.split("max_duration:")[1])
                except:
                    pass
            else:
                search_terms.append(token)

        self.mix_view.filter(search_terms, max_duration)