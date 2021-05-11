# RTSP Simulator using Live555 Media Server

The following instructions enable using [Live555 Media Server](http://www.live555.com/mediaServer/) as a RTSP simulator in a docker container.

Note: References to third-party software in this repo are for informational and convenience purposes only. Microsoft does not endorse nor provide rights for the third-party software. For more information on third-party software please see [Live555 Media Server](http://www.live555.com/mediaServer/).

## Prerequisites

1. [Install Docker](http://docs.docker.com/docker-for-windows/install/) on your machine
2. Install a RTSP player such as [VLC Media Player](http://www.videolan.org/vlc/) on your machine. This will be useful for testing.

## Building the docker container

Build the container image (should take around 10 minutes or less) by running the following docker command from a command window in that directory

```powershell
    docker build . -t live555:latest
```

The build may generate warnings, but they should not prevent the server from working.

## Running and Testing

Run the container using the following docker command

```powershell
    docker run -p 554:554  -i live555:latest
```

Test the stream using a RTSP media player such as [VLC media player](https://www.videolan.org/vlc/)

```powershell
    vlc rtsp://localhost:554/media/win10.mkv
```

You can also run the container while mounting the /media folder in the container to a local media folder (e.g. /home/xyz/Videos/) on your host machine

```powershell
    # This exposes the 554 port on the host and mounts the local media folder to the /media folder in the server
    docker run -p 554:554 -v <local_media_folder>:/live/mediaServer/media -i live555:latest 
```

Test the stream

```powershell
    vlc rtsp://localhost:554/media/<my-media-file>
```

my-media-file refers to a media file in your local_media_folder. 

Note that only file formats supported by Live555 will work. Further, in order to use Live555 with Live Video Analytics, we recommend that you use an MKV, MPEG-TS, or MPG file with H.264 video (and, optionally, AAC audio).


Another option is to run the container on Azure Container Instance while mounting the /media folder inte container to Azure Files Share

```powershell
#set script parameters
resource_group=change_to_your_resource_group_name
location=change_to_your_azure_region
storage_account_name=change_to_your_account_name

#create azure storage account
az storage account create -n $storage_account_name -g $resource_group -l $location

#get storage primary key
storage_key=$(az storage account keys list -n $storage_account_name --query [0].value
 -o tsv)

#create file share
az storage share create -n media --account-name $storage_account_name

#create container instance mounted to your azure files share
container_name=change_to_your_container_name
az container create \
    --resource-group $resource_group \
    --name $container_name \
    --image mcr.microsoft.com/lva-utilities/rtspsim-live555:1.2 \
    --dns-name-label $container_name \
    --ports 554 \
    --azure-file-volume-account-name $storage_account_name \
    --azure-file-volume-account-key $storage_key \
    --azure-file-volume-share-name media \
    --azure-file-volume-mount-path /live/mediaServer/media \
    --query ipAddress.fqdn \
    -o tsv

```
after running the last command you should see your container FQDN with the following format: "yourcontainerdns.yourregion.azurecontainer.io".

upload some video files into the file share using Azure Storage Explorer / azcopy / Azure portal.

open vlc player with the following uri: 

rtsp://<container_fqdn>:554/media/<my-media-file>

example:

rtsp://yourcontainerdns.yourregion.azurecontainer.io:554/media/camera-300s.mkv

## Cleanup

Once you are done, stop the docker container by executing the following commands

```powershell
    docker ps -a
```

This will enumerate all the containers. Copy the container id of the live555:latest container

```powershell
    docker stop <container-id>
```

Once stopped, you can remove the container with the following command

```powershell
    docker rm <container-id>
```

## Upload docker image to Azure container registry

Follow the instructions in [Push and Pull Docker images  - Azure Container Registry](http://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-docker-cli) to save your image in your private Azure container registry for later use on another machine.

Note: In the next section, you will be using Azure portal in order to deploy the container as an IoT Edge module. The Azure portal today requires you to provide a user name as password to enable IoT Edge to connect to your container registry. A quick way to accomplish this is by creating an [Admin Account](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-authentication#admin-account) for your container registry.

## Deploy as an Azure IoT Edge module

Follow the instructions in [Deploy module from Azure portal](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-deploy-modules-portal) to deploy the container image (in your private registry) as an IoT Edge module (use the IoT Edge module option). In step 5 of this [section](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-deploy-modules-portal#configure-a-deployment-manifest), use the admin account credentials created in the previous section.

To play videos from an RTSP client, you will need to bind the container port to a host port and mount a local media folder to the /media folder. You can do this by specifying the following in the "Container Create Options"

```JSON
    {
        "HostConfig": {
            "Binds": [
                "<local_media_folder>:/live/mediaServer/media"
            ],
           "PortBindings": {
                "554/tcp": [
                    {
                        "HostPort": "5001"
                    }
                ]
           }
        }
     }
```

Note: after you have reviewed and created the IoT Edge module, on your Edge device, you can run "sudo docker ps -a" to list the available containers. The "live555" container should be in that list, and it should have an entry such as "0.0.0.0:5001->554/tcp" under the PORTS column.

You can now play a video file, in the appropriate format, (located in local_media_folder) on the IoT Edge device using a RTSP media player such as [VLC media player](https://www.videolan.org/vlc/)

```powershell
    vlc rtsp://localhost:5001/media/<my-media>
```
