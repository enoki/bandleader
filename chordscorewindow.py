from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
from chordbarwindow import ChordBarWindow

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
        #self.create_cursors(score)

    def create_controls(self, score):
        inner_widget = QWidget(self)
        set_background(inner_widget, QColor('white'))
        self.inner_widget = inner_widget

        bar_layout = QGridLayout(inner_widget)
        bar_layout.setSpacing(0)
        self.bar_layout = bar_layout

        col_count = 4

        for i, bar in enumerate(score):
            b = self.create_bar(i)
            row, column = divmod(i, col_count)
            bar_layout.addWidget(b, row, column)

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
