import notify

class ScoreBar(object):
    def __init__(self, beats_per_bar, bar_value, divisions_per_beat):
        self.compute(beats_per_bar, bar_value, divisions_per_beat)
        self.entered = [0 for x in xrange(self.bar_divisions)]
        self.note_of = [0 for x in xrange(self.bar_divisions)]
        self.chords = ['/' for x in xrange(self.beats_per_bar)]
        self.lyrics = ['']
        self.entered[0] = 1
        self.tie_first = False
        self.tie_last = False

    def compute(self, beats_per_bar, bar_value, divisions_per_beat):
        self.bar_divisions = beats_per_bar * divisions_per_beat
        self.bar_divisions = self.bar_divisions
        self.beats_per_bar = beats_per_bar
        self.divisions_per_beat = divisions_per_beat
        self.bar_value = bar_value
        self.bar_total_value = beats_per_bar * bar_value

    def __repr__(self):
        return repr((self.entered, self.note_of))

def each_score_bar_coord(score_bar):
    bar_divisions = score_bar.bar_divisions
    entered = score_bar.entered
    note_of = score_bar.note_of
    i = 0
    while i < bar_divisions:
        if entered[i] > 0:
            col = i
            row = note_of[i]
            i += 1
            duration = 1
            while i < bar_divisions and entered[i] == 0:
                duration += 1
                i += 1
            yield (col, row, duration)
        else:
            i += 1

class Score(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)
        self.about_to_delete_bar = notify.Signal()
        self.bar_deleted = notify.Signal()
        self.about_to_insert_bar = notify.Signal()
        self.bar_inserted = notify.Signal()
        self.bar_appended = notify.Signal()
        self.chord_text_changed = notify.Signal()

    def add_bars(self, beats_per_bar, bar_value, divisions_per_beat, count=1):
        self.extend(ScoreBar(beats_per_bar, bar_value, divisions_per_beat)
                        for x in xrange(count))

    def delete_bar(self, bar_index):
        self.about_to_delete_bar(bar_index)
        del self[bar_index]
        self.bar_deleted(bar_index)

    def insert_bar(self, bar_index, bar):
        self.about_to_insert_bar(bar_index)
        self.insert(bar_index, bar)
        self.bar_inserted(bar_index)

    def append_bar(self, bar):
        self.append(bar)
        self.bar_appended()

    def set_chord(self, parent_id, bar_index, beat_index, text):
        self[bar_index].chords[beat_index] = text
        self.chord_text_changed(parent_id, bar_index, beat_index)
