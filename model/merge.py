import numpy as np 
import cv2 

def merge_bbox(head_pos, viz, img): 
    merged_bbox = [] 
    head = 0 
    while head < len(head_pos) - 1: 
        which1, pos1 = head_pos[head]
        label1, x1, y1, w1, h1 = pos1[0], pos1[1], pos1[2], pos1[3], pos1[4]
        margin = ( w1 + h1 ) / 2 

        similar = True
        sim = []
        sim.append([which1, [label1, x1, y1, w1, h1]])
        while head < len(head_pos) - 1 and similar:
            which2, pos2 = head_pos[head+1]
            label2, x2, y2, w2, h2 = pos2[0], pos2[1], pos2[2], pos2[3], pos2[4]

            if abs(x1-x2) <= margin and abs(y1-y2) <= margin: 
                sim.append([which2, [label2, x2, y2, w2, h2]])
                head += 1
            else: 
                similar = False
        
        if len(sim) == 1: 
            merged_bbox.append([which1, [label1, x1, y1, w1, h1]])
        else: 
            # print('merged') 
            # print(sim)
            x = int(np.average([sim[i][1][1] for i in range(len(sim))]))
            y = int(np.average([sim[i][1][2] for i in range(len(sim))]))
            w = int(np.average([sim[i][1][3] for i in range(len(sim))]))
            h = int(np.average([sim[i][1][4] for i in range(len(sim))]))

            which = np.bincount([sim[i][0] for i in range(len(sim))]).argmax()

            merged_bbox.append([which, [label1, x, y, w, h]])
        
        head += 1
    
    if viz: 
        for box in merged_bbox: 
            which, pos = box
            label, x, y, w, h = pos[0], pos[1], pos[2], pos[3], pos[4]
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 1, cv2.LINE_AA)
        
        cv2.imwrite('merged_label.jpg', img)

    return merged_bbox 


