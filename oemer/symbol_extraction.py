import enum

import cv2
import numpy as np
import scipy.ndimage
import matplotlib.pyplot as plt
import sys 
sys.path.append(".")
sys.path.append("..")
from oemer import layers
from oemer import exceptions as E
from oemer.inference import predict
from oemer.utils import get_global_unit_size, slope_to_degree, get_unit_size, get_logger, find_closest_staffs
from oemer.general_filtering_rules import filter_out_of_range_bbox, filter_out_small_area
from oemer.bbox import (
    merge_nearby_bbox,
    rm_merge_overlap_bbox,
    find_lines,
    draw_lines,
    draw_bounding_boxes,
    get_bbox,
    get_center,
    to_rgb_img
)



logger = get_logger(__name__)


class ClefType(enum.Enum):
    G_CLEF = 1
    F_CLEF = 2


class SfnType(enum.Enum):
    FLAT = 1
    SHARP = 2
    NATURAL = 3


class RestType(enum.Enum):
    WHOLE_HALF = 1
    QUARTER = 2
    EIGHTH = 3
    SIXTEENTH = 4
    THIRTY_SECOND = 5
    SIXTY_FOURTH = 6
    WHOLE = 7
    HALF = 8


class Clef:
    def __init__(self):
        self.bbox: list[int] = None
        self.track: int = None
        self.group: int = None
        self._label: ClefType = None

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, val):
        assert isinstance(val, ClefType)
        self._label = val

    @property
    def x_center(self):
        return (self.bbox[0] + self.bbox[2]) / 2

    def __repr__(self):
        return f"Clef: {self.label.name} / Track: {self.track} / Group: {self.group}"


class Sfn:
    def __init__(self):
        self.bbox: list[int] = None
        self.note_id: int = None
        self.is_key: bool = None  # Whether is key or accidental
        self.track: int = None
        self.group: int = None
        self._label: SfnType = None

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, val):
        assert isinstance(val, SfnType)
        self._label = val

    @property
    def x_center(self):
        return (self.bbox[0] + self.bbox[2]) / 2

    def __repr__(self):
        return f"SFN: {self.label.name} / Note ID: {self.note_id} / Is key: {self.is_key}" \
            f" / Track: {self.track} / Group: {self.group}"


class Rest:
    def __init__(self):
        self.bbox: list[int] = None
        self.has_dot: bool = None
        self.track: int = None
        self.group: int = None
        self._label: RestType = None

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, val):
        assert isinstance(val, RestType)
        self._label = val

    @property
    def x_center(self):
        return (self.bbox[0] + self.bbox[2]) / 2

    def __repr__(self):
        return f"Rest: {self.label.name} / Has dot: {self.has_dot} / Track: {self.track}" \
            f" / Group: {self.group}"


class Barline:
    def __init__(self):
        self.bbox: list[int] = None
        self.group: int = None

    @property
    def x_center(self):
        return (self.bbox[0] + self.bbox[2]) / 2

    def __repr__(self):
        return f"Barline / Group: {self.group}"


def filter_barlines(lines, min_height_unit_ratio=3.75,
                    zones = None 
                    , staffs = None):
    lines = filter_out_of_range_bbox(lines, zones = zones)
    # lines = merge_nearby_bbox(lines, 100, x_factor=100)
    lines = rm_merge_overlap_bbox(lines, mode='merge', overlap_ratio=0)

    # First round check, with line mode.
    valid_lines = []
    for line in lines:
        x1, y1, x2, y2 = line
        unit_size = get_unit_size(*get_center(line), staffs = staffs)

        # Check slope. Degree should be within 80~100.
        deg = slope_to_degree(y2-y1, x2-x1)
        if abs(deg) < 75:
            continue

        valid_lines.append(line)

    # Second round check, in bbox mode.
    valid_lines = np.array(valid_lines)
    max_x = np.max(valid_lines[..., 2])
    max_y = np.max(valid_lines[..., 3])
    data = np.zeros((max_y+10, max_x+10, 3))
    data = draw_lines(valid_lines, data, width=1)
    boxes = get_bbox(data[..., 1])
    valid_box = []
    for box in boxes:
        _, y1, _, y2 = box

        # Check height
        if (y2 - y1) < unit_size * min_height_unit_ratio:
          continue

        valid_box.append(box)

    # Check overall height. Filter out height below threshold after norm.
    valid_box = sorted(valid_box, key=lambda box:box[3]-box[1])
    heights = [b[3] - b[1] for b in valid_box]
    top_5 = np.mean(heights[-5:])
    norm = np.array(heights) / top_5
    idx = np.where(norm > 0.5)[0]
    valid_box = np.array(valid_box)[idx]

    return valid_box


