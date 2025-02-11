from attrs import define


@define
class ChannelConfig:
    record_ece: bool = True
    record_charge: bool = True
    live_plot: bool = True
    logging: bool = False
    external_control: bool = False
    record_analog_In1: bool = False
    record_analog_In2: bool = False
