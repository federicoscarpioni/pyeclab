from pyeclab.device import BiologicDevice
from pyeclab.techniques import ChronoPotentiometryWithLimits, build_limit
from pyeclab.channel import Channel
from pyeclab.channel.config import ChannelConfig
import pyeclab.api.kbio_types as KBIO

ip_address = "172.28.20.81"
binary_path = "C:/EC-Lab Development Package/EC-Lab Development Package/"
device = BiologicDevice(ip_address, binary_path=binary_path)

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

sequence = [cplim]

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
