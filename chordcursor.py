import notify
from music import ScoreBar

class ChordCursor(object):
    def __init__(self, score):
        self.score = score
        self.bar_index = 0
        self.beat_index = 0
        self.zoomlevel = 2
        self.editing = False
        self.about_to_be_moved = notify.Signal()
        self.moved = notify.Signal()
        self.request_text = notify.Signal()
        self.request_append = notify.Signal()
        self.request_backspace = notify.Signal()
        self.request_delete = notify.Signal()
        self.request_change_text = notify.Signal()

    def connect(self, row_column_of, bar_index_of, parent):
        self.row_column_of = row_column_of
        self.bar_index_of = bar_index_of
        self.parent_id = id(parent)

    def move(self, move_function):
        self.about_to_be_moved(self.bar_index, self.beat_index)
        move_function()
        self.moved(self.bar_index, self.beat_index)

    def move_nowhere(self):
        def do_nothing():
            pass
        self.move(do_nothing)

    def move_right(self):
        self.move(self.do_move_right)

    def move_left(self):
        self.move(self.do_move_left)

    def move_up(self):
        self.move(self.do_move_up)

    def move_down(self):
        self.move(self.do_move_down)

    def move_to(self, bar_index, beat_index):
        self.move(lambda: self.do_move_to(bar_index, beat_index))

    def move_to_row_start(self):
        self.move(self.do_move_to_row_start)

    def move_to_row_end(self):
        self.move(self.do_move_to_row_end)

    def move_to_start(self):
        self.move(self.do_move_to_start)

    def move_to_end(self):
        self.move(self.do_move_to_end)

    def do_move_right(self):
        beat_index = self.beat_index + self.zoomfactor()
        if beat_index >= self.current_bar().beats_per_bar:
            if self.bar_index < self.bar_count()-1:
                self.bar_index += 1
                self.beat_index = 0
        else:
            self.beat_index = beat_index

    def do_move_left(self):
        beat_index = self.beat_index - self.zoomfactor()
        if beat_index < 0:
            if self.bar_index > 0:
                self.bar_index -= 1
                beats_per_bar = self.current_bar().beats_per_bar
                self.beat_index = beats_per_bar - self.zoomfactor()
        else:
            self.beat_index = beat_index

    def do_move_down(self):
        row, column = self.row_column()
        if row < self.last_row():
            row += 1
            while 1:
                try:
                    self.bar_index = self.bar_index_of(row, column)
                except KeyError:
                    column -= 1
                    beats_per_bar = self.current_bar().beats_per_bar
                    self.beat_index = beats_per_bar - self.zoomfactor()
                else:
                    break

    def do_move_up(self):
        row, column = self.row_column()
        if row > 0:
            row -= 1
            self.bar_index = self.bar_index_of(row, column)

    def do_move_to(self, bar_index, beat_index):
        self.bar_index = bar_index
        self.beat_index = beat_index

    def do_move_to_row_start(self):
        row, column = self.row_column()
        self.bar_index = self.bar_index_of(row, 0)
        self.beat_index = 0

    def do_move_to_row_end(self):
        row, column = self.row_column()
        while 1:
            try:
                self.bar_index = self.bar_index_of(row, column)
                self.beat_index = self.score[self.bar_index].beats_per_bar-1
                column += 1
            except KeyError:
                break

    def do_move_to_start(self):
        self.bar_index = 0
        self.beat_index = 0

    def do_move_to_end(self):
        self.bar_index = len(self.score)-1
        self.beat_index = self.score[self.bar_index].beats_per_bar-1

    def zoomfactor(self):
        beats_per_bar = self.current_bar().beats_per_bar
        if beats_per_bar == 4:
            return self.zoomlevel
        elif beats_per_bar == 3 and self.zoomlevel == 4:
            return 3
        else:
            return 1

    def zoom_in(self):
        if self.zoomlevel == 1:
            self.zoomlevel = 2
        else:
            self.zoomlevel = 1

    def zoom_in_lots(self):
        if self.zoomlevel == 4:
            self.zoomlevel = 2
        else:
            self.zoomlevel = 4

    def bar_count(self):
        return len(self.score)

    def current_bar(self):
        return self.score[self.bar_index]

    def row_column(self):
        return self.row_column_of(self.bar_index)

    def last_row(self):
        row, column = self.row_column_of(self.bar_count()-1)
        return row

    def commit(self):
        if self.editing:
            self.editing = False
            if len(self.current_text()) == 0:
                self.append_text('/')
            self.score.set_chord(self.parent_id,
                                 self.bar_index,
                                 self.beat_index,
                                 self.current_text())

    def revert(self):
        if self.editing:
            self.editing = False
            self.change_text(
                self.score[self.bar_index].chords[self.beat_index])
            self.move_nowhere()

    def current_text(self):
        r = self.request_text(self.bar_index, self.beat_index)
        for x, text in r:
            return text
        return ''

    def append_text(self, text):
        self.editing = True
        self.request_append(self.bar_index, self.beat_index, text)

    def backspace_text(self):
        self.request_backspace(self.bar_index, self.beat_index)

    def delete_text(self):
        self.request_delete(self.bar_index, self.beat_index)

    def change_text(self, text):
        self.change_text_at(text, self.bar_index, self.beat_index)

    def change_text_at(self, text, bar_index, beat_index):
        self.request_change_text(bar_index, beat_index, text)
        self.score[self.bar_index].chords[self.beat_index] = text

    def delete_bar(self):
        if len(self.score) > 1:
            self.score.delete_bar(self.bar_index)

            if self.bar_index == len(self.score):
                self.bar_index -= 1
                self.beat_index = self.score[self.bar_index].beats_per_bar-1
            self.moved(self.bar_index, self.beat_index)

    def insert_bar(self):
        self.move(self.do_insert_bar)

    def do_insert_bar(self):
        self.score.insert_bar(self.bar_index, ScoreBar(4, 4, 4))
        self.beat_index = 0

    def append_bar(self):
        self.move(self.do_append_bar)

    def do_append_bar(self):
        self.score.append_bar(ScoreBar(4, 4, 4))
        self.bar_index = len(self.score)-1
        self.beat_index = 0

    def reset_bar(self):
        for beat_index in xrange(len(self.score[self.bar_index].chords)):
            self.change_text_at(self.bar_index, beat_index, '/')
