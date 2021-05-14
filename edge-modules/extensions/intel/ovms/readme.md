# OpenVINO™ Model Server – AI Extension from Intel 

The OpenVINO™ Model Server (OVMS) is an inference server that’s highly optimized for AI vision workloads. OVMS is powered by [OpenVINO™ toolkit](https://software.intel.com/content/www/us/en/develop/tools/openvino-toolkit.html), a high-performance inference engine optimized for Intel® hardware on the Edge. An extension has been added to OVMS for easy exchange of video frames and inference results between the inference server and Azure Video Analyzer edge module, thus empowering you to run any OpenVINO™ toolkit supported model, and select from the wide variety of acceleration mechanisms provided by Intel® hardware. These include CPUs (Atom, Core, Xeon), FPGAs, VPUs.

## Building the Docker container

To build the container image please see these [instructions](https://github.com/openvinotoolkit/model_server/tree/master/extras/ams_wrapper). 

> <span> [!TIP] </span>  
> If you do not wish to build the local Dockerfile, you may pull it off of the [Azure Marketplace](https://aka.ms/ava-intel-ovms)


## Running and testing
A full fledged [tutorial](https://aka.ms/ava-intel-ovms-tutorial) is available to learn more about how to use this module.
