import os
import uuid
import time
import json
import cv2
from fastapi import FastAPI, status, Request, File, BackgroundTasks, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from main_app.logger import logger
from templates import templates

import torch
import shutil


class Upload(BaseModel):
    path: str
    filename: str


class Status(BaseModel):
    percent: int
    path: str | None = None
    filename: str | None = None


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/test", StaticFiles(directory="test"), name="test")

logger.add('out.log', format="{time} {level} {message}", level="DEBUG")


@app.get("/", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def index(request: Request):
    data = {'title': 'Сервис по классификации качественных и некачественных фото'}
    template_data = {"request": request}
    template_data.update(**data)
    return templates.TemplateResponse("index.html", template_data)


@app.post("/upload")
async def upload(file: bytes = File(...)) -> Upload:
    filename = uuid.uuid4().hex + '.mp4'
    path = './test'
    with open(f'{path}/{filename}', 'wb') as f:
        f.write(file)
    return Upload(path=path, filename=filename)


def predict_file(filename: str, out_path: str, fr=600, step=30):
    path = './test'
    name = f'{path}/{filename}'
    #out_path = f'{path}/res'


@app.post("/predict")
async def predict(filename: str) -> Status:
    path = './test'
    name = f'{path}/{filename}'
    suffix = 'out'
    fn, ext = os.path.splitext(filename)

    out_name = f'{path}/res/{fn}_{suffix}{ext}'

    return Status(**{'percent': 100, 'path': path, 'filename': out_name})
