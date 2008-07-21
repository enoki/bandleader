from PyQt4.QtCore import QRectF, QPointF, QSize, QPoint, QRect, Qt
from PyQt4.QtGui import *
import notify

class ChordLabel(QLineEdit):
    def __init__(self, beat_index, *args):
        QLineEdit.__init__(self, *args)
        self.beat_index = beat_index
        self.focused_by_mouse = notify.Signal()
        self.focused_out = notify.Signal()
        self.setAlignment(Qt.AlignCenter)
        self.setFrame(False)

    def sizeHint(self):
        metrics = QFontMetrics(self.font())
        size = metrics.size(Qt.TextSingleLine, self.text())
        size.setWidth(size.width() + 10)
        return size

    def select_all(self):
        self.selectAll()

    def select_none(self):
        self.deselect()

    def append(self, text):
        self.insert(text)

    def delete_text(self):
        self.del_()

    def keyPressEvent(self, event):
        event.ignore()

    def keyReleaseEvent(self, event):
        event.ignore()

    def focusInEvent(self, event):
        if event.reason() == Qt.MouseFocusReason:
            self.select_all()
            self.focused_by_mouse(self.beat_index)
        QLineEdit.focusInEvent(self, event)

    def focusOutEvent(self, event):
        self.focused_out(self.beat_index)
        QLineEdit.focusOutEvent(self, event)

    def mousePressEvent(self, event):
        if self.hasFocus():
            event.ignore()
        else:
            QLineEdit.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        event.ignore()

    def mouseReleaseEvent(self, event):
        event.ignore()

    def mouseDoubleClickEvent(self, event):
        event.ignore()

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
        self.focused_out = chord_label.focused_out
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

    def get_chord(self):
        if self.chord_label.hasSelectedText():
            return ''
        return str(self.chord_label.text())

    def append_to_chord(self, text):
        self.chord_label.append(text)
        self.adjust_size()

    def backspace_chord(self):
        self.chord_label.backspace()
        self.adjust_size()

    def delete_chord(self):
        self.chord_label.delete_text()
        self.adjust_size()

    def change_chord(self, text):
        self.chord_label.setText(text)
        self.adjust_size()

    def adjust_size(self):
        self.chord_label.updateGeometry()

class ChordBarWindow(QFrame):
    def __init__(self, score_bar, parent=None):
        QFrame.__init__(self, parent)
        self.score_bar = score_bar
        self.beats = []
        self.chord_label_focused_by_mouse = notify.Signal()
        self.request_chord_label_commit = notify.Signal()
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
            beat.focused_out.connect(self.on_beat_focused_out)
            self.beats.append(beat)

        return layout

    def on_beat_click(self, beat_index):
        self.chord_label_focused_by_mouse(self, beat_index)

    def on_beat_focused_out(self, beat_index):
        self.request_chord_label_commit()

    def focus_chord(self, beat_index):
        self.beats[beat_index].set_focus()

    def unfocus_chord(self, beat_index):
        self.beats[beat_index].unset_focus()

    def get_chord(self, beat_index):
        return self.beats[beat_index].get_chord()

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
