class ChordCursor(object):
    def __init__(self, parent):
        self.is_bar_visible = parent.is_bar_visible
        self.bars_per_row = parent.col_count
        self.bar_count = parent.bar_count
        self.bar_window_at = parent.bar_window
        self.bar_index = 0
        self.beat_index = 0
        self.editing_chord = False
        self.zoomlevel = 2

    def move(self, move_function):
        self.start_move()
        move_function()
        self.end_move()

    def start_move(self):
        self.commit_chord()
        self.bar_window().erase_chord_cursor()

    def end_move(self):
        self.bar_window().draw_chord_cursor(self.beat_index)

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
        beat_index = self.beat_index + 1 * self.zoomlevel # TODO
        if beat_index >= beats_per_bar:
            if self.bar_index < self.bar_count()-1:
                self.bar_index += 1
                self.beat_index = 0
        else:
            self.beat_index = beat_index

    def do_move_left(self):
        beat_index = self.beat_index - 1 * self.zoomlevel # TODO
        if beat_index < 0:
            if self.bar_index > 0:
                self.bar_index -= 1
                self.beat_index = beats_per_bar - 1*self.zoomlevel # TODO
        else:
            self.beat_index = beat_index

    def do_move_down(self):
        row, column = self.row_column()
        if row < self.last_row():
            row += 1
            self.bar_index = self.bar_number_of(row, column)

    def do_move_up(self):
        row, column = self.row_column()
        if row > 0:
            row -= 1
            self.bar_index = self.bar_number_of(row, column)

    def do_move_to(self, bar_index, beat_index):
        self.bar_index = bar_index
        self.beat_index = beat_index

    def row_column(self):
        return divmod(self.bar_index, self.bars_per_row)

    def last_row(self):
        return (self.bar_count()-1) // self.bars_per_row

    def bar_number_of(self, row, col):
        return row * self.bars_per_row + col

    def commit_chord(self):
        if self.editing_chord:
            self.bar_window().commit_chord(self.beat_index)
            self.editing_chord = False

    def backspace(self):
        if self.editing_chord:
            self.bar_window().backspace_focused_text()

    def delete(self):
        if not self.editing_chord:
            self.bar_window().delete_chord()

    def append(self, char):
        self.editing_chord = True
        self.bar_window().append_to_focused_text(char)

    def bar_window(self):
        return self.bar_window_at(self.bar_index)

    # TODO
    def zoom_in(self):
        if self.zoomlevel == 1:
            self.zoomlevel = 2
        else:
            self.zoomlevel = 1

    # TODO
    def zoom_in_lots(self):
        if self.zoomlevel == 4:
            self.zoomlevel = 2
        else:
            self.zoomlevel = 4

    def setup(self):
        self.bar_window().after(500, self.end_move)

