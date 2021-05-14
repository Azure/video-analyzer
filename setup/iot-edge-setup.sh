#!/usr/bin/env bash

####################################################################################################
# This script is designed for use as a deployment script in a template
# https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/deployment-script-template
#
# It expects the following environment variables
# $IOTHUB                   - the name of the IoT Hub where the edge device is registered
# $EDGE_DEVICE              - the name of the edge device
# $AZ_SCRIPTS_OUTPUT_PATH   - file to write output (provided by the deployment script runtime) 
#
####################################################################################################

# automatically install any extensions
az config set extension.use_dynamic_install=yes_without_prompt

# check to see if the device already exists
if test -z "$(az iot hub device-identity list -n $IOTHUB | grep "deviceId" | grep $EDGE_DEVICE)"; then
    # if not, we create a new edge enable device
    az iot hub device-identity create --hub-name $IOTHUB --device-id $EDGE_DEVICE --edge-enabled -o none
    # TODO check for errors
fi

# capture the connection string for the new edge device
DEVICE_CONNECTION_STRING=$(az iot hub device-identity connection-string show --device-id $EDGE_DEVICE --hub-name $IOTHUB --query='connectionString')

echo "{ \"deviceConnectionString\": $DEVICE_CONNECTION_STRING }" > $AZ_SCRIPTS_OUTPUT_PATH