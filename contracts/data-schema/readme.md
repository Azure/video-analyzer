# Live Video Analytics Inference Data Schema

As discussed in the [concept](https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/media-graph-extension-concept) document, you can use a graph extension node to send video frames from the Live Video Analytics on IoT Edge module to an endpoint. This endpoint can expose AI models, image processing techniques, etc. If the former, then the endpoint should return the inference results using the defined [object model](https://docs.microsoft.com/azure/media-services/live-video-analytics-edge/inference-metadata-schema). You can use the JSON schema provided here in order to validate the results against the model.

