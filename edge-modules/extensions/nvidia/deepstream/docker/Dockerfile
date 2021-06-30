FROM nvcr.io/nvidia/deepstream:5.1-21.02-samples

USER root

# Copy AVA extension specific files
RUN mkdir /app
COPY ./app/*.py /app/
COPY ./app/grpc-autogen/*.py /app/
COPY ./app/gst-extension/*.* /app/
COPY ./app/config/*.* /app/

# Install gstreamer-1.0-dev
RUN apt-get update -y && \
    apt-get -y install cmake && \
    apt-get install -y --no-install-recommends build-essential && \
    apt-get install -y --no-install-recommends libgstreamer1.0-dev && \
    apt-get install -y python3-pip

# Build AVA GST library
RUN mkdir -p /app/build && \
    cd /app/build && \
    cmake .. && \
    make

RUN apt-get -y install python3-gst-1.0

# Install required python packages 
RUN pip3 install requests pyyaml protobuf grpcio && \
    apt-get clean

# Install additional python packages
RUN pip3 install numpy flask pillow gunicorn && \
    apt-get clean

# Install runit, nginx
RUN apt-get update -y && \
    apt-get install --no-install-recommends -y wget runit nginx

# Install Nchan module. For details goto http://nchan.io
RUN apt-get update -y && \
    apt-get install -y libnginx-mod-nchan

# Copy nginx config file
COPY ./app/nginx/grpc_app.conf /etc/nginx/sites-available

# Copy flask app
COPY ./app/nginx/grpc_app.py /app

# Setup runit file for nginx and gunicorn
RUN mkdir /var/runit && \
    mkdir /var/runit/nginx && \
    /bin/bash -c "echo -e '"'#!/bin/bash\nexec nginx -g "daemon off;"\n'"' > /var/runit/nginx/run" && \
    chmod +x /var/runit/nginx/run && \
    ln -s /etc/nginx/sites-available/grpc_app.conf /etc/nginx/sites-enabled/ && \
    rm -rf /etc/nginx/sites-enabled/default && \
    mkdir /var/runit/gunicorn && \
    /bin/bash -c "echo -e '"'#!/bin/bash\nexec gunicorn -b 127.0.0.1:8000 --chdir /app grpc_app:app\n'"' > /var/runit/gunicorn/run" && \
    chmod +x /var/runit/gunicorn/run

EXPOSE 80
EXPOSE 5001

# Starts the AVA gRPC extension server
WORKDIR /app
COPY ./app/start.sh /app
RUN chmod +x /app/start.sh
CMD exec /app/start.sh