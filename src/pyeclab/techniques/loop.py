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
class Loop:
    device: BiologicDevice
    repeat_N: int
    loop_start: int

    def make_loop_params(self):
        # Dictionary of parameters used to call the labrary later
        loop_parms = {
            "reapeat": ECC_parm("loop_N_times", int),
            "loop_start": ECC_parm("protocol_number", int),
        }

        p_repeat_N = make_ecc_parm(self.device, loop_parms["reapeat"], parameters.repeat_N)
        p_loop_start = make_ecc_parm(self.device, loop_parms["loop_start"], parameters.loop_start)

        ecc_parms_loop = make_ecc_parms(self.device, p_repeat_N, p_loop_start)
        return ecc_parms_loop
    
    def make_technique(self):
         # .ecc file names
        loop3_tech_file = "loop.ecc"
        loop4_tech_file = "loop4.ecc"

        # pick the correct ecc file based on the instrument family
        tech_file_loop = loop3_tech_file if is_VMP3 else loop4_tech_file

        ecc_parms_loop = self.make_loop_params()

        LoopTech = namedtuple("LoopTech", "ecc_file ecc_params user_params")
        return LoopTech(tech_file_loop, ecc_parms_loop, parameters)