import os
from os.path import exists, isfile, isdir, join, splitext
import uuid
import time
import json
import cv2
import zipfile
from fastapi import FastAPI, status, Request, File, BackgroundTasks, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from main_app.logger import logger
from templates import templates
from neural_nets import Net

import torch
import shutil

EXTS = ['.jpg', '.png']


class Upload(BaseModel):
    path: str
    filename: str


class Status(BaseModel):
    percent: int
    path: str | None = None
    filename: str | None = None


class ColumnImg(BaseModel):
    blurred: list[str]
    nobody: list[str]
    animals: list[str]


class PredictData(BaseModel):
    filename: str
    images: ColumnImg


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/test", StaticFiles(directory="test"), name="test")

net = Net()
logger.add('out.log', format="{time} {level} {message}", level="DEBUG")


@app.get("/", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def index(request: Request):
    data = {'title': 'Сервис по классификации качественных и некачественных фото'}
    template_data = {"request": request}
    template_data.update(**data)
    return templates.TemplateResponse("index.html", template_data)


@app.post("/upload")
async def upload(file: bytes = File(...)) -> Upload:
    path = './test'
    name = uuid.uuid4().hex

    filename = name + '.zip'
    with open(f'{path}/{filename}', 'wb') as f:
        f.write(file)

    with zipfile.ZipFile(f'{path}/{filename}') as zip_ref:
        zip_ref.extractall(f'{path}/{name}')

    os.remove(f'{path}/{filename}')

    return Upload(path=path, filename=name)


def predict_file(filename: str, out_path: str, fr=600, step=30):
    path = './test'
    name = f'{path}/{filename}'
    # out_path = f'{path}/res'


def predict_images_in_dir(path: str, path_res: str):
    files = os.listdir(path)  # [f for f in os.listdir(path) if splitext(join(path, f))
    for f in files:
        if isfile(join(path, f)) and splitext(join(path, f))[-1].lower() in EXTS:
            try:
                img = cv2.imread(join(path, f))
                cl, img_pred = net.predict(img)
                if cl == 0:
                    pass
                elif cl == 1:
                    pass
                else:
                    pass
            except Exception as exc:
                logger.error(str(exc))


@app.post("/predict")
async def predict(filename: str) -> PredictData:
    path = './test'
    name = f'{path}/{filename}'
    name_res = name + '_res'

    if exists(name):
        if not exists(name_res):
            os.makedirs(name_res)
        # predict_images_in_dir(name, name_res)

    blurred = [
        'broken_31.JPG',
        'broken_43.JPG',
        'broken_50.JPG'
    ]

    nobody = [
        'blurred_303.jpg',
        'clear_103__лабаз.jpg',
        'clear_173__PICT0711_кабанчик_в_бабочках.jpg',
        'clear_216__PICT0220_бабочки_боярышница.jpg',
        'clear_243__PICT0002хатка_зимой.jpg',
        'clear_346__PICT0433.JPG'
        ]

    animals = ['photo1696081846 (1).jpeg',
               'photo1696081846 (2).jpeg',
               'photo1696081846 (3).jpeg',
               'photo1696081846 (4).jpeg',
               'photo1696081846 (5).jpeg',
               'photo1696081846 (6).jpeg',
               'photo1696081846 (7).jpeg',
               'photo1696081846 (8).jpeg',
               'photo1696081846.jpeg'
               ]

    blurred = [join(path, 'blurred', x) for x in blurred]
    animals = [join(path, 'animals', x) for x in animals]
    nobody = [join(path, 'nobody', x) for x in nobody]

    return PredictData(filename='', images=ColumnImg(
        blurred=blurred,
        nobody=nobody,
        animals=animals
    ))
