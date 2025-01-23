from pyeclab.device import BiologicDevice
from pyeclab.techniques import EXIT_COND, OCV_params, OCV_tech, CPLIM
from pyeclab.channel import Channel, ChannelOptions
from pyeclab.api.kbio_types import I_RANGE, E_RANGE, BANDWIDTH

IP = "172.28.20.81"
binary_path = "C:/EC-Lab Development Package/lib/"

device = BiologicDevice(IP, binary_path)

ocv_params = OCV_params(20, 1, 0, 4)
ocv_technique = OCV_tech(device, device.is_VMP3, ocv_params)


cppl = CPLIM(
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

cppl_technique = cppl.make_technique()

sequence_test = [cppl_technique]

test_options = ChannelOptions("20250122_1112_cppl-test")

channel1 = Channel(
    device,
    1,
    "C:/Users/jconen/Desktop/biologic_data",
    test_options,
)
channel1.load_sequence(sequence_test, ask_ok=True)
channel1.start()
