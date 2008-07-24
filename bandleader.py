from PyQt4.QtGui import QApplication
from music import Score
from mainwindow import MainWindow
from chordcursor import ChordCursor
from keymode import KeyMode
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('Bandleader')

    score = Score()
    score.add_bars(4, 4, 4, count=6)
    score.add_bars(3, 4, 4)
    score.add_bars(4, 4, 4)
    score.add_bars(4, 4, 4, count=8)

    chord_cursor = ChordCursor(score)
    keymode = KeyMode(chord_cursor)

    window = MainWindow(score, keymode)
    window.show()

    sys.exit(app.exec_())
