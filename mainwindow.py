from __future__ import with_statement
from PyQt4.QtCore import Qt, SIGNAL, SLOT
from PyQt4.QtGui import QTabWidget, QMainWindow, QAction, QFileDialog, QApplication
from scorewindow import ScoreWindow
from chordscorewindow import ScoreWindow as ChordScoreWindow
import cPickle as pickle

class ScoreTabs(QTabWidget):
    def __init__(self, score, *args):
        QTabWidget.__init__(self, *args)
        self.addTab(ScoreWindow(score, self), 'Leadsheet')
        self.setFocusPolicy(Qt.NoFocus)

class MainWindow(QMainWindow):
    def __init__(self, score, *args):
        QMainWindow.__init__(self, *args)
        tabs = ScoreTabs(score)
        self.setCentralWidget(tabs)
        self.score = score
        self.tabs = tabs
        xtile_size = 24  # XXX
        self.resize(int((xtile_size*16+2)*2.5), self.height())
        self.setFocusPolicy(Qt.NoFocus)
        self.setWindowFilePath('Untitled')
        self.setWindowModified(False)
        self.create_actions()
        self.create_menus()

    def create_actions(self):
        new_tab_action = QAction('New Tab', self)
        new_tab_action.setShortcut('Ctrl+T')
        self.connect(new_tab_action, SIGNAL('triggered()'), self.new_tab)
        self.new_tab_action = new_tab_action

        open_action = QAction('&Open...', self)
        open_action.setShortcut('Ctrl+O')
        self.connect(open_action, SIGNAL('triggered()'), self.open_file)
        self.open_action = open_action

        save_as_action = QAction('Save &As...', self)
        self.connect(save_as_action, SIGNAL('triggered()'), self.save_as_file)
        self.save_as_action = save_as_action

        exit_action = QAction('E&xit', self)
        exit_action.setMenuRole(QAction.QuitRole)
        self.connect(exit_action, SIGNAL('triggered()'),
                     self, SLOT('close()'))
        self.exit_action = exit_action

    def create_menus(self):
        filemenu = self.menuBar().addMenu('&File')
        filemenu.addAction(self.new_tab_action)
        filemenu.addAction(self.open_action)
        filemenu.addSeparator()
        filemenu.addAction(self.save_as_action)
        filemenu.addSeparator()
        filemenu.addAction(self.exit_action)

    def new_tab(self):
        self.tabs.currentWidget().keymode.commit()
        index = self.tabs.addTab(
                        ChordScoreWindow(self.score, self),
                        'Chords')
        self.tabs.setCurrentIndex(index)

    def open_file(self):
        filename = str(QFileDialog.getOpenFileName(self,
                            'Open', '',
                            'Bandleader files (*.score)'))
        if not filename:
            return

        score = None
        with open(filename, mode='rb') as f:
            score = pickle.load(f)

        # replace the old score with the new one
        del self.score[:]
        self.score.extend(score)

        index = self.tabs.addTab(ScoreWindow(self.score, self),
                                 'Leadsheet')

        # remove the existing tabs
        self.tabs.setCurrentIndex(index)
        QApplication.processEvents()
        while self.tabs.count() > 1:
            self.tabs.removeTab(0)

        self.setWindowFilePath(filename)
        self.setWindowModified(False)

    def save_as_file(self):
        filename = str(QFileDialog.getSaveFileName(self,
                        'Save', '',
                        'Bandleader files (*.score)'))
        if not filename:
            return
        if filename.endswith('.score'):
            self.tabs.currentWidget().keymode.commit()
            with open(filename, mode='wb') as f:
                pickle.dump(self.score, f)
            self.setWindowFilePath(filename)
            self.setWindowModified(False)

if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    from music import Score
    import sys
    app = QApplication(sys.argv)
    score = Score()
    score.add_bars(4, 4, 4, count=6)
    window = MainWindow(score)
    window.show()
    sys.exit(app.exec_())
