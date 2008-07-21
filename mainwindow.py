from PyQt4.QtCore import Qt, SIGNAL, SLOT
from PyQt4.QtGui import QTabWidget, QMainWindow, QAction
from scorewindow import ScoreWindow

class ScoreTabs(QTabWidget):
    def __init__(self, score, *args):
        QTabWidget.__init__(self, *args)
        self.addTab(ScoreWindow(score, self), 'Untitled')
        self.setFocusPolicy(Qt.NoFocus)

class MainWindow(QMainWindow):
    def __init__(self, score, *args):
        QMainWindow.__init__(self, *args)
        central = ScoreTabs(score)
        self.setCentralWidget(central)
        xtile_size = 24  # XXX
        self.resize(int((xtile_size*16+2)*2.5), self.height())
        self.setFocusPolicy(Qt.NoFocus)
        self.create_actions()
        self.create_menus()

    def create_actions(self):
        exitAction = QAction('E&xit', self)
        exitAction.setMenuRole(QAction.QuitRole)
        self.connect(exitAction, SIGNAL('triggered()'),
                     self, SLOT('close()'))
        self.exitAction = exitAction

    def create_menus(self):
        filemenu = self.menuBar().addMenu('&File')
        filemenu.addAction(self.exitAction)
