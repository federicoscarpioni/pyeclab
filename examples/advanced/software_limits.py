from pathlib import Path

from pyeclab import BANDWIDTH, E_RANGE, I_RANGE, BiologicDevice, Channel, ChannelConfig, FileWriter
from pyeclab.techniques import ChronoPotentiometry

ip_address = "172.28.20.81"
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
device = BiologicDevice(ip_address, binary_path=binary_path)

cp = ChronoPotentiometry(
    device=device,
    current=0.0045,
    duration=60,
    vs_init=False,
    nb_steps=0,
    record_dt=1,
    record_dE=0.1,
    repeat=0,
    i_range=I_RANGE.I_RANGE_10mA,
    e_range=E_RANGE.E_RANGE_5V,
    bandwidth=BANDWIDTH.BW_9,
)
cp.make_technique()

sequence = [cp]

writer = FileWriter(
    file_dir=Path("E:/Experimental_data/Federico/2025/python_software_test/"),
    experiment_name="2503101428_example_software_limits",
)

channel1 = Channel(
    device,
    1,
    writer=writer,
    config=ChannelConfig(live_plot=True),
)

channel1.load_sequence(sequence)

# Set condition on the voltage
channel1.set_condition(0, "Ewe", ">", 2.80)

channel1.start()
