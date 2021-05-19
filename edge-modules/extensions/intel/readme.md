# Intel module extensions to be used with Azure Video Analyzer

This folder contains a set of IoT Edge modules from Intel that can be used in conjunction with Azure Video Analyzer.

The modules act as AI inference servers. They implement the Video Analyzer [gRPC extension protocol](https://docs.microsoft.com/azure/azure-video-analyzer/video-analyzer-docs/grpc-extension-protocol) and [HTTP extension protocol](https://docs.microsoft.com/azure/azure-video-analyzer/video-analyzer-docs/http-extension-protocol). This enables you to implement live video workflows, shown in tutorials [here](https://docs.microsoft.com/azure/azure-video-analyzer/video-analyzer-docs/use-intel-openvino-tutorial) and [here](https://docs.microsoft.com/azure/azure-video-analyzer/video-analyzer-docs/use-intel-grpc-video-analytics-serving-tutorial).

## Contents

| Folders | Description |
|---------|-------------|
|dl-streamer|Docker container to build the OpenVINO™ DL Streamer - Edge AI Extension |
|ovms|Docker container to build the OpenVINO™ Model Server (OVMS) |
