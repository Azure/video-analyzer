#!/bin/bash
runsvdir /var/runit &
export GST_DEBUG=1
echo 'install new pyds.so'
# Copy nvidia deepstream models
cp /opt/nvidia/deepstream/deepstream-5.1/lib/pyds.so /app
cp /opt/nvidia/deepstream/deepstream-5.1/lib/setup.py /app
cp -r /opt/nvidia/deepstream/deepstream-5.1/samples/models/ /app
python3 setup.py install
python3 main.py -p 5001