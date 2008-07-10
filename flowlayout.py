from PyQt4.QtCore import QRectF, QPointF, QSize, QPoint, QRect, Qt
from PyQt4.QtGui import *

class FlowLayout(QLayout):
    def __init__(self, parent=None):
        QLayout.__init__(self, parent)
        self.items = []
        self.setMargin(0)
        self.setSpacing(-1)

    def addItem(self, item):
        self.items.append(item)

    def count(self):
        return len(self.items)

    def itemAt(self, index):
        if 0 <= index < len(self.items):
            return self.items[index]
        else:
            return None

    def takeAt(self, index):
        if 0 <= index < len(self.items):
            item = self.items[index]
            self.items.remove(item)
            return item
        else:
            return None

    def expandingDirections(self):
        return 0

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        QLayout.setGeometry(self, rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.items:
            size = size.expandedTo(item.minimumSize())

        margin = self.margin()
        size += QSize(2*margin, 2*margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        spacing = self.spacing()
        if spacing < 0:
            spacing = 0

        right_x = x

        for item in self.items:
            nextX = x + item.sizeHint().width() + spacing
            if (nextX - spacing > rect.right()) and lineHeight > 0:
                right_x = max(x, right_x)
                x = rect.x()
                y = y + lineHeight + spacing
                nextX = x + item.sizeHint().width() + spacing
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        if not testOnly and self.alignment() == Qt.AlignHCenter:
            inner_width = (right_x - rect.x())
            outer_width = rect.width()
            offset_x = (outer_width - inner_width) / 2

            if offset_x >= 0:
                for item in self.items:
                    geometry = item.geometry()
                    point = QPoint(geometry.x() + offset_x, geometry.y())
                    item.setGeometry(QRect(point, geometry.size()))

        return y + lineHeight - rect.y()
