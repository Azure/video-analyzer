# Analyzing Live Video with Computer Vision for Spatial Analysis

The video from an RTSP-capable camera is sent to an external module ([spatialAnalysis](https://docs.microsoft.com/azure/cognitive-services/computer-vision/spatial-analysis-operations)) which carries out a supported AI operation. When the criteria defined by the AI operation is met, events are sent to a signal gate processor which opens, sending the frames to an asset sink node. As a result, new Assets are created containing clips where the criteria defined by the AI operation are met. You can read more about how to use Live Video Analytics together with Computer Vision for spatial analysis AI service from Azure Cognitive Services in [this](https://aka.ms/lva-spatial-analysis) documentation page.

<br>
<p align="center">
  <img src="./topology.png" title="Analyzing Live Video with Computer Vision for Spatial Analysis"/>
</p>
<br>
