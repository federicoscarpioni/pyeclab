"""
This module contain functions to create a technique object to be loaded on the
BioLogic potentiost to perform electrochemical experiments.

For each technique a set of parameters are allowed (see OEM User's Guide).

NOTE: the following explanation is not contained in the manual (which uses only
Delphi language as example) but it can be found in the examples provided with
the Python wrapper in the installation folder of EC-lab Developer Package.

A technique object must be prepared in the following way:
- Python type numbers (int or floats) representing the parameters must be
  converted to c-types using the OEM function make_ecc_parm
- All the parameters must be incorporated in one object using the function
  make_ecc_parms (mind the 's')
- For convenience technique file (.ecc) and the parameters object can be converted
  to a namedtuple; this way, the technique file and parameters belong to one
  name space and can be easily accessed with the attribute notation.
The namedtuple istance can be used in the LoadTechnique function of the Python API.
Calling such function multiple times creates a sequence of techniques.

This library supports the following techniques (not all!):
- Open Circuit Voltage
- Chono-Amperometry with Potential Limitation
- Chrono-Potentiometry
- Loop
Note: some techniques like CP and CA allows multiple steps but in the following
functions, only one is abilitated. For most battery-related reasearch that is
enough.

For each technique are provided:
- A dictionary XXX_params for storing all the parameters
- A function convert_XXX_ecc_params to create the parameters object
- A function make_XXX_tech to create the namedtuple

"""

from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from wsgiref.validate import validator

from attrs import define, field, validators

import pyeclab.api.kbio_types as KBIO
from pyeclab.api.tech_types import TECH_ID
from pyeclab.device import BiologicDevice
import pyeclab.tech_names as tn
from pyeclab.api.kbio_api import KBIO_api
from pyeclab.api.kbio_tech import ECC_parm, make_ecc_parm, make_ecc_parms

# === Auxiliary functions ======================================================#


def set_duration_to_1s(api, technique, tech_id):
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
        p_current_steps.append(make_ecc_parm(api, parameters["current_step"], technique.user_params.current, idx))

    elif tech_id == TECH_ID.CA.value:
        p_current_steps.append(make_ecc_parm(api, parameters["voltage_step"], technique.user_params.voltage, idx))

    if tech_id != TECH_ID.OCV.value:
        p_current_steps.append(make_ecc_parm(api, parameters["vs_init"], technique.user_params.vs_init, idx))

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
        p_current_steps.append(make_ecc_parm(api, parameters["current_step"], technique.user_params.current, idx))

    elif tech_id == TECH_ID.CA.value:
        p_current_steps.append(make_ecc_parm(api, parameters["voltage_step"], technique.user_params.voltage, idx))

    if tech_id != TECH_ID.OCV.value:
        p_current_steps.append(make_ecc_parm(api, parameters["vs_init"], technique.user_params.vs_init, idx))

    p_current_steps.append(make_ecc_parm(api, parameters["step_duration"], technique.user_params.duration, idx))

    return make_ecc_parms(api, *p_current_steps)


# === Techniques definition functions =========================================#

# ------ OCV ------- #

@define(kw_only=True)
class OpenCircuitVoltage:
    device: BiologicDevice
    duration: float
    record_dt: float
    e_range: KBIO.E_RANGE
    bandwidth: KBIO.BANDWIDTH

    def make_ocv_params(self):
        # List of OCV parameters
        OCV_parm_names = {
        "duration": ECC_parm("Rest_time_T", float),
        "record_dt": ECC_parm("Record_every_dT", float),
        "record_dE": ECC_parm("Record_every_dE", float),
        "E_range": ECC_parm("E_Range", int),
        "bandwidth": ECC_parm("Bandwidth", int),
        }

        p_duration = make_ecc_parm(api, OCV_parm_names["duration"], parameters.duration)
        p_record = make_ecc_parm(api, OCV_parm_names["record_dt"], parameters.record_dt)
        p_erange = make_ecc_parm(api, OCV_parm_names["E_range"], parameters.e_range)
        p_band = make_ecc_parm(api, OCV_parm_names["bandwidth"], parameters.bandwidth)

        return make_ecc_parms(api, p_duration, p_record, p_erange, p_band)
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



# ------CPLIM------- #


