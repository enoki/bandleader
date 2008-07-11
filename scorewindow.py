from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
import louie as notify
from barwindow import BarWindow, BarScene
from flowlayout import FlowLayout
from chordcursor import ChordCursor
from keymode import KeyMode

def set_background(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.Window, color)
    widget.setPalette(palette)

class ScoreWindow(QWidget):
    def __init__(self, score, *args):
        QWidget.__init__(self, *args)
        self.score = score
        self.bars = []
        self.bar_windows = []
        self.create_controls(score)
        self.create_cursors(score)

    def create_controls(self, score):
        inner_widget = QWidget(self)
        set_background(inner_widget, QColor('white'))

        bar_layout = FlowLayout(inner_widget)
        bar_layout.setAlignment(Qt.AlignHCenter)
        self.bar_layout = bar_layout

        for i, bar in enumerate(score):
            scene = BarScene(bar, i)
            b = BarWindow()
            b.setScene(scene)
            bar_layout.addWidget(b)
            self.bars.append(scene)
            self.bar_windows.append(b)

        scroller = QScrollArea()
        scroller.setWidget(inner_widget)
        scroller.setWidgetResizable(True)
        self.scroller = scroller

        layout = QVBoxLayout(self)
        layout.addWidget(scroller)

    def create_cursors(self, score):
        self.chord_cursor = ChordCursor(score,
                                        self.bar_layout.row_column_of,
                                        self.bar_layout.index_of)
        self.connect_chord_cursor()

        self.grabKeyboard()

        self.keymode = KeyMode(self.chord_cursor)
        self.keymode.switch_mode('chord')

    def connect_chord_cursor(self):
        notify.connect(self.unmove_chord_cursor, ChordCursor.AboutToBeMoved,
                       self.chord_cursor)
        notify.connect(self.move_chord_cursor, ChordCursor.Moved,
                       self.chord_cursor)

    def move_chord_cursor(self, bar_index, beat_index):
        self.bars[bar_index].focus_chord_label(beat_index)
        self.scroller.ensureWidgetVisible(self.bar_windows[bar_index])

    def unmove_chord_cursor(self, bar_index, beat_index):
        self.bars[bar_index].unfocus_chord_label(beat_index)

    def keyPressEvent(self, event):
        handled = self.keymode.keyPressEvent(event)
        if not handled:
            QWidget.keyPressEvent(self, event)
