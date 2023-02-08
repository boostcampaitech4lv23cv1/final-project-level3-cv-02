import os
import pickle
import argparse
import urllib.request
from pathlib import Path
from PIL import Image

import sys 
sys.path.append(".")
sys.path.append("..")

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import numpy as np

from oemer import MODULE_PATH
from oemer import layers
from oemer.inference import inference
from oemer.utils import get_logger
from oemer.dewarp import estimate_coords, dewarp
from oemer.staffline_extraction import extract as staff_extract
from oemer.notehead_extraction import extract as note_extract
from oemer.note_group_extraction import extract as group_extract
from oemer.symbol_extraction import extract as symbol_extract
from oemer.rhythm_extraction import extract as rhythm_extract
from oemer.build_system import MusicXMLBuilder
from oemer.draw_teaser import teaser
import warnings 
import time
warnings.filterwarnings("ignore")

logger = get_logger(__name__)


CHECKPOINTS_URL = {
    "1st_model.onnx": "https://github.com/BreezeWhite/oemer/releases/download/checkpoints/1st_model.onnx",
    "1st_weights.h5": "https://github.com/BreezeWhite/oemer/releases/download/checkpoints/1st_weights.h5",
    "2nd_model.onnx": "https://github.com/BreezeWhite/oemer/releases/download/checkpoints/2nd_model.onnx",
    "2nd_weights.h5": "https://github.com/BreezeWhite/oemer/releases/download/checkpoints/2nd_weights.h5"
}





def clear_data():
    lls = layers.list_layers()
    for l in lls:
        layers.delete_layer(l)


def generate_pred(img_path, step_size, thresh, use_tf=False):
    logger.info("Extracting staffline and symbols")
    staff_symbols_map, _ = inference(
        os.path.join(MODULE_PATH, "checkpoints/unet_big"),
        img_path,
        step_size = step_size, #FIXME
        use_tf=use_tf,
        thresh =  thresh #FIXME
    )
    staff = np.where(staff_symbols_map==1, 1, 0)
    symbols = np.where(staff_symbols_map==2, 1, 0)

    logger.info("Extracting layers of different symbols")
    symbol_thresholds = [0.5, 0.4, 0.4]
    sep, _ = inference(
        os.path.join(MODULE_PATH, "checkpoints/seg_net"),
        img_path,
        step_size = step_size, #FIXME
        manual_th=None,
        use_tf=use_tf,
        thresh = thresh #FIXME
    )
    stems_rests = np.where(sep==1, 1, 0)
    notehead = np.where(sep==2, 1, 0)
    clefs_keys = np.where(sep==3, 1, 0)
    # stems_rests = sep[..., 0]
    # notehead = sep[..., 1]
    # clefs_keys = sep[..., 2]

    return staff, symbols, stems_rests, notehead, clefs_keys


def polish_symbols(rgb_black_th=300):
    # img = layers.get_layer('original_image')
    # sym_pred = layers.get_layer('symbols_pred')

    img = Image.fromarray(img).resize((sym_pred.shape[1], sym_pred.shape[0]))
    arr = np.sum(np.array(img), axis=-1)
    arr = np.where(arr < rgb_black_th, 1, 0)  # Filter background
    ker = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
    arr = cv2.dilate(cv2.erode(arr.astype(np.uint8), ker), ker)  # Filter staff lines
    mix = np.where(sym_pred+arr>1, 1, 0)
    return mix


def register_notehead_bbox(bboxes):
    symbols = layers.get_layer('symbols_pred')
    layer = layers.get_layer('bboxes')
    for (x1, y1, x2, y2) in bboxes:
        yi, xi = np.where(symbols[y1:y2, x1:x2]>0)
        yi += y1
        xi += x1
        layer[yi, xi] = np.array([x1, y1, x2, y2])
    return layer


def register_note_id(symbols = None, layer = None, notes = None):
    # symbols = layers.get_layer('symbols_pred')
    # layer = layers.get_layer('note_id')
    # notes = layers.get_layer('notes')
    for idx, note in enumerate(notes):
        x1, y1, x2, y2 = note.bbox
        yi, xi = np.where(symbols[y1:y2, x1:x2]>0)
        yi += y1
        xi += x1
        layer[yi, xi] = idx
        notes[idx].id = idx
    return symbols, layer, notes


