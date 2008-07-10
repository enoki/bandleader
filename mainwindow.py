from PyQt4.QtGui import QTabWidget, QMainWindow
from scorewindow import ScoreWindow

class ScoreTabs(QTabWidget):
    def __init__(self, score, *args):
        QTabWidget.__init__(self, *args)
        self.addTab(ScoreWindow(score, self), 'Untitled')

class MainWindow(QMainWindow):
    def __init__(self, score, *args):
        QMainWindow.__init__(self, *args)
        central = ScoreTabs(score)
        self.setCentralWidget(central)
        xtile_size = 24  # XXX
        self.resize(int((xtile_size*16+2)*2.5), self.height())
