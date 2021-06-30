import logging
import os
import inferencing_pb2
import media_pb2
import extension_pb2
import extension_pb2_grpc

from queue import Queue
from enum import Enum
from shared_memory import SharedMemoryManager
from exception_handler import PrintGetExceptionDetails
from gst_ava_pipeline import Gst_Ava_Pipeline

# Get debug flag from env variable (Returns None if not set)
# Set this environment variables in the IoTEdge Deployment manifest to activate debugging.
# You should also map the DebugOutputFolder on the host machine to write out the debug frames...
DEBUG = os.getenv('Debug')
DEBUG_OUTPUT_FOLDER = os.getenv('DebugOutputFolder')

class TransferType(Enum):
    BYTES = 1           # Embedded Content
    REFERENCE = 2       # Shared Memory
    HANDLE = 3          # Reserverd...

class State:
    def __init__(self, mediaStreamDescriptor):
        try:
            # media descriptor holding input data format
            self._mediaStreamDescriptor = mediaStreamDescriptor

            # Get how data will be transferred
            if self._mediaStreamDescriptor.WhichOneof("data_transfer_properties") is None:
                self._contentTransferType = TransferType.BYTES
            elif self._mediaStreamDescriptor.HasField("shared_memory_buffer_transfer_properties"):
                self._contentTransferType = TransferType.REFERENCE
            elif self._mediaStreamDescriptor.HasField("shared_memory_segments_transfer_properties"):
                self._contentTransferType = TransferType.HANDLE

            # Setup if shared mem used
            if self._contentTransferType == TransferType.REFERENCE:
                # Create shared memory accessor specific to the client
                self._sharedMemoryManager = SharedMemoryManager(
                    name=self._mediaStreamDescriptor.shared_memory_buffer_transfer_properties.handle_name,
                    size=self._mediaStreamDescriptor.shared_memory_buffer_transfer_properties.length_bytes)
            else:
                self._sharedMemoryManager = None

        except:
            PrintGetExceptionDetails()
            raise

