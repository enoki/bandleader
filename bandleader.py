from PyQt4.QtGui import QApplication
from music import ScoreBar
from mainwindow import MainWindow
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)

    score = [ScoreBar(4, 4, 4) for x in xrange(32)]

    window = MainWindow(score)
    window.show()

    sys.exit(app.exec_())
