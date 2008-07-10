from music import each_score_bar_coord

def note_to_goo(score_bar, *args):
    if score_bar.beats_per_bar == 4 and score_bar.divisions_per_beat == 4:
        return note_to_goo_4_4(score_bar, *args)
    elif score_bar.beats_per_bar == 3 and score_bar.divisions_per_beat == 4:
        return note_to_goo_3_4(score_bar, *args)
    return []

def note_to_goo_3_4(score_bar, note, duration, bar_index):
    goo = []

    beat_offset = bar_index % 4

    if beat_offset in (1, 3):
        goo.append((note, '16'))
        duration -= 1
        bar_index += 1
    elif beat_offset == 2 and duration >= 2:
        goo.append((note, '8'))
        duration -= 2
        bar_index += 2
    else: # beat_offset == 0
        if duration == 1:
            goo.append((note, '16'))
        elif duration == 2:
            goo.append((note, '8'))
        elif duration == 3:
            goo.append((note, '8.'))
        elif duration == 4:
            goo.append((note, '4'))
        elif duration == 5:
            goo.append((note, '4'))
            goo.append(('~', '0'))
            goo.append((note, '16'))
        elif duration == 6:
            goo.append((note, '4.'))
        elif duration == 7:
            goo.append((note, '4'))
            goo.append(('~', '0'))
            goo.append((note, '8.'))
        elif duration == 8:
            goo.append((note, '2'))
        elif duration == 9:
            goo.append((note, '2'))
            goo.append(('~', '0'))
            goo.append((note, '16'))
        elif duration == 10:
            goo.append((note, '2'))
            goo.append(('~', '0'))
            goo.append((note, '8'))
        elif duration == 11:
            goo.append((note, '2'))
            goo.append(('~', '0'))
            goo.append((note, '8.'))
        elif duration == 12:
            goo.append((note, '2.'))
        return goo

    if duration > 0:
        goo.append(('~', '0'))
        goo.extend(note_to_goo_3_4(score_bar, note, duration, bar_index))

    return goo

def note_to_goo_4_4(score_bar, note, duration, bar_index):
    goo = []

    beat_offset = bar_index % 4

    if beat_offset in (1, 3):
        goo.append((note, '16'))
        duration -= 1
        bar_index += 1
    elif beat_offset == 2 and duration >= 2:
        goo.append((note, '8'))
        duration -= 2
        bar_index += 2
    else: # beat_offset == 0
        if duration == 1:
            goo.append((note, '16'))
        elif duration == 2:
            goo.append((note, '8'))
        elif duration == 3:
            goo.append((note, '8.'))
        elif duration == 4:
            goo.append((note, '4'))
        elif duration == 5:
            goo.append((note, '4'))
            goo.append(('~', '0'))
            goo.append((note, '16'))
        elif duration == 6:
            goo.append((note, '4.'))
        elif duration == 7:
            goo.append((note, '4'))
            goo.append(('~', '0'))
            goo.append((note, '8.'))
        elif duration == 8:
            goo.append((note, '2'))
        elif duration == 9:
            goo.append((note, '2'))
            goo.append(('~', '0'))
            goo.append((note, '16'))
        elif duration == 10:
            goo.append((note, '2'))
            goo.append(('~', '0'))
            goo.append((note, '8'))
        elif duration == 11:
            goo.append((note, '2'))
            goo.append(('~', '0'))
            goo.append((note, '8.'))
        elif duration == 12:
            goo.append((note, '2.'))
        if duration == 13:
            goo.append((note, '2.'))
            goo.append(('~', '0'))
            goo.append((note, '16'))
        elif duration == 14:
            goo.append((note, '2'))
            goo.append(('~', '0'))
            goo.append((note, '4.'))
        elif duration == 15:
            goo.append((note, '2.'))
            goo.append(('~', '0'))
            goo.append((note, '8.'))
        elif duration == 16:
            goo.append((note, '1'))
        return goo

    if duration > 0:
        goo.append(('~', '0'))
        goo.extend(note_to_goo(score_bar, note, duration, bar_index))
    return goo

def score_bar_to_goo(score_bar):
    for col, row, duration in each_score_bar_coord(score_bar):
        for goo_note in note_to_goo(score_bar, row, duration, col):
            yield goo_note

def goo_without_dots(goo, bar_total_value):
    new_goo = []
    for goo_note, goo_duration in goo:
        if goo_duration.endswith('.'):
            undotted = goo_duration.replace('.', '')
            duration = bar_total_value // int(undotted)
            halfduration = bar_total_value // (duration // 2)
            new_goo.append((goo_note, undotted))
            new_goo.append((goo_note, str(halfduration)))
        else:
            new_goo.append((goo_note, goo_duration))
    return new_goo

def goo_duration_to_duration(goo_duration, score_bar):
    duration = int(goo_duration.replace('.', ''))
    if duration != 0:
        duration = score_bar.bar_total_value // duration
    if goo_duration.endswith('.'):
        duration += duration / 2
    return duration

