from pathlib import Path

from pyeclab import BANDWIDTH, E_RANGE, I_RANGE, BiologicDevice, Channel, ChannelConfig, FileWriter
from pyeclab.techniques import ChronoAmperometry

ip_address = "172.28.26.10"
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
device = BiologicDevice(ip_address, binary_path=binary_path)

ca = ChronoAmperometry(
    device=device,
    voltage=0,
    duration=10,
    vs_init=True,
    nb_steps=0,
    record_dt=1,
    record_dI=1,
    repeat=0,
    e_range=E_RANGE.E_RANGE_5V,
    i_range=I_RANGE.I_RANGE_100mA,
    bandwidth=BANDWIDTH.BW_4,
)
ca = ca.make_technique()

sequence = [ca]

writer = FileWriter(
    file_dir=Path("E:/Experimental_data/Federico/2025/python_software_test/"),
    experiment_name="2503051605_example_basic_channel_ocv_after_refactoring",
)

channel1 = Channel(
    device,
    1,
    writer=writer,
    config=ChannelConfig(live_plot=True),
)

channel1.load_sequence(sequence)

channel1.start()
