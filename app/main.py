from fastapi import FastAPI, Request, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
import uvicorn

app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def file_form(request: Request): 
    return templates.TemplateResponse('index.html', context={'request': request})

@app.get("/sign-in")
def file_form(request: Request): 
    return templates.TemplateResponse('sign-in.html', context={'request': request})

@app.get("/sign-up")
def file_form(request: Request): 
    return templates.TemplateResponse('sign-up.html', context={'request': request})

@app.post('/play')
def play_form(request:Request, images: List[bytes] = File(...)):
    print({"file_sizes": [len(image) for image in images]})
    return templates.TemplateResponse('play.html', context = {'request': request})

if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)