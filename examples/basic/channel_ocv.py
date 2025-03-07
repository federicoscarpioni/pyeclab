from pathlib import Path

from pyeclab import BANDWIDTH, E_RANGE, EXIT_COND, I_RANGE, BiologicDevice, Channel, ChannelConfig, FileWriter
from pyeclab.techniques import OpenCircuitVoltage

IP = "172.28.26.10"
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
device = BiologicDevice(IP, binary_path)

ocv = OpenCircuitVoltage(
    device=device,
    duration=20,
    record_dt=1,
    e_range=E_RANGE.E_RANGE_5V,
    bandwidth=BANDWIDTH.BW_4,
)
ocv.make_technique()

sequence = [ocv]

writer = FileWriter(
    file_dir=Path("E:/Experimental_data/Federico/2025/python_software_test/"),
    experiment_name="2503071435_example_basic_channel_ocv_after_refactoring",
)

config = ChannelConfig(
    record_ece=False,
    record_charge=False,
    live_plot=True,
    print_values=False,
    external_control=False,
    record_analog_In1=False,
    record_analog_In2=False,
)

channel1 = Channel(
    device,
    1,
    writer=writer,
    config=config,
)

channel1.load_sequence(sequence)

channel1.start()
