#!/bin/bash

# resource path -> 연주하려는 악보의 경로 
# save_name = source -> 전처리된 악보의 저장 경로 및 이름; 모델 input

RESOURCE_PATH='/opt/ml/model/source/bear.png'
SAVE_NAME='/opt/ml/model/source/bear_processed.jpg'
S_NAME='bear_processed.txt'
NAME='0208_7'

# read -p RESOURCE_PATH
# read -p SAVE_NAME
# read -p S_NAME
# read -p NAME

python preprocess.py \
    --resource_path $RESOURCE_PATH \
    --save_name $SAVE_NAME \

python /opt/ml/yolov7/detect.py \
    --weights /opt/ml/yolov7/weights/notehead.pt \
    --save-txt \
    --img-size 1024 \
    --no-trace \
    --project runs/notehead \
    --conf-thres 0.25 \
    --name $NAME\
    --source $SAVE_NAME \

python /opt/ml/yolov7/detect.py \
    --weights /opt/ml/yolov7/weights/best_symbol.pt \
    --save-txt \
    --img-size 1024 \
    --no-trace \
    --project runs/symbols \
    --conf-thres 0.25 \
    --name $NAME\
    --source $SAVE_NAME \

python postprocess.py \
    --note_label_file /opt/ml/model/runs/notehead/$NAME/labels/$S_NAME \
    --symbol_label_file /opt/ml/model/runs/symbols/$NAME/labels/$S_NAME \
    --img_path $RESOURCE_PATH \
    --staves /opt/ml/model/staves.txt