def extract(args):
    start_time = time.time()
    
    img_path = Path(args.img_path)
    f_name = os.path.splitext(img_path.name)[0]
    pkl_path = img_path.parent / f"{f_name}.pkl"
    if pkl_path.exists():
        # Load from cache
        pred = pickle.load(open(pkl_path, "rb"))
        notehead = pred["note"]
        symbols = pred["symbols"]
        staff = pred["staff"]
        clefs_keys = pred["clefs_keys"]
        stems_rests = pred["stems_rests"]
    else:
        # Make predictions
        if args.use_tf:
            ori_inf_type = os.environ.get("INFERENCE_WITH_TF", None)
            os.environ["INFERENCE_WITH_TF"] = "true"
        staff, symbols, stems_rests, notehead, clefs_keys = generate_pred(str(img_path), 
                                                                          step_size = args.step_size,
                                                                          thresh = args.thresh,
                                                                          use_tf=args.use_tf)
        if args.use_tf:
            os.environ["INFERENCE_WITH_TF"] = ori_inf_type
        if args.save_cache:
            data = {
                'staff': staff,
                'note': notehead,
                'symbols': symbols,
                'stems_rests': stems_rests,
                'clefs_keys': clefs_keys
            }
            pickle.dump(data, open(pkl_path, "wb"))

    # Load the original image, resize to the same size as prediction.
    image = cv2.imread(str(img_path))
    image = cv2.resize(image, (staff.shape[1], staff.shape[0]))

    if not args.without_deskew:
        logger.info("Dewarping")
        coords_x, coords_y = estimate_coords(staff)
        staff = dewarp(staff, coords_x, coords_y)
        symbols = dewarp(symbols, coords_x, coords_y)
        stems_rests = dewarp(stems_rests, coords_x, coords_y)
        clefs_keys = dewarp(clefs_keys, coords_x, coords_y)
        notehead = dewarp(notehead, coords_x, coords_y)
        for i in range(image.shape[2]):
            image[..., i] = dewarp(image[..., i], coords_x, coords_y)

    # Register predictions
    symbols = symbols + clefs_keys + stems_rests
    symbols[symbols>1] = 1
    # layers.register_layer("stems_rests_pred", stems_rests)
    # layers.register_layer("clefs_keys_pred", clefs_keys)
    # layers.register_layer("notehead_pred", notehead)
    # layers.register_layer("symbols_pred", symbols)
    # layers.register_layer("staff_pred", staff)
    # layers.register_layer("original_image", image)

    # ---- Extract staff lines and group informations ---- #
    logger.info("Extracting stafflines")
    staffs, zones = staff_extract(staff_pred = staff
                                  , symbols = symbols 
                                  , stems = stems_rests
                                  , notehead = notehead 
                                  , clefs = clefs_keys
                                  )  #인자를 넣어서 반환
    # layers.register_layer("staffs", staffs)  # Array of 'Staff' instances
    # layers.register_layer("zones", zones)  # Range of each zones, array of 'range' object.

    # ---- Extract noteheads ---- #
    logger.info("Extracting noteheads") 
    
    notes = note_extract(
          pred = notehead
        , symbols = symbols
        , zones = zones
        , staffs = staffs
        , stems = stems_rests
        )

    # Array of 'NoteHead' instances.
    notes= np.array(notes)
    # layers.register_layer('notes', np.array(notes))

    # Add a new layer (w * h), indicating note id of each pixel.
    note_id = np.zeros(symbols.shape, dtype=int) -1
    # layers.register_layer('note_id', np.zeros(symbols.shape, dtype=int)-1)
    symbols, layer, notes = register_note_id(symbols = symbols,
                     layer = note_id,
                     notes = notes)

    # ---- Extract groups of note ---- #
    logger.info("Grouping noteheads")
    groups, group_map = group_extract(
        note_id_map = note_id
        , notehead = notehead
        , stems = stems_rests
        , notes = notes
        , staffs = staffs 
    ) 
    
    note_groups = np.array(groups)
    group_map = group_map
    # layers.register_layer('note_groups', np.array(groups))
    # layers.register_layer('group_map', group_map)


    # ---- Extract symbols ---- #
    logger.info("Extracting symbols")
    barlines, clefs, sfns, rests = symbol_extract(
        symbols = symbols , 
        stems_rests = stems_rests , 
        clefs_keys =  clefs_keys ,
        group_map =  group_map ,
        zones = zones , 
        staffs = staffs , 
        note_id_map = note_id , 
        notes = notes
    ) 
    
    barlines = np.array(barlines)
    clefs = np.array(clefs)
    sfns = np.array(sfns)
    rests = np.array(rests)
    # layers.register_layer('barlines', np.array(barlines))
    # layers.register_layer('clefs', np.array(clefs))
    # layers.register_layer('sfns', np.array(sfns))
    # layers.register_layer('rests', np.array(rests))

    # ---- Parse rhythm ---- #
    logger.info("Extracting rhythm types")
    rhythm_extract(
        symbols = symbols, 
        staffs = staffs, 
        stems = stems_rests , 
        group_map = group_map, 
        clefs_sfns = clefs_keys , 
        barlines = barlines, 
        groups = groups,         
        notehead = notehead, 
        notes = notes, 
        note_id_map = note_id, 
        staff_pred = staff
    )

    # ---- Build MusicXML ---- #
    logger.info("Building MusicXML document")
    basename = os.path.basename(img_path).replace(".jpg", "").replace(".png", "")
    builder = MusicXMLBuilder(title=basename.capitalize() 
                              , notes = notes 
                              , note_groups = note_groups 
                              , barlines = barlines 
                              , rests = rests
                              , clefs = clefs
                              , sfns = sfns
                              , staffs = staffs
                              )
    builder.build()
    xml = builder.to_musicxml()

    # ---- Write out the MusicXML ---- #
    out_path = args.output_path
    if not out_path.endswith(".musicxml"):
        # Take the output path as the folder.
        out_path = os.path.join(out_path, basename+".musicxml")

    with open(out_path, "wb") as ff:
        ff.write(xml)

    duration = time.time() - start_time 
    print("Total time:", duration)
    
    img = teaser(
        ori_img =  image
        , notes  = notes 
        , groups = note_groups 
        , barlines = barlines 
        , clefs = clefs 
        , sfns  = sfns
        , rests = rests
    )
    img.save(out_path.replace(".musicxml", "_teaser.png"))
    clear_data()
    return out_path, xml


