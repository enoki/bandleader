import louie as notify

class ChordCursor(object):
    AboutToBeMoved = notify.Signal()
    Moved = notify.Signal()

    def __init__(self, score, bars_per_row):
        self.score = score
        self.bars_per_row = bars_per_row
        self.bar_index = 0
        self.beat_index = 0
        self.zoomlevel = 2

    def move(self, move_function):
        notify.send(self.AboutToBeMoved, self, self.bar_index, self.beat_index)
        move_function()
        notify.send(self.Moved, self, self.bar_index, self.beat_index)

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
            self.bar_index = self.bar_number_of(row, column)
            if self.bar_index > self.bar_count()-1:
                self.bar_index = self.bar_count()-1

    def do_move_up(self):
        row, column = self.row_column()
        if row > 0:
            row -= 1
            self.bar_index = self.bar_number_of(row, column)

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
        return divmod(self.bar_index, self.bars_per_row)

    def last_row(self):
        return (self.bar_count()-1) // self.bars_per_row

    def bar_number_of(self, row, col):
        return row * self.bars_per_row + col
