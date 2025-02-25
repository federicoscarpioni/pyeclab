"""
This module
"""

import logging
from collections.abc import Sequence

import pyeclab.api.kbio_types as types
from pyeclab.api.c_utils import c_is_64b
from pyeclab.api.kbio_api import KBIO_api


class BiologicDevice(KBIO_api):
    """
    Connect and setup BioLogic device and perform measurement techniques on
    channels. Inherits from BioLogic api module and simplifies the calls to
    the functions.
    IMPORTANT: The class doesn't retrieve the measurement data from the instrument!
    """

    def __init__(
        self,
        address: str,
        binary_path: str = "C:/EC-Lab Development Package/EC-Lab Development Package/",
        autoconnect: bool = True,
    ):
        DLL_path = self._choose_library(binary_path)
        super(BiologicDevice, self).__init__(DLL_path)
        self.address = address
        if autoconnect:
            self.connect()
            self.test_connection()
            self.test_channels_plugged()
            self.is_VMP3 = self.device_info.model in types.VMP3_FAMILY
            self._load_firmware_channels(force_load=False)

    def _choose_library(self, binary_path: str):
        """
        Choose the proper BioLogic dll according to Python version (32/64bit)'
        """
        if c_is_64b:
            DLL_file = "EClib64.dll"
        else:
            DLL_file = "EClib.dll"
        return binary_path + DLL_file

    def connect(self):
        self.device_id, self.device_info = self.Connect(self.address)
        print(f"> device[{self.address}] info :")
        print(self.device_info)

    def disconnect(self):
        self.Disconnect(self.device_id)
        print(f"> Disconnected device {self.address}")

    def test_connection(self):
        ok = "OK" if self.TestConnection(self.device_id) else "not OK"
        print(f"> device[{self.address}] connection : {ok}")

    def test_channels_plugged(self):
        "Check the number of plugged channel and print the result"
        self.number_channels = self.PluggedChannels(self.device_id)
        print(f"> number of channel plugged: {self.number_channels}")

    def set_hardware_configuration(self, channel, cnx, mode):
        """See pag 154 of the manual"""
        self.SetHardwareConf(
            self.device_id,
            channel,
        )

    def _load_firmware_channels(self, force_load: bool):
        """
        Load the firmware in a channel if needed
        """
        # based on family, determine firmware filenames
        if self.is_VMP3:
            firmware_path = "kernel.bin"
            fpga_path = "Vmp_ii_0437_a6.xlx"
        else:
            firmware_path = "kernel4.bin"
            fpga_path = "vmp_iv_0395_aa.xlx"
        print(f"> Loading {firmware_path} ...")

        # create a map from channel set
        channel_map = [True] * self.device_info.NumberOfChannels

        self.LoadFirmware(self.device_id, channel_map, firmware=firmware_path, fpga=fpga_path, force=force_load)
        print("> ... firmware loaded")

    def start_channel(self, channel: int):
        self.StartChannel(self.device_id, channel)
        print(f"> Started channel {channel}")

    # !!! Implement start_channels for channel synchronization

    def stop_channel(self, channel: int):
        self.StopChannel(self.device_id, channel)
        print(f"> Channel {channel} stopped")

    def status(self, current_values):
        status = current_values.State
        status = types.PROG_STATE(status).name
        return status

    def load_sequence(self, channel: int, sequence: Sequence, display: bool = False):
        for i in range(0, len(sequence)):
            # Determine the "first"and "last" parameter needed in LoadTechnique
            # from the length of sequence list.
            if len(sequence) == 1:  # If there is only one technique
                first = True
                last = True
            elif i == 0:  # If this is the first technique
                first = True
                last = False
            elif i == len(sequence) - 1:  # If this is the last technique
                first = False
                last = True
            else:  # If this is a technique in the middle
                first = False
                last = False
            self.LoadTechnique(
                self.device_id, channel, sequence[i].ecc_file, sequence[i].ecc_params, first, last, display
            )
            print(f"Loaded technique {i} in the sequence.")
