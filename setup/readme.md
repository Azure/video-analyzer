# Azure Video Analyzer

The scripts in this folder are used to deploy the Azure Video Analyzer.  This deployment enables quickstarts and other samples for Video Analyzer.

- deploy-modules.sh - This script is used to deploy the IoT Edge modules to the IoT Edge device based off of the deployment manifest (general-sample-setup.modules.json)
- form.json- custom deployment form used in Azure Portal
- general-sample-setup-modules.json - Azure IoT Edge deployment manifest 
- iot-edge-setup.sh - Checks to see if an existing Edge device exist, if not it creates a new Edge device and captures the connection string.
- iot.deploy.json - Deploys an IoT Hub
- prepare-device.sh - Configures the IoT Edge device with the required user and folder structures.
- simulated-device.deploy.json - Deploys a VM to be used as a simulated IoT Edge device.
- start.deploy.json - Master template and controls the flow between the rest of the deployment templates
- video-analyzer.deploy.json - Deploys storage, identities, and the Azure Video Analyzer resources.



> NOTE: Things like VM availability in the selected region will cause the deployment to fail.

### Deploy the required Video Analyzer resources

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Fvideo-analyzer%2Fmain%2Fsetup%2Fstart.deploy.json/createUIDefinitionUri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Fvideo-analyzer%2Fmain%2Fsetup%2Fform.json)

After the script finishes you will have the following Azure resources:

- [IoT Hub](https://docs.microsoft.com/azure/iot-hub/about-iot-hub)
- [Virtual Machine (virtual Edge device)](https://docs.microsoft.com/azure/virtual-machines/)
  - [Network interface](https://docs.microsoft.com/rest/api/virtualnetwork/networkinterfaces)
  - [Disk](https://docs.microsoft.com/azure/virtual-machines/managed-disks-overview)
  - [Network security group](https://docs.microsoft.com/azure/virtual-network/network-security-groups-overview)
  - [Public IP address (if the Bastion option was not set)](https://docs.microsoft.com/azure/virtual-network/public-ip-addresses)
- [Virtual network](https://docs.microsoft.com/azure/virtual-network/virtual-networks-overview)
- [Storage account](https://docs.microsoft.com/azure/storage/common/storage-account-overview) 
- [Azure Video Analyzer](https://docs.microsoft.com/azure/azure-video-analyzer/overview)
- [Managed Identities](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)
- [Bastion Host (if the Bastion option was set)](https://docs.microsoft.com/azure/bastion/)




