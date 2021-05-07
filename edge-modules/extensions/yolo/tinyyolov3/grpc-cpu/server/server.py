import sys
import os
#sys.path.insert(0, '../lib')

import logging

from arguments import ArgumentParser, ArgumentsType
from exception_handler import PrintGetExceptionDetails
from inference_engine import  InferenceEngine

import grpc
import extension_pb2_grpc
from concurrent import futures

# Main thread
def Main():
    try:
        # Get application arguments
        ap = ArgumentParser(ArgumentsType.SERVER)

        # Get port number
        grpcServerPort = ap.GetGrpcServerPort()
        logging.info('gRPC server port: {0}'.format(grpcServerPort))

        # create gRPC server and start running
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=3))
        extension_pb2_grpc.add_MediaGraphExtensionServicer_to_server(InferenceEngine(), server)
        server.add_insecure_port(f'[::]:{grpcServerPort}')
        server.start()
        server.wait_for_termination()

    except:
        PrintGetExceptionDetails()
        exit(-1)

if __name__ == "__main__": 
    logging_level = logging.DEBUG if os.getenv('DEBUG') else logging.INFO

    # Set logging parameters
    logging.basicConfig(
        level=logging_level,
        format='[AVAX] [%(asctime)-15s] [%(threadName)-12.12s] [%(levelname)s]: %(message)s',
        handlers=[
            #logging.FileHandler(LOG_FILE_NAME),     # write in a log file
            logging.StreamHandler(sys.stdout)       # write in stdout
        ]
    )

    # Call Main logic
    Main()