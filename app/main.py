from fastapi import FastAPI, Request, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
import uvicorn 
import sys 
sys.path.append("..")

from starlette.responses import RedirectResponse
import service

app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def file_form(request: Request): 
    return templates.TemplateResponse('index.html', context={'request': request})

@app.get("/play")
def file_form(request: Request): 
    return templates.TemplateResponse('play.html', context={'request': request})

# #(TODO) 인증 기능 구현 후 play에 query_parameter, path_parameter해서 유저별 페이지 만들기 
# # ex. /play?user_id=sangmo
# @app.post('/play')
# def play_form(request:Request, images: List[bytes] = File(...)):
#     fpaths = service.loading_form(images)
#     print(fpaths)
#     print({"file_sizes": [len(image) for image in images]})
#     return templates.TemplateResponse('play.html', context = {'request': request, "file_path": fpaths})

#(TODO 1) /opt/ml/tmp/file(로컬 저장)을 전제로 하고 있는데, DB 저장 혹은 버킷 저장 시 경로를 인자로 받기
#(TODO 2) print문 등을 logging으로 대체하기
@app.post("/loading")
def loading_form(request: Request, images: List[bytes] = File(...)) :
    fpaths = service.loading_form(images)
    return templates.TemplateResponse('loading.html', context={'request': request, "file_path": fpaths})

@app.post("/hard-loading")
def loading_form2(request: Request, images: List[bytes] = File(...)) :
    fpaths = service.loading_form(images)
    return templates.TemplateResponse('hard-loading.html', context={'request': request, "file_path": fpaths})

#(TODO) 지금은 img_path를 함수 인자로 안 받고 있지만, REST API에서 img_path를 받을 수 있다면, 거기에 접근해서 img_path를 가져올 수 있게끔 하기]
#(TODO 2) 에러 페이지 별도로 만들어서 띄우기... 근데 이거 나중에 해라
@app.get("/predict_model")
def predict_model(request: Request):
    #(TODO) img_path를 제대로 넘길 법 고민하기
    #(BETTER_WAY) img_path = request[...] 이런 느낌으로 가져오는 것이 좋다.
    try:
        results = service.predict_model()
    except Exception as e:
        print(e)
        return RedirectResponse("/error")
    print(results)
    return templates.TemplateResponse('play.html', context={'request': request, "results:" : results})

#(TODO) E-mail 연결
@app.get("/predict_model_hard")
def predict_model(request: Request):
    try:
        results = service.predict_model_hard()
    except Exception as e:
        print(e)
        return RedirectResponse("/error")
    print(results)
    return templates.TemplateResponse('hard-loading.html', context={'request': request, "results:" : results})

@app.post("/error")
def error_form(request: Request) :
    return templates.TemplateResponse('error.html', context={'request': request})

@app.get("/sign-in")
def file_form(request: Request): 
    return templates.TemplateResponse('sign-in.html', context={'request': request})

@app.get("/sign-up")
def file_form(request: Request): 
    return templates.TemplateResponse('sign-up.html', context={'request': request})

@app.get("/sign-check")
def check_form(request: Request): 
    return templates.TemplateResponse('sign-check.html', context={'request': request})

@app.get('/error')
def error_form(request: Request) :
    return templates.TemplateResponse('error.html', context={'request': request})

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)