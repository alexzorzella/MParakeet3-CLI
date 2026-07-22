from pathlib import Path
from PySide6.QtCore import Qt, QSize

AQtAlignCenterLeft = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
AQtAlignCenterRight = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
AQtAlignCenterTop = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignTop

DEFAULT_MUSIC_DIR: Path = Path(__file__).resolve().parent / "Music"
DEFAULT_MIX_DIR: Path = Path(__file__).resolve().parent / "Mixes"
DEFAULT_MIX_NAME = "New Mix"

NOTHING_PLAYING_MESSAGE = "Nothing is currently playing"

ICON_SIDE_LENGTH = 35
ICON_SIZE = QSize(28, 28)