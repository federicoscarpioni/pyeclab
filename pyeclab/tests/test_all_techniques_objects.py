from device import BiologicDevice
import tech_objects as tech
from channel import Channel, ChannelOptions

# IP address of the instrument
ip_address = '172.28.26.11'
# Path of the SDK from BioLogic installed in the machine
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
# Istantiate device class
device = BiologicDevice(ip_address, binary_path = binary_path)
# Create OCV technique
ocv = tech.OCV(10,1,0,0,4)
ocv_technique = ocv
sequence_test = [ocv_technique]
# Istantiate channel
test_options = ChannelOptions('same_name')
channel1=Channel(device,
                 1,
                 'E:/Experimental_data/Federico/2024/python_software_test',
                 test_options,
                 do_live_plot = True,
                 do_print_values = False,
                 )
channel1.load_sequence(sequence_test, ask_ok=True)
channel1.start()