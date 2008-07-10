from PyQt4.QtCore import QRectF, QPointF, QSize, QPoint, QRect, Qt
from PyQt4.QtGui import *
import louie as notify
from music import ScoreBar, each_score_bar_coord
from goo import *

# beamtypes
beam_none = -1
beam_next = -2

class StemInfo(object):
    def __init__(self, valid, row, item_id, duration, notetype, beamtype):
        self.valid = valid
        self.row = row
        self.item_id = item_id
        self.duration = duration
        self.notetype = notetype
        self.beamtype = beamtype
        self.stem_y = 0

global_images = {
    "notehead_solid": """R0lGODlhDQAKAPAAAAAAAP///yH5BAEAAAEALAAAAAANAAoAAAIUjA2ph+pwngxy1ospTjq3ynQL
UwAAOw==
""",
    "notehead_2": """R0lGODlhDgALAPAAAAAAAP///yH5BAEAAAEALAAAAAAOAAsAAAIbjB+gi7avDgSIptfSjXnbjHXY
J4XkVE6kA3UFADs=
""",
    "notehead_1": """R0lGODlhFAAKAPAAAAAAAP///yH5BAEAAAEALAAAAAAUAAoAAAIejA2pe73QwoOIRfmwvXPe2imf
FlJc5p0iuB6Z2kUFADs=
""",
    "noteflag_up_8": """R0lGODlhCwAdAPAAAAAAAP///yH5BAEAAAEALAAAAAALAB0AAAIrjI8BmcvnnpImPmBbRnjXfnWb
iDVfCUFopaXtxDjeNC+zct+wpPeU/wsGCgA7
""",
    "noteflag_up_16": """R0lGODlhCwAeAPAAAAAAAP///yH5BAEAAAEALAAAAAALAB4AAAIyjI8BmcvnnpImPmAblniz7iEL
2EDhZEZZV33bWY0wyIrvWSsq7sCtH6MAIZSWsJgpCQsAOw==
""",
    "noteflag_down_8": """R0lGODlhCwAdAPAAAAAAAP///yH5BAEAAAEALAAAAAALAB0AAAItjG+Am4zqWpQR1hmAZXp2p2xP
BlLHJ35koq5a+75LLGYy1z71uZsc1vPNMMQCADs=
""",
    "noteflag_down_16": """R0lGODlhCwAeAPAAAAAAAP///yH5BAEAAAEALAAAAAALAB4AAAIyjI+AG8rnXpMmMrsATrs2zVWg
CIGadZ5Zuqrr1MKlg46y67EcPnd8KOlAKLKH0EMkFgAAOw==
""",
    "rest_8": """R0lGODlhDQASAPAAAAAAAP///yH5BAEAAAEALAAAAAANABIAAAIghB+px5rcFngQSmucfnvPLoGL
SJFBRqKgun4i67mt2RUAOw==
""",
    "rest_16": """R0lGODlhDwAcAPAAAAAAAP///yH5BAEAAAEALAAAAAAPABwAAAI5jIEJdqzp1nkyIGYpxFllDk4h
WI2OiV3TFq3e6bJq936RNsc1mpv9WPIFgcPQj1REolrLo3Jpg44KADs=
""",
    "rest_4": """R0lGODlhCwAbAPAAAAAAAP///yH5BAEAAAEALAAAAAALABsAAAIsjAOnB7naHouy0WWvyXZy91Gh
g3wQ92RSSaZtum6veo3gKGvie8aIz8P4VgUAOw==
""",
}
image_of = None

def create_images():
    global image_of
    if image_of:
        return
    image_of = {}
    for key, value in global_images.iteritems():
        image_of[key] = QPixmap("images/%s.png" % key)

    image_of['notehead_4'] = image_of['notehead_solid']
    image_of['notehead_8'] = image_of['notehead_solid']
    image_of['notehead_16'] = image_of['notehead_solid']

lilypond_notename = [
    "_",
    "e'''", "d'''", "c'''", "b''", "a''",
    "g''", "f''", "e''", "d''", "c''", "b'", "a'",
    "g'", "f'", "e'", "d'", "c'", "b", "a",
    "g", "f"]
