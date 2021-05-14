import threading
from PIL import Image
import numpy as np
import io
import tensorflow as tf
import json
import logging
import os
import linecache
import sys
import math
from object_detection import ObjectDetection

logging.basicConfig(level=logging.DEBUG)

def PrintGetExceptionDetails():
    exType, exValue, exTraceback = sys.exc_info()

    tbFrame = exTraceback.tb_frame
    lineNo = exTraceback.tb_lineno
    fileName = tbFrame.f_code.co_filename

    linecache.checkcache(fileName)
    line = linecache.getline(fileName, lineNo, tbFrame.f_globals)

    exMessage = '[AVAX] Exception:\n\tFile name: {0}\n\tLine number: {1}\n\tLine: {2}\n\tValue: {3}'.format(fileName, lineNo, line.strip(), exValue)

    logging.info(exMessage)

class TFObjectDetection(ObjectDetection):
    """Object Detection class for TensorFlow"""

    def __init__(self, graph_def, labels, prob_threshold, max_detections):
        super(TFObjectDetection, self).__init__(labels, prob_threshold, max_detections)
        self.graph = tf.compat.v1.Graph()
        with self.graph.as_default():
            input_data = tf.compat.v1.placeholder(tf.float32, [1, None, None, 3], name='Placeholder')
            tf.import_graph_def(graph_def, input_map={"Placeholder:0": input_data}, name="")

    def predict(self, preprocessed_image):
        inputs = np.array(preprocessed_image, dtype=np.float)[:, :, (2, 1, 0)]  # RGB -> BGR

        with tf.compat.v1.Session(graph=self.graph) as sess:
            output_tensor = sess.graph.get_tensor_by_name('model_outputs:0')
            outputs = sess.run(output_tensor, {'Placeholder:0': inputs[np.newaxis, ...]})
            return outputs[0]

class MLModel:
    
    def __init__(self):
        try:
            self._modelFileName = 'model.pb'
            self._labelFileName = 'labels.txt'
            self._lock = threading.Lock()
            self.prob_threshold = 0.1
            self.max_detections = 20

            graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(self._modelFileName, 'rb') as f:
                graph_def.ParseFromString(f.read())

            # Load labels
            with open(self._labelFileName, 'r') as f:
                labels = [l.strip() for l in f.readlines()]

            self.od_model = TFObjectDetection(graph_def, labels, self.prob_threshold, self.max_detections)

        except:
            PrintGetExceptionDetails()

 
    def Score(self, pilImage):
        try:
            with self._lock:
                predictions = self.od_model.predict_image(pilImage)

                return predictions

        except:
            PrintGetExceptionDetails()