class EXIT_COND(Enum):
    NEXT_STEP = 0
    NEXT_TECHNIQUE = 1
    STOP_EXPERIMENT = 2


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

    @i_range.validator
    def check(self, attribute, value):
        if value == KBIO.I_RANGE.I_RANGE_AUTO:
            raise ValueError("For this technique, I_RANGE_AUTO is not allowed.")

    e_range: KBIO.E_RANGE
    exit_cond: EXIT_COND
    limit_variable: int
    limit_values: float
    bandwidth: KBIO.BANDWIDTH
    xctr: int | None = None
    # analog_filter  : int

    def make_cplim_parms(self):
        # dictionary of CPLIM parameters (non exhaustive)
        CPLIM_parm_names = {
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
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["current_step"], self.current, idx))
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["step_duration"], self.duration, idx))
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["vs_init"], self.vs_init, idx))
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["exit_cond"], self.exit_cond.value, idx))
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["test1_config"], self.limit_variable, idx))
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["test1_value"], self.limit_values, idx))
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["nb_steps"], self.nb_steps))
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["record_dt"], self.record_dt))
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["record_dE"], self.record_dE))
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["repeat"], self.repeat))
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["i_range"], self.i_range.value))
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["e_range"], self.e_range.value))
        p_current_steps.append(make_ecc_parm(self.device, CPLIM_parm_names["bandwidth"], self.bandwidth.value))
        # p_filter         = make_ecc_parm( api, CPLIM_parm_names['analog_filter'], 0)#KBIO.FILTER[parameters.analog_filter].value)
        # make the technique parameter array

        if self.xctr:
            p_xctr = make_ecc_parm(self.device, CPLIM_parm_names["xctr"], self.xctr)
            p_current_steps.append(p_xctr)

        ecc_parms_CPLIM = make_ecc_parms(
            self.device,
            *p_current_steps,
        )
        return ecc_parms_cplim

    def make_technique(self):
        # Name of the dll for the CPLIM technique (for both types of instruments VMP3/VSP300)
        cplim3_tech_file = "cplimit.ecc"
        cplim4_tech_file = "cplimit4.ecc"

        # pick the correct ecc file based on the instrument family
        tech_file_CPLIM = cplim3_tech_file if self.device.is_VMP3 else cplim4_tech_file

        # Define parameters for loading in the device using the templates
        ecc_parms_CPLIM = self.make_cplim_parms()

        CplimTech = namedtuple("CplimTech", "ecc_file ecc_params")
        return CplimTech(tech_file_CPLIM, ecc_parms_CPLIM)


# ------CA------- #


@dataclass
class CA_params:
    voltage: float
    duration: float
    vs_init: bool
    nb_steps: int
    record_dt: float
    record_dI: float
    repeat: int
    i_range: int
    e_range: int
    exit_cond: int
    xctr: int
    bandwidth: int


def make_CA_ecc_params(api, parameters):
    # dictionary of CP parameters (non exhaustive)
    CA_parm_names = {
        "voltage_step": ECC_parm("Voltage_step", float),
        "step_duration": ECC_parm("Duration_step", float),
        "vs_init": ECC_parm("vs_initial", bool),
        "nb_steps": ECC_parm("Step_number", int),
        "record_dt": ECC_parm("Record_every_dT", float),
        "record_dI": ECC_parm("Record_every_dI", float),
        "repeat": ECC_parm("N_Cycles", int),
        "i_range": ECC_parm("I_Range", int),
        "e_range": ECC_parm("E_Range", int),
        "exit_cond": ECC_parm("Exit_Cond", int),
        "xctr": ECC_parm("xctr", int),
        "bandwidth": ECC_parm("Bandwidth", int),
    }
    idx = 0  # Only one current step is used
    p_voltage_steps = list()
    p_voltage_steps.append(make_ecc_parm(api, CA_parm_names["voltage_step"], parameters.voltage, idx))
    p_voltage_steps.append(make_ecc_parm(api, CA_parm_names["step_duration"], parameters.duration, idx))
    p_voltage_steps.append(make_ecc_parm(api, CA_parm_names["vs_init"], parameters.vs_init, idx))
    p_nb_steps = make_ecc_parm(api, CA_parm_names["nb_steps"], parameters.nb_steps)
    p_record_dt = make_ecc_parm(api, CA_parm_names["record_dt"], parameters.record_dt)
    p_record_dI = make_ecc_parm(api, CA_parm_names["record_dI"], parameters.record_dI)
    p_xctr = make_ecc_parm(api, CA_parm_names["xctr"], parameters.xctr)
    p_repeat = make_ecc_parm(api, CA_parm_names["repeat"], parameters.repeat)
    p_IRange = make_ecc_parm(api, CA_parm_names["i_range"], parameters.i_range)
    p_ERange = make_ecc_parm(api, CA_parm_names["e_range"], parameters.e_range)
    p_band = make_ecc_parm(api, CA_parm_names["bandwidth"], parameters.bandwidth)
    # make the technique parameter array
    ecc_parms_CA = make_ecc_parms(
        api,
        *p_voltage_steps,  # all array type paramaters goes together
        p_nb_steps,
        p_record_dt,
        p_record_dI,
        p_IRange,
        p_ERange,
        p_repeat,
        p_xctr,
        p_band,
    )
    return ecc_parms_CA


