"""
Channel class can execute functions when a new technique from the sequence starts.
In this script, a simple printing funcion and class methods are used as examples.
In practice, the function to excecute can be appended to the list attribute
'callbacks' of Channel class.
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
    device=device,
    duration=5,
    record_dt=1,
    e_range=E_RANGE.E_RANGE_5V,
    bandwidth=BANDWIDTH.BW_4,
)
ocv.make_technique()

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

# Add the function and method to the list of callbacks to excecute.
channel1.callbacks.append(printer_function)
fake_instrument = FakeInstrument()
channel1.callbacks.append(fake_instrument.print_massage)

channel1.start()
