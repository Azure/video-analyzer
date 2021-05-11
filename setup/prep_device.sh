#!/usr/bin/env bash

##################################################################################################

# This script creates folders and downloads the media samples needed for running AVA             #

##################################################################################################

sudo groupadd -g 1010 localusergroup
sudo useradd --home-dir /home/avaedgeuser --uid 1010 --gid 1010 avaedgeuser
sudo mkdir -p /home/avaedgeuser

sudo mkdir -p /home/avaedgeuser/samples
sudo mkdir -p /home/avaedgeuser/samples/input

sudo curl https://lvamedia.blob.core.windows.net/public/camera-300s.mkv --output /home/avaedgeuser/samples/input/camera-300s.mkv
sudo curl https://lvamedia.blob.core.windows.net/public/lots_284.mkv --output /home/avaedgeuser/samples/input/lots_284.mkv
sudo curl https://lvamedia.blob.core.windows.net/public/lots_015.mkv --output /home/avaedgeuser/samples/input/lots_015.mkv
sudo curl https://lvamedia.blob.core.windows.net/public/t2.mkv --output /home/avaedgeuser/samples/input/t2.mkv

sudo mkdir -p /var/lib/videoanalyzer
sudo mkdir -p /var/media

sudo chown -R avaedgeuser:localusergroup /var/lib/videoanalyzer/
sudo chown -R avaedgeuser:localusergroup /var/media/

sudo chown -R avaedgeuser:localusergroup /home/avaedgeuser/