FROM python:3.8-slim

WORKDIR /avaextension

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
	  libglib2.0-0 libsm6 libxext6 libxrender-dev libgl1-mesa-dev \
	  libgomp1 libprotobuf-dev wget \
    && pip install -U pip \
	&& pip install grpcio grpcio-tools opencv-python onnxruntime \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN wget https://media.githubusercontent.com/media/onnx/models/master/vision/object_detection_segmentation/yolov3/model/yolov3-10.onnx -q --show-progress --progress=bar:force 2>&1 \
    && wget https://raw.githubusercontent.com/qqwweee/keras-yolo3/master/model_data/coco_classes.txt -q --show-progress --progress=bar:force 2>&1

COPY server/* ./
COPY lib/* ./

CMD ["python", "server.py", "-p", "44000"]