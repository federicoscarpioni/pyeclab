from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from wsgiref.validate import validator

from attrs import define, field, validators

import pyeclab.api.kbio_types as KBIO
from pyeclab.api.tech_types import TECH_ID
from pyeclab.device import BiologicDevice

from pyeclab.api.kbio_api import KBIO_api
from pyeclab.api.kbio_tech import ECC_parm, make_ecc_parm, make_ecc_parms


@define(kw_only=True)
class OpenCircuitVoltage:
    device: BiologicDevice
    duration: float
    record_dt: float
    e_range: KBIO.E_RANGE
    bandwidth: KBIO.BANDWIDTH
    ecc_file : str | None = field(init = False, default = None)
    ecc_params : list | None = field(init = False, default = None) 

    def make_ocv_params(self):
        # List of OCV parameters
        ocv_param_names = {
        "duration": ECC_parm("Rest_time_T", float),
        "record_dt": ECC_parm("Record_every_dT", float),
        "record_dE": ECC_parm("Record_every_dE", float),
        "E_range": ECC_parm("E_Range", int),
        "bandwidth": ECC_parm("Bandwidth", int),
        }

        p_duration = make_ecc_parm(self.device, ocv_param_names["duration"], self.duration)
        p_record = make_ecc_parm(self.device, ocv_param_names["record_dt"], self.record_dt)
        p_erange = make_ecc_parm(self.device, ocv_param_names["E_range"], self.e_range.value)
        p_band = make_ecc_parm(self.device, ocv_param_names["bandwidth"], self.bandwidth.value)
        # Make the technique parameter array
        return make_ecc_parms(self.device, p_duration, p_record, p_erange, p_band)

    def choose_ecc_file(self):
        # Name of the dll for the OCV technique (for both types of instruments VMP3/VSP300)
        ocv3_tech_file = "ocv.ecc"
        ocv4_tech_file = "ocv4.ecc"

        # pick the correct ecc file based on the instrument family
        return ocv3_tech_file if self.device.is_VMP3 else ocv4_tech_file

    def  make_technique(self):

        self.ecc_file = self.choose_ecc_file()   
        self.ecc_params = self.make_ocv_params()

