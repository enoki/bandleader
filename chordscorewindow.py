from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
from chordbarwindow import ChordBarWindow
from music import ScoreBar

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

class ScoreWindow(QWidget):
    def __init__(self, score, *args):
        QWidget.__init__(self, *args)
        self.score = score
        self.bars = []
        self.create_controls(score)
        #self.create_cursors(score)

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

    def create_bar(self, bar_index):
        b = ChordBarWindow(self.score[bar_index], bar_index, self.inner_widget)
        self.bars.insert(bar_index, b)
        #self.connect_bar(scene)
        return b

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_A:
            self.bar_layout.remove_widget(self.bars[1], 1)
            del self.bars[1]
        elif key == Qt.Key_B:
            self.score.insert(1, ScoreBar(2, 4, 4))
            bar = self.create_bar(1)
            self.bar_layout.insert_widget(self.bars[1], 1)

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
