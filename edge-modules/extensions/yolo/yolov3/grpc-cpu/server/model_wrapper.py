import os
import threading
import cv2
import numpy as np
from exception_handler import PrintGetExceptionDetails

import onnxruntime

import logging

class YoloV3Model:
    def __init__(self):
        try:
            self._lock = threading.Lock()
            self._modelFileName = 'yolov3-10.onnx'
            self._modelLabelFileName = 'coco_classes.txt'
            self._labelList = None

            with open(self._modelLabelFileName, "r") as f:
                self._labelList = [l.rstrip() for l in f]

            self._onnxSession = onnxruntime.InferenceSession(self._modelFileName)
            self.image_shape = [416, 416]

        except:
            PrintGetExceptionDetails()
            raise

    def Preprocess(self, cvImage):
        try:
            imageBlob = cv2.cvtColor(cvImage, cv2.COLOR_BGR2RGB)
            imageBlob = np.array(imageBlob, dtype='float32')
            imageBlob /= 255.
            imageBlob = np.transpose(imageBlob, [2, 0, 1])
            imageBlob = np.expand_dims(imageBlob, 0)

            return imageBlob
        except:
            PrintGetExceptionDetails()
            raise

    def Score(self, cvImage):
        try:
            with self._lock:
                imageBlob = self.Preprocess(cvImage)
                boxes, scores, indices = self._onnxSession.run(None, {"input_1": imageBlob, "image_shape":np.array([self.image_shape], dtype=np.float32)})

            return boxes, scores, indices

        except:
            PrintGetExceptionDetails()
            raise