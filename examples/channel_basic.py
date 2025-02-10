from pyeclab.techniques import OpenCircuitVoltage
from pyeclab.channel import Channel, ChannelOptions
from pyeclab.device import BiologicDevice
import pyeclab.api.kbio_types as KBIO

# IP address of the instrument
ip_address = "172.28.20.81"
# Path of the SDK from BioLogic installed in the machine
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
# Istantiate device class
device = BiologicDevice(ip_address, binary_path=binary_path)
# Create OCV technique
ocv = OpenCircuitVoltage(device = device,
                         duration=10, 
                         record_dt=1, 
                         e_range=KBIO.E_RANGE.E_RANGE_2_5V, 
                         bandwidth=KBIO.BANDWIDTH.BW_4)
ocv.make_technique()
sequence_test = [ocv]
# Istantiate channel
test_options = ChannelOptions("250210_test_ocv")
channel1 = Channel(
    device,
    1,
    "C:/Experimental_data/Federico/2025/python_software_test",
    test_options,
    is_live_plotting=True,
    is_printing_values= True
)
channel1.load_sequence(sequence_test, ask_ok=True)
channel1.start()