bar_row_count = len(lilypond_notename)

ledger_rows = (7, 9, 11, 13, 15)
fake_ledger_rows = (1, 3, 5, 17, 19, 21)
ledger_thickness = 2

barnum_offsety = 0
chordlabel_offsety = 10

offsetx = 0
offsety = chordlabel_offsety + 5
xtile_size = 24
ytile_size = 8
lyric_size = 2
def bbox_rect_of(col, row):
    x, y, x2, y2 = bbox_of(col, row)
    return QRectF(QPointF(x, y), QPointF(x2, y2))
def bbox_of(col, row):
    x = col * xtile_size + offsetx
    y = row * ytile_size + offsety
    return x, y, x + xtile_size, y + ytile_size
def ledger_bbox_of(col, row, col2, row2):
    x, y, a, a = bbox_of(col, row)
    a, a, x2, y2 = bbox_of(col2, row2)
    y += ytile_size // 2
    y2 -= ytile_size // 2
    return (x, y, x2, y2)

class NoteSlot(QGraphicsRectItem):
    def __init__(self, rect, col, row, parent=None):
        QGraphicsRectItem.__init__(self, rect, parent)
        self.col, self.row = col, row
        self.on_mouse_press = notify.Signal()

    def mousePressEvent(self, event):
        notify.send(self.on_mouse_press, self, event, self.col, self.row)

    def paint(self, painter, option, widget=None):
        pass

class NoteShadow(QGraphicsRectItem):
    def __init__(self, rect, col, row, fill, parent=None):
        QGraphicsRectItem.__init__(self, rect, parent)
        self.set_look(fill)
        self.col, self.row = col, row
        self.on_mouse_press = notify.Signal()

    def set_look(self, fill):
        self.setPen(QPen(Qt.NoPen))
        color = QColor(fill)
        color.setAlpha(120)
        self.setBrush(QBrush(color))

    def mousePressEvent(self, event):
        notify.send(self.on_mouse_press, self, event, self.col, self.row)

class ChordLabel(QGraphicsTextItem):
    def __init__(self, x, y, beat_index, *args):
        QGraphicsTextItem.__init__(self, *args)
        self.setPos(x, y)
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.beat_index = beat_index

    def focusInEvent(self, event):
        QGraphicsTextItem.focusInEvent(self, event)

    def keyPressEvent(self, event):
        QGraphicsTextItem.keyPressEvent(self, event)

