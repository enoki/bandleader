from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
import louie as notify
from barwindow import BarWindow, BarScene
from flowlayout import FlowLayout
from chordcursor import ChordCursor

def set_background(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.Window, color)
    widget.setPalette(palette)

class ScoreWindow(QWidget):
    def __init__(self, score, *args):
        QWidget.__init__(self, *args)
        self.score = score
        self.bars = []
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

        scroller = QScrollArea()
        scroller.setWidget(inner_widget)
        scroller.setWidgetResizable(True)
        self.scroller = scroller

        layout = QVBoxLayout(self)
        layout.addWidget(scroller)

    def create_cursors(self, score):
        self.chord_cursor = ChordCursor(score, 2)

        def move_cursor():
            self.bars[self.chord_cursor.bar_index].focus_chord_label(self.chord_cursor.beat_index)

        notify.connect(ChordCursor.Moved, move_cursor)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.chord_cursor.move_left()
            print 'move left'
        elif key == Qt.Key_Right:
            self.chord_cursor.move_right()
            print 'move right'
        elif key == Qt.Key_Up:
            self.chord_cursor.move_up()
        elif key == Qt.Key_Down:
            self.chord_cursor.move_down()
            print 'move dodwn'
        else:
            print 'key %d' % key
            QWidget.keyPressEvent(self, event)
