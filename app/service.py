from PIL import Image 
import io
import os
from argparse import Namespace
from constant import fast_dict, slow_dict
import sys 
sys.path.append("..")

from oemer.ete import main as predict 
from oemer.ete import extract

def loading_form(images):
    for order, image_byte in enumerate(images):
        image = Image.open(io.BytesIO(image_byte))
        image.save(f"/opt/ml/tmp/file_{order}.png")
        print(f"Image {order} 저장되었습니다.")
    IMG_PATH = "/opt/ml/tmp"
    return [f"/opt/ml/tmp/{fname}" for fname in os.listdir(IMG_PATH)]

def predict_model():
    img_path = "/opt/ml/tmp"
    results=[]
    for fpath in os.listdir(img_path):
        fname = os.path.join(img_path, fpath)
        fast_dict["img_path"] = fname
        dict_args = Namespace(**fast_dict)
        result_xml = extract(dict_args)  
        results.append(result_xml)
    return results