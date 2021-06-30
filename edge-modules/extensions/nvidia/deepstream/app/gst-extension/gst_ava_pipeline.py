import os
import random
from random import randint
import numpy as np
import time
import gi
import io
from io import BytesIO
import logging

from PIL import Image, ImageDraw, ImageFont
import math
import requests

gi.require_version('Gst', '1.0')
gi.require_version('GstApp', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import GObject, Gst, GstVideo

from gst_ava_message import add_message, remove_message, get_message
from exception_handler import PrintGetExceptionDetails
import pyds
import inferencing_pb2
import media_pb2
import extension_pb2
import configparser
import platform

PGIE_CLASS_ID_VEHICLE_COLOR = 2
PGIE_CLASS_ID_VEHICLE_TYPE = 3

GObject.threads_init()
Gst.init(None)

def has_flag(value: GstVideo.VideoFormatFlags,
             flag: GstVideo.VideoFormatFlags) -> bool:

    # in VideoFormatFlags each new value is 1 << 2**{0...8}
    return bool(value & (1 << max(1, math.ceil(math.log2(int(flag))))))

def get_num_channels(fmt: GstVideo.VideoFormat) -> int:
	"""
		-1: means complex format (YUV, ...)
	"""
	frmt_info = GstVideo.VideoFormat.get_info(fmt)
	
	# temporal fix
	if fmt == GstVideo.VideoFormat.BGRX:
		return 4
	
	if has_flag(frmt_info.flags, GstVideo.VideoFormatFlags.ALPHA):
		return 4

	if has_flag(frmt_info.flags, GstVideo.VideoFormatFlags.RGB):
		return 3

	if has_flag(frmt_info.flags, GstVideo.VideoFormatFlags.GRAY):
		return 1

	return -1


class Gst_Ava_Pipeline:
	def __init__(self, msgQueue, graphName, width, height):
		self.msgQueue = msgQueue
		self.graphName = graphName
		self.trackinEnabled = False
		self.is_push_buffer_allowed = None
		self._mainloop = GObject.MainLoop()

		# Set memory type depending platform (T4 or Jetson)
		nv_memory_type = 1 if (platform.uname().machine == 'x86_64') else 4

		configFile = os.environ.get('GST_CONFIG_FILE')
		if (configFile is None):
			configFile = "inference.txt"	
		
		trackerFile = os.environ.get('GST_TRACKER_FILE')

		classificationFile = os.environ.get('GST_CLASSIFICATION_FILES')
		
		pipelineHeader = "appsrc name=avasource ! videoconvert ! nvvideoconvert nvbuf-memory-type={0} ! capsfilter caps=video/x-raw(memory:NVMM) ! m.sink_0 nvstreammux name=m batch-size=1 width={1} height={2} batched-push-timeout=33000 nvbuf-memory-type={0} ! nvinfer name=primary-inference config-file-path={3} ! ".format(nv_memory_type, width, height, configFile)
		
		pipelineTracker = ""
		
		if(trackerFile is not None):
			#Set properties of tracker
			self.trackinEnabled = True
			config = configparser.ConfigParser()
			config.read(trackerFile)
			config.sections()

			pipelineTracker = "nvtracker "
			for key in config['tracker']:
				if key == 'tracker-width':
					pipelineTracker += 'tracker-width={} '.format(config.getint('tracker', key))
				if key == 'tracker-height':
					pipelineTracker += 'tracker-height={} '.format(config.getint('tracker', key))
				if key == 'gpu-id':
					pipelineTracker += 'gpu-id={} '.format(config.getint('tracker', key))
				if key == 'll-lib-file':
					pipelineTracker += 'll-lib-file={} '.format(config.get('tracker', key))
				if key == 'll-config-file':
					pipelineTracker += 'll-config-file={} '.format(config.get('tracker', key))
				if key == 'enable-batch-process':
					pipelineTracker += 'enable-batch-process={} '.format(config.getint('tracker', key))
				if key == 'enable-past-frame':
					pipelineTracker += 'enable-past-frame={} '.format(config.getint('tracker', key))
				if key == 'useBufferedOutput':
					pipelineTracker += 'useBufferedOutput={} '.format(config.getint('tracker', key))
		
			pipelineTracker += "!"
		
		pipelineClassifiers = ""
		
		if (classificationFile is not None):
			for file in classificationFile.split(','):
				pipelineClassifiers += " nvinfer config-file-path={} !".format(file)

		pipelineFooter = " nvvideoconvert name=converter nvbuf-memory-type={} ! videoconvert ! video/x-raw,format=RGB ! appsink name=avasink".format(nv_memory_type)
		
		pipeline = pipelineHeader + pipelineTracker + pipelineClassifiers + pipelineFooter

		self.MJPEGOutput = os.environ.get('MJPEG_OUTPUT')

		print('graphName = {}, width = {}, height = {}, configuration: {}'.format(graphName, width, height, configFile))
		logging.info('Gst pipeline\n' + pipeline)
		
		self._pipeline = Gst.parse_launch(pipeline)

		self._src = self._pipeline.get_by_name('avasource')
		self._src.connect('need-data', self.start_feed)
		self._src.connect('enough-data', self.stop_feed)

		self._src.set_property('format', 'time')
		self._src.set_property('do-timestamp', True)

		self._sink = self._pipeline.get_by_name('avasink')
		self._sink.set_property("emit-signals", True)
		self._sink.set_property("max-buffers", 1)		

		self._sink.connect("new-sample", self.on_new_sample)

	def get_ava_MediaStreamMessage(self, buffer, gst_ava_message, ih, iw):

		msg = extension_pb2.MediaStreamMessage()		
		msg.ack_sequence_number = gst_ava_message.sequence_number
		msg.media_sample.timestamp = gst_ava_message.timestamp
			
		# # Retrieve batch metadata from the gst_buffer
		# # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
		# # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
		batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(buffer))

		frame = batch_meta.frame_meta_list
		
		while frame is not None:
			try:
				# Note that frame.data needs a cast to pyds.NvDsFrameMeta
				# The casting is done by pyds.NvDsFrameMeta.cast()
				# The casting also keeps ownership of the underlying memory
				# in the C code, so the Python garbage collector will leave
				# it alone.
				frame_meta = pyds.NvDsFrameMeta.cast(frame.data)
				objInference = frame_meta.obj_meta_list
				frameWidth = frame_meta.source_frame_width
				frameHeight = frame_meta.source_frame_height
				# iterate through objects 
				while objInference is not None:
					try: 
						# Casting objInference.data to pyds.NvDsObjectMeta
						obj_meta=pyds.NvDsObjectMeta.cast(objInference.data)
					except StopIteration:
						break

					inference = msg.media_sample.inferences.add()	

					attributes = []
					obj_label = None
					obj_confidence = 0
					obj_left = 0
					obj_width = 0
					obj_top = 0
					obj_width = 0

					color = ''
					# Classification 
					attribute = None
					if(obj_meta.class_id == 0 and obj_meta.classifier_meta_list is not None):
						classifier_meta = obj_meta.classifier_meta_list
						while classifier_meta is not None:
							classifierItem = pyds.NvDsClassifierMeta.cast(classifier_meta.data)
							if(classifierItem is not None):
								label_meta = classifierItem.label_info_list
								while label_meta is not None:
									labelItem = pyds.NvDsLabelInfo.cast(label_meta.data)
									prob = round(labelItem.result_prob, 2)
									attrValue = labelItem.result_label

									attrName = 'unknown'
									if(classifierItem.unique_component_id == PGIE_CLASS_ID_VEHICLE_COLOR):
										attrName = 'color'
									else:
										attrName = 'type'

									attributes.append([attrName, attrValue, prob])
									
									try: 
										label_meta=label_meta.next
									except StopIteration:
										break

							try: 
								classifier_meta=classifier_meta.next
							except StopIteration:
								break
							
					rect_params=obj_meta.rect_params
					top=int(rect_params.top)
					left=int(rect_params.left)
					width=int(rect_params.width)
					height=int(rect_params.height)
					obj_confidence = obj_meta.confidence
					obj_label = obj_meta.obj_label
					
					obj_left = left / iw
					obj_top = top / ih
					obj_width = width/ iw
					obj_height = height / ih
					obj_id = None

					# Tracking: Active tracking bbox information
					if(self.trackinEnabled):
						obj_id = obj_meta.object_id
						obj_active_tracking = obj_meta.tracker_bbox_info
						tracking_coord = obj_active_tracking.org_bbox_coords
						if(tracking_coord is not None and tracking_coord.left > 0 and tracking_coord.width > 0 and tracking_coord.top > 0 and tracking_coord.height > 0):
							obj_left = tracking_coord.left / iw
							obj_top = tracking_coord.top / ih
							obj_width = tracking_coord.width/ iw
							obj_height = tracking_coord.height / ih

					inference.type = inferencing_pb2.Inference.InferenceType.ENTITY

					if obj_label is not None:
						try:
							entity = inferencing_pb2.Entity(
													tag = inferencing_pb2.Tag(
														value = obj_label,
														confidence = obj_confidence
													),
													box = inferencing_pb2.Rectangle(
														l = obj_left,
														t = obj_top,
														w = obj_width,
														h = obj_height
													)												
												)

							if(self.trackinEnabled and obj_id is not None):
								entity.id = str(obj_id)

							for attr in attributes:
								attribute = inferencing_pb2.Attribute(
									name = attr[0],
									value = attr[1],
									confidence = attr[2]
								)

								entity.attributes.append(attribute)
						except:
							PrintGetExceptionDetails()
										
						inference.entity.CopyFrom(entity)

					try: 
						objInference=objInference.next
					except StopIteration:
						break

			except StopIteration:
				break

			try:
				frame = frame.next
			except StopIteration:
				break

		return msg		

	def pushImageWithInference(self, sample, inferences):
		try:
			buffer = sample.get_buffer()	
			caps_format = sample.get_caps().get_structure(0)  

			#print(caps_format.get_value('format'))
			video_format = GstVideo.VideoFormat.from_string(caps_format.get_value('format'))
			w, h = caps_format.get_value('width'), caps_format.get_value('height')
			frmt_info = GstVideo.VideoFormat.get_info(video_format)
			
			c = get_num_channels(video_format)	
			buffer_size = buffer.get_size()
			shape = (h, w, c) if (h * w * c == buffer_size) else buffer_size
			#print (shape)
			array = np.ndarray(shape=shape, buffer=buffer.extract_dup(0, buffer_size), dtype=np.uint8) 

			im = Image.fromarray(array)	
			draw = ImageDraw.Draw(im)
			textfont = ImageFont.load_default()

			for inference in inferences:
				x1 = inference.entity.box.l
				y1 = inference.entity.box.t
				x2 = inference.entity.box.w
				y2 = inference.entity.box.h

				x1 = x1 * w
				y1 = y1 * h
				x2 = (x2 * w) + x1
				y2 = (y2 * h) + y1
				objClass = str(inference.entity.tag.value)

				draw.rectangle((x1, y1, x2, y2), outline = 'blue', width = 1)				
				draw.text((x1, y1-10), objClass, fill = "white", font = textfont)

			imgBuf = io.BytesIO()
			im.save(imgBuf, format='JPEG')
			#im.save('test.jpeg')

			# post the image with bounding boxes so that it can be viewed as an MJPEG stream
			postData = b'--boundary\r\n' + b'Content-Type: image/jpeg\r\n\r\n' + imgBuf.getvalue() + b'\r\n'
			requests.post('http://127.0.0.1:80/mjpeg_pub/' + self.graphName, data = postData)		
		except:
			PrintGetExceptionDetails()

	def on_new_sample(self, appsink):
		try:
			sample = appsink.emit("pull-sample")
			buffer = sample.get_buffer()	
			
			caps = sample.get_caps()		

			height = caps.get_structure(0).get_value('height')
			width = caps.get_structure(0).get_value('width')						
			
			gst_ava_message = get_message(buffer)
			
			msg = self.get_ava_MediaStreamMessage(buffer, gst_ava_message, height, width)

			if msg is None:
				logging.info('media stream message is None')
			else:				
				if (self.msgQueue is not None):
					if (self.msgQueue.full()):
						logging.info("queue is full")
						self.msgQueue.get()

					self.msgQueue.put(msg)				
				else:
					logging.info("msgQueue is null")
			
			remove_message(buffer)

			if self.MJPEGOutput is not None:
				self.pushImageWithInference(sample, msg.media_sample.inferences)
		except:
			PrintGetExceptionDetails()

		return Gst.FlowReturn.OK		

	def start_feed(self, src, length):		
		self.is_push_buffer_allowed = True

	def stop_feed(self, src):		
		self.is_push_buffer_allowed = False

	def play(self):
		self._pipeline.set_state(Gst.State.PLAYING)

	def stop(self):
		self._pipeline.set_state(Gst.State.NULL)

	def run(self):		
		self._mainloop.run()

	def push(self, imgRawBytes, caps, seq_num, timestamp):
		retVal = False

		if self.is_push_buffer_allowed:
			bufferLength = len(imgRawBytes)
			
			# Allocate GstBuffer			
			buf = Gst.Buffer.new_allocate(None, bufferLength, None)
			buf.fill(0, imgRawBytes)

			# Write message to buffer
			add_message(buf, seq_num, timestamp)
			
			# Create GstSample
			sample = Gst.Sample.new(buf, Gst.caps_from_string(caps), None, None)

			# Push sample on appsrc
			gst_flow_return = self._src.emit('push-sample', sample)

			if gst_flow_return != Gst.FlowReturn.OK:
				logging.info('We got some error, stop sending data')
			else:
				retVal = True
		else:
			logging.info('Cannot push buffer forward and hence dropping frame with seq_num ' + str(seq_num))

		return retVal