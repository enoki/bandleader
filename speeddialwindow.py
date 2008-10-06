from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL
from scorewindow import ScoreWindow
from chordscorewindow import ScoreWindow as ChordScoreWindow

class SpeedDialWindow(QWidget):
    def __init__(self, score, *args):
        QWidget.__init__(self, *args)
        self.score = score
        self.create_controls()

    def create_controls(self):
        chord_button = QPushButton("&Chords")
        notation_button = QPushButton("&Leadsheet")
        lyrics_button = QPushButton("L&yrics")

        lyrics_button.setEnabled(False)

        self.connect(chord_button, SIGNAL('triggered()'), self.new_chord)
        self.connect(notation_button, SIGNAL('triggered()'), self.new_notation)
        self.connect(lyrics_button, SIGNAL('triggered()'), self.new_lyrics)

        layout = QGridLayout(self)
        layout.addWidget(chord_button, 1, 0)
        layout.addWidget(notation_button, 0, 1)
        layout.addWidget(lyrics_button, 1, 2)

    def new_chord(self):
        """ Opens a new chord window """
        self.new_window(ChordScoreWindow(self.score, self))

    def new_notation(self):
        """ Opens a new notation window """
        self.new_window(ScoreWindow(self.score, self))

    def new_lyrics(self):
        """ Opens a new lyrics window """
        pass

    def new_window(self, window):
        layout = QHBoxLayout()
        layout.addWidget(window)
        self.setLayout(layout)

if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    from music import Score
    import sys
    app = QApplication(sys.argv)
    score = Score()
    score.add_bars(4, 4, 4, count=6)
    window = SpeedDialWindow(score)
    window.show()
    sys.exit(app.exec_())
