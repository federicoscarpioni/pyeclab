from pyeclab.device import BiologicDevice
from pyeclab.techniques import ChronoPotentiometryWithLimits
from pyeclab.channel import Channel, ChannelOptions

# IP address of the instrument
ip_address = "172.28.26.11"
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
                                      i_range='I_RANGE_100mA')
pclim_tech = cplim.make_technique()
sequence_test = [pclim_tech]
# Istantiate channel
test_options = ChannelOptions("2408240935_working_example_live_plot_channel")
channel1 = Channel(
    device,
    1,
    "E:/Experimental_data/Federico/2024/python_software_test",
    test_options,
    do_live_plot=True,
    do_print_values=False,
)
channel1.load_sequence(sequence_test, ask_ok=True)
channel1.start()