def CA_tech(api, is_VMP3, parameters):
    # Name of the dll for the CPLIM technique (for both types of instruments VMP3/VSP300)
    cplim3_tech_file = "ca.ecc"
    cplim4_tech_file = "ca4.ecc"

    # pick the correct ecc file based on the instrument family
    tech_file_CA = cplim3_tech_file if is_VMP3 else cplim4_tech_file
    # Define parameters for loading in the device using the templates
    ecc_parms_CA = make_CA_ecc_params(api, parameters)

    CA_tech = namedtuple("CA_tech", "ecc_file ecc_params user_params")
    ca_tech = CA_tech(tech_file_CA, ecc_parms_CA, parameters)

    return ca_tech


# ------Loop------- #


@dataclass
class LOOP_params:
    repeat_N: int
    loop_start: int


def make_loop_ecc_params(api, parameters):
    # Dictionary of parameters used to call the labrary later
    loop_parms = {
        "reapeat": ECC_parm("loop_N_times", int),
        "loop_start": ECC_parm("protocol_number", int),
    }

    p_repeat_N = make_ecc_parm(api, loop_parms["reapeat"], parameters.repeat_N)
    p_loop_start = make_ecc_parm(api, loop_parms["loop_start"], parameters.loop_start)

    ecc_parms_loop = make_ecc_parms(api, p_repeat_N, p_loop_start)
    return ecc_parms_loop


def loop_tech(api, is_VMP3, parameters):
    # .ecc file names
    loop3_tech_file = "loop.ecc"
    loop4_tech_file = "loop4.ecc"

    # pick the correct ecc file based on the instrument family
    tech_file_loop = loop3_tech_file if is_VMP3 else loop4_tech_file

    ecc_parms_loop = make_loop_ecc_params(api, parameters)

    LOOP_tech = namedtuple("LOOP_tech", "ecc_file ecc_params user_params")
    loop_tech = LOOP_tech(tech_file_loop, ecc_parms_loop, parameters)

    return loop_tech


#  !!! From old module. Must review them later
# def duration_to_1s(api, technique, tech_id):
#     new_duration = 1
#     parameters={
#         'current_step':  ECC_parm("Current_step", float),
#         'voltage_step':  ECC_parm("Voltage_step", float),
#         'step_duration': ECC_parm("Duration_step", float),
#         'vs_init':       ECC_parm("vs_initial", bool),
#         }
#     idx = 0 # Only one current step is used
#     p_current_steps  = list()
#     if tech_id == 155:
#        p_current_steps.append( make_ecc_parm(api, parameters['current_step'], technique.user_params.current, idx ) )
#     elif tech_id == 101:
#        p_current_steps.append( make_ecc_parm(api, parameters['voltage_step'], technique.user_params.voltage, idx ) )
#     p_current_steps.append( make_ecc_parm(api, parameters['step_duration'], new_duration, idx ) )
#     p_current_steps.append( make_ecc_parm(api, parameters['vs_init'], technique.user_params.vs_init, idx ) )
#     return make_ecc_parms(api,*p_current_steps)


# def reset_duration(api, technique, tech_id):
#     parameters={
#         'current_step':  ECC_parm("Current_step", float),
#         'voltage_step':  ECC_parm("Voltage_step", float),
#         'step_duration': ECC_parm("Duration_step", float),
#         'vs_init':       ECC_parm("vs_initial", bool),}
#     idx = 0 # Only one current step is used
#     p_current_steps  = list()
#     if tech_id == 155:
#        p_current_steps.append( make_ecc_parm(api, parameters['current_step'], technique.user_params.current, idx ) )
#     elif tech_id == 101:
#        p_current_steps.append( make_ecc_parm(api, parameters['voltage_step'], technique.user_params.voltage, idx ) )
#     p_current_steps.append( make_ecc_parm(api, parameters['step_duration'], technique.user_params.duration, idx ) )
#     p_current_steps.append( make_ecc_parm(api, parameters['vs_init'], technique.user_params.vs_init, idx ) )
#     return make_ecc_parms(api,*p_current_steps)

# def update_CA_voltage(api, Ewe, technique):
#     CA_parm_names = {
#         'voltage_step':  ECC_parm("Voltage_step", float),
#         'step_duration': ECC_parm("Duration_step", float),
#         'vs_init':       ECC_parm("vs_initial", bool),
#         }
#     idx = 0 # Only one current step is used
#     p_voltage_steps  = list()
#     p_voltage_steps.append( make_ecc_parm(api, CA_parm_names['voltage_step'], Ewe, idx ) )
#     p_voltage_steps.append( make_ecc_parm(api, CA_parm_names['step_duration'], technique.user_params.duration, idx ) )
#     p_voltage_steps.append( make_ecc_parm(api, CA_parm_names['vs_init'], technique.user_params.vs_init, idx ) )
#     return make_ecc_parms(api,*p_voltage_steps)
