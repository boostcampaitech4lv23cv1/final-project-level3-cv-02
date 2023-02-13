import numpy as np 
import copy 
import cv2 

def measure_calculation(beats, time, combined, original): 
    ## 한 줄에 네 마디를 가정 
    ## 4분의 2박자 or 4박자 

    original_copy = copy.deepcopy(original)

    four = int(time[0]) 
    full_time = int(time[0]) * int(time[0])

    measure_pos = []
    curr_measure = 0 
    curr_beat = 0 
    for i, (b, c) in enumerate(zip(beats, combined)): 
        if curr_measure == 4: 
            curr_measure = 0 
            
        if b == 2: 
            curr_beat += four * 2
        elif b == 4:
            curr_beat += four 
        elif b == 8:
            curr_beat += int(four / 2)
        
        # print(b, curr_beat, curr_measure)
        measure_pos.append(curr_measure) 

        if curr_beat >= full_time: 
            curr_measure += 1 
            curr_beat = 0 

        _, x, y, w, h = c[1]
        cv2.rectangle(original_copy, (x, y), (x+w, y+h), (0, 0, 255), 1, cv2.LINE_AA)
        cv2.putText(original_copy, str(measure_pos[i]), (x+10, y+10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
    
    cv2.imwrite('measure.jpg', original_copy)

    return measure_pos 


