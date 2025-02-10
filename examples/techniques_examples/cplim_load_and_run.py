from pyeclab.device import BiologicDevice
from pyeclab.techniques import ChronoPotentiometryWithLimits
from pyeclab.channel import Channel, ChannelOptions
import pyeclab.api.kbio_types as KBIO

# IP address of the instrument
ip_address = "172.28.20.81"
# Path of the SDK from BioLogic installed in the machine
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
# Istantiate device class
device = BiologicDevice(ip_address, binary_path=binary_path)
# Create OCV technique
cplim = ChronoPotentiometryWithLimits(device=device,
                                      current=0.001,
                                      duration=10,
                                      vs_init=False,
                                      nb_steps=0,
                                      record_dt=1,
                                      record_dE=12,
                                      repeat=0,
                                      limit_variable=0b011101,
                                      limit_values=10,
                                      e_range=KBIO.E_RANGE.E_RANGE_2_5V,
                                      i_range=KBIO.I_RANGE.I_RANGE_100mA,
                                      bandwidth=KBIO.BANDWIDTH.BW_4)
cplim.make_technique()
sequence_test = [cplim]
# Istantiate channel
test_options = ChannelOptions("250210_test_cplim")
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
