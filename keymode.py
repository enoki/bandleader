from PyQt4.QtCore import Qt
import notify

chord_modifiers = set(['aug', 'dim', 'sus'])
chord_tonalities = set(['m', 'M'])
chord_lifts = set(['#', 'b'])
note_names = set(['A', 'B', 'C', 'D', 'E', 'F', 'G'])
chord_numbers = set(['1', '2', '4', '5', '6', '7', '9'])
legal_before_lift = note_names
legal_before_tonality = note_names | chord_lifts
legal_before_modifier = note_names | chord_lifts | chord_tonalities

def handle_chord_input(cursor, key, key_modifiers):
    current_text = cursor.current_text()
    shift_down = key_modifiers & Qt.SHIFT

    def append_slash():
        if len(current_text) > 0 and current_text.find('/') == -1:
            cursor.append_text('/')

    def append_modifier(text):
        if len(current_text) > 0 and current_text[-1] in legal_before_modifier:
            cursor.append_text(text)

    def append_lift(text):
        if len(current_text) > 0 and current_text[-1] in legal_before_lift:
            cursor.append_text(text)

    def append_tonality(text):
        if len(current_text) > 0 and current_text[-1] in legal_before_tonality:
            cursor.append_text(text)

    def append_notename(text):
        if len(current_text) == 0 or current_text[-1] == '/':
            cursor.append_text(text)

    def append_number(text):
        if len(current_text) > 0 and ((
                current_text[-1] in legal_before_modifier and (
                    text in ['1', '5', '7', '6', '9'])
                )
                or
                (current_text[-1] == '1' and current_text[-2] != '1' and
                 text in ['1', '3', '5'])
                or
                (len(current_text) > 3 and
                 current_text[-3] == 'sus' and text in ['2', '4', '9'])
                or
                (len(current_text) > 3 and
                 current_text[-3] == 'aug' and text in ['7', '9'])
                or
                (len(current_text) > 3 and
                 current_text[-3] == 'dim' and text == '7')
        ):
            cursor.append_text(text)

    def backspace():
        if len(current_text) > 0:
            if current_text[-3:] in chord_modifiers:
                cursor.backspace_text()
                cursor.backspace_text()
                cursor.backspace_text()
            else:
                cursor.backspace_text()

    def append_note_or_else(note, do_else):
        if len(current_text) == 0 or current_text[-1] == '/':
            cursor.append_text(note)
        else:
            do_else()

    def append_note_or_modifier(note, modifier):
        append_note_or_else(note, lambda: append_modifier(modifier))

    def append_note_or_lift(note, modifier):
        append_note_or_else(note, lambda: append_lift(modifier))

    def append_note_or_tonality(note, modifier):
        append_note_or_else(note, lambda: append_tonality(modifier))

    def append_3():
        if len(current_text) > 0 and current_text[-1] == '1':
            append_number('3')
        else:
            append_lift('#')

    if key == Qt.Key_A:
        append_note_or_modifier('A', 'aug')
    elif key == Qt.Key_B:
        append_note_or_lift('B', 'b')
    elif key == Qt.Key_C:
        append_notename('C')
    elif key == Qt.Key_D:
        append_note_or_modifier('D', 'dim')
    elif key == Qt.Key_E:
        append_notename('E')
    elif key == Qt.Key_F:
        append_notename('F')
    elif key == Qt.Key_G:
        append_notename('G')
    elif key == Qt.Key_S:
        append_modifier('sus')
    elif key == Qt.Key_M and shift_down:
        append_tonality('M')
    elif key == Qt.Key_M:
        append_tonality('m')
    elif key == Qt.Key_Slash:
        append_slash()
    elif key == Qt.Key_1:
        append_number('1')
    elif key == Qt.Key_2:
        append_number('2')
    elif key == Qt.Key_3:
        append_3()
    elif key == Qt.Key_4:
        append_number('4')
    elif key == Qt.Key_5:
        append_number('5')
    elif key == Qt.Key_6:
        append_number('4')
    elif key == Qt.Key_7:
        append_number('7')
    elif key == Qt.Key_9:
        append_number('9')
    elif key == Qt.Key_Backspace:
        backspace()
    elif key == Qt.Key_Delete:
        cursor.delete_text()
    else:
        return False
    return True

class ChordMode(object):
    def __init__(self, cursor):
        self.cursor = cursor

    def keyPressEvent(self, event):
        key = event.key()
        key_modifiers = event.modifiers()
        shift_down = key_modifiers & Qt.SHIFT
        cursor = self.cursor
        if key == Qt.Key_H or key == Qt.Key_Left:
            cursor.move_left()
        elif key == Qt.Key_L or key == Qt.Key_Right or key == Qt.Key_Return:
            cursor.move_right()
        elif key == Qt.Key_K or key == Qt.Key_Up:
            cursor.move_up()
        elif key == Qt.Key_J or key == Qt.Key_Down:
            cursor.move_down()
        elif key == Qt.Key_Z and shift_down:
            cursor.zoom_in_lots()
        elif key == Qt.Key_Z:
            cursor.zoom_in()
        else:
            return handle_chord_input(cursor, key, key_modifiers)
        return True

    def setup(self):
        def do_nothing():
            pass
        self.cursor.move(do_nothing)

    def migrate_from(self, mode):
        if hasattr(mode, 'cursor'):
            self.cursor.bar_index = mode.cursor.bar_index

    def commit(self):
        self.cursor.commit()

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
        old_mode.commit()
        self.mode = self.modes[modename]
        self.mode.setup()
        self.mode.migrate_from(old_mode)

    def commit(self):
        self.mode.commit()
