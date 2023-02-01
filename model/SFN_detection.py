import numpy as np 

def sfn_detection(sharp, flat, natural, head_pos): 
    # sharp, flat, natural을 다 구별해서 input으로 들어온다고 가정 
    
    if len(sharp) > 0: 
        sfn_pitch_array = sharp_flat_check(sharp, natural, head_pos)
    elif len(flat) > 0: 
        sfn_pitch_array = sharp_flat_check(flat, natural, head_pos)

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


def sharp_flat_check(s_or_f, natural, pitches, head_pos): 
    # 모르겠음 바꿀수도 
    margin_x = w / 2
    margin_y = h / 2
    natural_margin = w / 2 

    sfn_pitch_array = [False] * len(head_pos) 

    if s_or_f is not None:
        for s in s_or_f: 
            s_which, pos = s 
            label_s, s_x, s_y, s_w, s_h = pos[0], pos[1], pos[2], pos[3], pos[4]
            sharp_cen = s_y + s_h

            if label_s == 24: # 모든 노트헤드에 적용되는 sharp 
                for i, head in enumerate(head_pos):
                    which, pos = head 
                    _, x, y, w, h = pos[0], pos[1], pos[2], pos[3], pos[4]
                        
                    if len(natural) > 0:
                        if natural_check(natural, head, natural_margin):
                            sfn_pitch_array[i]=True 

                    if s_which == which: 
                        sfn_pitch_array[i] = True     

            else: # 특정 노트헤드에만 적용되는 sharp 
                for i, head in enumerate(head_pos[s_which]):
                    which, pos = head 
                    _, x, y, w, h = pos[0], pos[1], pos[2], pos[3], pos[4]
                        
                    if len(natural) > 0:
                        if natural_check(natural, head, natural_margin):
                            sfn_pitch_array[i]=True 

                    if s_x < abs(x - margin_x) and s_y < abs(y - margin_y) : 
                        sfn_pitch_array[i] = True  
                        break 

    return sfn_pitch_array