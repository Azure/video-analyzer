# Azure Video Analyzer Inference Data Schema

As discussed in the [concept](https://docs.microsoft.com/azure/azure-video-analyzer/video-analyzer-docs/pipeline-extension) document, you can use a pipeline extension node to send video frames from the Azure Video Analyzer edge module to an endpoint. This endpoint can expose AI models, image processing techniques, etc. If the former, then the endpoint should return the inference results using the defined [object model](https://docs.microsoft.com/azure/azure-video-analyzer/video-analyzer-docs/inference-metadata-schema). You can use the JSON schema provided here in order to validate the results against the model.

