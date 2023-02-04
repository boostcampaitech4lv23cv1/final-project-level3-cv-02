import sys 
sys.path.append("..")
from typing import List, Any
import urllib

from sqlalchemy.orm import Session

from concurrent.futures import ProcessPoolExecutor

from fastapi import FastAPI, Request, File, Form, Depends, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
import uvicorn 

import __init__
import service
from db.connection import get_db
from  db.routes import image_bundle, sound, users
from db.routes.users import get_user_by_email
from db.service import image_bundle as image_bundle_service 
from db.service import users as users_service
from db.models import image as image_model
from constant import DEFAULT_EMAIL


app = FastAPI()
#crud router 추가
app.include_router(users.router)
app.include_router(image_bundle.router)
app.include_router(sound.router)

templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def file_form(request: Request): 
    
    #DEFAULT_VALUE
    access_auth = "no"
    user_id = DEFAULT_EMAIL
    return templates.TemplateResponse('index.html', context={'request': request, "access_auth" : access_auth, "user_email" : user_id})

@app.post("/")
def login_user(request: Request, db: Session = Depends(get_db), user_id : str= Form(...), user_pwd: str = Form(...)):
    response = get_user_by_email(db, user_id)    
    result = response["res"]
    
    # 로그인 시 가입정보가 없다면
    if result is None: 
        return templates.TemplateResponse("error.html", context = {"request" : request}) 
    access_auth = "yes"
    
    #있다면, 인증성공여부와 함께 email_id를 response에 반환
    return templates.TemplateResponse('index.html', context={'request': request, "access_auth" : access_auth, "user_email" : user_id})
    


#(TODO) 인증 기능 구현 후 play에 query_parameter, path_parameter해서 유저별 페이지 만들기 
# ex. /play?user_id=sangmo
@app.post('/play')
def play_form(request:Request, images: List[bytes] = File(...)):
    print({"file_sizes": [len(image) for image in images]})
    return templates.TemplateResponse('play.html', context = {'request': request})

#(TODO 1) /opt/ml/tmp/file(로컬 저장)을 전제로 하고 있는데, DB 저장 혹은 버킷 저장 시 경로를 인자로 받기
#(TODO 2) print문 등을 logging으로 대체하기
@app.post("/loading")
def loading_form(request: Request, images: List[bytes] = File(...)) :
    fpaths = service.loading_form(images)
    return templates.TemplateResponse('loading.html', context={'request': request, "file_path": fpaths})

@app.post("/hard-loading")
def loading_form2(request: Request
                  , images: List[UploadFile] = File(...)
                  , db : Session = Depends(get_db)
                  , access_auth : str = Form(...)
                  , user_email: str = Form(...)
                  ) :
    paths, image_bundle_id = image_bundle_service.upload_images(db, user_email, images)
    image_url = db.query(image_model.Image).filter(image_model.Image.image_bundle_id ==image_bundle_id).first().image_url
    
    
    #predict_model_hard


    return templates.TemplateResponse('hard-loading.html', context={'request': request})

  
@app.post("/play/{image_bundle_id}")
def predict_model(request: Request, image_bundle_id, db: Session = Depends(get_db)):
    for _ in range(100):
        print("parameter:", image_bundle_id)
    try:
        image_url = db.query(image_model.Image)\
            .filter(image_model.Image.image_bundle_id ==image_bundle_id).first().image_url
        mp3_url = service.predict_model(db, image_bundle_id) 
        
        for _ in range(5):
            print("predict model 떄의 image_url:", image_url)
            print("predict model 떄의 image_url:", mp3_url)
        
    except Exception as e:
        print(e)
        return RedirectResponse("/error")
    print(mp3_url)
    return templates.TemplateResponse('play.html', context={'request': request, "mp3_url" : mp3_url, "image_url" : image_url})

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
    print("request:", request)
    return templates.TemplateResponse('sign-check.html', context={'request': request})

@app.get('/error')
def error_form(request: Request) :
    return templates.TemplateResponse('error.html', context={'request': request})

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)