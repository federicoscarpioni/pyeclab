import logging

import numpy as np

import pyeclab.channel.buffer_converters as buffer_converters

logger = logging.getLogger("pyeclab")


class DataAcquisition:
    """
    Retrieves the latest measurement data from a BioLogic device channel and
    converts it from raw ADC counts into physical values (time, voltage,
    current, and optionally charge/Ece).
    """

    def __init__(self, bio_device, channel_num: int, config):
        self.bio_device = bio_device
        self.channel_num = channel_num
        self.config = config

    def poll(self):
        """
        Fetch the latest agglomerated data from the instrument and convert it.

        Returns a tuple (current_values, data_info, converted_data):
        current_values = current values of the measurement
        data_info = info on the technique that is running and on the buffer content, e.g. TechniqueID
        converted_data = (t, Ewe, I, [Ece], [Q]) physical values, see buffer_converters
        See the EC-Lab Development Kit manual for details on the data structures.
        """
        current_values, data_info, data_buffer = self.bio_device.GetData(
            self.bio_device.device_id, self.channel_num
        )
        logger.debug(f"Got Data:\n{data_info}")
        converted_data = self._convert_buffer(current_values, data_info, data_buffer)
        return current_values, data_info, converted_data

    def _convert_buffer(self, current_values, data_info, data_buffer):
        """Convert digitalized signal from ADC to physical values."""
        buffer = np.array(data_buffer).reshape(data_info.NbRows, data_info.NbCols)
        if self.config.record_charge and self.config.record_ece:
            return buffer_converters.with_charge_and_Ece(self.bio_device, data_info, current_values, buffer)
        elif self.config.record_charge:
            return buffer_converters.with_charge(self.bio_device, data_info, current_values, buffer)
        elif self.config.record_ece:
            return buffer_converters.with_Ece(self.bio_device, data_info, current_values, buffer)
        else:
            return buffer_converters.base(self.bio_device, data_info, current_values, buffer)
