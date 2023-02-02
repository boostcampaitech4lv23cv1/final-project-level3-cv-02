from PIL import Image 
import io
import os
from argparse import Namespace
from constant import fast_dict, slow_dict, paths
from MusicXML2Audio.main import main as xml2mp3
from constant import BUCKET_URL
from db.service import sound as sound_service

import sys 
sys.path.append("..")
sys.path.append(".")
from MusicXML2Audio.main import main as xml2mp3

import urllib
from oemer.ete import extract

def predict_model(db, image_bundle_id):
    img_path = os.path.join(paths['img_path'], image_bundle_id)
    xml_path = os.path.join(paths['xml_path'], image_bundle_id)
    os.makedirs(xml_path)
    mp3_path = os.path.join(paths['mp3_path'], image_bundle_id)
    os.makedirs(mp3_path)
    filename='result'

    results=[]
    for fpath in os.listdir(img_path):
        fname = os.path.join(img_path, fpath)
        fast_dict["img_path"] = fname
        fast_dict["output_path"] = xml_path
        dict_args = Namespace(**fast_dict)
        result_path = extract(dict_args)  
        results.append(result_path)

    xml2mp3(filename, xml_path, mp3_path, True, True, False)
    mp3_url = sound_service.upload_sound(db, image_bundle_id)
    
    return mp3_url

def predict_model_hard(img_path = paths['img_path'], img_bundle_id = ''):
    img_path = os.path.join(img_path, img_bundle_id)
    xml_path = os.path.join(paths['xml_path'], img_bundle_id)
    mp3_path = os.path.join(paths['mp3_path'], img_bundle_id)
    filename='result'

    results=[]
    for fpath in os.listdir(img_path):
        fname = os.path.join(img_path, fpath)
        slow_dict["img_path"] = fname
        slow_dict["output_path"] = paths["xml_path"]
        dict_args = Namespace(**slow_dict)
        result_path = extract(dict_args)  
        results.append(result_path)

    xml2mp3(filename, xml_path, mp3_path, True, True, False)

    return os.path.join(mp3_path, f"{filename}_0.mp3")