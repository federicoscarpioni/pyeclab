from pathlib import Path
from pyeclab.channel.writers.filewriter import FileWriter
from pyeclab.device import BiologicDevice
from pyeclab import EXIT_COND, Channel, I_RANGE, E_RANGE, BANDWIDTH
from pyeclab.techniques import ChronoPotentiometryWithLimits, OpenCircuitVoltage

IP = "172.28.20.81"
binary_path = "C:/EC-Lab Development Package/lib/"

device = BiologicDevice(IP, binary_path)

ocv = OpenCircuitVoltage(device=device, duration=5, record_dt=1, e_range=E_RANGE.E_RANGE_2_5V, bandwidth=BANDWIDTH.BW_4)
ocv.make_technique()

cppl = ChronoPotentiometryWithLimits(
    device=device,
    current=0.01,
    duration=1 * 1 * 5,
    vs_init=False,
    nb_steps=0,
    record_dt=0.5,
    record_dE=0.01,
    repeat=0,
    i_range=I_RANGE.I_RANGE_1mA,
    e_range=E_RANGE.E_RANGE_2_5V,
    exit_cond=EXIT_COND.NEXT_STEP,
    limit_variable=0b011101,
    limit_values=10,
    bandwidth=BANDWIDTH.BW_5,
)
cppl.make_technique()

sequence_test = [ocv, cppl, ocv]


writer = FileWriter(Path("C:/Users/jconen/Desktop/data"), experiment_name="2025_02_11-Test")

channel1 = Channel(
    device,
    1,
    writer,
)
channel1.load_sequence(sequence_test, ask_ok=True)
channel1.start()
