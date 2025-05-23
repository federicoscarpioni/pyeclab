from pyeclab.channel.config import ChannelConfig

def generate_xctr_param(config:ChannelConfig):
    bitfield = 0
    bitfield |= config.record_ece << 0  # Record Ece at bit position 1
    bitfield |= config.record_analog_In1 << 1  # Record Analog IN1 at bit position 2
    bitfield |= config.record_analog_In2 << 2  # Record Analog IN2 at bit position 3
    bitfield |= config.external_control << 3  # Enable External ctrl at bit position 4
    # bit 5 is reserved
    # No information for bit position 6 (Record Control), assuming not needed
    bitfield |= config.record_charge << 6  # Record Charge at bit position 7
    # No information for bit position 8 (Record IRange), assuming not needed
    return bitfield