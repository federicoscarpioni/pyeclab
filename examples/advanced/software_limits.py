from pathlib import Path

from pyeclab import BANDWIDTH, E_RANGE, I_RANGE, BiologicDevice, Channel, ChannelConfig, FileWriter
from pyeclab.techniques import ChronoAmperometry

ip_address = "172.28.20.81"
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
device = BiologicDevice(ip_address, binary_path=binary_path)

ca = ChronoAmperometry(
    device=device,
    voltage=0,
    duration=10,
    vs_init=True,
    nb_steps=0,
    record_dt=1,
    record_dI=12,
    repeat=0,
    e_range=E_RANGE.E_RANGE_2_5V,
    i_range=I_RANGE.I_RANGE_100mA,
    bandwidth=BANDWIDTH.BW_4,
)

ca = ca.make_technique()

sequence = [ca]

writer = FileWriter(
    file_dir=Path("C:/Users/385-lab/Desktop/data/"),
    experiment_name="2025-02-19_Test_02",
)

channel1 = Channel(
    device,
    1,
    writer=writer,
    config=ChannelConfig(live_plot=False),
)

channel1.load_sequence(sequence)

# Set condition on the voltage
channel1.set_condition(1, "Ewe", ">", 0.005)

channel1.start()
