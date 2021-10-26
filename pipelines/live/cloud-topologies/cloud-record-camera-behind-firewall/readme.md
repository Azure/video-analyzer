# Capture, record, and stream live video from a cameras behind a firewall

This topology enables you to capture, record, and stream live video from an RTSP-capable camera that is behind a firewall, using Azure Video Analyzer service. You can read more about the scenario in [this](https://docs.microsoft.com/azure/azure-video-analyzer/video-analyzer-docs/cloud/use-remote-device-adapter) article.

In the topology, you can see that it uses
* **segmentLength** of PT30S or 30 seconds, which means the service waits until at least 30 seconds of the video has been aggregated before it records it to Azure storage. Increasing the value of segmentLength has the benefit of further lowering your storage transaction costs. However, this will mean an increase in the delay before you can watch recorded content.
* **retentionPeriod** of 30 days, which means the service will periodically scan the video archive and delete content older than 30 days

The RTSP credentials, the IoT Hub device ID, and the video resource name (to which content will be archived) are all parametrized - meaning you would specify unique values for these for each unique camera when creating a live pipeline under this topology. The IoT Hub name is also parametrized since it cannot be restricted to a common string across all users.

<br>
<p align="center">
  <img src="./topology.png" title="Capture, record, and stream live video from a camera behind a firewall"/>
</p>
<br>
