from PyQt4.QtCore import Qt
from PyQt4.QtGui import *
from barwindow import BarWindow, BarScene
from flowlayout import FlowLayout
from chordcursor import ChordCursor
from keymode import KeyMode
from pianowindow import PianoScene, PianoWindow

def set_background(widget, color):
    palette = widget.palette()
    palette.setColor(QPalette.Window, color)
    widget.setPalette(palette)

class ScoreWindow(QWidget):
    def __init__(self, score, *args):
        QWidget.__init__(self, *args)
        self.score = score
        self.bars = []
        self.chord_cursor = ChordCursor(score)
        self.keymode = KeyMode(self.chord_cursor)
        self.create_controls(score)
        self.connect_cursors(score)
        self.connect_score(score)

    def create_controls(self, score):
        inner_widget = QWidget(self)
        set_background(inner_widget, QColor('white'))
        self.inner_widget = inner_widget

        bar_layout = FlowLayout(inner_widget)
        bar_layout.setAlignment(Qt.AlignHCenter)
        self.bar_layout = bar_layout

        for i, bar in enumerate(score):
            b = self.create_bar(i)
            bar_layout.addWidget(b)

        scroller = QScrollArea()
        scroller.setWidget(inner_widget)
        scroller.setWidgetResizable(True)
        scroller.setFocusPolicy(Qt.NoFocus)
        self.scroller = scroller

        layout = QVBoxLayout(self)
        layout.addWidget(scroller)
        self.layout = layout

    def connect_cursors(self, score):
        self.chord_cursor.connect(self.bar_layout.row_column_of,
                                  self.bar_layout.index_of,
                                  self)
        self.connect_chord_cursor()

    def connect_bar(self, bar):
        bar.chord_label_focused_by_mouse.connect(
                self.chord_label_focused_by_mouse)
        bar.request_chord_label_commit.connect(
                self.commit_chord_cursor)

    def connect_chord_cursor(self):
        cursor = self.chord_cursor
        cursor.about_to_be_moved.connect(self.unmove_chord_cursor)
        cursor.moved.connect(self.move_chord_cursor)
        cursor.request_text.connect(self.get_chord_cursor_text)
        cursor.request_append.connect(self.append_chord_cursor_text)
        cursor.request_backspace.connect(self.backspace_chord_cursor_text)
        cursor.request_delete.connect(self.delete_chord_cursor_text)
        cursor.request_change_text.connect(self.change_chord_cursor_text)

    def connect_score(self, score):
        score.bar_deleted.connect(self.delete_bar)
        score.bar_inserted.connect(self.insert_bar)
        score.bar_appended.connect(self.append_bar)
        score.chord_text_changed.connect(self.chord_cursor_text_changed)

    def move_chord_cursor(self, bar_index, beat_index):
        self.bars[bar_index].focus_chord_label(beat_index)
        for view in self.bars[bar_index].views():
            self.scroller.ensureWidgetVisible(view)

    def unmove_chord_cursor(self, bar_index, beat_index):
        self.bars[bar_index].unfocus_chord_label(beat_index)

    def get_chord_cursor_text(self, bar_index, beat_index):
        return self.bars[bar_index].get_chord_label(beat_index)

    def append_chord_cursor_text(self, bar_index, beat_index, text):
        self.bars[bar_index].append_to_chord_label(beat_index, text)

    def backspace_chord_cursor_text(self, bar_index, beat_index):
        self.bars[bar_index].backspace_in_chord_label(beat_index)

    def delete_chord_cursor_text(self, bar_index, beat_index):
        self.bars[bar_index].delete_in_chord_label(beat_index)

    def change_chord_cursor_text(self, bar_index, beat_index, text):
        self.bars[bar_index].change_chord_label(beat_index, text)

    def chord_label_focused_by_mouse(self, bar_index, beat_index):
        self.chord_cursor.move_to(bar_index, beat_index)

    def commit_chord_cursor(self):
        self.chord_cursor.commit()

    def delete_bar(self, bar_index):
        for widget in self.bars[bar_index].views():
            self.bar_layout.removeWidget(widget)
            widget.deleteLater()

        del self.bars[bar_index]

        for i in xrange(bar_index, len(self.score)):
            self.bars[i].set_bar_index(i)

    def insert_bar(self, bar_index):
        b = self.create_bar(bar_index)
        self.bar_layout.insert_widget(bar_index, b)
        b.show()

        for i in xrange(bar_index, len(self.score)):
            self.bars[i].set_bar_index(i)

    def append_bar(self):
        b = self.create_bar(len(self.score)-1)
        self.bar_layout.addWidget(b)
        b.show()
        QApplication.processEvents()

    def chord_cursor_text_changed(self, parent_id, bar_index, beat_index):
        if id(self) != parent_id:
            self.bars[bar_index].update_chord_label(beat_index)

    def create_bar(self, bar_index):
        scene = BarScene(self.score[bar_index], bar_index)
        b = BarWindow(self.inner_widget)
        b.setScene(scene)
        self.bars.insert(bar_index, scene)
        self.connect_bar(scene)
        return b

    def toggle_beat_lines(self):
        for bar in self.bars:
            bar.toggle_beat_lines()

    def show_piano(self):
        if not hasattr(self, 'piano_scene'):
            scene = PianoScene()
            scene.note_pressed.connect(self.insert_piano_note)
            self.piano_scene = scene
            window = PianoWindow()
            window.setScene(scene)
            self.layout.addWidget(window)
            window.show()
            self.piano_window = window
        else:
            self.piano_window.setVisible(not self.piano_window.isVisible())

    def insert_piano_note(self, index):
        print 'note clicked at %d' % index

    def showEvent(self, event):
        self.setFocus()
        self.chord_cursor.connect(self.bar_layout.row_column_of,
                                  self.bar_layout.index_of,
                                  self)
        self.keymode.switch_mode('chord')
        QWidget.showEvent(self, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Comma:
            self.toggle_beat_lines()
            return
        elif event.key() == Qt.Key_F8:
            self.show_piano()
            return
        handled = self.keymode.keyPressEvent(event)
        if not handled:
            QWidget.keyPressEvent(self, event)

if __name__ == '__main__':
    import sys
    from music import Score
    app = QApplication(sys.argv)
    score = Score()
    score.add_bars(4, 4, 4, 4)
    window = ScoreWindow(score)
    window.show()
    app.exec_()
