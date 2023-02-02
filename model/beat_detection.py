import cv2
import numpy as np 
import copy 

def beat_detection(flag_dot, note_pos, img): 
    img_copy = copy.deepcopy(img)
    beat = []
    cnt = 0
    for i, head in enumerate(note_pos): 
        which, pos = head 
        label, x, y, w, h = pos[0], pos[1], pos[2], pos[3], pos[4]

        if label == '0':   
            b = flag(flag_dot[cnt:], which, x, w, y) 
            if b == False: 
                beat.append('4') 
            else: 
                beat.append(b) 
                cnt += 1
        elif label == '1': 
            beat.append('2') # 2분음표 

        cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(img_copy, beat[i], (x+10, y+10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
    
    cv2.imwrite('beat_detection.jpg', img_copy)

    return beat 

def flag(flag_dot, h_which, h_x, h_w, h_y):
    margin_h = h_y / 1.5
    margin_w = h_w / 1.5
    for f in flag_dot: 
        f_which, f_pos = f
        f_label, f_x, f_y, f_w, f_h = f_pos[0], f_pos[1], f_pos[2], f_pos[3], f_pos[4]
        
        if f_which != h_which: 
            return False
        
        if abs((f_y + f_h) - h_y) <= margin_h and abs((h_x + h_w) - f_x) <= margin_w: 
            # head의 왼쪽 위와 tail의 오른쪽 아래의 y 좌표가 margin 이내 
            # head의 오른쪽 위와 tail의 왼쪽 아래의 x좌표가 margin 이내 
            return f_label.split()[1]


    return False