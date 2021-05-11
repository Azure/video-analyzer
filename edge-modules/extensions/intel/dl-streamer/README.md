# Intel OpenVINO DL Streamer - Edge AI Extension

The [OpenVINO™ DL Streamer - Edge AI Extension](https://aka.ms/ava-intel-openvino-dl-streamer) module is a microservice based on Intel’s [Video Analytics Serving (VA Serving)](https://github.com/intel/video-analytics-serving/blob/master/README.md) that serves video analytics pipelines built with OpenVINO™ DL Streamer. Developers can send decoded video frames to the AI extension module which performs detection, classification, or tracking and returns the results. The AI extension module exposes gRPC APIs that are compatible with video analytics platforms like Azure Video Analyzer edge module from Microsoft.

In order to build complex, high-performance live video analytics solutions, the Azure Video Analyzer edge module module should be paired with a powerful inference engine that can leverage the scale at the edge. In this tutorial, inference requests are sent to the Intel OpenVINO™ DL Streamer – Edge AI Extension, an Edge module that has been designed to work with Azure Video Analyzer edge module.

## Building the Docker container

To build the container image please see these [instructions](https://github.com/intel/video-analytics-serving/tree/master/docker).

> <span> [!TIP] </span>  
> If you do not wish to build the local Dockerfile, you may pull it off of the [Azure Marketplace](https://aka.ms/ava-intel-openvino-dl-streamer-offer)

## Running and testing
A full fledged [tutorial](https://aka.ms/ava-intel-openvino-dl-streamer) is available to learn more about how to use this module.


