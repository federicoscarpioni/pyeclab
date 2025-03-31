from pathlib import Path
from typing import Literal

from pyeclab import BANDWIDTH, E_RANGE, I_RANGE, BiologicDevice, Channel
from pyeclab.channel.config import ChannelConfig
from pyeclab.channel.writers.filewriter import FileWriter
from pyeclab.techniques import ChronoPotentiometry, generate_xctr_param

ip_address = "172.28.26.10"
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
device = BiologicDevice(ip_address, binary_path)


# Activate the counter of the charge from the configuration object
config = ChannelConfig(
    record_ece=False,
    record_charge=True,
    live_plot=True,
    print_values=False,
    external_control=False,
    record_analog_In1=False,
    record_analog_In2=False,
)

cp = ChronoPotentiometry(
    device=device,
    current=-0.0001,
    duration=10,
    vs_init=False,
    nb_steps=0,
    record_dt=1,
    record_dE=0.1,
    repeat=0,
    i_range=I_RANGE.I_RANGE_1mA,
    e_range=E_RANGE.E_RANGE_5V,
    bandwidth=BANDWIDTH.BW_4,
    xctr= generate_xctr_param(config)
)
cp.make_technique()

sequence = [cp]

writer = FileWriter(
    file_dir=Path("E:/Experimental_data/Federico/2025/python_software_test/"),
    experiment_name="2503101426_example_record_charge",
)


channel1 = Channel(
    device,
    1,
    writer=writer,
    config=config,
)

channel1.load_sequence(sequence)

channel1.start()
