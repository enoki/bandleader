from PyQt4.QtGui import QApplication
from music import Score
from mainwindow import MainWindow
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)

    score = Score()
    score.add_bars(4, 4, 4, count=6)
    score.add_bars(3, 4, 4)
    score.add_bars(4, 4, 4)
    score.add_bars(4, 4, 4, count=8)

    window = MainWindow(score)
    window.show()

    sys.exit(app.exec_())
