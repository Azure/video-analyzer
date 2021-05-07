# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from datetime import datetime
import io
import json
import os
import logging
import time
from typing import Tuple

from flask import Flask, Response, Request, abort, request
import numpy as np
import onnxruntime
from PIL import Image, ImageDraw, ImageFont
import requests

class YoloV3Model:
    def __init__(self):
        model_path = 'yolov3.onnx'
        
        self._session = onnxruntime.InferenceSession(model_path)
        tags_file = 'tags.txt'
        with open(tags_file) as f:
            self.tags = [line.strip() for line in f.readlines()]

        self.input_size = (416, 416)


    def preprocess(self, image: Image) -> np.ndarray:
        image_data = np.array(image, dtype='float32')
        image_data /= 255.
        image_data = np.transpose(image_data, [2, 0, 1])
        image_data = np.expand_dims(image_data, 0)

        return image_data


    def postprocess(self, boxes, scores, indices, image_size: Tuple[int, int], object_type: str = None, confidenceThreshold: float = 0.0) -> list:
        detected_objects = []
        image_width, image_height = image_size

        if indices.ndim == 3: 
            # Tiny YOLOv3 uses a 3D numpy array, while YOLOv3 uses a 2D numpy array
            indices = indices[0]  

        for index_ in indices:
            
            # See https://github.com/onnx/models/tree/master/vision/object_detection_segmentation/yolov3#output-of-model for more details
            object_tag = self.tags[index_[1].tolist()]
            confidence = scores[tuple(index_)].tolist()
            y1, x1, y2, x2 = boxes[(index_[0], index_[2])].tolist()
            width = (x2 - x1) / image_width
            height = (y2 - y1) / image_height
            left = x1 / image_width
            top = y1 / image_height

            dobj = {
                "type" : "entity",
                "entity" : {
                    "tag" : {
                        "value" : object_tag,
                        "confidence" : confidence
                    },
                    "box" : {
                        "l" : left,
                        "t" : top,
                        "w" : width,
                        "h" : height
                    }
                }
            }

            if object_type is None:
                detected_objects.append(dobj)
            else:
                if (object_type == object_tag) and (confidence > confidenceThreshold):
                    detected_objects.append(dobj)

        return detected_objects


    def process_image(self, image: Image, object_type: str = None, confidence_threshold: float = 0.0) -> Tuple[list, float]:
        # Preprocess input according to the functions specified above
        image_data = self.preprocess(image)
        image_size = np.array([image.size[1], image.size[0]], dtype=np.float32).reshape(1, 2)

        inference_time_start = time.time()
        boxes, scores, indices = self._session.run(None, {"input_1": image_data, "image_shape": image_size})
        inference_time_end = time.time()
        inference_duration_s = inference_time_end - inference_time_start
        
        detected_objects = self.postprocess(boxes, scores, indices, image.size, object_type, confidence_threshold)
        return detected_objects, inference_duration_s


def init_logging():
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger != None:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)


def draw_bounding_boxes(image: Image, detected_objects: list):
    objects_identified = len(detected_objects)
    
    image_width, image_height = image.size
    draw = ImageDraw.Draw(image)

    textfont = ImageFont.load_default()
    
    for pos in range(objects_identified):
        entity = detected_objects[pos]['entity']
        box = entity["box"]
        x1 = box["l"]
        y1 = box["t"]
        x2 = box["w"]
        y2 = box["h"]
        
        x1 = x1 * image_width
        y1 = y1 * image_height
        x2 = (x2 * image_width) + x1
        y2 = (y2 * image_height) + y1
        tag = entity['tag']
        object_class = tag['value']

        draw.rectangle((x1, y1, x2, y2), outline = 'blue', width = 1)
        draw.text((x1, y1), str(object_class), fill = "white", font = textfont)

    return image


def letterbox_image(image, size):
    '''Resize image with unchanged aspect ratio using padding'''
    iw, ih = image.size
    w, h = size
    scale = min(w/iw, h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)

    image = image.resize((nw,nh), Image.BICUBIC)
    new_image = Image.new('RGB', size, (128,128,128))
    new_image.paste(image, ((w-nw)//2, (h-nh)//2))

    return new_image

def load_image(request: Request):
    try:
        image_data = io.BytesIO(request.get_data())
        image = Image.open(image_data)
    except Exception:
        abort(Response(response='Could not decode image', status=400))

    # If size is not 416x416 then resize
    if image.size != model.input_size:
        model_image_size = (416, 416)
        new_image = image
        image = letterbox_image(new_image, tuple(reversed(model_image_size)))

    return image


app = Flask(__name__)

init_logging()

model = YoloV3Model()
app.logger.info('Model initialized')

# / routes to the default function which returns 'Hello World'
@app.route('/', methods=['GET'])
def default_page():
    return Response(response='Hello from Yolov3 inferencing based on ONNX', status=200)

@app.route('/stream/<id>')
def stream(id):
    respBody = ("<html>"
                "<h1>Stream with inferencing overlays</h1>"
                "<img src=\"/mjpeg/" + id + "\"/>"
                "</html>")

    return Response(respBody, status=200)

# /score routes to scoring function 
# This function returns a JSON object with inference duration and detected objects
@app.route("/score", methods=['POST'])
def score():
    confidence = request.args.get('confidence', default = 0.0, type = float)
    object_type = request.args.get('object')
    stream = request.args.get('stream')

    image = load_image(request)
    detected_objects, _ = model.process_image(image, object_type, confidence)

    if stream is not None:
        output_image = draw_bounding_boxes(image, detected_objects)

        image_buffer = io.BytesIO()
        output_image.save(image_buffer, format='JPEG')

        # post the image with bounding boxes so that it can be viewed as an MJPEG stream
        postData = b'--boundary\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + image_buffer.getvalue() + b'\r\n'
        requests.post('http://127.0.0.1:80/mjpeg_pub/' + stream, data = postData)

    if len(detected_objects) > 0:
        respBody = {
            "inferences" : detected_objects
        }

        respBody = json.dumps(respBody)
        return Response(respBody, status= 200, mimetype ='application/json')
    else:
        return Response(status= 204)

# /score-debug routes to score_debug
# This function scores the image and stores an annotated image for debugging purposes
@app.route('/score-debug', methods=['POST'])
def score_debug():
    image = load_image(request)

    detected_objects, inference_duration_s = model.process_image(image)
    app.logger.info('Inference took %.2f seconds', inference_duration_s)

    output_image = draw_bounding_boxes(image, detected_objects)

    # datetime object containing current date and time
    now = datetime.now()

    output_dir = 'images'
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    output_image_file = now.strftime("%d_%m_%Y_%H_%M_%S.jpeg")
    output_image.save(output_dir + "/" + output_image_file)

    respBody = {
        "inferences" : detected_objects
    }

    return respBody

# /annotate routes to annotation function 
# This function returns an image with bounding boxes drawn around detected objects
@app.route('/annotate', methods=['POST'])
def annotate():
    image = load_image(request)

    detected_objects, inference_duration_s = model.process_image(image)
    app.logger.info('Inference took %.2f seconds', inference_duration_s)

    image = draw_bounding_boxes(image, detected_objects)

    image_bytes = io.BytesIO()
    image.save(image_bytes, format = 'JPEG')
    image_bytes = image_bytes.getvalue()

    return Response(response = image_bytes, status = 200, mimetype = "image/jpeg")

if __name__ == '__main__':
    # Running the file directly
    app.run(host='0.0.0.0', port=8888)