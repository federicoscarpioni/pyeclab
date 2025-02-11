from attrs import define


@define
class ChannelConfig:
    record_ece: bool = False
    record_charge: bool = False
    live_plot: bool = True
    print_values: bool = False
    external_control: bool = False
    record_analog_In1: bool = False
    record_analog_In2: bool = False
