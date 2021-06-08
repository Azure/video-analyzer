# Continuous video recording to an Azure Video Analyzer Video

This topology enables you to capture video from an RTSP-capable camera and continuously record it to an Azure Video Analyzer Video. You can read more about the continuous video recording scenario in [this](https://docs.microsoft.com/en-us/azure/azure-video-analyzer/video-analyzer-docs/continuous-video-recording) documentation page. This topology is also used in [this](https://docs.microsoft.com/en-us/azure/azure-video-analyzer/video-analyzer-docs/use-continuous-video-recording) tutorial.

In the topology, you can see that it uses
* **segmentLength** of PT0M30S or 30 seconds, which means the edge module waits until at least 30 seconds of the video has been aggregated before it uploads it to the Asset. Increasing the value of segmentLength has the benefit of further lowering your storage transaction costs. However, it will increase the latency for playback of the video through Azure Media Services.
* **outputSelectors** that is filtering out the audio from the rtsp source camera and sending only the video frames to the Video sink.

<br>
<p align="center">
  <img src="./topology.png" title="Continuous video recording to AVA Video Sink"/>
</p>
<br>
