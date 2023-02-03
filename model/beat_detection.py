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

        if len(flag_dot) > cnt: 
            b = check_flag_dot(flag_dot[cnt:], which, x, y, w, h)
        else: 
            b = False 
        
        if label == '0':   
            if b == False: 
                beat.append(['4', '']) # 4분음표 
            else: 
                beat.append(b) 
                cnt += 1
        elif label == '1' or label == '2': 
            ## 학교종이 땡땡땡에서 2분음표를 다른 음표로 착각해서 임시로 처치 
            if b is not False and b[0] == 'dot': 
                beat.append(['2', 'dot']) # 점 2분음표 
                cnt += 1
            else: 
                beat.append(['2','']) # 2분음표 

        cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(img_copy, beat[i][0], (x+10, y+10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
    
    cv2.imwrite('beat_detection.jpg', img_copy)

    return beat 

def check_flag_dot(flag_dot, h_which, h_x, h_y, h_w, h_h):
    margin_h = h_y / 1.5
    margin_w = h_w / 1.5 
    b = []
    flag = 0 

    for f in flag_dot: 
        f_which, f_pos = f
        f_label, f_x, f_y, f_w, f_h = f_pos[0], f_pos[1], f_pos[2], f_pos[3], f_pos[4]
 
        if flag == 0 and f_which != h_which: 
            return False
        
        if flag == 3: # dot도 있는지 확인하도록 함 
            break 

        ratio = f_h / f_w 
        if ratio > 1.2: # flag 
            if (abs((f_y + f_h) - h_y) <= margin_h and abs((h_x + h_w) - f_x) <= margin_w) or \
                ((abs((h_y + h_h) - f_y) <= margin_h and abs(f_x - h_x) <= margin_w)) : 
                
                # head의 왼쪽 위와 tail의 오른쪽 아래의 y 좌표가 margin 이내 
                # head의 오른쪽 위와 tail의 왼쪽 아래의 x좌표가 margin 이내 
                b.append(f_label.split()[1])
                flag = 1
        
        else: # dot
            if abs(f_y - h_y) <= margin_h and abs((h_x + h_w) - f_x) <= margin_w:
                return b.append(f_label)
        
        if flag > 0:
            flag += 1 
                
    if len(b) > 0: 
        if 'dot' not in b: 
            b.append('')
        return b
    else:
        return False