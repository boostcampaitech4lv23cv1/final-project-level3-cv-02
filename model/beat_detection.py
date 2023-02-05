import cv2
import numpy as np 
import copy 

def beat_detection(flag_dot, rest, note_pos, img): 
    img_copy = copy.deepcopy(img)
    beat = []
    cnt = 0

    if rest is not None: 
        combined = flag_dot + rest
    else: 
        combined = flag_dot 

    combined.sort(key=lambda x: (x[0], x[1][1])) ## 우선순위: staff line -> x좌표 

    i = -1
    for head in note_pos: 
        rest = 0 
        which, pos = head 
        label, x, y, w, h = pos[0], pos[1], pos[2], pos[3], pos[4]

        if len(combined) > cnt: 
            b = check_beat(combined[cnt:], label, which, x, y, w, h)
        else: 
            b = False 

        if label == '0':   
            if b is not False and b[0] == 'dot':
                beat.append(['4', 'dot']) 
                cnt += 1
            elif b is not False and b[0] == '8': 
                beat.append(['8', ''])
                cnt += 1
            else: 
                beat.append(['4', '']) # 4분음표
            i += 1

            if b is not False and 'quarter_rest' in b: 
                beat.append(['4', '']) 
                cnt += 1
                rest = 1
            elif b is not False and '8th_rest' in b: 
                beat.append(['8', '']) 
                cnt += 1
                rest = 1

        elif label == '1' or label == '2': 
            ## 학교종이 땡땡땡에서 2분음표를 다른 음표로 착각해서 임시로 처치 
            if b is not False and 'dot' in b: 
                beat.append(['2', 'dot']) # 점 2분음표 
                cnt += 1
            else: 
                beat.append(['2','']) # 2분음표
            i += 1

            if b is not False and 'quarter_rest' in b: 
                beat.append(['4', '']) 
                cnt += 1
                rest = 1
            elif b is not False and '8th_rest' in b: 
                beat.append(['8', '']) 
                cnt += 1
                rest = 1

        cv2.rectangle(img_copy, (x, y), (x+w, y+h), (255, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(img_copy, beat[i][0], (x+10, y+10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        
        if rest: 
            i += 1
    
    cv2.imwrite('beat_detection.jpg', img_copy)

    return beat 

def check_beat(symbols, h_label, h_which, h_x, h_y, h_w, h_h):
    # 학교종 / 1.2 
    # 나비야 
    margin_h = h_y * 2
    margin_w = h_w * 2
    b = []
    flag = 0 

    for f in symbols: 
        f_which, f_pos = f
        f_label, f_x, f_y, f_w, f_h = f_pos[0], f_pos[1], f_pos[2], f_pos[3], f_pos[4]
        if flag == 0 and f_which != h_which: 
            return False
        
        if flag == 3: 
            break 

        ## rest 
        if f_label == 'quarter_rest':
            if h_label == '0' and ((f_x + f_w) - (h_x + h_w)) < margin_w * 5 :
                b.append(f_label)
                return b 
            elif (h_label == '1' or h_label == '2') and ((f_x + f_w) - (h_x + h_w)) < margin_w * 15 :
                b.append(f_label)
                return b
        elif f_label == '8th_rest':
            if h_label == '0' and ((f_x + f_w) - (h_x + h_w)) < margin_w * 5 :
                b.append(f_label)
                return b 
            elif (h_label == '1' or h_label == '2') and ((f_x + f_w) - (h_x + h_w)) < margin_w * 15 :
                b.append(f_label)
                return b

        ## flag 
        if f_label == 'flag 8': 
            if (abs((f_y + f_h) - h_y) <= margin_h and abs((h_x + h_w) - f_x) <= margin_w) or \
                ((abs((h_y + h_h) - f_y) <= margin_h and abs(f_x - h_x) <= margin_w)) : 
                # head의 왼쪽 위와 tail의 오른쪽 아래의 y 좌표가 margin 이내 
                # head의 오른쪽 위와 tail의 왼쪽 아래의 x좌표가 margin 이내 
                b.append(f_label.split()[1])
                flag = 1
        
        ## dot 
        elif f_label == 'dot' : 
            if abs(f_y - h_y) <= margin_h * 1.2 and abs((h_x + h_w) - f_x) <= margin_w * 1.2:
                b.append(f_label)

        if flag > 0:
            flag += 1 
                
    if len(b) == 0:
        return False
    else: 
        return b 