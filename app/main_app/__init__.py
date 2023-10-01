import os
from os.path import exists, isfile, isdir, join, splitext
import uuid
import time
import json
import shutil
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
    broken: list[str]
    empty: list[str]
    animal: list[str]


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


def unpack_zipfile(filename, extract_dir, encoding='cp437'):
    with zipfile.ZipFile(filename) as archive:
        for entry in archive.infolist():
            name = entry.filename.encode('cp437').decode(encoding)  # reencode!!!

            # don't extract absolute paths or ones with .. in them
            if name.startswith('/') or '..' in name:
                continue

            target = os.path.join(extract_dir, *name.split('/'))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if not entry.is_dir():  # file
                with archive.open(entry) as source, open(target, 'wb') as dest:
                    shutil.copyfileobj(source, dest)


@app.post("/upload")
async def upload(file: bytes = File(...)) -> Upload:
    path = './test'
    name = uuid.uuid4().hex

    filename = name + '.zip'
    with open(f'{path}/{filename}', 'wb') as f:
        f.write(file)

    unpack_zipfile(f'{path}/{filename}', f'{path}/{name}', encoding='cp866')

    # with zipfile.ZipFile(f'{path}/{filename}') as zip_ref:  # , metadata_encoding='utf-8'
    #     zip_ref.extractall(f'{path}/{name}')

    os.remove(f'{path}/{filename}')

    return Upload(path=path, filename=name)


def predict_file(filename: str, out_path: str, fr=600, step=30):
    path = './test'
    name = f'{path}/{filename}'
    # out_path = f'{path}/res'


def predict_images_in_dir(path: str, path_res: str):
    path_test = './test'
    cur_path = '/'.join(path.replace('\\', '/').replace(path_test + '/', '').split('/')[1:])
    logger.info(cur_path)
    files = os.listdir(path)  # [f for f in os.listdir(path) if splitext(join(path, f))
    for f in files:
        if isfile(join(path, f)) and splitext(join(path, f))[-1].lower() in EXTS:
            try:
                img = cv2.imread(join(path, f))
                cl, img_pred = net.predict(img)

                write_path = None
                if cl == 0:
                    write_path = join(path_res, 'broken', cur_path)
                elif cl == 1:
                    write_path = join(path_res, 'empty', cur_path)
                else:
                    write_path = join(path_res, 'animal', cur_path)

                if write_path is not None:
                    if not exists(write_path):
                        os.makedirs(write_path)
                    cv2.imwrite(join(write_path, f), img_pred)
            except Exception as exc:
                logger.error(str(exc))
        elif isdir(join(path, f)):
            predict_images_in_dir(join(path, f), path_res)


def get_images_list(path) -> list[str]:
    res = []
    files = os.listdir(path)
    for f in files:
        if isfile(join(path, f)):
            res.append(join(path, f))
        if isdir(join(path, f)):
            res += get_images_list(join(path, f))
    return res


def create_predict_result(path_res: str) -> ColumnImg:
    broken = []
    empty = []
    animal = []
    if exists(join(path_res, 'broken')):
        broken = get_images_list(join(path_res, 'broken'))
    if exists(join(path_res, 'empty')):
        empty = get_images_list(join(path_res, 'empty'))
    if exists(join(path_res, 'animal')):
        animal = get_images_list(join(path_res, 'animal'))

    return ColumnImg(broken=broken, empty=empty, animal=animal)


def create_csv(filename: str, column_img: ColumnImg) -> None:
    with open(filename, 'wt') as f:
        f.write('filename;broken;empty;animal\n')

        for item in column_img.broken:
            f.write(f'{item};1;0;0\n')

        for item in column_img.empty:
            f.write(f'{item};0;1;0\n')

        for item in column_img.animal:
            f.write(f'{item};0;0;1\n')


@app.post("/predict")
async def predict(filename: str) -> PredictData:
    path = './test'
    name = f'{path}/{filename}'
    name_res = name + '_res'

    if exists(name):
        if not exists(name_res):
            os.makedirs(name_res)
        predict_images_in_dir(name, name_res)
        column_img = create_predict_result(name_res)
        create_csv(name + '.csv', column_img)
        return PredictData(filename=name + '.csv', images=column_img)

    return PredictData(filename='', images=ColumnImg(broken=[], empty=[], animal=[]))
