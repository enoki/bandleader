from PyQt4.QtGui import QWidget, QPlainTextEdit, QHBoxLayout, QApplication
from itertools import izip
import notify

class LyricsEditor(QPlainTextEdit):
    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)

class KeyMode(object):
    def __init__(self):
        self.on_commit = notify.Signal()

    def commit(self):
        self.on_commit()

class LyricsWindow(QWidget):
    def __init__(self, score, *args):
        QWidget.__init__(self, *args)
        self.score = score
        self.keymode = KeyMode()
        self.keymode.on_commit.connect(self.update_score)
        self.create_controls()

    def create_controls(self):
        editor = LyricsEditor()
        layout = QHBoxLayout()
        layout.addWidget(editor)
        self.setLayout(layout)
        self.editor = editor

    def update_score(self):
        text = self.text()
        text_bars = text.split("/")
        for bar, text_bar in izip(self.score, text_bars):
            bar.lyrics[0] = text_bar

    def text(self):
        return self.editor.toPlainText()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = LyricsWindow()
    window.show()
    app.exec_()
    print window.text()