def parse_barlines(group_map, stems_rests, symbols, min_height_unit_ratio=3.75,
                   zones = None, staffs = None):
    # Remove notehead from prediction
    barline_cand = np.where(stems_rests-group_map>1, 1, 0)

    # Straight lines and rest symbols
    no_note = np.where(symbols-group_map>1, 1, 0)

    # Label each regions by connected pixels.
    bar_label, bnum = scipy.ndimage.label(barline_cand)
    sym_label, _ = scipy.ndimage.label(no_note)

    # Check overlapping with symbols prediction
    sym_barline_map = np.zeros_like(no_note)
    for i in range(1, bnum+1):
        idx = (bar_label == i)
        region = sym_label[idx]
        labels = set(np.unique(region))
        if 0 in labels:
            labels.remove(0)
        for label in labels:
            sym_idx = (sym_label == label)
            sym_barline_map[sym_idx] += no_note[sym_idx]
    sym_barline_map[sym_barline_map>0] = 1

    lines = find_lines(sym_barline_map)
    line_box = filter_barlines(lines, min_height_unit_ratio,
                               zones = zones, staffs = staffs)
    logger.debug("Detected barlines: %d", len(line_box))

    return line_box


def filter_clef_box(bboxes, staffs = None):
    valid_box = []
    for box in bboxes:
        w = box[2] - box[0]
        h = box[3] - box[1]
        cen_x, cen_y = get_center(box)
        unit_size = get_unit_size(cen_x, cen_y, staffs = staffs)

        # Check size
        if w < unit_size*1.5 or h < unit_size*1.5:
            continue

        # Check position
        staff, _ = find_closest_staffs(cen_x, cen_y, staffs = staffs)
        if cen_y < staff.y_upper or cen_y > staff.y_lower:
            continue

        valid_box.append(box)
    return valid_box


