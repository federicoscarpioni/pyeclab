import time

import pyeclab.techniques.techniques as tech
from pyeclab.device import BiologicDevice

#!!! Has to be refactored for the new techniques objects!

# IP address of the instrument
ip_address = "172.28.26.11"
# Pth of the SDK from BioLogic installed in the machine
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
# Istantiate device class
device = BiologicDevice(ip_address, binary_path=binary_path)
# Create OCV technique
ocv_params = tech.OCV_params(10, 1, 0, 4, 0)
ocv_technique = tech.make_OCV_tech(device, ocv_params)
sequence_test = [ocv_technique]
# Load to sequence on channel 1
device.load_sequence(1, sequence_test)
# Start the  technique in channel 1
device.start_channel(1)
# Stop manually after 8 seconds
time.sleep(8)
device.stop_channel(1)
# Disconnect the device
device.disconnect()
