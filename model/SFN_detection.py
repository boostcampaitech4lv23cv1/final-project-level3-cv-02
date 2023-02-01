import numpy as np 
import cv2 
import copy
import constant as pitch 

def sfn_detection(sharp, flat, natural, pitches, original): 
    # sharp, flat, natural을 다 구별해서 input으로 들어온다고 가정 

    original_copy = copy.deepcopy(original)
    sfn_pitch_array = []
    
    for i in range(len(pitches)): 
        pitches[i].append('') # key value 추가, default로 key 없음 

    if len(sharp) > 0: 
        sfn_pitch_array = sharp_flat_check(sharp, 'sharp', natural, pitches, original_copy)
    if len(flat) > 0:
        sfn_pitch_array = sharp_flat_check(flat, 'flat', natural, pitches, original_copy)

    return sfn_pitch_array 

def natural_check(natural_pos, head_pos, margin): 
    # natural이 head에 해당하는 natural인지 확인 
    nx, ny, nh, nw = natural_pos
    hx, hy, hh, hw = head_pos 

    n_cy = ny + nh/2
    n_cx = nx + nw/2
    h_cy = hy + hh/2
    h_cx = hx + hw/2

    dist = ((n_cy - h_cy)**2 + (n_cx - h_cx)**2)**0.5 

    if dist < margin: 
        return True 
    else: 
        return False 


def sharp_flat_check(array, s_or_f, natural, pitches, original_copy): 
    if array is not None:
        for s in array: 
            s_whichpos, s_pitch = s 
            s_which, s_pos = s_whichpos[0][0], s_whichpos[0][1]  
            label_s, s_x, s_y, s_w, s_h = s_pos[0], s_pos[1], s_pos[2], s_pos[3], s_pos[4]

            if label_s == '24' or label_s == '20': # 모든 노트헤드에 적용되는 sharp / flat
                flag = 0 
                for i, pit in enumerate(pitches):
                    head_pitch, key = pit 
                    lab_pos, pitch = head_pitch[0], head_pitch[1]
                    which, pos = lab_pos[0], lab_pos[1]
                    label, x, y, w, h = pos[0], pos[1], pos[2], pos[3], pos[4]

                    # 모르겠음 바꿀수도 
                    margin_x = w / 2
                    margin_y = h / 2
                    natural_margin = w / 2 
                        
                    if len(natural) > 0: # natural이 있고 
                        if natural_check(natural, [x, y, w, h], natural_margin): 
                            # 해당 note head에 해당이 되는 경우 
                            pitches[i][0][1] = ''

                    if s_pitch == pitch:
                        pitches[i][0][1] = s_or_f
                        flag = 1
                    
                    if flag:
                        cv2.rectangle(original_copy, (x, y), (x+w, y+h), (0, 0, 255), 1, cv2.LINE_AA)


            else: # 특정 노트헤드에만 적용되는 sharp 
                for i, pit in enumerate(pitches):
                    head_pitch, key = pit 
                    lab_pos, pitch = head_pitch[0], head_pitch[1]
                    which, pos = lab_pos[0], lab_pos[1]
                    if which != s_which: 
                        continue 
                     
                    label, x, y, w, h = pos[0], pos[1], pos[2], pos[3], pos[4]
                        
                    if len(natural) > 0:
                        if natural_check(natural, [x, y, w, h], natural_margin):
                            pitches[i][0][1] = ''

                    if s_x < abs(x - margin_x) and s_y < abs(y - margin_y) : 
                        pitches[i][0][1] = s_or_f
                        break 
                
    cv2.imwrite('pitch_sfn_detection_test.jpg', original_copy)
            
    return pitches