import numpy as np 
import cv2 

# head = '/opt/ml/yolov7/runs/notehead/exp/labels/school_bell_processed.txt'
# symbols = '/opt/ml/yolov7/runs/symbols/exp/labels/school_bell_processed.txt'
# img_path = '/opt/ml/yolov7/source/school_bell.jpg'

def conversion(mode, label_file, img_path, staff_line): 
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
                cv2.putText(img, label, (x+15, y+10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        
        cv2.imwrite('conversion_label.jpg', img)

        converted = sort_head_pos(converted, staff_line)

        return converted, staff_line

    ## symbol conversion 
    else: 
        sharp, flat, natural = [], [], [] 
        while True: 
            line = file.readline() 
            if not line: 
                break   

            label, x, y, w, h = convert(line, H, W)

            if label == '24' or label == '25' or label == '26' or label == '27': 
                label, x, y, w, h = convert(line, H, W)
                sharp.append([label, x, y, w, h])
            elif label == '20' or label == '21': 
                label, x, y, w, h = convert(line, H, W)
                flat.append([label, x, y, w, h])
            elif label == '22' or label == '23': 
                label, x, y, w, h = convert(line, H, W)
                natural.append([label, x, y, w, h])
        
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 1, cv2.LINE_AA)
            cv2.putText(img, label, (x+15, y+10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        cv2.imwrite('conversion_symbol.jpg', img)

        if len(sharp) > 1: 
            sharp = sort_head_pos(sharp, staff_line)
        if len(flat) > 1: 
            flat = sort_head_pos(flat, staff_line)
        if len(natural) > 1: 
            natural = sort_head_pos(natural, staff_line)

        return sharp, flat, natural


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
        margin = h / 2
        if h < head_h - margin or head_h + margin < h: 
            continue 

        cen_y = ymin + h/2
        
        which = which_staff(cen_y, staff_line)
        sorted_pos.append([which, head]) 
        sorted_pos.sort(key=lambda x: (x[0], x[1][1])) ## 우선순위: staff line -> x좌표 
    
    return sorted_pos