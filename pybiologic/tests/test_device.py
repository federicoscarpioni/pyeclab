import time
from pybiologic.device import BiologicDevice
from pybiologic.techniques import OCV

# IP address of the instrument
ip_address = ''
# Pth of the SDK from BioLogic installed in the machine
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/",
# Istantiate device class
bldev = BiologicDevice(ip_address, binary_path)
# Change  some configuration
bldev.set_hardware_configuration(self, channel, cnx, mode)
# Create a simple OCV sequence of 10 seconds
...
ocv = OCV()
sequence_test = [ocv]
# Load to sequence on channel 1
bldev.load_sequence(1,sequence_test)
# Start the  technique in channel 1
bldev.start_channel(1)
# Stop manually after 8 seconds
time.sleep(8)
bldev.stop_channel(1)
# Disconnect the device
bldev.disconnect()