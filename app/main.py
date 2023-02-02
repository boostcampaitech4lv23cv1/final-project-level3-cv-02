from fastapi import FastAPI, Request, File, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
import uvicorn 
import sys 
from  db.routes import image_bundle, sound, users
from sqlalchemy.orm import Session
from db.connection import get_db

sys.path.append("..")

from starlette.responses import RedirectResponse
import service

app = FastAPI()
#crud router 추가
app.include_router(users.router)
app.include_router(image_bundle.router)
app.include_router(sound.router)

templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def file_form(request: Request): 
    return templates.TemplateResponse('index.html', context={'request': request})

@app.post("/play/{image_bundle_id}")
def predict_model(request: Request, image_bundle_id, db: Session = Depends(get_db)):
    try:
        results = service.predict_model(db, image_bundle_id)
    except Exception as e:
        print(e)
        return RedirectResponse("/error")
    print(results)
    return templates.TemplateResponse('play.html', context={'request': request, "results:" : results})

@app.post("/error")
def error_form(request: Request) :
    return templates.TemplateResponse('error.html', context={'request': request})

@app.get("/error")
def error_form(request: Request) :
    return templates.TemplateResponse('error.html', context={'request': request})

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)