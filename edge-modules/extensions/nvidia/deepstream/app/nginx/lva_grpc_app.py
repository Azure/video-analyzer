# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from PIL import Image, ImageDraw, ImageFont
import numpy as np

import io
import json
#import os
#from datetime import datetime
import requests

# Imports for the REST API
from flask import Flask, request, jsonify, Response     

app = Flask(__name__)

# / routes to the default function which returns 'Hello World'
@app.route('/', methods=['GET'])
def defaultPage():
    return Response(response='Hello', status=200)

@app.route('/stream/<id>')
def stream(id):
    respBody = ("<html>"
                "<h1>MJPEG stream</h1>"
                "<img src=\"/mjpeg/" + id + "\"/>"
                "</html>")

    return Response(respBody, status= 200)



if __name__ == '__main__':
    # Run the server
    app.run(host='0.0.0.0', port=8888)