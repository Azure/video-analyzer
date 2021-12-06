# Event-based video recording to AVA Video based on events from external AI

This topology enables you to perform event-based recording. When an event of interest is detected by the external AI service, those events are published to the IoT Edge Hub. In addition, the events are used to trigger the signal gate processor node which results in the appending of new clips to the Azure Video Analyzer video, corresponding to when the event of interest was detected.

<br>
<p align="center">
  <img src="./topology.png" title="Event-based video recording to AVA Video based on events from external AI"/>
</p>
<br>
