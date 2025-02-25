from pathlib import Path
from typing import Literal
from pyeclab import BANDWIDTH, E_RANGE, EXIT_COND, I_RANGE, BiologicDevice, Channel
from pyeclab.channel.config import ChannelConfig
from pyeclab.channel.writers.filewriter import FileWriter
from pyeclab.techniques import ChronoPotentiometryWithLimits, OpenCircuitVoltage, Loop, ChronoAmperometry


IP = "172.28.20.81"
binary_path = "C:/EC-Lab Development Package/lib/"
device = BiologicDevice(IP, binary_path)

ocv = OpenCircuitVoltage(
    device=device,
    duration=5,
    record_dt=1,
    e_range=E_RANGE.E_RANGE_2_5V,
    bandwidth=BANDWIDTH.BW_4,
)
ocv.make_technique()

ca = ChronoAmperometry(
    device=device,
    voltage=-0.01,
    duration=20,
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

sequence = [ocv, ca]

writer = FileWriter(
    file_dir=Path("C:/Users/385-lab/Desktop/data/"),
    experiment_name="2025-02-19_Test_02",
)

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

channel1 = Channel(
    device,
    1,
    writer=writer,
    config=config,
)

channel1.load_sequence(sequence)

channel1.start()
