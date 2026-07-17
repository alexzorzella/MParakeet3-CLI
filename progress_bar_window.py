from PySide6.QtWidgets import QDialog, QProgressBar

class ProgressBarWindow(QDialog):
    bar: QProgressBar

    def __init__(self, parent=None, size: int = 0):
        super().__init__(parent)

        self.bar = QProgressBar(self)
        self.bar.setRange(0, size)

        self.resize(100, 40)
        self.show()

    def update_progress(self, i):
        self.bar.setValue(i)

    def finish(self):
        self.close()