class BarScene(QGraphicsScene):
    def __init__(self, score_bar, bar_index):
        QGraphicsScene.__init__(self)
        self.score_bar = score_bar
        self.bar_index = bar_index
        self.items_by_tag = {}
        self.items_by_id = {}
        create_images()
        self.create_initial_scene()

    def create_initial_scene(self):
        bar_divisions = self.score_bar.bar_divisions
        for col in xrange(bar_divisions):
            for row in xrange(1, bar_row_count):
                self.create_note_slot(col, row)
        self.create_bar_number()
        self.create_microbeat_lines()
        self.create_beat_lines()
        self.create_bar_lines()
        self.create_ledger_lines()
        self.create_fake_ledger_lines()
        self.create_chord_labels()
        self.create_lyric_label()
        self.render_notes()

    def create_note_slot(self, col, row):
        note_slot = NoteSlot(bbox_rect_of(col, row), col, row)
        notify.connect(self.on_note_slot_clicked, note_slot.on_mouse_press)
        self.add_item(note_slot, tags=('static', 'noteslot'))

    def on_note_slot_clicked(self, event, col, row):
        if event.modifiers() & Qt.ShiftModifier:
            self.insert_rest(col)
        else:
            self.insert_note(col, row)

    def create_bar_number(self):
        x, y = offsetx, barnum_offsety
        self.add_simple_text(x, y, str(self.bar_index+1),
                             tags=('static', 'barnum'))

    def create_microbeat_lines(self):
        bar_divisions = self.score_bar.bar_divisions
        x, y, x2, y2 = ledger_bbox_of(0, 1, bar_divisions-1, bar_row_count-1)
        pen = QPen(Qt.DotLine)
        self.add_line(x, y, x, y2, pen, tags=('static', 'mbeatline'))
        self.add_line(x2, y, x2, y2, pen, tags=('static', 'mbeatline'))
        for col in xrange(1, bar_divisions):
            x, a, a, a = bbox_of(col, 0)
            self.add_line(x, y, x, y2, pen, tags=('static', 'mbeatline'))

    def create_beat_lines(self):
        a, y, a, y2 = ledger_bbox_of(0, ledger_rows[0], 0, ledger_rows[-1])
        bar_divisions = self.score_bar.bar_divisions
        pen = QPen(Qt.NoPen)
        color = QColor('lightblue')
        color.setAlpha(130)
        brush = QBrush(color)
        for col in xrange(0, bar_divisions, 4):
            x, a, x2, a = bbox_of(col, 0)
            self.add_rect(x, y, x2-x, y2-y, pen, brush,
                          tags=('static', 'beatline'))

    def create_bar_lines(self):
        bar_divisions = self.score_bar.bar_divisions
        x, y, x2, y2 = ledger_bbox_of(0, ledger_rows[0],
                                      bar_divisions-1, ledger_rows[-1])
        pen = QPen()
        pen.setWidth(ledger_thickness)
        self.add_line(x, y, x, y2, pen, tags=('static', 'barline'))
        self.add_line(x2, y, x2, y2, pen, tags=('static', 'barline'))

    def create_ledger_lines(self):
        pen = QPen()
        pen.setWidth(ledger_thickness)
        for row in ledger_rows:
            self.create_ledger_line(row, pen)

    def create_fake_ledger_lines(self):
        pen = QPen(Qt.DashLine)
        for row in fake_ledger_rows:
            self.create_ledger_line(row, pen)

    def create_ledger_line(self, row, pen):
        bar_divisions = self.score_bar.bar_divisions
        x, y, x2, y2 = ledger_bbox_of(0, row, bar_divisions-1, row)
        self.add_line(x, y, x2, y, pen, tags=('static', 'ledger'))

    def create_chord_labels(self):
        score_bar = self.score_bar
        bar_divisions = score_bar.bar_divisions
        divisions_per_beat = score_bar.divisions_per_beat
        for index, col in enumerate(xrange(0, bar_divisions,
                                          divisions_per_beat)):
            self.create_chord_label(col, index)

    def create_chord_label(self, col, index):
        x, a, x2, a = bbox_of(col, 0)
        x = (x + x2) // 2
        y = chordlabel_offsety

        chords = self.score_bar.chords
        self.add_item(ChordLabel(x, y, index, chords[index]),
                      tags=('static', 'chordlabel'))

    def create_lyric_label(self):
        x, y, a, a = bbox_of(0, bar_row_count+1)
        item = self.add_simple_text(x, y,
                                    text=(self.score_bar.lyrics[0] or ' '),
                                    tags=('static', 'lyriclabel'))

    def add_line(self, x, y, x2, y2, pen, tags=None):
        item = self.addLine(x, y, x2, y2, pen)
        return self.register_item(item, tags)

    def add_rect(self, x, y, w, h, pen, brush, tags=None):
        item = self.addRect(x, y, w, h, pen, brush)
        return self.register_item(item, tags)

    def add_pixmap(self, x, y, pixmap, tags=None):
        item = QGraphicsPixmapItem(pixmap)
        item.setPos(x, y)
        return self.add_item(item, tags)

    def add_ellipse(self, x, y, w, h, pen, brush, tags=None):
        item = self.addEllipse(x, y, w, h, pen, brush)
        return self.register_item(item, tags)

    def add_simple_text(self, x, y, text, tags=None):
        item = QGraphicsSimpleTextItem(text)
        item.setPos(x, y)
        return self.add_item(item, tags)

    def add_text(self, x, y, text, tags=None):
        item = QGraphicsTextItem(text)
        item.setPos(x, y)
        return self.add_item(item, tags)

    def add_item(self, item, tags=None):
        self.addItem(item)
        return self.register_item(item, tags)

    def register_item(self, item, tags):
        self.add_tags(item, tags)
        self.items_by_id[id(item)] = item
        return item

    def add_tags(self, item, tags):
        if tags is None:
            return
        if isinstance(tags, basestring):
            tags = (tags,)
        for tag in tags:
            self.tag_item(item, tag)
        item.tags = tags

    def tag_item(self, item, tag):
        if tag not in self.items_by_tag:
            self.items_by_tag[tag] = []
        self.items_by_tag[tag].append(id(item))

    def delete_with_tag(self, tag):
        if tag not in self.items_by_tag:
            return
        items_to_delete = []
        for item_id in self.items_by_tag[tag]:
            items_to_delete.append(self.items_by_id[item_id])
        del self.items_by_tag[tag]

        for item in items_to_delete:
            item_id = id(item)
            del self.items_by_id[item_id]
            self.removeItem(item)
            for tag in item.tags:
                if tag in self.items_by_tag:
                    self.items_by_tag[tag].remove(item_id)

    def items_with_tag(self, tag):
        if tag not in self.items_by_tag:
            return
        for item_id in self.items_by_tag[tag]:
            item = self.items_by_id[item_id]
            yield item

    def insert_rest(self, col):
        self.insert_note(col, 0)

    def insert_note(self, col, row):
        entered = self.score_bar.entered
        note_of = self.score_bar.note_of
        bar_divisions = self.score_bar.bar_divisions
        entered[col] = 1
        note_of[col] = row
        duration = 1
        for c in xrange(col+1, bar_divisions):
            if entered[c] != 0:
                break
            duration += 1
            note_of[c] = row
        self.render_notes()

    def delete_note(self, col, row):
        entered = self.score_bar.entered
        note_of = self.score_bar.note_of
        bar_divisions = self.score_bar.bar_divisions
        if col > 0:
            entered[col] = 0
        note_of[col] = 0
        col += 1
        while col < bar_divisions and entered[col] != 0:
            note_of[col] = 0
            col += 1
        self.render_notes()

    def render_notes(self):
        self.delete_with_tag('note')
        self.plan_beams()

        for col, row, duration in each_score_bar_coord(self.score_bar):
            self.render_note(col, row, duration)

        self.render_stems()
        for item in self.items_with_tag('noteshadow'):
            item.setZValue(-1)
        for item in self.items_with_tag('beatline'):
            item.setZValue(-2)

    def plan_beams(self):
        self.plan_beams_4_4()

    def plan_beams_4_4(self):
        score_bar = self.score_bar
        bar_divisions = score_bar.bar_divisions
        self.beamplan = [beam_none for i in xrange(bar_divisions)]
        self.stem_info_of = [StemInfo(False, 0, 0, 0, 0, 0) for x in xrange(bar_divisions)]

        goo = list(score_bar_to_goo(score_bar))
        i = 0
        for n, (goo_note, goo_duration) in enumerate(goo):
            if goo_note <= 0:
                pass
            elif i % 4 == 0:
                pass
            elif goo_duration == '16' and i % 2 == 0:
                pass
            elif (goo_duration == '8' and n > 0
                  and goo[n-1][1] == '8' and goo[n-1][0] > 0):
                self.beamplan[i-2] = beam_next
                self.beamplan[i] = i-2
            elif (goo_duration == '16' and n > 0
                  and goo[n-1][1] == '16' and goo[n-1][0] > 0):
                self.beamplan[i-1] = beam_next
                self.beamplan[i] = i-1
            duration = goo_duration_to_duration(goo_duration, score_bar)
            if duration > 0:
                i += duration

    def render_note(self, col, row, duration):
        if row == 0:
            row = 10
            self.render_note_shadow(col, row, duration, 'blue')
            self.render_rest_images(col, row, duration)
        else:
            self.render_note_shadow(col, row, duration, 'coral')
            self.render_note_images(col, row, duration)

    def render_note_shadow(self, col, row, duration, fill):
        x, y, a, a = bbox_of(col, row)
        a, a, x2, y2 = bbox_of(col + duration - 1, row)
        rect = QRectF(QPointF(x, y), QPointF(x2, y2))
        item = self.add_item(NoteShadow(rect, col, row, fill),
                             tags=('note', 'noteshadow'))
        notify.connect(self.on_note_shadow_clicked, item.on_mouse_press)

    def on_note_shadow_clicked(self, event, col, row):
        if event.modifiers() & Qt.ControlModifier:
            self.delete_note(col, row)
        else:
            event.ignore()

    def render_rest_images(self, col, row, duration):
        goo = goo_without_dots(note_to_goo(self.score_bar, row, duration, col),
                               self.score_bar.bar_total_value)
        last_col = col
        for note, goo_duration in goo:
            if note == '~':
                pass
            else:
                note_duration = goo_duration_to_duration(goo_duration,
                                                         self.score_bar)
                self.render_rest_goo(col, row, goo_duration)
                last_col = col
                col += note_duration

    def render_rest_goo(self, col, row, goo_duration):
        note_type = int(goo_duration.replace('.', ''))

        if note_type == 1:
            self.render_whole_rest(col, row)
        elif note_type == 2:
            self.render_half_rest(col, row)
        else:
            self.render_rest_image(col, row, note_type)

    def render_whole_rest(self, col, row):
        bar_divisions = self.score_bar.bar_divisions
        x, y, a, a = bbox_of(bar_divisions // 2 - 1, row-1)
        a, y2, a, a = bbox_of(0, row)
        x += 3
        y = (y + y2) / 2
        width = 10
        height = 3
        pen = QPen()
        brush = QBrush(QColor('black'))
        self.add_rect(x, y, width, height, pen, brush,
                      tags=('note', 'noteimage'))

    def render_half_rest(self, col, row):
        x, a, a, y = bbox_of(col, row+1)
        x2, a, a, a  = bbox_of(col + 1, 0)
        width = 9
        height = 2
        x = (x + x2 - width) // 2
        y -= 5
        pen = QPen()
        brush = QBrush(QColor('black'))
        self.add_rect(x, y, width, height, pen, brush,
                      tags=('note', 'noteimage'))

    def render_rest_image(self, col, row, note_type):
        x, y, a, a = bbox_of(col, row)
        x2, y2, a, a = bbox_of(col+1, row+1)
        image = image_of['rest_%d' % note_type]
        x = (x + x2 - image.width()) // 2
        y = (y + y2 - image.height()) // 2
        self.add_pixmap(x, y, image, tags=('note', 'noteimage'))

    def render_note_images(self, col, row, duration):
        goo = note_to_goo(self.score_bar, row, duration, col)
        last_col = col
        for note, goo_duration in goo:
            if note == '~':
                self.render_tie(last_col, row, col, row)
            else:
                note_duration = goo_duration_to_duration(goo_duration,
                                                         self.score_bar)
                self.render_note_goo(col, row, note, goo_duration,
                                     note_duration)
                last_col = col
                col += note_duration

    def render_note_goo(self, col, row, note, goo_duration, note_duration):
        dotted = goo_duration.endswith('.')
        note_type = int(goo_duration.replace('.', ''))
        stemmed = (note_type != 1)
        beamtype = self.beamplan[col]
        image = image_of['notehead_%d' % note_type]
        self.render_note_image(col, row, image, dotted, stemmed,
                               note_type, beamtype, note_duration)

    def render_note_image(self, col, row, image, dotted, stemmed, notetype,
                          beamtype, note_duration):
        x, y, x2, y2 = bbox_of(col, row)
        #x = (x + x2 - image.width()) / 2
        x + image.width() / 2
        y = (y + y2 - image.height()) / 2
        item = self.add_pixmap(x, y, image, tags=('note', 'noteimage'))
        if stemmed:
            self.stem_info_of[col] = StemInfo(True, row, id(item),
                                              note_duration,
                                              notetype, beamtype)
        if dotted:
            x = item.x() + image.width()
            x += 4
            r = 2
            pen = QPen()
            brush = QBrush(QColor('black'))
            self.add_ellipse(x-r, y-r, r+r, r+r, pen, brush,
                             tags=('note', 'noteimage'))

    def render_stems(self):
        preferred_down_stem_y = bbox_of(0, 16)[3]
        preferred_up_stem_y = bbox_of(0, 6)[1]

        for col, steminfo in enumerate(self.stem_info_of):
            if not steminfo.valid:
                continue
            x, y, y2 = 0, 0, 0
            direction = ''
            item_id = steminfo.item_id
            item = self.items_by_id[item_id]
            row = steminfo.row
            if row < 11:
                x = item.x()
                y = item.y() + item.pixmap().height()
                y -= 3
                y2 = y + 40
                y2 = max(y2, preferred_down_stem_y)
                direction = 'down'
            else:
                x = item.x() + item.pixmap().width()
                y = item.y() + item.pixmap().height()
                y -= 4
                y2 = y - 40
                y2 = min(y2, preferred_up_stem_y)
                direction = 'up'

            beamtype = steminfo.beamtype
            duration = steminfo.duration
            notetype = steminfo.notetype
            if beamtype == beam_none:
                self.render_stemflag(x, y2 - 7, direction, notetype)
                self.add_line(x, y, x, y2, QPen(), tags=('note', 'noteimage'))
            elif beamtype == beam_next:
                sy = y2
                next_col = col + duration
                next_stem = self.stem_info_of[next_col]
                next_item = self.items_by_id[next_stem.item_id]
                sy2 = next_item.y() + next_item.pixmap().height()
                if direction == 'down':
                    sy2 = max(sy2 + 15, preferred_down_stem_y)
                else:
                    sy2 = min(sy2 - 20, preferred_up_stem_y)
                self.stem_info_of[col].stem_y = sy2
                self.add_line(x, y, x, sy2, QPen(), tags=('note', 'noteimage'))
                self.render_beam(x, sy2, notetype, direction)
            else:
                sy = y2
                prev_stem = self.stem_info_of[beamtype]
                if prev_stem.row < 11:
                    x = item.x()
                else:
                    x = item.x() + item.pixmap().width()
                self.add_line(x, y, x, prev_stem.stem_y, QPen(),
                              tags=('note', 'noteimage'))

    def render_stemflag(self, x, y, direction, notetype):
        if notetype in (8, 16):
            #x += 5
            stemflag_image = image_of['noteflag_%s_%d' % (direction, notetype)]
            self.add_pixmap(x, y, stemflag_image, tags=('note', 'noteimage'))

    def render_beam(self, x, y, notetype, direction):
        if notetype in (8, 16):
            beamlength = 0
            if notetype == 8:
                beamlength = xtile_size * 2
                #beamlength = 32
            elif notetype == 16:
                beamlength = xtile_size
                #beamlength = 17
                y2 = y
                if direction == 'down':
                    y2 -= 3
                else:
                    y2 += 3
                self.add_line(x, y2, x + beamlength, y2, QPen(),
                              tags=('note', 'noteimage'))
            self.add_line(x, y, x + beamlength, y, QPen(),
                          tags=('note', 'noteimage'))

    def render_tie(self, col1, row1, col2, row2):
        x, y, x2, d = bbox_of(col1, row1)
        x = (x + x2) / 2
        a, b, x2, y2 = bbox_of(col2, row2)
        x2 = (a + x2) / 2
        extent = 0
        if row1 < 11:
            y -= 11
            y2 -= 4
            extent = 180
        else:
            y += 4
            y2 += 12
            extent = -180
        path = QPainterPath()
        path.moveTo(x2, (y+y2)/2)
        path.arcTo(x, y, abs(x2-x), abs(y2-y), 0, extent)
        item = QGraphicsPathItem(path)
        self.add_item(item, tags=('note', 'noteimage'))

class BarWindow(QGraphicsView):
    def __init__(self, *args):
        QGraphicsView.__init__(self, *args)
        self.setFrameStyle(QFrame.NoFrame)

    def setScene(self, scene):
        QGraphicsView.setScene(self, scene)
        self.setFixedWidth(xtile_size * scene.score_bar.bar_divisions + 2)
