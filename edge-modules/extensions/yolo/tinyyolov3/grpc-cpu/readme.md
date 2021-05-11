# Tiny YOLOv3 ONNX model with gRPC

The following instructions will enable you to build a Docker container with a [Tiny YOLOv3](http://pjreddie.com/darknet/yolo/) [ONNX](http://onnx.ai/) model running behind a gRPC endpoint.


## Contributions needed

* Improved logging


## Prerequisites

1. [Install Docker](http://docs.docker.com/docker-for-windows/install/) on your machine
2. Install [curl](http://curl.haxx.se/)

## Building the Docker container

To build the container image locally, run the following Docker command from a terminal in that directory. The process should take a few minutes to complete. 

YOLOv3:
```bash
    docker build -f Dockerfile . -t avaextension:grpc-tiny-yolov3-onnx-v1.0
```

> <span> [!TIP] </span>  
> If you do not wish to build the local Dockerfile, you may pull it off of Microsoft Container Registry and skip the following step <br>
> `docker run --name my_tiny_yolo_container -p 8080:80 -d  -i mcr.microsoft.com/ava-utilities/avaextension:grpc-yolov3-tiny-onnx-v1.0`

## Running and testing
Please see [this](https://aka.ms/ava-grpc-quickstart) quickstart.

## Compiling the protobuf files for python

Install the protoc tool for python:

```bash
python -m pip install grpcio-tools
```

Use the following command to regenerate the protobuf files using the python protoc complier

```bash
python -m grpc_tools.protoc -I../../../../../../../contracts/grpc ../../../../../../../contracts/grpc/extension.proto --grpc_python_out=lib --python_out=lib
python -m grpc_tools.protoc -I../../../../../../../contracts/grpc ../../../../../../../contracts/grpc/media.proto --python_out=lib
python -m grpc_tools.protoc -I../../../../../../../contracts/grpc ../../../../../../../contracts/grpc/inferencing.proto --python_out=lib
```
