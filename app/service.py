from PIL import Image 
import io
import os
from argparse import Namespace
from constant import fast_dict, slow_dict, paths
import sys 
sys.path.append("..")
sys.path.append(".")
from MusicXML2Audio.main import main as xml2mp3

import urllib
from oemer.ete import extract

def loading_form(images):
    IMG_PATH = paths['img_path']
    for order, image_byte in enumerate(images):
        image = Image.open(io.BytesIO(image_byte))
        image.save(f"{IMG_PATH}/file_{order}.png")
        print(f"Image {order} 저장되었습니다.")
    return [f"{IMG_PATH}/{fname}" for fname in os.listdir(IMG_PATH)]

def predict_model(img_path = paths['img_path'], img_bundle_id = ''):
    img_path = os.path.join(img_path, img_bundle_id)
    xml_path = os.path.join(paths['xml_path'], img_bundle_id)
    mp3_path = os.path.join(paths['mp3_path'], img_bundle_id)
    filename='result'

    results=[]
    for fpath in os.listdir(img_path):
        fname = os.path.join(img_path, fpath)
        fast_dict["img_path"] = fname
        fast_dict["output_path"] = paths["xml_path"]
        dict_args = Namespace(**fast_dict)
        result_path = extract(dict_args)  
        results.append(result_path)

    xml2mp3(filename, xml_path, mp3_path, True, True, False)
    return os.path.join(mp3_path, f"{filename}_0.mp3")