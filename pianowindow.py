from PyQt4.QtCore import QRectF, QPointF, QSizeF, QPoint, QRect, Qt
from PyQt4.QtGui import *
import notify

white_key_width = 50
black_key_width = 25
white_key_height = 200
black_key_height = 100

white_key_count = 7
black_key_map = [(0, 1), (1, 2), (3, 4), (4, 5), (5, 6)]

def rect_of_white_key(index):
    x = index * white_key_width
    y = 0
    return QRectF(QPointF(x, y), QSizeF(white_key_width, white_key_height))

def rect_of_black_key(index1, index2):
    x = (index1 * white_key_width + index2 * white_key_width
            + black_key_width) / 2.0
    y = 0
    return QRectF(QPointF(x, y), QSizeF(black_key_width, black_key_height))

class WhitePianoKey(QGraphicsRectItem):
    def __init__(self, index, parent=None):
        QGraphicsItem.__init__(self, rect_of_white_key(index), parent)
        self.on_mouse_press = notify.Signal()
        self.index = index

    def mousePressEvent(self, event):
        self.on_mouse_press(event, self.index)

class BlackPianoKey(QGraphicsRectItem):
    def __init__(self, i1, i2, parent=None):
        QGraphicsItem.__init__(self, rect_of_black_key(i1, i2), parent)
        self.setBrush(QBrush(QColor('black')))
        self.on_mouse_press = notify.Signal()
        self.index = (i1, i2)

    def mousePressEvent(self, event):
        self.on_mouse_press(event, self.index)

class PianoScene(QGraphicsScene):
    def __init__(self):
        QGraphicsScene.__init__(self)
        self.create_scene()
        self.note_pressed = notify.Signal()

    def create_scene(self):
        self.create_white_keys()
        self.create_black_keys()

    def create_white_keys(self):
        for i in xrange(white_key_count):
            key = WhitePianoKey(i)
            self.addItem(key)
            key.on_mouse_press.connect(self.white_key_pressed)

    def create_black_keys(self):
        for i1, i2 in black_key_map:
            key = BlackPianoKey(i1, i2)
            self.addItem(key)
            key.on_mouse_press.connect(self.black_key_pressed)

    def white_key_pressed(self, event, index):
        self.note_pressed(index)

    def black_key_pressed(self, event, index):
        pass

class PianoWindow(QGraphicsView):
    def __init__(self, *args):
        QGraphicsView.__init__(self, *args)
        #self.setFrameStyle(QFrame.NoFrame)

    #def setScene(self, scene):
    #    QGraphicsView.setScene(self, scene)
    #    self.fit_to_scene()

    #def fit_to_scene(self):
    #    scene = self.scene()
    #    self.setFixedWidth(xtile_size * scene.score_bar.bar_divisions + 2)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    scene = PianoScene()
    def print_note(index):
        print 'note pressed %d' % index
    scene.note_pressed.connect(print_note)
    window = PianoWindow()
    window.setScene(scene)
    window.show()
    app.exec_()
