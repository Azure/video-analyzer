FROM ubuntu:18.04

ARG WORK_DIR=/avaExtension
WORKDIR ${WORK_DIR}

# Copy the app file
COPY . ${WORK_DIR}/
COPY etc /etc

# Install runit, python, nginx, and necessary python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-dev libglib2.0-0 libsm6 libxext6 libxrender-dev nginx supervisor python3-setuptools \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 install --upgrade pip \
    && pip install numpy tensorflow flask pillow gunicorn json-logging-py \
    && apt-get clean \
    && apt-get update && apt-get install -y --no-install-recommends \
    wget runit nginx \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm /etc/nginx/sites-enabled/default \
    && cp /avaExtension/nginx/app /etc/nginx/sites-available/ \
    && ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled/

EXPOSE 80
CMD ["supervisord", "-c", "/avaExtension/etc/supervisord.conf"]
