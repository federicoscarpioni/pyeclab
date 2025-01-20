"""
This module contains dataclasses to define user parameter for each technique
as object to be passed to the instrument for loading the technique. The dataclass
stores:
- The user paramters as attributees of the dataclass (they are not used by the
instrument)
- The ecc_file path of the technique (use from the device to define the technique
in the hardware)
- The params tuple of the technique parameters (used to send the correct format
to the hardware and override default technique paramters with users one)

Having one dataclass per technique allows to concatante techniques into a sequence
passed as a list to the load_sequence() method of the BiologiDevice class.
"""

import pyeclab.tech_names as tn
from pyeclab.api.kbio_tech import make_ecc_parm, make_ecc_parms
import pyeclab.tech_names as tnames
from dataclasses import dataclass


@dataclass
class OCV:
    duration: float
    record_dt: float
    record_dE: float
    E_range: int
    bandwidth: int

    def __postinit__(self):
        self.param_names = tn.OCV_parm_names

    def choose_ecc_file(self, device):
        # .ecc file names
        ocv3_tech_file = "ocv.ecc"
        ocv4_tech_file = "ocv4.ecc"
        # pick the correct ecc file based on the instrument family
        self.ecc_file = ocv3_tech_file if device.is_VMP3 else ocv4_tech_file

    def make_ecc_params(self, device):
        p_duration = make_ecc_parm(device, tnames.OCV_parm_names["duration"], self.duration)
        p_record = make_ecc_parm(device, tnames.OCV_parm_names["record_dt"], self.record_dt)
        p_erange = make_ecc_parm(device, tnames.OCV_parm_names["E_range"], self.e_range)
        p_band = make_ecc_parm(device, tnames.OCV_parm_names["bandwidth"], self.bandwidth)
        self.ecc_parms_OCV = make_ecc_parms(device, p_duration, p_record, p_erange, p_band)

    def make_tech(self, device):
        self.choose_ecc_file(device)
        self.make_ecc_params(device)
