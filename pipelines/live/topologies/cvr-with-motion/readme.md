# Continuous video recording with Motion Detection

This topology enables you to continuously record the video from an RTSP-capable camera to an Azure Media Services Asset. Note that the topology also removes the audio before storing it as an Azure Media Services Asset. You can read more about the relevant settings in [this](https://github.com/Azure/live-video-analytics/blob/master/MediaGraph/topologies/cvr-asset/readme.md) page.

Additionally, the video from the camera is analyzed for the presence of motion. When motion is detected, relevant inferncing events are published to the IoT Edge Hub.


<br>
<p align="center">
  <img src="./topology.png" title="Continuous video recording with Motion Detection"/>
</p>
<br>
