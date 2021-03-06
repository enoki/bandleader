from __future__ import with_statement
from PyQt4.QtCore import QString, Qt, SIGNAL, SLOT
from PyQt4.QtGui import QTabWidget, QMainWindow, QAction, QFileDialog, QApplication, QKeySequence
from scorewindow import ScoreWindow
from chordscorewindow import ScoreWindow as ChordScoreWindow
from speeddialwindow import SpeedDialWindow
import export
import cPickle as pickle
import sys

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
        new_tab_action = QAction('&New Tab', self)
        new_tab_action.setShortcuts(QKeySequence.AddTab)
        self.connect(new_tab_action, SIGNAL('triggered()'), self.new_tab)
        self.new_tab_action = new_tab_action

        close_tab_action = QAction('&Close Tab', self)
        close_tab_action.setShortcuts(QKeySequence.Close)
        self.connect(close_tab_action, SIGNAL('triggered()'), self.close_tab)
        self.close_tab_action = close_tab_action

        open_action = QAction('&Open...', self)
        open_action.setShortcuts(QKeySequence.Open)
        self.connect(open_action, SIGNAL('triggered()'), self.open_file)
        self.open_action = open_action

        save_as_action = QAction('Save &As...', self)
        save_as_action.setShortcuts(QKeySequence.SaveAs)
        self.connect(save_as_action, SIGNAL('triggered()'), self.save_as_file)
        self.save_as_action = save_as_action

        exit_action = QAction('E&xit', self)
        exit_action.setMenuRole(QAction.QuitRole)
        self.connect(exit_action, SIGNAL('triggered()'),
                     self, SLOT('close()'))
        self.exit_action = exit_action

        next_tab_action = QAction('Next Tab', self)
        bindings = QKeySequence.keyBindings(QKeySequence.NextChild)
        if sys.platform == 'darwin':
            bindings.append('Meta+PgDown')
            bindings.append('Meta+Tab')
        else:
            bindings.append('Ctrl+PgDown')
        next_tab_action.setShortcuts(bindings)
        self.connect(next_tab_action, SIGNAL('triggered()'), self.focus_next_tab);
        self.addAction(next_tab_action)

        previous_tab_action = QAction('Previous Tab', self)
        bindings = QKeySequence.keyBindings(QKeySequence.PreviousChild)
        if sys.platform == 'darwin':
            bindings.append('Meta+PgUp')
            bindings.append('Meta+Shift+Tab')
        else:
            bindings.append('Ctrl+PgUp')
        previous_tab_action.setShortcuts(bindings)
        self.connect(previous_tab_action, SIGNAL('triggered()'), self.focus_previous_tab);
        self.addAction(previous_tab_action)

    def create_menus(self):
        filemenu = self.menuBar().addMenu('&File')
        filemenu.addAction(self.new_tab_action)
        filemenu.addAction(self.open_action)
        filemenu.addAction(self.close_tab_action)
        filemenu.addSeparator()
        filemenu.addAction(self.save_as_action)
        filemenu.addSeparator()
        filemenu.addAction(self.exit_action)

    def commit_current_tab(self):
        if hasattr(self.tabs.currentWidget(), "keymode"):
            self.tabs.currentWidget().keymode.commit()

    def new_tab(self):
        self.commit_current_tab()
        tab = SpeedDialWindow(self.score, self)
        index = self.tabs.addTab(tab, 'Blank')
        def change_tab_title(title):
            self.tabs.setTabText(index, title)
        tab.title_changed.connect_lambda(change_tab_title)
        self.tabs.setCurrentIndex(index)

    def close_tab(self):
        self.commit_current_tab()
        self.tabs.removeTab(self.tabs.currentIndex())

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
        filters = [
            'Bandleader files (*.score)',
            'MMA files (*.mma)',
            'Lilypond files (*.ly)',
        ]
        exporters = [
            export.export_bandleader,
            export.export_mma,
            export.export_lilypond,
        ]
        selected = QString()
        filename = str(QFileDialog.getSaveFileName(self,
                        'Save', '',
                        ';;'.join(filters), selected))
        if not filename:
            return
        self.save_tab_to(filename, exporters[filters.index(selected)])

    def save_tab_to(self, filename, do_save):
        self.commit_current_tab()
        do_save(filename, self.score)
        self.setWindowFilePath(filename)
        self.setWindowModified(False)

    def focus_next_tab(self):
        index = self.tabs.currentIndex() + 1
        if index >= self.tabs.count():
            index = 0
        self.tabs.setCurrentIndex(index)

    def focus_previous_tab(self):
        index = self.tabs.currentIndex() - 1
        if index < 0:
            index = self.tabs.count() - 1
        self.tabs.setCurrentIndex(index)

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
