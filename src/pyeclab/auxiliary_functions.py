from dataclasses import dataclass
import os
from pyeclab.api.kbio_tech import ECC_parm, make_ecc_parm, make_ecc_parms

# ------------------------------------------------------------------------------#


def load_sequence_from_json(path: str) -> list:  # Specify which object type will be the list elements
    return sequence


# ------------------------------------------------------------------------------#


def create_empty_json_sequence(path: str, techniques: list[str]): ...


# ------------------------------------------------------------------------------#


def update_CA_voltage(api, Ewe, technique):
    CA_parm_names = {
        "voltage_step": ECC_parm("Voltage_step", float),
        "step_duration": ECC_parm("Duration_step", float),
        "vs_init": ECC_parm("vs_initial", bool),
    }
    idx = 0  # Only one current step is used
    p_voltage_steps = list()
    p_voltage_steps.append(make_ecc_parm(api, CA_parm_names["voltage_step"], Ewe, idx))
    p_voltage_steps.append(make_ecc_parm(api, CA_parm_names["step_duration"], technique.user_params.duration, idx))
    p_voltage_steps.append(make_ecc_parm(api, CA_parm_names["vs_init"], technique.user_params.vs_init, idx))
    return make_ecc_parms(api, *p_voltage_steps)


# ==============================================================================#
