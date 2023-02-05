import numpy as np 
import cv2 
from pitch_detection_only_G import pitch_detection_only_G

# head = '/opt/ml/yolov7/runs/notehead/exp/labels/school_bell_processed.txt'
# symbols = '/opt/ml/yolov7/runs/symbols/exp/labels/school_bell_processed.txt'
# img_path = '/opt/ml/yolov7/source/school_bell.jpg'

key_sharp = ['f', 'c', 'g', 'd', 'a', 'e', 'b']
key_flat = ['b', 'e', 'a', 'd', 'g', 'c', 'f']
key_natural = ['c', 'd', 'e', 'f', 'g', 'a', 'b', 'c']

def conversion_oneline(mode, label_file, img_path, staff_line): 
    ## label file 읽어오기 
    file = open(label_file, 'r') 
    img = cv2.imread(img_path)
    H, W, _ = img.shape 

    converted = []
    ## note head conversion 
    if mode == 'note':
        while True: 
            line = file.readline() 
            if not line: 
                break
            label, x, y, w, h = convert(line, H, W)

            if label == '0' or label == '1' or label == '2' or label == '3': 
                label, x, y, w, h = convert(line, H, W)
                converted.append([label, x, y, w, h])

                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 1, cv2.LINE_AA)
                cv2.putText(img, label, (x+10, y+10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        
        cv2.imwrite('conversion_label.jpg', img)

        converted = sort_head_pos(converted, staff_line)

        return converted, staff_line

    ## SFN conversion 
    elif mode == 'SFN': 
        sharp, flat, natural = [], [], []
        while True: 
            line = file.readline() 
            if not line: 
                break   

            label, x, y, w, h = convert(line, H, W)
            closest = which_staff(y+h/2, staff_line) 
            if closest > 0: 
                continue 

            if label == '24': 
                sharp.append([label, x, y, w, h])
            elif label == '20': 
                flat.append([label, x, y, w, h])
            elif label == '22': 
                natural.append([label, x, y, w, h])
            else: 
                continue 
        
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(img, label, (x+10, y+10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        cv2.imwrite('conversion_symbol.jpg', img)

        if len(sharp) > 0: 
            sharp = check_rep(sharp, key_sharp, staff_line) 
        if len(flat) > 0: 
            flat = check_rep(flat, key_flat, staff_line) 
        ## natural check_rep 임시 
        if len(natural) > 0: 
            natural = check_rep(natural, key_natural, staff_line) 
         
        return sharp, flat, natural
    
    ## beat conversion 
    elif mode == 'beat':
        beat = [] 
        while True: 
            line = file.readline() 
            if not line: 
                break   
            
            label, x, y, w, h = convert(line, H, W)

            # if label == '4': 
            #     beat.append(['dot', x, y, w, h])
            # elif label == '5' or label == '10': 
            #     beat.append(['flag 8', x, y, w, h])
            # elif label == '6' or label == '11': 
            #     beat.append(['flag 16', x, y, w, h])
            # elif label == '7' or label == '12': 
            #     beat.append(['flag 32', x, y, w, h])
            # elif label == '8' or label == '13': 
            #     beat.append(['flag 64', x, y, w, h])
            # elif label == '9' or label == '14': 
            #     beat.append(['flag 128', x, y, w, h])
            # else: 
            #     continue 

            if label == '4': 
                beat.append(['dot', x, y, w, h])
            elif label == '5' or label == '10' or label == '6' or label == '11': 
                ## 8분음표, 16분음표 -> 8분음표 
                beat.append(['flag 8', x, y, w, h])
            else: 
                continue 

            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(img, label, (x+10, y+10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
            
        cv2.imwrite('conversion_beat.jpg', img)

        beat = sort_head_pos(beat, staff_line)

        return beat

    elif mode == 'rest': 
        rest = [] 
        while True: 
            line = file.readline() 
            if not line: 
                break   
            
            label, x, y, w, h = convert(line, H, W)

            if label == '31':
                rest.append(['quarter_rest', x, y, w, h])
            elif label == '32': 
                rest.append(['8th_rest', x, y, w, h])
            else: 
                continue 

            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(img, label, (x+10, y+10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
            
        cv2.imwrite('conversion_rest.jpg', img)

        rest = sort_head_pos(rest, staff_line)

        return rest

    elif mode == 'time': 
        time_bbox = [] 
        while True: 
            line = file.readline() 
            if not line: 
                break   
            
            label, x, y, w, h = convert(line, H, W)

            ## 나비야에서 3을 검출하는 관계로 3은 임시로 지움 
            if label == '9':
                time_bbox.append(['1', x, y, w, h])
            elif label == '10': 
                time_bbox.append(['2', x, y, w, h])
            # elif label == '11': 
            #     time.append(['3', x, y, w, h])
            elif label == '12': 
                time_bbox.append(['4', x, y, w, h])
            else: 
                continue 

            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(img, label, (x+10, y+10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
            
        cv2.imwrite('conversion_time.jpg', img)
        
        if len(time_bbox) == 0: 
            time = '4/4' # 안 쓰여있는 경우 4/4박자 가정 
        else: 
            time_bbox.sort(key=lambda x: (x[2]))
            time = str(time_bbox[0][0]) + '/' + str(time_bbox[1][0]) 

        return time_bbox, time
    
    elif mode == 'clef': 
        clef_bbox = [] 
        while True: 
            line = file.readline() 
            if not line: 
                break   
            
            label, x, y, w, h = convert(line, H, W)

            ## 나비야에서 3을 검출하는 관계로 3은 임시로 지움 
            if label == '1':
                clef_bbox.append(['clef G', x, y, w, h])
            if label == '4':
                clef_bbox.append(['clef F', x, y, w, h])
            else: 
                continue 

            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(img, label, (x+10, y+10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
            
        cv2.imwrite('conversion_clef.jpg', img)
        
        if clef_bbox[0] == 'clef_G': 
            clef = 'clef_G' 
        else: 
            clef = 'clef_F'
        
        return clef_bbox, clef
    

def convert(line, H, W): 
    label, cen_x, cen_y, norm_w, norm_h = line.split() 

    w, h = int(float(norm_w) * W), int(float(norm_h) * H)
    x = int(float(cen_x) * W - w/2)
    y = int(float(cen_y) * H - h/2)

    return label, x, y, w, h


def which_staff(cen_y, staff_line): 
    ## 어느 줄의 staff line에 가장 가까운지 
    staff_med = []  
    dist = list()
    
    for i in range(0, len(staff_line), 5): 
        tmp = staff_line[i+2]
        staff_med.append(tmp)

    tmp2 = np.full(shape=len(staff_med), fill_value=cen_y)
    diff = abs(staff_med - tmp2) 

    for d in diff:
        dist.append(d)
    
    dist = np.array(dist)
    closest = np.where(dist == dist.min()) 

    return closest[0][0]

def sort_head_pos(head_pos, staff_line): 
    sorted_pos = []

    head_h = staff_line[1] - staff_line[0] 

    for head in head_pos: 
        label, xmin, ymin, w, h = head
        margin = h 
        if h < head_h - margin or head_h + margin < h: 
            continue 

        cen_y = ymin + h/2
        
        which = which_staff(cen_y, staff_line)
        sorted_pos.append([which, head]) 
        sorted_pos.sort(key=lambda x: (x[0], x[1][1])) ## 우선순위: staff line -> x좌표 
    
    return sorted_pos


def check_rep(sfn, s_or_f, staff_line, flat=False):
    new_arr = [] 
    for i, sig in enumerate(sfn): 
        _, x, y, w, h = sig 

        cen_y = y + h/2
        which = which_staff(cen_y, staff_line)
        s = [which, sig]
        
        new_arr.append([s_or_f[i], s])

    return new_arr 

        
