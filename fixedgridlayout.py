from PyQt4.QtCore import Qt, QSize, QRect, QPoint
from PyQt4.QtGui import QLayout, QWidgetItem

class FixedGridLayout(QLayout):
    def __init__(self, column_count, *args):
        QLayout.__init__(self, *args)
        self.items = []
        self.column_count = column_count
        self.setMargin(0)
        self.setSpacing(-1)

##
    def row_column_of(self, index):
        return divmod(index, self.column_count)

    def index_of(self, row, column):
        return row * self.column_count + column

    def widget_by_index(self, index):
        return self.items[index].widget()

    def insert_widget(self, index, widget):
        self.items.insert(index, QWidgetItem(widget))
##

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

    def setGeometry(self, rect):
        QLayout.setGeometry(self, rect)
        self.doLayout(rect)

    def max_height(self):
        max_height = 0
        for item in self.items:
            max_height = max(max_height, item.sizeHint().height())
        return max_height

    def sizeHint(self):
        if self.count() <= 0:
            return QSize(0, 0)
        itemheight = self.items[0].sizeHint().height()
        row_count = self.count() // self.column_count
        return QSize(500, itemheight * row_count)

    def minimumSize(self):
        return self.sizeHint()

    def doLayout(self, rect):
        if len(self.items) <= 0:
            return

        x = rect.x()
        y = rect.y()

        col = 0
        row = 0

        column_count = self.column_count

        itemwidth = rect.width() // column_count
        itemheight = self.items[0].sizeHint().height()
        itemsize = QSize(itemwidth, itemheight)

        for index, item in enumerate(self.items):
            item.setGeometry(QRect(QPoint(x, y), itemsize))

            x += itemwidth
            col += 1

            if col >= column_count:
                x = rect.x()
                y = y + itemheight
                col = 0
                row += 1

        return y + itemheight - rect.y()
