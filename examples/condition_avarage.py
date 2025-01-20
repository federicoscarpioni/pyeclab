import pyeclab.techniques as tech
from pyeclab.channel import Channel, ChannelOptions
from pyeclab.device import BiologicDevice

# IP address of the instrument
ip_address = "172.28.26.11"
# Path of the SDK from BioLogic installed in the machine
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
# Istantiate device class
device = BiologicDevice(ip_address, binary_path=binary_path)
# Create OCV technique
duration_OCV = 10
dt_OCV = 1
E_range = 0
bw = 4
OCV_user_params = tech.OCV_params(duration_OCV, dt_OCV, E_range, bw)
OCV_tech = tech.OCV_tech(device, device.is_VMP3, OCV_user_params)
# Create CP technique
repeat_count = 0
record_dt = 1
record_dE = 1  # Volts
current = 0.000001  # Ampers
duration_CP = 10  # Seconds (sec * min * hours)
limit_E_crg = 0b11111
E_lim_high = 5  # Volts
E_lim_low = -5  # Volts
i_range = 5
exit_cond = 1
xctr = 0
CP_user_params = tech.CPLIM_params(
    current,
    duration_CP,
    False,
    0,
    record_dt,
    record_dE,
    repeat_count,
    i_range,
    E_range,
    exit_cond,
    xctr,
    E_lim_high,
    limit_E_crg,
    bw,
)
CP_tech = tech.CPLIM_tech(device, device.is_VMP3, CP_user_params)
# Create loop technique
number_repetition = 1
tech_index_start = 0
LOOP_user_params = tech.LOOP_params(number_repetition, tech_index_start)
LOOP_tech = tech.loop_tech(device, device.is_VMP3, LOOP_user_params)
# Make sequence
sequence = [OCV_tech, CP_tech, LOOP_tech]
# Istantiate channel
test_options = ChannelOptions("2408261127_test_software_limits_avarage_channel")
channel1 = Channel(
    device,
    1,
    "E:/Experimental_data/Federico/2024/python_software_test",
    test_options,
    do_live_plot=True,
    do_print_values=False,
)
channel1.load_sequence(sequence, ask_ok=False)
# Set conditions on the voltage
channel1.set_condition_avarage("Ewe", ">", 0.005, 3)
channel1.start()
