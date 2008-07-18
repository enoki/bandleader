from PyQt4.QtCore import QRectF, QPointF, QSize, QPoint, QRect, Qt
from PyQt4.QtGui import *

class BeatWidget(QWidget):
    def __init__(self, score_bar, beat_index, parent=None):
        QWidget.__init__(self, parent)
        self.score_bar = score_bar
        self.beat_index = beat_index
        self.setLayout(self.create_layout())

    def create_layout(self):
        layout = QHBoxLayout()
        chord_label = QLabel(self.score_bar.chords[self.beat_index])
        layout.addWidget(chord_label)
        self.chord_label = chord_label
        return layout

    def set_focus(self):
        self.chord_label.setFrameShape(QFrame.Box)

    def unset_focus(self):
        self.chord_label.setFrameShape(QFrame.NoFrame)

class ChordBarWindow(QFrame):
    def __init__(self, score_bar, bar_index, parent=None):
        QFrame.__init__(self, parent)
        self.score_bar = score_bar
        self.bar_index = bar_index
        self.beats = []
        self.set_style()
        self.setLayout(self.create_layout())

    def set_style(self):
        self.setFrameShape(QFrame.Box)

    def create_layout(self):
        layout = QHBoxLayout()
        layout.setSpacing(0)

        for beat_index in xrange(self.score_bar.beats_per_bar):
            beat = BeatWidget(self.score_bar, beat_index)
            layout.addWidget(beat)
            self.beats.append(beat)

        return layout

    def focus_chord(self, beat_index):
        self.beats[beat_index].set_focus()

    def unfocus_chord(self, beat_index):
        self.beats[beat_index].unset_focus()

if __name__ == '__main__':
    import sys
    from music import ScoreBar
    app = QApplication(sys.argv)
    bar = ScoreBar(4, 4, 4)
    window = ChordBarWindow(bar, 0)
    window.show()
    app.exec_()
