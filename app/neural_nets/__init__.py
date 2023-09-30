import numpy as np
import cv2
from ultralytics import YOLO
import albumentations as alb
from main_app.logger import logger


FRAME_WIDTH, FRAME_HEIGHT = 640, 360
CONTROL_SET = set([14, 15, 16, 17, 18, 19, 20, 21, 22])
PERSON_SET = set([0])


class Net:
    def __init__(self,
                 frame_height: int = FRAME_HEIGHT,
                 frame_width: int = FRAME_WIDTH
                 ) -> None:
        self.frame_height = frame_height
        self.frame_width = frame_width

        # self.weights = 'neural_nets/weights/yolov8s_50ep_bs16.pt'
        self.weights_cl = 'neural_nets/weights/best.pt'  # yolov8n-cls.pt'

        self.model = YOLO('yolov8x-seg.pt')  # "yolov8n-cls.pt")  # self.weights)
        self.model_cls = YOLO(self.weights_cl)

        self.transform = alb.Compose([alb.Resize(self.frame_height, self.frame_width, cv2.INTER_LANCZOS4)])

    def predict(self, img: np.ndarray) -> tuple[int, np.ndarray]:
        img = np.array(self.transform(image=img)["image"])

        results = self.model(img, verbose=False, conf=0.5)
        class_list = results[0].boxes.cls.to('cpu').tolist()

        if len(CONTROL_SET.intersection(set(class_list))) != 0 and len(PERSON_SET.intersection(set(class_list))) == 0:
            return 1, results[0].plot(labels=False)

        pred = self.model_cls(img, verbose=False, conf=0.5)
        # logger.info(pred[0].probs.top1)

        return pred[0].probs.top1, img

        # if len(class_list) == 0:
        #     return 0, img
        #
        #     newfilepath = f'{os.path.join(yolov_path, empty_folder, filename)}'
        #     out = cv2.resize(im, None, fx = 0.2,fy=0.2)
        #     cv2.imwrite(newfilepath, out)
        # elif len(CONTROL_SET.intersection(set(class_list))) != 0 and len(PERSON_SET.intersection(set(class_list))) == 0:
        #     return 1, results[0].plot(labels=False)
        #
        #     # out = cv2.resize(im_array, None, fx = 0.2,fy=0.2)
        #     # newfilepath = f'{os.path.join(yolov_path, animal_folder, filename)}'
        #     # cv2.imwrite(newfilepath, out)
        # else:
        #     newfilepath = f'{os.path.join(yolov_path, empty_folder, filename)}'
        #     im_array = results[0].plot()
        #     out = cv2.resize(im_array, None, fx = 0.2,fy=0.2)
        #     cv2.imwrite(newfilepath, out)
