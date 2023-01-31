import os
from pathlib import Path

default_dict = dict(
    output_path = "./",
    use_tf = False,
    without_deskew = True,
    save_cache = False
)

fast_only_dict = dict(thresh = 768, step_size = 256)
slow_only_dict = dict(thresh = 1024,step_size = 128)

fast_dict = {**default_dict, **fast_only_dict}
slow_dict = {**default_dict, **slow_only_dict}

#(TODO) DB로 바꿔야함.
MODULE_PATH = "/opt/ml/oemer"

paths = {'img_path': '/opt/ml/results/images',
         'xml_path': '/opt/ml/results/xml',
         'mp3_path': '/opt/ml/results/sound'}


for k,v in paths.items():
    if not os.path.exists(v):
        os.makedirs(v, exist_ok = True)

