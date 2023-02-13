import cv2 
import os 
import sys 
import numpy as np 
import argparse 

from blog_functions import remove_noise, remove_staves, normalization

parser = argparse.ArgumentParser()
parser.add_argument('--resource_path', type=str, default='')
parser.add_argument('--save_name', type=str, default='')
opt = parser.parse_args()
print(opt)

original = cv2.imread(opt.resource_path)
# 1. 보표 영역 추출 및 그 외 노이즈 제거
image_1 = remove_noise(opt.resource_path)
# cv2.imwrite('image1.jpg', image_1)

# 2. 오선 제거
image_2, staves = remove_staves(image_1, original)
# cv2.imwrite('image2.jpg', image_2)

# 3. 악보 이미지 정규화
image_3 = normalization(image_2, staves, 10)
cv2.imwrite(opt.save_name, image_3)

