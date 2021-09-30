# YOLOv3 ONNX GPU models with gRPC

The following instructions will enable you to build a Docker container with a [YOLOv3](http://pjreddie.com/darknet/yolo/) [ONNX](http://onnx.ai/) model running behind a gRPC endpoint. If the YOLOv3 is used in a composite live pipeline, it will use the configured inference confidence to determine whether to run inferences using the YOLOv3 or return the inference results from the upstream module. You can specify the inference confidence by passing the -c parameter, by default the inference confidence is set to 0.75.


## Contributions needed

* Improved logging


## Prerequisites

1. [Install Docker](http://docs.docker.com/docker-for-windows/install/) on your machine
2. Install [curl](http://curl.haxx.se/)

## Building the Docker container

To build the container image locally, run the following Docker command from a terminal in that directory. The process should take a few minutes to complete. 

YOLOv3:
```bash
    docker build -f Dockerfile . -t avaextension:grpc-yolov3-gpu-onnx-v1.0
```

> <span> [!TIP] </span>  
> If you do not wish to build the local Dockerfile, you may pull it off of Microsoft Container Registry and skip the following step <br>
> `docker run --name my_yolo_container --runtime nvidia -p 8080:80 -d  -i mcr.microsoft.com/ava-utilities/avaextension:grpc-yolov3-gpu-onnx-v1.0`

## Running and testing
Please see [this](https://aka.ms/ava-grpc-quickstart) quickstart.

**Note:** This container requires a GPU optimized VM with CUDA drivers installed in order to run. 

### Select the VM size:
[GPU optimized virtual machine sizes](https://docs.microsoft.com/en-us/azure/virtual-machines/sizes-gpu)

### Installing CUDA drivers:
* Set up Nvidia container toolkit: [Installation Guide — NVIDIA Cloud Native Technologies documentation](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#setting-up-nvidia-container-toolkit)

* For N-series VMs: [NVIDIA GPU Driver Extension for Linux](https://docs.microsoft.com/en-us/azure/virtual-machines/extensions/hpccompute-gpu-linux)

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
