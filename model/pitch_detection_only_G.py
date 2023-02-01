import constant as pitch 
import numpy as np 
import cv2 
import copy 

G_above = [pitch.C2, pitch.B2, pitch.A2, pitch.G2]
G_on = [pitch.F2, pitch.D2, pitch.B1, pitch.G1, pitch.E1]
G_btw = [pitch.E2, pitch.C1, pitch.A1, pitch.F1]
G_below = [pitch.D1, pitch.C1, pitch.B0, pitch.A0, pitch.G0]

def pitch_detection_only_G(head_pos, staff_line, original):
    # head pos 순서대로 주어졌다고 가정 
    # staff line만 주어졌다고 가정 

    # head_pos = [[x, y, w, h], ...]
    # staff_line = [y1, y2, y3, ...]

    original_copy = copy.deepcopy(original)

    pitches = [] 
    pitch_img = []
    i = 0 
    for head in head_pos: 
        flag = 0 
        which, pos = head
        label, x, y, w, h = pos[0], pos[1], pos[2], pos[3], pos[4]

        gap = staff_line[1]-staff_line[0]
        if h > gap * 1.5 or h < gap * 0.5: 
            continue 

        cen_y = y + h/2
        
        tmp = np.full(shape=(1,5), fill_value=cen_y)
        dist = abs(staff_line[which*5:which*5+5] - tmp)

        d = min(dist[0])
        closest = np.where(dist[0] == dist[0].min())
        closest_len = (closest[0] >= 0).sum()
        mul = d / (h/2) # 거리가 head의 몇 배인지 
        if round(mul) - 1 > 4:
            continue 

        margin, head_h = cal_margin(closest_len, closest, staff_line, which)

        # print('margin', margin)
        # print('d', d)
        # print('closest', closest)
        # print('mul', mul) 

        ## on 
        if closest_len == 1 and d <= margin/2: 
            # print('on\n')
            pitches.append([which, head, G_on[closest[0][0]]])
            flag = 1

        ## btw
        elif closest_len == 2 and d <= margin: 
            # print('btw\n')
            p = closest[0][0] if closest[0][0] > closest[0][1] else closest[0][1]
            pitches.append([which, head, G_btw[p-1]]) 
            flag = 1
        
        elif closest_len == 1 and d <= margin: 
            s1 = np.where(dist[0] == dist[0].min())[0][0]
            dist[0][s1] = 10000
            s2 = np.where(dist[0] == dist[0].min())[0][0]

            margin, _ = cal_margin(2, [[s1, s2]], staff_line, which)
            # print('s1, s2, margin', s1, s2, margin)

            if abs(s2 - s1) < margin: 
                # print('between\n')
                p = s2 if s2 > s1 else s1
                pitches.append([which, head, G_btw[p-1]]) 
                flag = 1

        # below 
        elif closest_len == 1 and closest[0][0] == 4: 
            # print('below\n')
            p = max(0, round(mul) - 1 )
            pitches.append([which, head, G_below[p]])
            flag = 1

        # above 
        elif closest_len == 1 and closest[0][0] == 0: 
            # print('above\n')
            p = max(0, round(mul) - 1 )
            pitches.append([which, head, G_above[p]])
            flag = 1


        if flag == 1:
            cv2.rectangle(original_copy, (x, y), (x+w, y+h), (0, 0, 255), 1, cv2.LINE_AA)
            cv2.putText(original_copy, pitches[i][2], (x+10, y+10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
        
            i += 1
    
    cv2.imwrite('pitch_detection_test.jpg', original_copy)

    # print(pitches)
    return pitches


def cal_margin(closest_len, closest, staff_line, which): 
    if closest_len == 1: 
        head_h = abs(staff_line[which*5+1] - staff_line[which*5])
    else: 
        head_h = abs(staff_line[which*5+closest[0][1]] - staff_line[which*5+closest[0][0]] )
    
    margin = head_h / 2

    return margin, head_h 