#!/bin/bash 

python postprocess.py \
    --note_label_file /opt/ml/yolov7/runs/notehead/test/labels/clock_processed.txt \
    --symbol_label_file /opt/ml/yolov7/runs/symbols/test/labels/clock_processed.txt \
    --img_path /opt/ml/yolov7/source/clock.png \
    --staves /opt/ml/yolov7/staves.txt