def get_parser():
    parser = argparse.ArgumentParser(
        "Oemer",
        description="End-to-end OMR command line tool. Receives an image as input, and outputs MusicXML file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("img_path", help="Path to the image.", type=str)
    parser.add_argument(
        "-o", "--output-path", help="Path to output the result file.", type=str, default="./")
    parser.add_argument(
        "--use-tf", help="Use Tensorflow for model inference. Default is to use Onnxruntime.", action="store_true")
    parser.add_argument(
        "--save-cache",
        help="Save the model predictions and the next time won't need to predict again.",
        action='store_true')
    parser.add_argument(
        "-d",
        "--without-deskew",
        help="Disable the deskewing step if you are sure the image has no skew.",
        action='store_true')
    parser.add_argument(
        "--step_size",
        help = "Step_size determines the number of datas to be parsed. Default is 256.  Set 128 to get quality"
        ,type = int
        ,default = 256
    )
    parser.add_argument(
        "--thresh",
        help = "Thresh determines the resize_img. Default is 768. Be careful that number less than 1024 often raises Error",
        type = int, 
        default = 768        
    )
    return parser


def download_file(title, url, save_path):
    resp = urllib.request.urlopen(url)
    length = int(resp.getheader("Content-Length", -1))

    chunk_size = 2**9
    total = 0
    with open(save_path, "wb") as out:
        while True:
            print(f"{title}: {total*100/length:.1f}% {total}/{length}", end="\r")
            data = resp.read(chunk_size)
            if not data:
                break
            total += out.write(data)
        print(f"{title}: 100% {length}/{length}"+" "*20)


def main():
    parser = get_parser()
    args = parser.parse_args()
    print("args:", args)

    if not os.path.exists(args.img_path):
        raise FileNotFoundError(f"The given image path doesn't exists: {args.img_path}")

    # Check there are checkpoints
    chk_path = os.path.join(MODULE_PATH, "checkpoints/unet_big/model.onnx")
    if not os.path.exists(chk_path):
        logger.warn("No checkpoint found in %s", chk_path)
        for idx, (title, url) in enumerate(CHECKPOINTS_URL.items()):
            logger.info(f"Downloading checkpoints ({idx+1}/{len(CHECKPOINTS_URL)})")
            save_dir = "unet_big" if title.startswith("1st") else "seg_net"
            save_dir = os.path.join(MODULE_PATH, "checkpoints", save_dir)
            save_path = os.path.join(save_dir, title.split("_")[1])
            download_file(title, url, save_path)

    clear_data()
    mxl_path, xml_result = extract(args)
    # img.save(mxl_path.replace(".musicxml", "_teaser.png"))
    return xml_result

if __name__ == "__main__":
    xml_result = main()
