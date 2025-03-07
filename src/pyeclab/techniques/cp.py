from attrs import define, field, validators

import pyeclab.api.kbio_types as KBIO
from pyeclab.api.kbio_tech import ECC_parm, make_ecc_parm, make_ecc_parms
from pyeclab.device import BiologicDevice
from pyeclab.techniques.exit_cond import EXIT_COND


@define(kw_only=True)
class ChronoPotentiometry:
    device: BiologicDevice
    current: float
    duration: float = field(validator=validators.ge(0))
    vs_init: bool
    nb_steps: int = field(validator=validators.and_(validators.ge(0), validators.le(19)))
    record_dt: float = field(validator=validators.ge(0))
    record_dE: float = field(validator=validators.ge(0))
    repeat: int = field(validator=validators.ge(0))
    i_range: KBIO.I_RANGE = field()

    # @i_range.validator
    # def check(self, attribute, value):
    #     if value == KBIO.I_RANGE.I_RANGE_AUTO:
    #         raise ValueError("For this technique, I_RANGE_AUTO is not allowed.")

    e_range: KBIO.E_RANGE
    exit_cond: EXIT_COND = EXIT_COND.NEXT_TECHNIQUE
    bandwidth: KBIO.BANDWIDTH
    xctr: int | None = None
    ecc_file: str | None = field(init=False, default=None)
    ecc_params: KBIO.EccParams | None = field(init=False, default=None)

    def make_cp_params(self):
        # dictionary of CP parameters (non exhaustive)
        cp_param_names = {
            "current_step": ECC_parm("Current_step", float),
            "step_duration": ECC_parm("Duration_step", float),
            "vs_init": ECC_parm("vs_initial", bool),
            "nb_steps": ECC_parm("Step_number", int),
            "record_dt": ECC_parm("Record_every_dT", float),
            "record_dE": ECC_parm("Record_every_dE", float),
            "repeat": ECC_parm("N_Cycles", int),
            "i_range": ECC_parm("I_Range", int),
            "e_range": ECC_parm("E_Range", int),
            "exit_cond": ECC_parm("Exit_Cond", int),
            "xctr": ECC_parm("xctr", int),
            "bandwidth": ECC_parm("Bandwidth", int),
        }

        if self.i_range == KBIO.I_RANGE.I_RANGE_AUTO:
            raise ValueError("For this technique, I_RANGE_AUTO is not allowed.")

        idx = 0  # Only one current step is used
        p_current_steps = list()
        p_current_steps.append(make_ecc_parm(self.device, cp_param_names["current_step"], self.current, idx))
        p_current_steps.append(make_ecc_parm(self.device, cp_param_names["step_duration"], self.duration, idx))
        p_current_steps.append(make_ecc_parm(self.device, cp_param_names["vs_init"], self.vs_init, idx))
        p_current_steps.append(make_ecc_parm(self.device, cp_param_names["exit_cond"], self.exit_cond.value, idx))
        p_nb_steps =make_ecc_parm(self.device, cp_param_names["nb_steps"], self.nb_steps)
        p_record_dt = make_ecc_parm(self.device, cp_param_names["record_dt"], self.record_dt)
        p_record_dE = make_ecc_parm(self.device, cp_param_names["record_dE"], self.record_dE)
        p_repeat = make_ecc_parm(self.device, cp_param_names["repeat"], self.repeat)
        p_IRange =  make_ecc_parm(self.device, cp_param_names["i_range"], self.i_range.value)
        p_ERange =  make_ecc_parm(self.device, cp_param_names["e_range"], self.e_range.value)
        p_band =  make_ecc_parm(self.device, cp_param_names["bandwidth"], self.bandwidth.value)

        # Make the technique parameter array
        if self.xctr:
            p_xctr = make_ecc_parm(self.device, cp_param_names["xctr"], self.xctr)
            p_current_steps.append(p_xctr)

        ecc_parms_cp = make_ecc_parms(
            self.device,
            *p_current_steps,
            p_nb_steps,
            p_record_dt,
            p_record_dE,
            p_IRange,
            p_ERange,
            p_repeat,
            p_band,
        )
        return ecc_parms_cp

    def choose_ecc_file(self):
        # Name of the dll for the OCV technique (for both types of instruments VMP3/VSP300)
        cp3_tech_file = "cp.ecc"
        cp4_tech_file = "cp4.ecc"
        # Pick the correct ecc file based on the instrument family
        return cp3_tech_file if self.device.is_VMP3 else cp4_tech_file

    def make_technique(self):
        self.ecc_file = self.choose_ecc_file()
        self.ecc_params = self.make_cp_params()
