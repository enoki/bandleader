from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
from barwindow import BarWindow, BarScene
from flowlayout import FlowLayout

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

    def create_controls(self, score):
        inner_widget = QWidget(self)
        self.inner_widget = inner_widget
        set_background(inner_widget, QColor('white'))

        bar_layout = FlowLayout(inner_widget)
        bar_layout.setAlignment(Qt.AlignHCenter)

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
