

from pyeclab.device import BiologicDevice


device = BiologicDevice(address="", binary_path="")

writer = FileWriter(
    file_dir = Path(""),
    experiment_name = "2025_02_01 - batt",
)

config_exp_1 = ChannelConfig(
    record_ece = True,
    record_charge = True,
    live_plot = True,
    logging = False,
    external_control = False,
    record_analog_In1 = False,
    record_analog_In2 = False,
)


channel_1 = Channel(
    device = device,
    ch_number = 1,
    writer: writer,
    conig: config_exp_1,
)

cplim_tech = CpLim(
    **params,
    device=device
)

channel_1.load_sequence([cplim_tech])
channel_1.start()




ChronPotentiometryWithLimits
















AutomatedSetup(
    channel: channel_1
)

class AutomatedSetup:

    def exeute(technique_sqx, loop_num)
        self.channel.data_infos[]
        if technique == 1:
            set_pump
        if techniq

