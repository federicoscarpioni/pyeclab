import time
from pyeclab.device import BiologicDevice
from pyeclab.techniques import OCV_params, make_OCV_tech

# IP address of the instrument
ip_address = ''
# Pth of the SDK from BioLogic installed in the machine
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/",
# Istantiate device class
device = BiologicDevice(ip_address, binary_path = binary_path)
# Create OCV technique
ocv_params = OCV_params(10, 1, 0, 4, 0)
ocv_technique = ocv_params.make_OCV_tech(device.is_VMP3)
sequence_test = [ocv_technique]
# Load to sequence on channel 1
device.load_sequence(1,sequence_test)
# Start the  technique in channel 1
device.start_channel(1)
# Stop manually after 8 seconds
time.sleep(8)
device.stop_channel(1)
# Disconnect the device
device.disconnect()