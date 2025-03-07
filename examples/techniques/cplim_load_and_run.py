from pathlib import Path

from pyeclab import BANDWIDTH, E_RANGE, EXIT_COND, I_RANGE, BiologicDevice, Channel, ChannelConfig, FileWriter
from pyeclab.techniques import ChronoPotentiometryWithLimits, build_limit

ip_address = "172.28.20.81"
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
device = BiologicDevice(ip_address, binary_path=binary_path)

cplim = ChronoPotentiometryWithLimits(
    device=device,
    current=0,
    duration=10,
    vs_init=False,
    nb_steps=0,
    record_dt=1,
    record_dE=0.1,
    repeat=0,
    i_range=I_RANGE.I_RANGE_10mA,
    e_range=E_RANGE.E_RANGE_5V,
    exit_cond=EXIT_COND.NEXT_TECHNIQUE,
    limit_variable=build_limit("voltage", "greater", "or", True),
    limit_values=3,
    bandwidth=BANDWIDTH.BW_5,
)

cplim.make_technique()

sequence = [cplim]

writer = FileWriter(
    file_dir=Path("E:/Experimental_data/Federico/2025/python_software_test/"),
    experiment_name="2503071524_example_cplim_after_refactoring",
)
channel1 = Channel(
    device,
    1,
    writer=writer,
    config=ChannelConfig(live_plot=True),
)
channel1.load_sequence(sequence, ask_ok=True)
channel1.start()
