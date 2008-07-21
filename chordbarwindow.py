from PyQt4.QtCore import QRectF, QPointF, QSize, QPoint, QRect, Qt
from PyQt4.QtGui import *
import notify

class ChordLabel(QLabel):
    def __init__(self, beat_index, *args):
        QLabel.__init__(self, *args)
        self.beat_index = beat_index
        self.focused_by_mouse = notify.Signal()
        self.setAlignment(Qt.AlignCenter)

    def select_all(self):
        self.setFrameShape(QFrame.Box)

    def select_none(self):
        self.setFrameShape(QFrame.NoFrame)

    def append(self, text):
        self.setText(self.text() + text)

    def backspace(self):
        self.setText(self.text()[:-1])

    def delete_text(self):
        self.setText('')

    def mousePressEvent(self, event):
        if self.hasFocus():
            event.ignore()
        else:
            self.select_all()
            self.focused_by_mouse(self.beat_index)

class BeatWidget(QWidget):
    def __init__(self, score_bar, beat_index, parent=None):
        QWidget.__init__(self, parent)
        self.score_bar = score_bar
        self.beat_index = beat_index
        self.setLayout(self.create_layout())
        self.clicked = notify.Signal()

    def create_layout(self):
        layout = QHBoxLayout()
        chord_label = ChordLabel(self.beat_index,
                                 self.score_bar.chords[self.beat_index])
        layout.addWidget(chord_label)
        self.chord_label = chord_label
        return layout

    def set_focus(self):
        self.chord_label.setFocus()
        self.chord_label.select_all()

    def unset_focus(self):
        self.chord_label.clearFocus()
        self.chord_label.select_none()

    def mousePressEvent(self, event):
        self.clicked(self.beat_index)

    def append_to_chord(self, text):
        self.chord_label.append(text)
        self.commit()

    def backspace_chord(self):
        self.chord_label.backspace()
        self.commit()

    def delete_chord(self):
        self.chord_label.delete_text()
        self.commit()

    def change_chord(self, text):
        self.chord_label.setText(text)
        self.commit()

    def commit(self):
        self.score_bar.chords[self.beat_index] = self.chord_label.text()

class ChordBarWindow(QFrame):
    def __init__(self, score_bar, parent=None):
        QFrame.__init__(self, parent)
        self.score_bar = score_bar
        self.beats = []
        self.chord_label_focused_by_mouse = notify.Signal()
        self.set_style()
        self.setLayout(self.create_layout())

    def set_style(self):
        self.setFrameShape(QFrame.Box)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def create_layout(self):
        layout = QHBoxLayout()
        layout.setSpacing(0)

        for beat_index in xrange(self.score_bar.beats_per_bar):
            beat = BeatWidget(self.score_bar, beat_index)
            layout.addWidget(beat)
            beat.clicked.connect(self.on_beat_click)
            self.beats.append(beat)

        return layout

    def on_beat_click(self, beat_index):
        self.chord_label_focused_by_mouse(self, beat_index)

    def focus_chord(self, beat_index):
        self.beats[beat_index].set_focus()

    def unfocus_chord(self, beat_index):
        self.beats[beat_index].unset_focus()

    def append_to_chord(self, beat_index, text):
        self.beats[beat_index].append_to_chord(text)

    def backspace_chord(self, beat_index):
        self.beats[beat_index].backspace_chord()

    def delete_chord(self, beat_index):
        self.beats[beat_index].delete_chord()

    def change_chord(self, beat_index, text):
        self.beats[beat_index].change_chord(text)

if __name__ == '__main__':
    import sys
    from music import ScoreBar
    app = QApplication(sys.argv)
    bar = ScoreBar(4, 4, 4)
    window = ChordBarWindow(bar)
    window.show()
    app.exec_()
