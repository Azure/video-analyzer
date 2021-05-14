import threading
from PIL import Image
import numpy as np
import io
import json
import logging
import linecache
import sys
from score import MLModel, PrintGetExceptionDetails
from flask import Flask, request, jsonify, Response

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
inferenceEngine = MLModel()

@app.route("/score", methods = ['POST'])
def scoreRRS():
    global inferenceEngine

    try:
        # get request as byte stream
        imageData = io.BytesIO(request.get_data())

        # load the image
        pilImage = Image.open(imageData)


        # Infer Image
        detectedObjects = inferenceEngine.Score(pilImage)

        if len(detectedObjects) > 0:
            respBody = {                    
                        "inferences" : detectedObjects
                    }

            respBody = json.dumps(respBody)
            
            logging.info("[LVAX] Sending response.")
            return Response(respBody, status= 200, mimetype ='application/json')
        else:
            logging.info("[LVAX] Sending empty response.")
            return Response(status= 204)

    except:
        PrintGetExceptionDetails()
        return Response(response='Exception occured while processing the image.', status=500)
    
@app.route("/")
def healthy():
    return "Healthy"
    
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8888)
