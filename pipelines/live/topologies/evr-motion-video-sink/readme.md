# Event-based video recording to Video Sink based on motion events

This topology enables you to perform event-based recording. The video from an RTSP-capable camera is analyzed for the presence of motion. When motion is detected, those events are published to the IoT Edge Hub. In addition, the motion events are used to trigger the signal gate processor node which will send frames to the video sink node when motion is detected. As a result, new video clips are appended to the video sink containing clips where motion was detected. You can see how this topology is used in [this](https://docs.microsoft.com/azure/azure-video-analyzer/video-analyzer-docs/detect-motion-record-video-clips-media-services-quickstart) quickstart.

<br>
<p align="center">
  <img src="./topology.png" title="Event-based video recording to Video Sink based on motion events"/>
</p>
<br>
