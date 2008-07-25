from PyQt4.QtCore import Qt, QSize, QRect, QPoint
from PyQt4.QtGui import *
from chordbarwindow import ChordBarWindow
from music import ScoreBar
from flowlayout import FlowLayout
from chordcursor import ChordCursor
from keymode import KeyMode

def set_background(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.Window, color)
    widget.setPalette(palette)

class ChordCursorHandler(object):
    def __init__(self):
        pass

    def connect(self, cursor, bar_layout, scroller):
        self.cursor = cursor
        self.bar_layout = bar_layout
        self.scroller = scroller
        self.connect_cursor(cursor)

    def connect_cursor(self, cursor):
        cursor.about_to_be_moved.connect(self.unmove_from)
        cursor.moved.connect(self.move_to)
        cursor.request_text.connect(self.get_chord_cursor_text)
        cursor.request_append.connect(self.append_chord_cursor_text)
        cursor.request_backspace.connect(self.backspace_chord_cursor_text)
        cursor.request_delete.connect(self.delete_chord_cursor_text)
        cursor.request_change_text.connect(self.change_chord_cursor_text)

    def bar_at(self, bar_index):
        return self.bar_layout.widget_by_index(bar_index)

    def move_to(self, bar_index, beat_index):
        bar = self.bar_at(bar_index)
        bar.focus_chord(beat_index)
        self.scroller.ensureWidgetVisible(bar)

    def unmove_from(self, bar_index, beat_index):
        self.bar_at(bar_index).unfocus_chord(beat_index)

    def get_chord_cursor_text(self, bar_index, beat_index):
        return self.bar_at(bar_index).get_chord(beat_index)

    def append_chord_cursor_text(self, bar_index, beat_index, text):
        self.bar_at(bar_index).append_to_chord(beat_index, text)

    def backspace_chord_cursor_text(self, bar_index, beat_index):
        self.bar_at(bar_index).backspace_chord(beat_index)

    def delete_chord_cursor_text(self, bar_index, beat_index):
        self.bar_at(bar_index).delete_chord(beat_index)

    def change_chord_cursor_text(self, bar_index, beat_index, text):
        self.bar_at(bar_index).change_chord(beat_index, text)

    def chord_label_focused_by_mouse(self, bar, beat_index):
        bar_index = self.bar_layout.indexOf(bar)
        self.cursor.move_to(bar_index, beat_index)

    def commit_chord(self):
        self.cursor.commit()

    def chord_text_changed(self, parent_id, bar_index, beat_index):
        if id(self) != parent_id:
            self.bar_at(bar_index).update_chord(beat_index)

class ScoreWindow(QWidget):
    def __init__(self, score, *args):
        QWidget.__init__(self, *args)
        self.score = score
        self.chord_cursor = ChordCursor(score)
        self.keymode = KeyMode(self.chord_cursor)
        self.chord_handler = ChordCursorHandler()
        self.create_controls(score)
        self.connect_cursors(score)
        self.connect_score(score)

    def create_controls(self, score):
        inner_widget = QWidget(self)
        set_background(inner_widget, QColor('white'))
        self.inner_widget = inner_widget

        bar_layout = FlowLayout(inner_widget)
        self.bar_layout = bar_layout

        for i, bar in enumerate(score):
            b = self.create_bar(i)
            bar_layout.addWidget(b)

        scroller = QScrollArea()
        scroller.setWidget(inner_widget)
        scroller.setWidgetResizable(True)
        scroller.setFocusPolicy(Qt.NoFocus)
        self.scroller = scroller

        layout = QVBoxLayout(self)
        layout.addWidget(scroller)

    def connect_score(self, score):
        chord_handler = self.chord_handler
        score.bar_deleted.connect(self.delete_bar)
        score.bar_inserted.connect(self.insert_bar)
        score.bar_appended.connect(self.append_bar)
        score.chord_text_changed.connect(chord_handler.chord_text_changed)

    def connect_cursors(self, score):
        self.chord_cursor.connect(self.bar_layout.row_column_of,
                                  self.bar_layout.index_of,
                                  self.chord_handler)

        self.chord_handler.connect(self.chord_cursor,
                                   self.bar_layout,
                                   self.scroller)

    def connect_bar(self, bar):
        bar.chord_label_focused_by_mouse.connect(
                self.chord_handler.chord_label_focused_by_mouse)
        bar.request_chord_label_commit.connect(
                self.chord_handler.commit_chord)

    def create_bar(self, bar_index):
        b = ChordBarWindow(self.score[bar_index], self.inner_widget)
        self.connect_bar(b)
        return b

    def delete_bar(self, bar_index):
        widget = self.bar_layout.widget_by_index(bar_index)
        self.bar_layout.removeWidget(widget)
        widget.deleteLater()

    def insert_bar(self, bar_index):
        b = self.create_bar(bar_index)
        self.bar_layout.insert_widget(bar_index, b)
        b.show()

    def append_bar(self):
        b = self.create_bar(len(self.score)-1)
        self.bar_layout.addWidget(b)
        b.show()
        QApplication.processEvents()

    def showEvent(self, event):
        self.chord_cursor.connect(self.bar_layout.row_column_of,
                                  self.bar_layout.index_of,
                                  self.chord_handler)
        self.keymode.switch_mode('chord')
        QWidget.showEvent(self, event)

    def keyPressEvent(self, event):
        handled = self.keymode.keyPressEvent(event)
        if not handled:
            QWidget.keyPressEvent(self, event)

    def oldkeyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_A:
            widget = self.bar_layout.widget_by_index(1)
            self.bar_layout.removeWidget(widget)
        elif key == Qt.Key_B:
            self.score.insert(1, ScoreBar(2, 4, 4))
            bar = self.create_bar(1)
            self.bar_layout.insert_widget(1, bar)
            bar.show()

if __name__ == '__main__':
    import sys
    from music import Score
    app = QApplication(sys.argv)
    score = Score()
    score.add_bars(4, 4, 4, 4)
    score.add_bars(3, 4, 4, 4)
    window = ScoreWindow(score)
    window.show()
    app.exec_()
