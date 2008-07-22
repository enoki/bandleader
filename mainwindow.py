from PyQt4.QtCore import Qt, SIGNAL, SLOT
from PyQt4.QtGui import QTabWidget, QMainWindow, QAction
from scorewindow import ScoreWindow
from chordscorewindow import ScoreWindow as ChordScoreWindow

class ScoreTabs(QTabWidget):
    def __init__(self, score, keymode, *args):
        QTabWidget.__init__(self, *args)
        self.addTab(ScoreWindow(score, keymode, self), 'Untitled')
        self.setFocusPolicy(Qt.NoFocus)

class MainWindow(QMainWindow):
    def __init__(self, score, keymode, *args):
        QMainWindow.__init__(self, *args)
        tabs = ScoreTabs(score, keymode)
        self.setCentralWidget(tabs)
        self.score = score
        self.keymode = keymode
        self.tabs = tabs
        xtile_size = 24  # XXX
        self.resize(int((xtile_size*16+2)*2.5), self.height())
        self.setFocusPolicy(Qt.NoFocus)
        self.create_actions()
        self.create_menus()

    def create_actions(self):
        newTabAction = QAction('New Tab', self)
        newTabAction.setShortcut('Ctrl+T')
        self.connect(newTabAction, SIGNAL('triggered()'), self.new_tab)
        self.newTabAction = newTabAction

        exitAction = QAction('E&xit', self)
        exitAction.setMenuRole(QAction.QuitRole)
        self.connect(exitAction, SIGNAL('triggered()'),
                     self, SLOT('close()'))
        self.exitAction = exitAction

    def create_menus(self):
        filemenu = self.menuBar().addMenu('&File')
        filemenu.addAction(self.newTabAction)
        filemenu.addAction(self.exitAction)

    def new_tab(self):
        self.keymode.commit()
        self.tabs.addTab(ChordScoreWindow(self.score, self.keymode, self),
                         'Untitled2')
