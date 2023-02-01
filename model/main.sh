#!/bin/bash

# resource path -> 연주하려는 악보의 경로 
# save_name = source -> 전처리된 악보의 저장 경로 및 이름; 모델 input

RESOURCE_PATH='/opt/ml/yolov7/source/clock.png'
SAVE_NAME='/opt/ml/yolov7/source/clock_processed.jpg'
S_NAME='clock_processed.txt'
NAME='0131_2'

# read -p RESOURCE_PATH
# read -p SAVE_NAME
# read -p S_NAME
# read -p NAME

python preprocess.py \
    --resource_path $RESOURCE_PATH \
    --save_name $SAVE_NAME \

python detect.py \
    --weights weights/notehead.pt \
    --save-txt \
    --conf 0.25 \
    --img-size 1024 \
    --no-trace \
    --project runs/notehead \
    --conf-thres 0.5 \
    --name $NAME\
    --source $SAVE_NAME \

python detect.py \
    --weights weights/best_symbol.pt \
    --save-txt \
    --conf 0.25 \
    --img-size 1024 \
    --no-trace \
    --project runs/symbols \
    --conf-thres 0.5 \
    --name $NAME\
    --source $SAVE_NAME \

python postprocess.py \
    --note_label_file /opt/ml/yolov7/runs/notehead/$NAME/labels/$S_NAME \
    --symbol_label_file /opt/ml/yolov7/runs/symbols/$NAME/labels/$S_NAME \
    --img_path $RESOURCE_PATH \
    --staves /opt/ml/yolov7/staves.txt