class InferenceServer(extension_pb2_grpc.MediaGraphExtensionServicer):
    def __init__(self):
        return

    def GetDummyMediaStreamMessageResponse(self, dummyValue):
        try:
            ih = 480
            iw = 640

            msg = extension_pb2.MediaStreamMessage()
            inference = msg.media_sample.inferences.add()
            inference.type = inferencing_pb2.Inference.InferenceType.ENTITY
            inference.entity.CopyFrom( inferencing_pb2.Entity(
                                            tag = inferencing_pb2.Tag(
                                                value = dummyValue,
                                                confidence = 0.0
                                            ),
                                            box = inferencing_pb2.Rectangle(
                                                l = 0,
                                                t = 0,
                                                w = iw,
                                                h = ih
                                            )

                                        )
                                    )

            return msg

        except:
            PrintGetExceptionDetails()
            raise


    def ProcessMediaSample(self, clientState, mediaStreamMessageRequest, gst_pipeline):
        retVal = False

        try:
            # Get reference to raw bytes
            if clientState._contentTransferType == TransferType.BYTES:
                rawBytes = memoryview(mediaSample.content_bytes.bytes)
            elif clientState._contentTransferType == TransferType.REFERENCE:
                # Data sent over shared memory buffer
                addressOffset = mediaStreamMessageRequest.media_sample.content_reference.address_offset
                lengthBytes = mediaStreamMessageRequest.media_sample.content_reference.length_bytes
                
                # Get memory reference to (in readonly mode) data sent over shared memory
                rawBytes = clientState._sharedMemoryManager.ReadBytes(addressOffset, lengthBytes)

            # Get encoding details of the media sent by client
            encoding = clientState._mediaStreamDescriptor.media_descriptor.video_frame_sample_format.encoding                        

            # Handle RAW content (Just place holder for the user to handle each variation...)
            if encoding == clientState._mediaStreamDescriptor.media_descriptor.video_frame_sample_format.Encoding.RAW:
                pixelFormat = clientState._mediaStreamDescriptor.media_descriptor.video_frame_sample_format.pixel_format
                capsFormat = None

                if pixelFormat == media_pb2.VideoFrameSampleFormat.PixelFormat.RGBA:
                    capsFormat = 'RGBA'
                elif pixelFormat == media_pb2.VideoFrameSampleFormat.PixelFormat.RGB24:
                    capsFormat = 'RGB'
                elif pixelFormat == media_pb2.VideoFrameSampleFormat.PixelFormat.BGR24:
                    capsFormat = 'BGR'

                width = clientState._mediaStreamDescriptor.media_descriptor.video_frame_sample_format.dimensions.width
                height = clientState._mediaStreamDescriptor.media_descriptor.video_frame_sample_format.dimensions.height

                if capsFormat is not None:
                    caps = ''.join(("video/x-raw,format=",
                            capsFormat,
                            ",width=",
                            str(width),
                            ",height=",
                            str(height)))                                                            
                    
                    retVal = gst_pipeline.push(rawBytes, 
                                                    caps,                                                     
                                                    mediaStreamMessageRequest.sequence_number,
                                                    mediaStreamMessageRequest.media_sample.timestamp)                                        
                
            else:
                logging.info('Sample format is not RAW')
        
        except:
            PrintGetExceptionDetails()
            raise
        
        return retVal

    def ProcessMediaStream(self, requestIterator, context):
        # Below logic can be extended into multi-process (per CPU cores, i.e. in case using CPU inferencing)
        # For simplicity below, we use single process to handle gRPC clients

        # Auto increment counter. Increases per client requests
        responseSeqNum = 1

        # First message from the client is (must be) MediaStreamDescriptor
        mediaStreamMessageRequest = next(requestIterator)

        # Extract message IDs
        requestSeqNum = mediaStreamMessageRequest.sequence_number
        requestAckSeqNum = mediaStreamMessageRequest.ack_sequence_number

        # State object per client       
        clientState = State(mediaStreamMessageRequest.media_stream_descriptor)
        
        logging.info('[Received] SeqNum: {0:07d} | AckNum: {1}\nMediaStreamDescriptor:\n{2}'.format(requestSeqNum, requestAckSeqNum, clientState._mediaStreamDescriptor))

        # First message response ...
        mediaStreamMessage = extension_pb2.MediaStreamMessage(
                                    sequence_number = responseSeqNum,
                                    ack_sequence_number = requestSeqNum,
                                    media_stream_descriptor = extension_pb2.MediaStreamDescriptor(
                                        media_descriptor = media_pb2.MediaDescriptor(
                                            timescale = clientState._mediaStreamDescriptor.media_descriptor.timescale
                                        )
                                    )
                                )
        yield mediaStreamMessage

        width = clientState._mediaStreamDescriptor.media_descriptor.video_frame_sample_format.dimensions.width
        height = clientState._mediaStreamDescriptor.media_descriptor.video_frame_sample_format.dimensions.height

        msgQueue = Queue(maxsize=10)
        gst_pipeline = Gst_Ava_Pipeline(msgQueue, mediaStreamMessageRequest.media_stream_descriptor.graph_identifier.graph_instance_name, width, height)
        gst_pipeline.play()
    

        # Process rest of the MediaStream message sequence
        for mediaStreamMessageRequest in requestIterator:
            try:               
                # Read request id, sent by client
                requestSeqNum = mediaStreamMessageRequest.sequence_number

                           
                logging.info('[Received] SequenceNum: {0:07d}'.format(requestSeqNum))

                # Get media content bytes. (bytes sent over shared memory buffer, segment or inline to message)                
                if (not self.ProcessMediaSample(clientState, mediaStreamMessageRequest, gst_pipeline)):
                    #logging.info('Error in processing media sample with sequence number ' + str(mediaStreamMessageRequest.sequence_number))     
                    
                    responseSeqNum += 1
                    # Respond with message without inferencing
                    mediaStreamMessage = extension_pb2.MediaStreamMessage()     
                    mediaStreamMessage.sequence_number = responseSeqNum
                    mediaStreamMessage.ack_sequence_number = mediaStreamMessageRequest.sequence_number
                    mediaStreamMessage.media_sample.timestamp = mediaStreamMessageRequest.media_sample.timestamp
                    logging.info("empty message for request seq = " + str(mediaStreamMessage.ack_sequence_number) + " response seq = " + str(responseSeqNum))

                    yield mediaStreamMessage

                elif context.is_active():                                                                             
                    while (not msgQueue.empty()):                        
                        mediaStreamMessage = msgQueue.get()
                        responseSeqNum += 1
                        mediaStreamMessage.sequence_number = responseSeqNum

                        logging.info("responding for message with request seq = " + str(mediaStreamMessage.ack_sequence_number) + " response seq = " + str(responseSeqNum))
                        #logging.info(mediaStreamMessage)

                        # yield response                        
                        yield mediaStreamMessage                    
                else:
                    break
            except:
                PrintGetExceptionDetails()

        logging.info('Done processing messages')
        logging.info('MediaStreamDescriptor:\n{0}'.format(clientState._mediaStreamDescriptor))