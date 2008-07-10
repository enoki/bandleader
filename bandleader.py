from PyQt4.QtGui import QApplication
from music import Score
from mainwindow import MainWindow
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)

    score = Score()
    score.add_bars(4, 4, 4, count=16)

    window = MainWindow(score)
    window.show()

    sys.exit(app.exec_())
