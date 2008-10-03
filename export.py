from __future__ import with_statement
from goo import *
import cPickle as pickle

mma_notetuples = [
    ('r', ''),
    ('e', '+'), ('d', '+'), ('c', '+'), ('b', '+'), ('a', '+'),
    ('g', '+'), ('f', '+'), ('e', '+'), ('d', '+'), ('c', '+'),
    ('b', ''), ('a', ''), ('g', ''), ('f', ''), ('e', ''),
    ('d', ''), ('c', ''),
    ('b', '-'), ('a', '-'), ('g', '-'), ('f', '-')
]

mma_durations = [
    '',
    '16',
    '8',
    '8.',
    '4',
    '16+4',
    '4.',
    '16+8+4',
    '2',
    '16+2',
    '8+2',
    '16+8+2',
    '2.',
    '16+2.',
    '4.+2',
    '16+8+2.',
    '1',
]

lilypond_notename = [
    "_",
    "e'''", "d'''", "c'''", "b''", "a''",
    "g''", "f''", "e''", "d''", "c''", "b'", "a'",
    "g'", "f'", "e'", "d'", "c'", "b", "a",
    "g", "f"]


def goo_to_lilypond(goo):
    lilypond = []
    for goo_note, goo_duration in goo:
        if goo_note == '~':
            lilypond.append('~')
        elif goo_note == 0:
            lilypond.append('r%s' % goo_duration)
        else:
            note = lilypond_notename[goo_note]
            lilypond.append('%s%s' % (note, goo_duration))
    return ' '.join(lilypond)

def chords_to_lilypond(bar_chords):
    lilypond = []
    for chord in bar_chords:
        if chord == '/':
            lilypond.append('r4')
        else:
            lilypond.append('%s4' % chord)
    return ' '.join(lilypond)

def score_chords_to_lilypond(score):
    lilypond = []
    for bar in score:
        lilypond.extend(chords_to_lilypond(bar.chords))
    return ' '.join(lilypond)

def score_to_lilypond(score):
    lilypond = []
    lilypond.append(r'\version "2.10.0"')
    lilypond.append('')
    lilypond.append('{')
    lilypond.append(goo_to_lilypond(flat_goo(score_to_goo(score))))
    lilypond.append('}')
    lilypond.append('')
    lilypond.append(r'\chords {')
    lilypond.append(score_chords_to_lilypond(score))
    lilypond.append('}')
    return '\n'.join(lilypond)

def goo_duration_to_abc_duration(goo_duration):
    dotted = goo_duration.endswith('.')
    goo_duration.replace('.', '')
    abc_duration = int(goo_duration)
    if dotted:
        abc_duration += abc_duration // 2
    return abc_duration

def score_to_abc(score):
    abc = []
    abc.append('% Autogenerated by Bandleader')
    abc.append('X: 1')
    abc.append('T: Untitled')
    abc.append('C: Anonymous')
    abc.append('M: 4/4')
    abc.append('L: 1')
    abc.append('R: unknowntype')
    abc.append('K: C')
    for bar in score_to_goo(score):
        barabc = []
        for goo_note, goo_duration in bar:
            abc_duration = goo_duration_to_abc_duration(goo_duration)
            barabc.append("%s/%d" % (abc_notename[goo_note], abc_duration))
        barabc.append("|")
        abc.append(' '.join(barabc))
    for bar in score:
        if bar.lyrics[0]:
            abc.append('W: %s' % bar.lyrics[0])
    return '\n'.join(abc)

def score_to_mma(score):
    mma = []

    mma.append('// Autogenerated by Bandleader')
    mma.append('')
    mma.append('Groove Swing')
    mma.append('Tempo 120')
    #mma.append('z * 2')
    mma.append('')

    mma.append('Begin Solo')
    #mma.append('Voice Piano1')
    mma.append('Voice Strings')
    mma.append('Volume ff')
    #mma.append('Articulate 99')
    mma.append('End')

    for bar_number, bar in enumerate(score):
        line = []
        line.append(str(bar_number+1))
        for chord in bar.chords:
            line.append(chord)
        if bar.lyrics[0]:
            line.append('[%s]' % bar.lyrics[0])
        line.append('{')
        if bar.tie_first:
            line.append('~')
        for note_index, note_row, note_duration in each_score_bar_coord(bar):
            note, octave = mma_notetuples[note_row]
            duration = mma_durations[note_duration]
            line.append("%s%s%s;" % (duration, note, octave))
        if bar.tie_last:
            last_line = line.pop()
            line.append(last_line[0:-1])
            line.append('~;')
        line.append('}')

        mma.append(' '.join(line))

    return '\n'.join(mma)

def export_lilypond(filename, score):
    with open(filename, mode='w') as f:
        f.write(score_to_lilypond(score))

def export_mma(filename, score):
    with open(filename, mode='w') as f:
        f.write(score_to_mma(score))

def export_bandleader(filename, score):
    with open(filename, mode='wb') as f:
        pickle.dump(score, f)
