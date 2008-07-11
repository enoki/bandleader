import notify

class ChordCursor(object):
    def __init__(self, score, row_column_of, bar_index_of):
        self.score = score
        self.row_column_of = row_column_of
        self.bar_index_of = bar_index_of
        self.bar_index = 0
        self.beat_index = 0
        self.zoomlevel = 2
        self.about_to_be_moved = notify.Signal()
        self.moved = notify.Signal()
        self.text_appended = notify.Signal()

    def move(self, move_function):
        self.about_to_be_moved(self.bar_index, self.beat_index)
        move_function()
        self.moved(self.bar_index, self.beat_index)

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

    def append_text(self, text):
        self.text_appended(self.bar_index, self.beat_index, text)
