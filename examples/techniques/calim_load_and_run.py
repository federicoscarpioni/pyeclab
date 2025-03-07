from pathlib import Path

from pyeclab import BANDWIDTH, E_RANGE, EXIT_COND, I_RANGE, BiologicDevice, Channel, ChannelConfig, FileWriter
from pyeclab.techniques import ChronoAmperometryWithLimits, build_limit

ip_address = "172.28.20.81"
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
device = BiologicDevice(ip_address, binary_path=binary_path)

calim = ChronoAmperometryWithLimits(
    device=device,
    voltage=0,
    duration=10,
    vs_init=True,
    nb_steps=0,
    record_dt=1,
    record_dI=12,
    repeat=0,
    e_range=E_RANGE.E_RANGE_5V,
    i_range=I_RANGE.I_RANGE_100uA,
    exit_cond=EXIT_COND.NEXT_TECHNIQUE,
    limit_variable=build_limit("current", "greater", "or", True),
    limit_values=1,
    bandwidth=BANDWIDTH.BW_4,
)
calim.make_technique()

sequence = [calim]

writer = FileWriter(
    file_dir=Path("E:/Experimental_data/Federico/2025/python_software_test/"),
    experiment_name="2503071658_example_calim_after_refactoring",
)

channel1 = Channel(
    device,
    1,
    writer=writer,
    config=ChannelConfig(live_plot=True,
                         print_values=True),
)

channel1.load_sequence(sequence)

channel1.start()
