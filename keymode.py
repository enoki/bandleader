from PyQt4.QtCore import Qt
import notify

class ChordMode(object):
    BeginInserting = notify.Signal()
    EndInserting = notify.Signal()

    def __init__(self, cursor):
        self.cursor = cursor

    def keyPressEvent(self, event):
        key = event.key()
        cursor = self.cursor
        if key == Qt.Key_H or key == Qt.Key_Left:
            cursor.move_left()
        elif key == Qt.Key_L or key == Qt.Key_Right or key == Qt.Key_Return:
            cursor.move_right()
        elif key == Qt.Key_K or key == Qt.Key_Up:
            cursor.move_up()
        elif key == Qt.Key_J or key == Qt.Key_Down:
            cursor.move_down()
        elif key == Qt.Key_C:
            cursor.append_text('C')
        else:
            return False
        return True

    def setup(self):
        def do_nothing():
            pass
        self.cursor.move(do_nothing)

    def migrate_from(self, mode):
        if hasattr(mode, 'cursor'):
            self.cursor.bar_index = mode.cursor.bar_index

class KeyMode(object):
    def __init__(self, chord_cursor):
        self.modes = {
                       'chord' : ChordMode(chord_cursor),
                     }
        self.mode = self.modes['chord']

    def keyPressEvent(self, event):
        return self.mode.keyPressEvent(event)

    def switch_mode(self, modename):
        old_mode = self.mode
        self.mode = self.modes[modename]
        self.mode.setup()
        self.mode.migrate_from(old_mode)
