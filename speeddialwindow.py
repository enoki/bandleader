from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL
from scorewindow import ScoreWindow
from chordscorewindow import ScoreWindow as ChordScoreWindow
from lyricswindow import LyricsWindow
import notify

class SpeedDialWindow(QStackedWidget):
    def __init__(self, score, *args):
        QWidget.__init__(self, *args)
        self.score = score
        self.title_changed = notify.Signal()
        self.create_controls()

    def create_controls(self):
        chord_button = QPushButton("&Chords")
        notation_button = QPushButton("&Leadsheet")
        lyrics_button = QPushButton("L&yrics")

        self.connect(chord_button, SIGNAL('clicked()'), self.new_chord)
        self.connect(notation_button, SIGNAL('clicked()'), self.new_notation)
        self.connect(lyrics_button, SIGNAL('clicked()'), self.new_lyrics)

        dial = QWidget()
        layout = QGridLayout(dial)
        layout.addWidget(chord_button, 1, 0)
        layout.addWidget(notation_button, 0, 1)
        layout.addWidget(lyrics_button, 1, 2)
        self.dial = dial

        self.addWidget(dial)

    def new_chord(self):
        """ Opens a new chord window """
        self.new_window(ChordScoreWindow(self.score, self), 'Chords')

    def new_notation(self):
        """ Opens a new notation window """
        self.new_window(ScoreWindow(self.score, self), 'Leadsheet')

    def new_lyrics(self):
        """ Opens a new lyrics window """
        self.new_window(LyricsWindow(self.score, self), 'Lyrics')

    def new_window(self, window, title):
        self.keymode = window.keymode
        self.addWidget(window)
        self.setCurrentWidget(window)
        self.removeWidget(self.dial)
        self.title_changed(title)

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
