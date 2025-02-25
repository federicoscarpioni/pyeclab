from pathlib import Path
from typing import Literal
from pyeclab import BANDWIDTH, E_RANGE, EXIT_COND, I_RANGE, BiologicDevice, Channel
from pyeclab.channel.config import ChannelConfig
from pyeclab.channel.writers.filewriter import FileWriter
from pyeclab.techniques import ChronoPotentiometryWithLimits, OpenCircuitVoltage, Loop


def set_bit(value, bit_index):
    return value | (1 << bit_index)


def build_limit(
    type: Literal["voltage", "current"], sign: Literal["greater", "less"], logic: Literal["and", "or"], active=True
):
    value = 0b0
    if active:
        value = set_bit(value, 0)

    if logic == "and":
        value = set_bit(value, 1)

    if sign == "greater":
        value = set_bit(value, 2)

    if type == "current":
        value = set_bit(value, 5)
        value = set_bit(value, 6)

    return value


IP = "172.28.20.81"
binary_path = "C:/EC-Lab Development Package/lib/"

device = BiologicDevice(IP, binary_path)

ocv = OpenCircuitVoltage(
    device=device,
    duration=60 * 60,
    record_dt=1,
    e_range=E_RANGE.E_RANGE_2_5V,
    bandwidth=BANDWIDTH.BW_4,
)
ocv.make_technique()

cppl_waste = ChronoPotentiometryWithLimits(
    device=device,
    current=0.1,
    duration=1 * 1 * 10,
    vs_init=False,
    nb_steps=0,
    record_dt=0.5,
    record_dE=0.1,
    repeat=0,
    i_range=I_RANGE.I_RANGE_1mA,
    e_range=E_RANGE.E_RANGE_2_5V,
    exit_cond=EXIT_COND.NEXT_TECHNIQUE,
    limit_variable=build_limit("voltage", "greater", "or", True),
    limit_values=10,  # if triggered by limit, the callback won't trigger at this point. might need to change something on that.
    bandwidth=BANDWIDTH.BW_5,
)
cppl_waste.make_technique()

cppl_recovery = ChronoPotentiometryWithLimits(
    device=device,
    current=-0.1,
    duration=1 * 1 * 10,
    vs_init=False,
    nb_steps=0,
    record_dt=0.5,
    record_dE=0.1,
    repeat=0,
    i_range=I_RANGE.I_RANGE_1mA,
    e_range=E_RANGE.E_RANGE_2_5V,
    exit_cond=EXIT_COND.NEXT_TECHNIQUE,
    limit_variable=0b11111,
    limit_values=10,
    bandwidth=BANDWIDTH.BW_5,
)
cppl_recovery.make_technique()

loop = Loop(device=device, repeat_N=-1, loop_start=0)  # loop forever
loop.make_technique()

sequence = [
    ocv,
    cppl_waste,
    ocv,
    cppl_recovery,
    ocv,
    # loop,
]

writer = FileWriter(
    # file_dir=Path("C:/Users/jconen/Desktop/data"),
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
 