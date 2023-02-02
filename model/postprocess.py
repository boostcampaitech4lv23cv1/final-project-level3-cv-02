from conversion import conversion
from conversion_oneline import conversion_oneline
import argparse
import sys
import cv2
from note_class import info

from pitch_detection_only_G import pitch_detection_only_G 
from merge import merge_bbox
from SFN_detection import sfn_detection
from noise_removal import noise_removal
from beat_detection import beat_detection

parser = argparse.ArgumentParser()
parser.add_argument('--note_label_file', type=str, default='')
parser.add_argument('--symbol_label_file', type=str, default='')
parser.add_argument('--img_path', type=str, default='')
parser.add_argument('--staves', type=str, default='')
opt = parser.parse_args()
print(opt)


## staff line 읽어오기 
original = cv2.imread(opt.img_path) 
staves = open(opt.staves, 'r')
staff_line = []
while True: 
    line = staves.readline() 
    if not line: 
        break
    staff_line.append(int(line.replace('\n', ''))) 
staves.close() 


## conversion 
note_pos, staff_line = conversion('note', opt.note_label_file, opt.img_path, staff_line)
# note pos = [which, [label, x, y, w, h]]
merged_note_pos = merge_bbox(note_pos, viz=True, img=original)
# merged_note pos = [which, [label, x, y, w, h]]

n = []
for note in note_pos: 
    m = info()
    m.staff = note[0]
    m.label = note[1][0]
    m.bbox = note[1][1:]
    n.append(m) 

sharp, flat, natural = conversion_oneline('SFN', opt.symbol_label_file, opt.img_path, staff_line) 
# sharp = [note, [label, x, y, w, h]]
flag_dot = conversion_oneline('beat', opt.note_label_file, opt.img_path, staff_line) 
merged_flag_dot = merge_bbox(flag_dot, viz=True, img=original)

## noise removal 
symbols = []
if len(sharp) > 0: 
    symbols.append(sharp) 
if len(flat) > 0: 
    symbols.append(flat) 
if len(natural) > 0: 
    symbols.append(natural)
# print('symbols', symbols)
noise_removed_note_pos = noise_removal(merged_note_pos, symbols, original)
# noise_removed_note_pos = [which, [label, x, y, w, h]]

## pitch detection 
pitches = pitch_detection_only_G(noise_removed_note_pos, staff_line, flat=False, original=original, viz=True) 
# pitches = [which, [label, x, y, w, h], pitch]


## sfn detection 
pitches_sfn = sfn_detection(sharp, flat, natural, pitches, original)
# pitches_sfn = [which, [label, x, y, w, h], pitch, sig여부]

for i, p in enumerate(pitches_sfn): 
    pos_pitch, key_sign = p 
    n[i].pitch = pos_pitch[1]
    if key_sign == 'sharp': 
        n[i].sharp = True 
    elif key_sign == 'flat': 
        n[i].flat = True 


## beat detection 
beats = beat_detection(merged_flag_dot, noise_removed_note_pos, original)
# beats = [beat]

for i in range(len(beats)): 
    n[i].duration = beats[i] 


for i in range(len(n)): 
    print(n[i].staff)
    print(n[i].label)
    print(n[i].bbox)
    print(n[i].pitch)
    print(n[i].sharp)
    print(n[i].flat)
    print(n[i].natural) 
    print(n[i].duration)
    break 