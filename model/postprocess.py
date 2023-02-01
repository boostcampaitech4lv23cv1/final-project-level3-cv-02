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
    staff_line.append(int(line.replace('\n', ''))) 
staves.close() 

note_pos, staff_line = conversion('note', opt.note_label_file, opt.img_path, staff_line)
# note pos = [which, [label, x, y, w, h]]
# merged_note_pos = merge_bbox(note_pos, viz=True, img=original)
# merged_note pos = [which, [label, x, y, w, h]]

n = []
for note in note_pos: 
    m = info()
    m.staff = note[0]
    m.label = note[1][0]
    m.bbox = note_pos[1][1:]
    n.append(m) 

sharp, flat, natural = conversion('symbol', opt.symbol_label_file, opt.img_path, staff_line) 
# sharp = [note, [label, x, y, w, h]]
# print(sharp)
# print(flat)

# duration = duration_detection(note_pos, symbol)
pitches = pitch_detection_only_G(note_pos, staff_line, original, viz=True) # 여기서 note head를 조금 filtering함 
# pitches = [which, [label, x, y, w, h]]
pitches_sfn = sfn_detection(sharp, flat, natural, pitches, original)
# pitches_sfn = [which, [label, x, y, w, h], sig여부]

for p in pitches_sfn: 
    pos_pitch, key_sign = p 
    m.pitch = pos_pitch[1]
    if key_sign == 'sharp': 
        m.sharp = True 
    elif key_sign == 'flat': 
        m.sharp = True 



