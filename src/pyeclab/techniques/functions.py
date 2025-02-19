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


def set_duration_to_1s(api: BiologicDevice, technique, tech_id: int):
    """
    Update the duration of CP or CA to 1s. It is used to force the technique to
    terminate not being present any specific function in the SDK.
    """
    new_duration = 1
    parameters = {
        "current_step": ECC_parm("Current_step", float),
        "voltage_step": ECC_parm("Voltage_step", float),
        "step_duration": ECC_parm("Duration_step", float),
        "vs_init": ECC_parm("vs_initial", bool),
    }
    idx = 0  # Only one current step is used
    p_current_steps = list()
    if tech_id == TECH_ID.CPLIMIT.value:
        p_current_steps.append(make_ecc_parm(api, parameters["current_step"], technique.current, idx))

    elif tech_id == TECH_ID.CA.value:
        p_current_steps.append(make_ecc_parm(api, parameters["voltage_step"], technique.voltage, idx))

    if tech_id != TECH_ID.OCV.value:
        p_current_steps.append(make_ecc_parm(api, parameters["vs_init"], technique.vs_init, idx))

    p_current_steps.append(make_ecc_parm(api, parameters["step_duration"], new_duration, idx))

    return make_ecc_parms(api, *p_current_steps)


# ------------------------------------------------------------------------------#


def reset_duration(api, technique, tech_id):
    parameters = {
        "current_step": ECC_parm("Current_step", float),
        "voltage_step": ECC_parm("Voltage_step", float),
        "step_duration": ECC_parm("Duration_step", float),
        "vs_init": ECC_parm("vs_initial", bool),
    }
    idx = 0  # Only one current step is used
    p_current_steps = list()
    if tech_id == TECH_ID.CPLIMIT.value:
        p_current_steps.append(make_ecc_parm(api, parameters["current_step"], technique.current, idx))

    elif tech_id == TECH_ID.CA.value:
        p_current_steps.append(make_ecc_parm(api, parameters["voltage_step"], technique.voltage, idx))

    if tech_id != TECH_ID.OCV.value:
        p_current_steps.append(make_ecc_parm(api, parameters["vs_init"], technique.vs_init, idx))

    p_current_steps.append(make_ecc_parm(api, parameters["step_duration"], technique.duration, idx))

    return make_ecc_parms(api, *p_current_steps)