def parse_clefs_keys(clefs_keys, unit_size, clef_size_ratio=3.5, max_clef_tp_ratio=0.45,
                     zones = None, 
                     staffs = None
                     ):
    global cs_img
    cs_img = to_rgb_img(clefs_keys)

    ker = np.ones((np.int32(unit_size//2), 1), dtype=np.uint8)
    clefs_keys = cv2.erode(cv2.dilate(clefs_keys.astype(np.uint8), ker), ker)
    bboxes = get_bbox(clefs_keys)
    bboxes = filter_out_of_range_bbox(bboxes, zones = zones)
    bboxes = rm_merge_overlap_bbox(bboxes, mode='merge', overlap_ratio=0.3)
    bboxes = filter_out_small_area(bboxes, area_size_func=lambda usize: usize**2, staffs = staffs)
    bboxes = merge_nearby_bbox(bboxes, unit_size*1.2)

    key_box = []
    clef_box = []
    for box in bboxes:
        w = box[2] - box[0]
        h = box[3] - box[1]
        region = clefs_keys[box[1]:box[3], box[0]:box[2]]
        usize = get_unit_size(*get_center(box), staffs = staffs)
        area_size_ratio = w * h / usize**2
        area_tp_ratio = region[region>0].size / (w * h)
        #cv2.rectangle(cs_img, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 1)
        #cv2.putText(cs_img, f"{area_tp_ratio:.2f} / {area_size_ratio:.2f}", (box[2]+2, box[3]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
        if area_size_ratio > clef_size_ratio \
                and area_tp_ratio < max_clef_tp_ratio:
            clef_box.append(box)
        elif w > usize/2 and h > usize/2:
            key_box.append(box)

    clef_box = filter_clef_box(clef_box, staffs = staffs)

    def pred_symbols(bboxes, model_name):
        label = []
        for x1, y1, x2, y2 in bboxes:
            region = np.copy(clefs_keys[y1:y2, x1:x2])
            ll = predict(region, model_name)
            label.append(ll)
            #cv2.putText(cs_img, str(ll), (x2+2, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
        return label

    clef_label = pred_symbols(clef_box, "clef")
    key_label = pred_symbols(key_box, "sfn")

    return clef_box, key_box, clef_label, key_label


def parse_rests(line_box, unit_size,
                stems_rests = None, 
                group_map = None,
                staffs = None, 
                zones = None
                ):
    # stems_rests = layers.get_layer('stems_rests_pred')
    # group_map = layers.get_layer('group_map')

    g_map = np.where(group_map>-1, 1, 0)

    data = np.zeros_like(group_map)
    for x1, y1, x2, y2 in line_box:
        data[y1:y2, x1:x2] = 1

    rests = stems_rests - g_map - data
    rests[rests<0] = 0

    global temp
    temp = np.copy(rests)

    bboxes = get_bbox(rests)
    bboxes = filter_out_of_range_bbox(bboxes, zones = zones)
    bboxes = merge_nearby_bbox(bboxes, unit_size*1.2)
    bboxes = rm_merge_overlap_bbox(bboxes)
    bboxes = filter_out_small_area(bboxes, area_size_func=lambda usize: usize**2 * 0.7, 
                                   staffs = staffs)
    temp = draw_bounding_boxes(bboxes, temp)

    label = []
    valid_box = []
    for box in bboxes:
        # Check size is valid
        if box[3] - box[1] > unit_size * 3.5 \
                or box[2] - box[0] < unit_size * 0.5:
            continue

        region = rests[box[1]:box[3], box[0]:box[2]]
        pred = predict(region, "rests")
        if "8th" in pred:
            pred = predict(region, "rests_above8")
        valid_box.append(box)
        label.append(pred)

    return valid_box, label


def gen_barlines(bboxes, staffs = None):
    barlines = []
    for box in bboxes:
        st1, _ = find_closest_staffs(*get_center(box), staffs = staffs)
        b = Barline()
        b.bbox = box
        b.group = st1.group
        barlines.append(b)
    return barlines


def gen_clefs(bboxes, labels, staffs = None):
    name_type_map = {
        "gclef": ClefType.G_CLEF,
        "fclef": ClefType.F_CLEF
    }
    clefs = []
    for box, label in zip(bboxes, labels):
        st1, _ = find_closest_staffs(*get_center(box), staffs = staffs)
        cc = Clef()
        cc.bbox = box
        cc.label = name_type_map[label]
        cc.track = st1.track
        cc.group = st1.group
        clefs.append(cc)
    return clefs


def get_nearby_note_id(box, note_id_map, 
                       staffs = None):
    cen_x, cen_y = get_center(box)
    unit_size = int(round(get_unit_size(cen_x, cen_y, staffs = staffs)))
    nid = None
    for x in range(box[2], box[2]+unit_size):
        if note_id_map[cen_y, x] != -1:
            nid = note_id_map[cen_y, x]
            break
    return nid


def gen_sfns(bboxes, labels,
             note_id_map = None, 
             notes= None,
             staffs = None
             ):
    # note_id_map = layers.get_layer('note_id')
    # notes = layers.get_layer('notes')

    name_type_map = {
        "sharp": SfnType.SHARP,
        "flat": SfnType.FLAT,
        "natural": SfnType.NATURAL
    }
    sfns = []
    for box, label in zip(bboxes, labels):
        st1, _ = find_closest_staffs(*get_center(box), staffs = staffs)
        ss = Sfn()
        ss.bbox = box
        ss.label = name_type_map[label]
        ss.note_id = get_nearby_note_id(box, note_id_map, staffs = staffs)
        ss.track = st1.track
        ss.group = st1.group

        if ss.note_id is not None:
            note = notes[ss.note_id]
            if ss.track != note.track:
                raise E.SfnNoteTrackMismatch(f"Track of sfn and note not mismatch: {ss}\n{note}")
            if ss.group != note.group:
                raise E.SfnNoteGroupMismatch(f"Group of sfn and note not mismatch: {ss}\n{note}")
            notes[ss.note_id].sfn = ss.label
            ss.is_key = False

        sfns.append(ss)
    return sfns


def gen_rests(bboxes, labels,
              symbols = None
              , staffs = None):
    # symbols = layers.get_layer('symbols_pred')

    name_type_map = {
        "rest_whole": RestType.WHOLE_HALF,
        "rest_quarter": RestType.QUARTER,
        "rest_8th": RestType.EIGHTH,
        "rest_16th": RestType.SIXTEENTH,
        "rest_32nd": RestType.THIRTY_SECOND,
        "rest_64th": RestType. SIXTY_FOURTH
    }
    rests = []
    for box, label in zip(bboxes, labels):
        st1, _ = find_closest_staffs(*get_center(box), staffs = staffs)
        rr = Rest()
        rr.bbox = box
        rr.label = name_type_map[label]
        rr.track = st1.track
        rr.group = st1.group

        unit_size = int(round(get_unit_size(*get_center(box), staffs = staffs )))
        dot_range = range(box[2]+1, box[2]+unit_size)
        dot_region = symbols[box[1]:box[3], dot_range]
        if 0 < np.sum(dot_region) < unit_size**2 / 7:
            rr.has_dot = True

        rests.append(rr)
    return rests


def extract(min_barline_h_unit_ratio=3.75,
            symbols = None, 
            stems_rests = None, 
            clefs_keys = None, 
            group_map = None,
            zones = None, 
            staffs = None,
            note_id_map = None,
            notes = None
            ):
    # Fetch paramters
    # symbols = layers.get_layer('symbols_pred')
    # stems_rests = layers.get_layer('stems_rests_pred')
    # clefs_keys = layers.get_layer('clefs_keys_pred')
    # group_map = layers.get_layer('group_map')

    line_box = parse_barlines(group_map, stems_rests, symbols, min_height_unit_ratio=min_barline_h_unit_ratio,
                              zones = zones, staffs = staffs)
    barlines = gen_barlines(line_box, staffs = staffs)

    unit_size = get_global_unit_size(staffs = staffs)
    clef_box, key_box, clef_label, key_label = parse_clefs_keys(clefs_keys, unit_size, zones = zones, staffs = staffs)
    clefs = gen_clefs(clef_box, clef_label, staffs = staffs)
    sfns = gen_sfns(key_box, key_label, note_id_map = note_id_map, notes = notes, staffs = staffs)

    rest_box, rest_label = parse_rests(line_box, unit_size, stems_rests= stems_rests, group_map = group_map,
                                       staffs = staffs, zones = zones)
    rests = gen_rests(rest_box, rest_label, symbols = symbols, staffs = staffs)

    return barlines, clefs, sfns, rests


def draw_symbols(symbols, ori_img, labels=None, color=(235, 64, 52)):
    bboxes = [sym.bbox for sym in symbols]
    labels = [sym.label.name for sym in symbols]
    out = np.copy(ori_img)
    for (x1, y1, x2, y2), label in zip(bboxes, labels):
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        cv2.putText(out, str(label), (x2+2, y2), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    return out


def show(data):
    plt.imshow(data, aspect='auto')
    plt.show()


if __name__ == "__main__":
    symbols = layers.get_layer('symbols_pred')
    stems_rests = layers.get_layer('stems_rests_pred')
    ori_img = layers.get_layer('original_image')
    clefs_keys = layers.get_layer('clefs_keys_pred')
    group_map = layers.get_layer('group_map')

    img = np.ones(group_map.shape+(3,)) * 255
    idx = np.where(stems_rests>0)
    img[idx[0], idx[1]] = 0

    barlines, clefs, sfns, rests = extract()

    aa = draw_symbols(clefs, ori_img)
    bb = draw_symbols(rests, aa, color=(11, 163, 0))
    cc = draw_symbols(sfns, bb, color=(53, 0, 168))
    dd = draw_bounding_boxes([b.bbox for b in barlines], cc, color=(250, 0, 200))
