#=== Helper functions =========================================================#

def duration_to_1s(api, technique, tech_id):
    new_duration = 1
    parameters={
        'current_step':  ECC_parm("Current_step", float),
        'voltage_step':  ECC_parm("Voltage_step", float),
        'step_duration': ECC_parm("Duration_step", float),
        'vs_init':       ECC_parm("vs_initial", bool),
        }
    idx = 0 # Only one current step is used 
    p_current_steps  = list()
    if tech_id == 155:
       p_current_steps.append( make_ecc_parm(api, parameters['current_step'], technique.user_params.current, idx ) )
    elif tech_id == 101:
       p_current_steps.append( make_ecc_parm(api, parameters['voltage_step'], technique.user_params.voltage, idx ) )
    p_current_steps.append( make_ecc_parm(api, parameters['step_duration'], new_duration, idx ) )
    p_current_steps.append( make_ecc_parm(api, parameters['vs_init'], technique.user_params.vs_init, idx ) )
    return make_ecc_parms(api,*p_current_steps)

#------------------------------------------------------------------------------#

def reset_duration(api, technique, tech_id):
    parameters={
        'current_step':  ECC_parm("Current_step", float),
        'voltage_step':  ECC_parm("Voltage_step", float),
        'step_duration': ECC_parm("Duration_step", float),
        'vs_init':       ECC_parm("vs_initial", bool),}
    idx = 0 # Only one current step is used 
    p_current_steps  = list()
    if tech_id == 155:
       p_current_steps.append( make_ecc_parm(api, parameters['current_step'], technique.user_params.current, idx ) )
    elif tech_id == 101:
       p_current_steps.append( make_ecc_parm(api, parameters['voltage_step'], technique.user_params.voltage, idx ) )
    p_current_steps.append( make_ecc_parm(api, parameters['step_duration'], technique.user_params.duration, idx ) )
    p_current_steps.append( make_ecc_parm(api, parameters['vs_init'], technique.user_params.vs_init, idx ) )
    return make_ecc_parms(api,*p_current_steps)

#------------------------------------------------------------------------------#

def update_CA_voltage(api, Ewe, technique):
    CA_parm_names = {
        'voltage_step':  ECC_parm("Voltage_step", float),
        'step_duration': ECC_parm("Duration_step", float),
        'vs_init':       ECC_parm("vs_initial", bool),
        }
    idx = 0 # Only one current step is used 
    p_voltage_steps  = list()
    p_voltage_steps.append( make_ecc_parm(api, CA_parm_names['voltage_step'], Ewe, idx ) )
    p_voltage_steps.append( make_ecc_parm(api, CA_parm_names['step_duration'], technique.user_params.duration, idx ) )
    p_voltage_steps.append( make_ecc_parm(api, CA_parm_names['vs_init'], technique.user_params.vs_init, idx ) )
    return make_ecc_parms(api,*p_voltage_steps)

#==============================================================================#