from pyeclab.api.kbio_tech import ECC_parm, make_ecc_parm, make_ecc_parms
from pyeclab.techniques.functions import reset_duration, set_duration_to_1s
from dataclasses import dataclass

# =============================
# Communication with the device
# =============================

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

#-------------------------------------------------------------------------------

def end_technique(channel):
    """
    End the current technique in the sequence by replacing its original
    duration to the value of 1 second (This is a workaround for the lack
    of a specific function in the EC-Lab SDK).
    """
    # Overwrite technique duration to 1 second to force automatic interruption
    channel.bio_device.UpdateParameters(
        channel.bio_device.device_id,
        channel.num,
        channel.current_tech_index,
        set_duration_to_1s(channel.bio_device, channel.sequence[channel.current_tech_index], channel.current_tech_id),
        channel.sequence[channel.current_tech_index].ecc_file,
    )
    # Reset duration to original value in case it is looped
    channel.bio_device.UpdateParameters(
        channel.bio_device.device_id,
        channel.num,
        channel.current_tech_index,
        reset_duration(channel.bio_device, channel.sequence[channel.current_tech_index], channel.current_tech_id),
        channel.sequence[channel.current_tech_index].ecc_file,
    )

# ===============
# Software limits
# ===============

@dataclass
class Condition:
     technique_index : int
     quantity : str
     operator : str
     threshold : float

#-------------------------------------------------------------------------------

# Original version
# def check_software_limits(channel):
#     """
#     Check if a certain condition (< or > of a trashold value) is met for a
#     value of the sampled data over a certain number of points.
#     """
#     for (
#             technique_index,
#             quantity,
#             operator,
#             threshold,
#         ) in (
#             channel.conditions
#         ):  # ? Can I manually add other attributes to current_values for the quantities that are missing?
#             if channel.data_info.TechniqueIndex == technique_index:
#                 quantity_value = getattr(
#                     channel.current_values, quantity, None
#                 )  # ! It works only for attributes of current_data. I need onther trick to make it work also for capacity or power
#                 if quantity_value is None:
#                     continue
#                 if operator == ">" and quantity_value >= threshold:
#                     return True
#                 elif operator == "<" and quantity_value <= threshold:
#                     return True
#     return False 

#-------------------------------------------------------------------------------

def check_software_limits(channel):
    """
    Check if a certain condition (< or > of a trashold value) is met for a
    value of the sampled data over a certain number of points.
    """
    for condition in channel.conditions:  # ? Can I manually add other attributes to current_values for the quantities that are missing?
        if channel.data_info.TechniqueIndex == condition.technique_index:
            quantity_value = getattr(
                channel.current_values, condition.quantity, None
            )  # ! It works only for attributes of current_data. I need onther trick to make it work also for capacity or power
            if quantity_value is None:
                continue
            if condition.operator == ">" and quantity_value >= condition.threshold:
                return True
            elif condition.operator == "<" and quantity_value <= condition.threshold:
                return True
    return False 