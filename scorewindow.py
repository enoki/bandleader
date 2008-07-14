from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
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
        self.create_controls(score)
        self.create_cursors(score)

    def create_controls(self, score):
        inner_widget = QWidget(self)
        set_background(inner_widget, QColor('white'))
        self.inner_widget = inner_widget

        bar_layout = FlowLayout(inner_widget)
        bar_layout.setAlignment(Qt.AlignHCenter)
        self.bar_layout = bar_layout

        for i, bar in enumerate(score):
            b = self.create_bar(i)
            bar_layout.addWidget(b)

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

    def connect_bar(self, bar):
        bar.chord_label_focused_by_mouse.connect(
                self.chord_label_focused_by_mouse)

    def connect_chord_cursor(self):
        cursor = self.chord_cursor
        cursor.about_to_be_moved.connect(self.unmove_chord_cursor)
        cursor.moved.connect(self.move_chord_cursor)
        cursor.request_append.connect(self.append_chord_cursor_text)
        cursor.request_backspace.connect(self.backspace_chord_cursor_text)
        cursor.request_delete.connect(self.delete_chord_cursor_text)
        cursor.request_change_text.connect(self.change_chord_cursor_text)
        cursor.about_to_delete_bar.connect(self.prepare_delete_bar)
        cursor.bar_deleted.connect(self.delete_bar)
        cursor.bar_inserted.connect(self.insert_bar)
        cursor.bar_appended.connect(self.append_bar)

    def move_chord_cursor(self, bar_index, beat_index):
        self.bars[bar_index].focus_chord_label(beat_index)
        for view in self.bars[bar_index].views():
            self.scroller.ensureWidgetVisible(view)

    def unmove_chord_cursor(self, bar_index, beat_index):
        self.chord_cursor.commit()
        self.bars[bar_index].unfocus_chord_label(beat_index)

    def append_chord_cursor_text(self, bar_index, beat_index, text):
        self.bars[bar_index].append_to_chord_label(beat_index, text)

    def backspace_chord_cursor_text(self, bar_index, beat_index):
        self.bars[bar_index].backspace_in_chord_label(beat_index)

    def delete_chord_cursor_text(self, bar_index, beat_index):
        self.bars[bar_index].delete_in_chord_label(beat_index)

    def change_chord_cursor_text(self, bar_index, beat_index, text):
        self.bars[bar_index].change_chord_label(beat_index, text)

    def chord_label_focused_by_mouse(self, bar_index, beat_index):
        self.chord_cursor.move_to(bar_index, beat_index)

    def prepare_delete_bar(self, bar_index):
        pass

    def delete_bar(self, bar_index):
        for widget in self.bars[bar_index].views():
            self.bar_layout.removeWidget(widget)
            widget.deleteLater()

        del self.bars[bar_index]

        for i in xrange(bar_index, len(self.score)):
            self.bars[i].set_bar_index(i)

    def insert_bar(self, bar_index):
        b = self.create_bar(bar_index)
        self.bar_layout.insert_widget(bar_index, b)
        b.show()

        for i in xrange(bar_index, len(self.score)):
            self.bars[i].set_bar_index(i)

    def append_bar(self):
        b = self.create_bar(len(self.score)-1)
        self.bar_layout.addWidget(b)
        b.show()
        QApplication.processEvents()

    def create_bar(self, bar_index):
        scene = BarScene(self.score[bar_index], bar_index)
        b = BarWindow(self.inner_widget)
        b.setScene(scene)
        self.bars.insert(bar_index, scene)
        self.connect_bar(scene)
        return b

    def keyPressEvent(self, event):
        handled = self.keymode.keyPressEvent(event)
        if not handled:
            QWidget.keyPressEvent(self, event)

if __name__ == '__main__':
    import sys
    from music import Score
    app = QApplication(sys.argv)
    score = Score()
    score.add_bars(4, 4, 4, 4)
    window = ScoreWindow(score)
    window.show()
    app.exec_()
