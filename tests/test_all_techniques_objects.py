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
duration_OCV = 60*60*1
dt_OCV       = 1
E_range      = 0
bw           = 4
OCV_user_params = tech.OCV_params(duration_OCV, dt_OCV, E_range, bw)
OCV_tech = tech.OCV_tech(device, device.is_VMP3, OCV_user_params)
# Create CP technique
repeat_count   = 0
record_dt      = 1
record_dE      = 1    # Volts
current        = 0    # Ampers
duration_CP    = 60*60*1        # Seconds (sec * min * hours)
limit_E_crg    = 0b11111
E_lim_high     = 5        # Volts
E_lim_low      = -5         # Volts
i_range        = 6
exit_cond      = 1
xctr           = 0b00001000
CP_user_params = tech.CPLIM_params(current, 
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
                                     bw)
CP_tech = tech.CPLIM_tech(device, device.is_VMP3, CP_user_params)
# Create CA technique
#---CA1---#
repeat_count   = 0
record_dI      = 1   # Ampers
voltage        = 0   # Volts
duration_CA    = 60*60*1     # Seconds (sec * min * hours)
CA_user_params    = tech.CA_params(voltage, 
                                  duration_CA, 
                                  False, 
                                  0, 
                                  record_dt, 
                                  record_dI, 
                                  repeat_count,
                                  i_range,
                                  E_range,
                                  exit_cond, 
                                  xctr,
                                  bw)
CA_tech = tech.CA_tech(device, device.is_VMP3, CA_user_params)
# Create loop technique
number_repetition  = 1
tech_index_start   = 0
LOOP_user_params = tech.LOOP_params(number_repetition, tech_index_start)
LOOP_tech    = tech.loop_tech(device, device.is_VMP3, LOOP_user_params)
# Make sequence
sequence = [CA_tech]
# Istantiate channel
test_options = ChannelOptions('2408290727_test_CA_full_dummy_3electrodes_pico_multisine')
channel1=Channel(device,
                 1,
                 'E:/Experimental_data/Federico/2024/python_software_test',
                 test_options,
                 do_live_plot = True,
                 do_print_values = False,
                 )
channel1.load_sequence(sequence, ask_ok=False)
channel1.start()
