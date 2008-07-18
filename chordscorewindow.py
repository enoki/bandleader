from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
from chordbarwindow import ChordBarWindow
from music import ScoreBar
from chordcursor import ChordCursor
from keymode import KeyMode

def set_background(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.Window, color)
    widget.setPalette(palette)

class FixedGridLayout(QGridLayout):
    def __init__(self, column_count, *args):
        QGridLayout.__init__(self, *args)
        self.column_count = column_count

    def add_widget(self, widget, index, *args):
        row, column = divmod(index, self.column_count)
        self.addWidget(widget, row, column, *args)

    def remove_widget(self, widget, index):
        for i in xrange(index+1, self.count()):
            row, column = divmod(i, self.column_count)
            item = self.itemAtPosition(row, column)
            self.removeItem(item)
            new_row, new_column = divmod(i-1, self.column_count)
            self.addItem(item, new_row, new_column)
        self.removeWidget(widget)
        widget.deleteLater()

    def insert_widget(self, widget, index, *args):
        for i in xrange(index, self.count()):
            row, column = divmod(i, self.column_count)
            item = self.itemAtPosition(row, column)
            self.removeItem(item)
            new_row, new_column = divmod(i+1, self.column_count)
            self.addItem(item, new_row, new_column)
        row, column = divmod(index, self.column_count)
        self.addWidget(widget, row, column, *args)

    def widget_at(self, row, column):
        return self.itemAtPosition(row, column).widget()

    def widget_by_index(self, index):
        row, column = divmod(index, self.column_count)
        return self.widget_at(row, column)

    def row_column_of(self, index):
        return divmod(index, self.column_count)

    def index_of(self, row, column):
        return row * self.column_count + column

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
        cursor.request_append.connect(self.append_chord_cursor_text)
        cursor.request_backspace.connect(self.backspace_chord_cursor_text)
        cursor.request_delete.connect(self.delete_chord_cursor_text)
        cursor.request_change_text.connect(self.change_chord_cursor_text)
        cursor.about_to_delete_bar.connect(self.prepare_delete_bar)
        cursor.bar_deleted.connect(self.delete_bar)
        cursor.bar_inserted.connect(self.insert_bar)
        cursor.bar_appended.connect(self.append_bar)

    def bar_at(self, bar_index):
        return self.bar_layout.widget_by_index(bar_index)

    def move_to(self, bar_index, beat_index):
        bar = self.bar_at(bar_index)
        bar.focus_chord(beat_index)
        self.scroller.ensureWidgetVisible(bar)

    def unmove_from(self, bar_index, beat_index):
        self.cursor.commit()
        self.bar_at(bar_index).unfocus_chord(beat_index)

    def append_chord_cursor_text(self, bar_index, beat_index, text):
        pass #self.bar_at(bar_index).append_to_chord_label(beat_index, text)

    def backspace_chord_cursor_text(self, bar_index, beat_index):
        pass #self.bars[bar_index].backspace_in_chord_label(beat_index)

    def delete_chord_cursor_text(self, bar_index, beat_index):
        pass #self.bars[bar_index].delete_in_chord_label(beat_index)

    def change_chord_cursor_text(self, bar_index, beat_index, text):
        pass #self.bars[bar_index].change_chord_label(beat_index, text)

    def chord_label_focused_by_mouse(self, bar_index, beat_index):
        self.cursor.move_to(bar_index, beat_index)

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

class ScoreWindow(QWidget):
    def __init__(self, score, *args):
        QWidget.__init__(self, *args)
        self.score = score
        self.chord_handler = ChordCursorHandler()
        self.create_controls(score)
        self.create_cursors(score)

    def create_controls(self, score):
        inner_widget = QWidget(self)
        set_background(inner_widget, QColor('white'))
        self.inner_widget = inner_widget

        bar_layout = FixedGridLayout(4, inner_widget)
        bar_layout.setSpacing(0)
        self.bar_layout = bar_layout

        for i, bar in enumerate(score):
            b = self.create_bar(i)
            bar_layout.add_widget(b, i)

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

        self.grabKeyboard()

        self.chord_handler.connect(self.chord_cursor,
                                   self.bar_layout,
                                   self.scroller)

        self.keymode = KeyMode(self.chord_cursor)
        self.keymode.switch_mode('chord')

    def connect_bar(self, bar):
        bar.chord_label_focused_by_mouse.connect(
                self.chord_handler.chord_label_focused_by_mouse)

    def create_bar(self, bar_index):
        b = ChordBarWindow(self.score[bar_index], bar_index, self.inner_widget)
        self.connect_bar(b)
        return b

    def keyPressEvent(self, event):
        handled = self.keymode.keyPressEvent(event)
        if not handled:
            QWidget.keyPressEvent(self, event)

    def oldkeyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_A:
            widget = self.bar_layout.widget_by_index(1)
            self.bar_layout.remove_widget(widget, 1)
        elif key == Qt.Key_B:
            self.score.insert(1, ScoreBar(2, 4, 4))
            bar = self.create_bar(1)
            self.bar_layout.insert_widget(bar, 1)

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
