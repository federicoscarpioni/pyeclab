from pyeclab.api.kbio_tech import ECC_parm, make_ecc_parm, make_ecc_parms
from pyeclab.channel import Channel
from pyeclab.techniques.functions import reset_duration, set_duration_to_1s

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

