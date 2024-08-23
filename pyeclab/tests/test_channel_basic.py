from device import BiologicDevice
import techniques as tech
from channel import Channel, ChannelOptions

# IP address of the instrument
ip_address = '172.28.26.11'
# Path of the SDK from BioLogic installed in the machine
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
# Istantiate device class
device = BiologicDevice(ip_address, binary_path = binary_path)
# Create OCV technique
ocv_params = tech.OCV_params(10, 1, 0, 4)
ocv_technique = tech.OCV_tech(device, device.is_VMP3, ocv_params)
sequence_test = [ocv_technique]
# Istantiate channel
test_options = ChannelOptions('2408230922_troubleshooting_duration_channel_class')
channel1=Channel(device,
                 1,
                 'E:/Experimental_data/Federico/2024/python_software_test',
                 test_options,
                 do_live_plot = True,
                 do_print_values = True,
                 )
channel1.load_sequence(sequence_test)
channel1.start()


