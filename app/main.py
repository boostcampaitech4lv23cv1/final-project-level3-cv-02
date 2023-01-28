from fastapi import FastAPI, Request, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
import uvicorn 
import sys 
sys.path.append("..")
from oemer.ete import main as predict 
from oemer.ete import extract
import subprocess
from PIL import Image 
import io
from argparse import Namespace
from starlette.responses import RedirectResponse

### 이거 분리가 필요하면 constant.py 같은 곳에 별도로. oemer 옵션 지정하는 곳


default_dict = dict(
    img_path = "/opt/ml/tmp.png",
    output_path = "./",
    use_tf = False,
    without_deskew = True,
    save_cache = False
)

fast_only_dict = dict(thresh = 512, step_size = 256)
slow_only_dict = dict(thresh = 1024,step_size = 128)

fast_dict = {**default_dict, **fast_only_dict}
slow_dict = {**default_dict, **slow_only_dict}

app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def file_form(request: Request): 
    return templates.TemplateResponse('index.html', context={'request': request})

@app.post('/play')
def play_form(request:Request):
    print("request:", request)
    print({"file_sizes": [len(image) for image in images]})
    
    dict_args = Namespace(**fast_dict)

    for image_byte in images: 
        print("type of image;", type(image_byte))
        image = Image.open(io.BytesIO(image_byte))
        image.save("/opt/ml/tmp.png")
        print("Successfully stored") 
        result_xml = extract(dict_args)  
        print("result_xml:", result_xml)
        print("type of result_xml:", type(result_xml))
    return templates.TemplateResponse('play.html', context = {'request': request})

@app.post("/loading")
def loading_form(request: Request, images: List[bytes] = File(...)) :
    return templates.TemplateResponse('loading.html', context={'request': request, "images": images})

# @app.get('/play')
# def play_formdef(request: Request): 
#     return templates.TemplateResponse('play.html', context={'request': request})

@app.post('/play')
def play_formdef(request: Request): 
    return templates.TemplateResponse('play.html', context={'request': request})

# @app.post('/play')
# def play_form(request:Request, images: List[bytes] = File(...)):
#     print({"file_sizes": [len(image) for image in images]})
#     return templates.TemplateResponse('play.html', context = {'request': request})

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)