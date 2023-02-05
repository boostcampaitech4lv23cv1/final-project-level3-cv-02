import cv2
import numpy as np 
import copy 

def noise_removal(note_pos, symbol_pos, clef, original): 
    original_copy = copy.deepcopy(original)
    new_pos = note_pos
    
    note_min_x = np.min([note_pos[i][1][1] for i in range(len(note_pos))])
    note_min_y = np.min([note_pos[i][1][2] for i in range(len(note_pos))])
    note_max_x = np.max([note_pos[i][1][1] for i in range(len(note_pos))])
    note_max_y = np.max([note_pos[i][1][2] for i in range(len(note_pos))])

    if len(symbol_pos) > 0: 
        sym_min_x = 0
        sym_min_y = 0
        sym_max_x = np.max([symbol_pos[0][i][1][1][1] for i in range(len(symbol_pos[0]))])
        sym_max_y = original.shape[1] 
        sym_max_w = np.max([symbol_pos[0][i][1][1][3] for i in range(len(symbol_pos[0]))])
        sym_max_h = np.max([symbol_pos[0][i][1][1][4] for i in range(len(symbol_pos[0]))])


        ## filtering note heads 
        new_pos = [] 
        for note in note_pos: 
            which, pos = note 
            _, x, y, w, h = pos[0], pos[1], pos[2], pos[3], pos[4] 

            if sym_min_x <= x <= sym_max_x+sym_max_w and sym_min_y <= y <= sym_max_y+sym_max_h: 
                continue 
            new_pos.append(note) 
        

        cv2.rectangle(original_copy, (note_min_x, note_min_y), (note_max_x, note_max_y), (0, 0, 255), 1, cv2.LINE_AA)
        cv2.rectangle(original_copy, (sym_min_x, sym_min_y), (sym_max_x+sym_max_w, sym_max_y+sym_max_h), (255, 0, 0), 1, cv2.LINE_AA)
        cv2.imwrite('testing_removal_symbols.jpg', original_copy)
    
    elif len(clef) > 0: 
        sym_min_x = 0
        sym_min_y = 0
        sym_max_x = np.max([clef[i][1] for i in range(len(clef))])
        sym_max_y = original.shape[1] 
        sym_max_w = np.max([clef[i][3] for i in range(len(clef))])
        sym_max_h = np.max([clef[i][4] for i in range(len(clef))])


        ## filtering note heads 
        new_pos = [] 
        for note in note_pos: 
            which, pos = note 
            _, x, y, w, h = pos[0], pos[1], pos[2], pos[3], pos[4] 

            if sym_min_x <= x <= sym_max_x+sym_max_w and sym_min_y <= y <= sym_max_y+sym_max_h: 
                continue 
            new_pos.append(note) 
        

        cv2.rectangle(original_copy, (note_min_x, note_min_y), (note_max_x, note_max_y), (0, 0, 255), 1, cv2.LINE_AA)
        cv2.rectangle(original_copy, (sym_min_x, sym_min_y), (sym_max_x+sym_max_w, sym_max_y+sym_max_h), (255, 0, 0), 1, cv2.LINE_AA)
        cv2.imwrite('testing_removal_clef.jpg', original_copy)

    return new_pos