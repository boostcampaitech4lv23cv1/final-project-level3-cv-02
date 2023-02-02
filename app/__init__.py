import urllib.request as urllib
import os
from pathlib import Path
CHECKPOINTS_URL = {
    "1st_model.onnx": "https://github.com/BreezeWhite/oemer/releases/download/checkpoints/1st_model.onnx",
    "1st_weights.h5": "https://github.com/BreezeWhite/oemer/releases/download/checkpoints/1st_weights.h5",
    "2nd_model.onnx": "https://github.com/BreezeWhite/oemer/releases/download/checkpoints/2nd_model.onnx",
    "2nd_weights.h5": "https://github.com/BreezeWhite/oemer/releases/download/checkpoints/2nd_weights.h5"
}
from constant import MODULE_PATH

def download_file(title, url, save_path):
    resp = urllib.urlopen(url)
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

def download_files():
    # Check there are checkpoints
    chk_path = os.path.join(MODULE_PATH, "checkpoints/unet_big/model.onnx")
    if not os.path.exists(chk_path):
        print("No checkpoint found in %s", chk_path)
        for idx, (title, url) in enumerate(CHECKPOINTS_URL.items()):
            print(f"Downloading checkpoints ({idx+1}/{len(CHECKPOINTS_URL)})")
            save_dir = "unet_big" if title.startswith("1st") else "seg_net"
            save_dir = os.path.join(MODULE_PATH, "checkpoints", save_dir)
            save_path = os.path.join(save_dir, title.split("_")[1])
            download_file(title, url, save_path)

download_files()