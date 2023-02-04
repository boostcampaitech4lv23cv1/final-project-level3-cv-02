import numpy as np 

def measure_calculation(beats): 
    ## 한 줄에 네 마디를 가정 
    ## 4/4 박자 가정 (수정 예정)
    measure_pos = []
    curr_measure = 0 
    curr_beat = 0 
    for b in beats: 
        if curr_measure == 4: 
            curr_measure = 0 
        
        bb = int(b[0])
    
        if bb == 2: 
            tmp = bb * 4 
            curr_beat += cal_beat(b, tmp)
        elif bb == 4:
            tmp = bb 
            curr_beat += cal_beat(b, tmp)
        elif bb == 8:
            tmp = int(bb / 2)
            curr_beat += cal_beat(b, tmp)
        
        # print(b, curr_beat, curr_measure)
        measure_pos.append(curr_measure) 

        if curr_beat >= 16: 
            curr_measure += 1 
            curr_beat = 0 
    

    return measure_pos 


def cal_beat(b, bb): 
    if b[1] == 'dot': 
        bb += int(bb/2)
    return bb

