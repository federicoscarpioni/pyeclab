from pathlib import Path
from typing import Literal
from pyeclab import BANDWIDTH, E_RANGE, EXIT_COND, I_RANGE, BiologicDevice, Channel
from pyeclab.channel.config import ChannelConfig
from pyeclab.channel.writers.filewriter import FileWriter
from pyeclab.techniques import ChronoPotentiometryWithLimits, OpenCircuitVoltage, Loop, build_limit


IP = "172.28.20.81"
binary_path = "C:/EC-Lab Development Package/lib/"
device = BiologicDevice(IP, binary_path)

ocv = OpenCircuitVoltage(
    device=device,
    duration=10,
    record_dt=1,
    e_range=E_RANGE.E_RANGE_2_5V,
    bandwidth=BANDWIDTH.BW_4,
)
ocv.make_technique()

cplim = ChronoPotentiometryWithLimits(
    device=device,
    current=0.001,
    duration=10,
    vs_init=False,
    nb_steps=0,
    record_dt=1,
    record_dE=0.1,
    repeat=0,
    i_range=I_RANGE.I_RANGE_100mA,
    e_range=E_RANGE.E_RANGE_2_5V,
    exit_cond=EXIT_COND.NEXT_TECHNIQUE,
    limit_variable=build_limit("voltage", "greater", "or", True),
    limit_values=3,  
    bandwidth=BANDWIDTH.BW_5,
)
cplim.make_technique()

ca = ChronoAmperometry(device=device,
                        voltage=0,
                        duration=10,
                        vs_init=True,
                        nb_steps=0,
                        record_dt=1,
                        record_dI=12,
                        repeat=0,
                        e_range=KBIO.E_RANGE.E_RANGE_2_5V,
                        i_range=KBIO.I_RANGE.I_RANGE_100mA,
                        bandwidth=KBIO.BANDWIDTH.BW_5)
ca = ca.make_technique()

loop = Loop(device=device, repeat_N=2, loop_start=0)  # loop forever
loop.make_technique()

sequence = [
    ocv,
    cplim,
    ocv,
    ca,
    loop,
]

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
channel1.start()