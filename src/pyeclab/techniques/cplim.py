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

from pyeclab.techniques.exit_cond import EXIT_COND

@define(kw_only=True)
class ChronoPotentiometryWithLimits:
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
    limit_variable: int 
    limit_values: float
    bandwidth: KBIO.BANDWIDTH
    xctr: int | None = None
    ecc_file : str | None = field(init = False, default = None)
    ecc_params : list | None = field(init = False, default = None)

    def make_cplim_params(self):
        # dictionary of CPLIM parameters (non exhaustive)
        cplim_param_names = {
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
            "test1_config": ECC_parm("Test1_Config", int),
            "test1_value": ECC_parm("Test1_Value", float),
            "bandwidth": ECC_parm("Bandwidth", int),
            # 'analog_filter': ECC_parm('Filter', int)
        }

        if self.i_range == KBIO.I_RANGE.I_RANGE_AUTO:
            raise ValueError("For this technique, I_RANGE_AUTO is not allowed.")

        idx = 0  # Only one current step is used
        p_current_steps = list()
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["current_step"], self.current, idx))
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["step_duration"], self.duration, idx))
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["vs_init"], self.vs_init, idx))
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["exit_cond"], self.exit_cond.value, idx))
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["test1_config"], self.limit_variable, idx))
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["test1_value"], self.limit_values, idx))
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["nb_steps"], self.nb_steps))
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["record_dt"], self.record_dt))
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["record_dE"], self.record_dE))
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["repeat"], self.repeat))
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["i_range"], self.i_range.value))
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["e_range"], self.e_range.value))
        p_current_steps.append(make_ecc_parm(self.device, cplim_param_names["bandwidth"], self.bandwidth.value))

        # Make the technique parameter array
        if self.xctr:
            p_xctr = make_ecc_parm(self.device, cplim_param_names["xctr"], self.xctr)
            p_current_steps.append(p_xctr)

        ecc_parms_cplim = make_ecc_parms(
            self.device,
            *p_current_steps,
        )
        return ecc_parms_cplim

    def choose_ecc_file(self):
        # Name of the dll for the OCV technique (for both types of instruments VMP3/VSP300)
        cplim3_tech_file = "cplimit.ecc"
        cplim4_tech_file = "cplimit4.ecc"
        # Pick the correct ecc file based on the instrument family
        return cplim3_tech_file if self.device.is_VMP3 else cplim4_tech_file


    def make_technique(self):
        self.ecc_file = self.choose_ecc_file()   
        self.ecc_params = self.make_cplim_params()