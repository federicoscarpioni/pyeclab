from device import BiologicDevice
import techniques as tech
from channel import Channel, ChannelOptions

# IP address of the instrument
ip_address = '172.28.26.10'
# Path of the SDK from BioLogic installed in the machine
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
# Istantiate device class
device = BiologicDevice(ip_address, binary_path = binary_path)
# Create CP technique
repeat_count   = 0
record_dt      = 0.1
record_dE      = 5    # Volts
current        = 0.001    # Ampers
duration_CP    = 15        # Seconds (sec * min * hours)
limit_E_crg    = 0b11111
E_lim_high     = 5        # Volts
E_lim_low      = -5         # Volts
i_range        = 9
exit_cond      = 1
E_range        = 1
bw             = 4
xctr           = 0b01001001
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
sequence_test = [CP_tech]
# Istantiate channel
test_options = ChannelOptions('2501281215_test_recording_capcity_in_CP')
channel1=Channel(device,
                 1,
                 'E:/Experimental_data/Federico/2025/python_software_test',
                 test_options,
                 is_live_plotting = True,
                 is_printing_values = False,
                 is_charge_recorded = True,
                 is_recording_Ece = True
                 )
channel1.load_sequence(sequence_test, ask_ok=True)
channel1.start()
