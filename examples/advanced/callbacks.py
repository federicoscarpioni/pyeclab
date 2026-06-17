"""
Channel class can execute a function when a new technique from the sequence starts.
In this script, a simple printing funcion and a class method are used as examples.
In practice, the callback can be assigned to channel.sequence_monitor.on_technique_change.
"""

from pathlib import Path
from typing import Literal

from pyeclab import BANDWIDTH, E_RANGE, I_RANGE, BiologicDevice, Channel
from pyeclab.channel.config import ChannelConfig
from pyeclab.channel.writers.filewriter import FileWriter
from pyeclab.techniques import ChronoPotentiometryWithLimits, Loop, OpenCircuitVoltage


# Example of a function
def printer_function():
    print("Hey! I am the printer function!")


# Example of a class with simple method
class FakeInstrument:
    def print_massage(self):
        print('I am a method of an object!')


IP = "172.28.20.81"
binary_path = "C:/EC-Lab Development Package/lib/"

device = BiologicDevice(IP, binary_path)

ocv = OpenCircuitVoltage(
    duration=5,
    record_dt=1,
    e_range=E_RANGE.E_RANGE_5V,
    bandwidth=BANDWIDTH.BW_4,
)
ocv.make_technique(device)

sequence = [ocv, ocv, ocv]

writer = FileWriter(
    file_dir=Path("E:/Experimental_data/Federico/2025/python_software_test/"),
    experiment_name="2503101144_example_callbacks_between_OCVs",
)
channel1 = Channel(
    device,
    1,
    writer=writer,
    config=ChannelConfig(live_plot=True),
)
channel1.load_sequence(sequence)

# Only a single callback is supported; wrap multiple actions in one function.
fake_instrument = FakeInstrument()


def on_technique_change():
    printer_function()
    fake_instrument.print_massage()


channel1.sequence_monitor.on_technique_change = on_technique_change

channel1.start()
