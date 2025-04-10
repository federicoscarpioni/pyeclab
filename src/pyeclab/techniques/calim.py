from attrs import define, field

import pyeclab.api.kbio_types as KBIO
from pyeclab.api.kbio_tech import ECC_parm, make_ecc_parm, make_ecc_parms
from pyeclab.device import BiologicDevice
from pyeclab.techniques.exit_cond import EXIT_COND


@define(kw_only=True)
class ChronoAmperometryWithLimits:
    device: BiologicDevice
    voltage: float
    duration: float
    vs_init: bool
    nb_steps: int
    record_dt: float
    record_dI: float
    repeat: int
    i_range: KBIO.I_RANGE

    # @i_range.validator
    # def check(self, attribute, value):
    #     if value == KBIO.I_RANGE.I_RANGE_AUTO:
    #         raise ValueError("For this technique, I_RANGE_AUTO is not allowed.")

    e_range: KBIO.E_RANGE
    exit_cond: EXIT_COND = EXIT_COND.NEXT_TECHNIQUE
    limit_variable: int
    limit_value: float
    bandwidth: KBIO.BANDWIDTH
    xctr: int | None = None
    ecc_file: str | None = field(init=False, default=None)
    ecc_params: KBIO.EccParams | None = field(init=False, default=None)

    def make_calim_params(self):
        # dictionary of CP parameters (non exhaustive)
        calim_param_names = {
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
            "test1_config": ECC_parm("Test1_Config", int),
            "test1_value": ECC_parm("Test1_Value", float),
            "bandwidth": ECC_parm("Bandwidth", int),
        }
        idx = 0  # Only one current step is used
        p_voltage_steps = list()
        p_voltage_steps.append(make_ecc_parm(self.device, calim_param_names["voltage_step"], self.voltage, idx))
        p_voltage_steps.append(make_ecc_parm(self.device, calim_param_names["step_duration"], self.duration, idx))
        p_voltage_steps.append(make_ecc_parm(self.device, calim_param_names["vs_init"], self.vs_init, idx))
        p_voltage_steps.append(make_ecc_parm(self.device, calim_param_names["exit_cond"], self.exit_cond.value, idx))
        p_voltage_steps.append(make_ecc_parm(self.device, calim_param_names["test1_config"], self.limit_variable, idx))
        p_voltage_steps.append(make_ecc_parm(self.device, calim_param_names["test1_value"], self.limit_value, idx))
        p_nb_steps = make_ecc_parm(self.device, calim_param_names["nb_steps"], self.nb_steps)
        p_record_dt = make_ecc_parm(self.device, calim_param_names["record_dt"], self.record_dt)
        p_record_dI = make_ecc_parm(self.device, calim_param_names["record_dI"], self.record_dI)
        p_repeat = make_ecc_parm(self.device, calim_param_names["repeat"], self.repeat)
        p_IRange = make_ecc_parm(self.device, calim_param_names["i_range"], self.i_range.value)
        p_ERange = make_ecc_parm(self.device, calim_param_names["e_range"], self.e_range.value)
        p_band = make_ecc_parm(self.device, calim_param_names["bandwidth"], self.bandwidth.value)
        # make the technique parameter array
        params_list = [
            *p_voltage_steps,  # all array type paramaters goes together
            p_nb_steps,
            p_record_dt,
            p_record_dI,
            p_IRange,
            p_ERange,
            p_repeat,
            p_band,
        ]
        if self.xctr:
            p_xctr = make_ecc_parm(self.device, calim_param_names["xctr"], self.xctr)
            params_list.append(p_xctr)
        ecc_parms_calim = make_ecc_parms(
            self.device,
            *params_list
        )
        return ecc_parms_calim

    def choose_ecc_file(self):
        # Name of the dll for the CPLIM technique (for both types of instruments VMP3/VSP300)
        calim3_tech_file = "calimit.ecc"
        calim4_tech_file = "calimit4.ecc"

        # pick the correct ecc file based on the instrument family
        return calim3_tech_file if self.device.is_VMP3 else calim4_tech_file

    def make_technique(self):
        self.ecc_file = self.choose_ecc_file()
        self.ecc_params = self.make_calim_params()
