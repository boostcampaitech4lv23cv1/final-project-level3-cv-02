from conversion import conversion
import argparse
import sys
import cv2
from note_class import info

from pitch_detection_only_G import pitch_detection_only_G 
from merge import merge_bbox
from SFN_detection import sfn_detection

parser = argparse.ArgumentParser()
parser.add_argument('--note_label_file', type=str, default='')
parser.add_argument('--symbol_label_file', type=str, default='')
parser.add_argument('--img_path', type=str, default='')
parser.add_argument('--staves', type=str, default='')
opt = parser.parse_args()
print(opt)

original = cv2.imread(opt.img_path) 
staves = open(opt.staves, 'r')
staff_line = []
while True: 
    line = staves.readline() 
    if not line: 
        break
    staff_line.append(int(line)) 
staves.close() 

note_pos, staff_line = conversion('note', opt.note_label_file, opt.img_path, staff_line)
# merged_note_pos = merge_bbox(note_pos, viz=True, img=original)

n = []
for note in note_pos: 
    m = info()
    m.staff = note[0]
    m.label = note[1][0]
    m.bbox = note_pos[1][1:]
    n.append(m) 

sharp, flat, natural = conversion('symbol', opt.symbol_label_file, opt.img_path, staff_line)

for s, f, n in zip(sharp, flat, natural): 
    m.sharp = True if len(s) > 0 else False 
    m.flat = True if len(f) > 0 else False 
    m.natural = True if len(n) > 0 else False 
    if m.sharp: 
        m.staff = s[0]
        m.bbox = s[1]
    if m.flat: 
        m.staff = f[0]
        m.bbox = f[1]
    if m.natural: 
        m.staff = n[0]
        m.bbox = n[1]
    n.append(m) 

# duration = duration_detection(note_pos, symbol)

pitches = pitch_detection_only_G(note_pos, staff_line, original)
pitches_sfn = sfn_detection(sharp, flat, natural, pitches, note_pos, original)

for p in pitches_sfn: 
    which, head, pitch, key_sign = p 
    m.pitch = pitch 
    if key_sign == 'sharp': 
        m.sharp = True 
    elif key_sign == 'flat': 
        m.sharp = True 



