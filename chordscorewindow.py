from PyQt4.QtCore import Qt, QSize, QRect, QPoint
from PyQt4.QtGui import *
from chordbarwindow import ChordBarWindow
from music import ScoreBar
from chordcursor import ChordCursor
from keymode import KeyMode

def set_background(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.Window, color)
    widget.setPalette(palette)

class FixedGridLayout(QLayout):
    def __init__(self, column_count, parent=None):
        QLayout.__init__(self, parent)
        self.items = []
        self.column_count = column_count
        self.setMargin(0)
        self.setSpacing(-1)

##
    def row_column_of(self, index):
        return divmod(index, self.column_count)

    def index_of(self, row, column):
        return row * self.column_count + column

    def widget_by_index(self, index):
        return self.items[index].widget()

    def insert_widget(self, index, widget):
        self.items.insert(index, QWidgetItem(widget))
##

    def addItem(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)

    def itemAt(self, index):
        if 0 <= index < len(self.items):
            return self.items[index]
        else:
            return None

    def takeAt(self, index):
        if 0 <= index < len(self.items):
            item = self.items[index]
            self.items.remove(item)
            return item
        else:
            return None

    def expandingDirections(self):
        return 0

    def setGeometry(self, rect):
        QLayout.setGeometry(self, rect)
        self.doLayout(rect)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.items:
            size = size.expandedTo(item.minimumSize())

        margin = self.margin()
        size += QSize(2*margin, 2*margin)
        return size

    def doLayout(self, rect):
        x = rect.x()
        y = rect.y()

        col = 0
        row = 0

        if len(self.items) <= 0:
            return

        itemwidth = rect.width() // self.column_count
        itemheight = self.items[0].sizeHint().height()
        itemsize = QSize(itemwidth, itemheight)

        for index, item in enumerate(self.items):
            nextX = x + itemwidth
            if (nextX > rect.right()):
                x = rect.x()
                y = y + itemheight
                nextX = x + itemwidth
                col = 0
                row += 1

            item.setGeometry(QRect(QPoint(x, y), itemsize))

            x = nextX
            col += 1

        return y + itemheight - rect.y()

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

    def chord_label_focused_by_mouse(self, bar, beat_index):
        bar_index = self.bar_layout.indexOf(bar)
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
        b = ChordBarWindow(self.score[bar_index], self.inner_widget)
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
