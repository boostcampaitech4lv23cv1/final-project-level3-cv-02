import constant as pitch 
import numpy as np 
import cv2 
import copy 
import math 

G_above = [pitch.C2, pitch.B2, pitch.A2, pitch.G2, pitch.F2]
G_on = [pitch.F2, pitch.D2, pitch.B1, pitch.G1, pitch.E1]
G_btw = [pitch.E2, pitch.C1, pitch.A1, pitch.F1]
G_below = [pitch.D1, pitch.C1, pitch.B0, pitch.A0, pitch.G0]


def pitch_detection_only_G(head_pos, staff_line, flat=False, original=None, viz=False):
    # head pos 순서대로 주어졌다고 가정 
    # staff line만 주어졌다고 가정 

    # head_pos = [[x, y, w, h], ...]
    # staff_line = [y1, y2, y3, ...]
    if viz: 
        original_copy = copy.deepcopy(original)

    pitches = [] 
    pitch_img = []
    i = 0 
    for i, head in enumerate(head_pos): 
        notes = []
        which, pos = head
        label, x, y, w, h = pos[0], pos[1], pos[2], pos[3], pos[4]
 
        notes = choose_note(staff_line, which, head, flat=flat)
        if len(notes) == 0:  
            notes = choose_note(staff_line, which, head, _margin=10) # 빈 음표 방지 
        
        pitches.append(notes)

        if viz:
            cv2.rectangle(original_copy, (x, y), (x+w, y+h), (0, 0, 255), 1, cv2.LINE_AA)
            cv2.putText(original_copy, str(pitches[i][0][1]), (x+10, y+10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        
            i += 1
    
    if viz: 
        cv2.imwrite('pitch_detection_test.jpg', original_copy)

    return pitches


def cal_margin(closest_len, closest, staff_line, which): 
    if closest_len == 1: 
        head_h = abs(staff_line[which*5+1] - staff_line[which*5])
    else: 
        head_h = abs(staff_line[which*5+closest[0][1]] - staff_line[which*5+closest[0][0]] )
    
    margin = head_h / 2

    return margin, head_h 

def choose_note(staff_line, which, head, flat=False, _margin=None):
    result = []
    which, pos = head
    label, x, y, w, h = pos[0], pos[1], pos[2], pos[3], pos[4]

    if label == 'quarter_rest' or label == '8th_rest': 
        result.append([head, 0]) 
        return result 
    
    if flat: 
        y += 5
        h -= 5 

    cen_y = y + h/2
        
    tmp = np.full(shape=(1,5), fill_value=cen_y)
    dist = abs(staff_line[which*5:which*5+5] - tmp)

    d = min(dist[0])
    closest = np.where(dist[0] == dist[0].min())
    closest_len = (closest[0] >= 0).sum()
    mul = d / (h/2) 

    # print('margin', margin)
    # print('d', d)
    # print('closest', closest)
    # print('mul', mul) 

    if _margin is None: 
        margin, head_h = cal_margin(closest_len, closest, staff_line, which)
    else: 
        margin = _margin 

    ## on & between 
    if closest_len == 1 and d <= margin / 2: 
        s1 = closest[0][0]
        dist[0][s1] = 10000
        s2 = np.where(dist[0] == dist[0].min())[0][0]
        
        margin, _ = cal_margin(2, [[s1, s2]], staff_line, which)
        d1 = d
        d2 = dist[0][s2]
        dist1 = None
        if d1 <= margin and d2 <= margin * 1.5:
            # 학교종 1.5 -1
            # 나비야 1.5 -4
            # 
            dist1 = min(d1, d2)
            dist2 = d
            # print(dist1, dist2)
        
        if dist1 is not None and dist1 <= dist2: 
            # print('between')
            p = s2 if s2 > s1 else s1
            result.append([head, G_btw[p-1]])
            # print(G_btw[p-1])
        elif dist1 is None or dist1 > dist2: 
            # print('on')
            result.append([head, G_on[closest[0][0]]])
            # print(G_on[closest[0][0]])

    ## btw
    elif closest_len >= 2 and d <= margin * 1.5: 
        # print('btw\n')
        p = closest[0][0] if closest[0][0] > closest[0][1] else closest[0][1]
        result.append([head, G_btw[p-1]])

    # below 
    elif closest_len == 1 and closest[0][0] == 4 and d >= margin: 
        # print('below\n')
        if mul > margin: 
            mul = math.ceil(mul) 
        else: 
            mul = math.floor(mul) 

        p = max(0, mul - 1 )
        result.append([head, G_below[p]])

    # above 
    elif closest_len == 1 and closest[0][0] == 0 and d >= margin: 
        # print('above\n')
        if mul > margin: 
            mul = math.ceil(mul) 
        else: 
            mul = math.floor(mul) 

        p = max(0, mul - 1 )
        result.append([head, G_above[p]])
    
    return result 