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

    def make_ocv_params(self):
        # List of OCV parameters
        ocv_param_names = {
        "duration": ECC_parm("Rest_time_T", float),
        "record_dt": ECC_parm("Record_every_dT", float),
        "record_dE": ECC_parm("Record_every_dE", float),
        "E_range": ECC_parm("E_Range", int),
        "bandwidth": ECC_parm("Bandwidth", int),
        }

        p_duration = make_ecc_parm(self.device, ocv_param_names["duration"], parameters.duration)
        p_record = make_ecc_parm(self.device, ocv_param_names["record_dt"], parameters.record_dt)
        p_erange = make_ecc_parm(self.device, ocv_param_names["E_range"], parameters.e_range)
        p_band = make_ecc_parm(self.device, ocv_param_names["bandwidth"], parameters.bandwidth)

        return make_ecc_parms(self.device, p_duration, p_record, p_erange, p_band)
        return ecc_parms_ocv

    def  make_technique(self):

        # Name of the dll for the OCV technique (for both types of instruments VMP3/VSP300)
        ocv3_tech_file = "ocv.ecc"
        ocv4_tech_file = "ocv4.ecc"

        # pick the correct ecc file based on the instrument family
        tech_file_ocv = ocv3_tech_file if is_VMP3 else ocv4_tech_file

        # Define parameters for loading in the device using the templates
        ecc_parms_ocv = self.make_ocv_params()
        
        OcvTech = namedtuple("OcvTech", "ecc_file ecc_params user_params")
        return OcvTech(tech_file_ocv, ecc_parms_OCV, parameters)
