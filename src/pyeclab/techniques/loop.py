from dataclasses import dataclass, field

import pyeclab.api.kbio_types as KBIO
from pyeclab.api.kbio_tech import ECC_parm, make_ecc_parm, make_ecc_parms
from pyeclab.device import BiologicDevice


@dataclass
class Loop:
    repeat_N: int
    loop_start: int
    ecc_file: str | None = field(init=False, default=None)
    ecc_params: KBIO.EccParams | None = field(init=False, default=None)

    def make_loop_params(self, device: BiologicDevice):
        # Dictionary of parameters used to call the labrary later
        loop_parms = {
            "reapeat": ECC_parm("loop_N_times", int),
            "loop_start": ECC_parm("protocol_number", int),
        }

        p_repeat_N = make_ecc_parm(device, loop_parms["reapeat"], self.repeat_N)
        p_loop_start = make_ecc_parm(device, loop_parms["loop_start"], self.loop_start)

        ecc_parms_loop = make_ecc_parms(device, p_repeat_N, p_loop_start)
        return ecc_parms_loop

    def choose_ecc_file(self, is_vmp3: bool):
        # .ecc file names
        loop3_tech_file = "loop.ecc"
        loop4_tech_file = "loop4.ecc"

        # pick the correct ecc file based on the instrument family
        return loop3_tech_file if is_vmp3 else loop4_tech_file

    def make_technique(self, device: BiologicDevice):
        self.ecc_file = self.choose_ecc_file(device.is_VMP3)
        self.ecc_params = self.make_loop_params(device)
