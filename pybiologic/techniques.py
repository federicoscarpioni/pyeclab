'''
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
- A dataclass XXX_params for storing all the parameters
- A function convert_XXX_ecc_params to create the parameters object
- A function make_XXX_tech to create the namedtuple

'''

import api.kbio_types as KBIO
from api.kbio_tech import ECC_parm, make_ecc_parm, make_ecc_parms
from dataclasses import dataclass
from collections import namedtuple


#=== Open Circuit Voltage =====================================================#

@dataclass
class OCV_params :
    duration  : float
    record_dt : float
    e_range   : float
    bandwidth : int

# -----------------------------------------------------------------------------#

def convert_OCV_params_ecc(parameters):
    '''
    Create parameters object from user values
    '''

    # Create dictionary with BioLogic parameters name
    OCV_parm_names = {
        'duration':  ECC_parm("Rest_time_T", float),
        'record_dt': ECC_parm("Record_every_dT", float),
        'record_dE': ECC_parm("Record_every_dE", float),
        'E_range':   ECC_parm("E_Range", int),
        'bandwidth': ECC_parm('Bandwidth', int),
    }

    # Convert user values to BioLogic parameters
    p_duration = make_ecc_parm(OCV_parm_names['duration'], parameters.duration)
    p_record = make_ecc_parm(OCV_parm_names['record_dt'], parameters.record_dt)
    p_erange = make_ecc_parm(OCV_parm_names['E_range'], KBIO.E_RANGE[parameters.e_range].value)
    p_band = make_ecc_parm(OCV_parm_names['bandwidth'], parameters.bandwidth)
    
    # Create parameters object
    ecc_parms_OCV = make_ecc_parms(p_duration,
                                   p_record,
                                   p_erange, 
                                   p_band)
    
    return ecc_parms_OCV

#------------------------------------------------------------------------------#

def make_OCV_tech(is_VMP3, parameters):
    '''
    Create a named tuple with technique file name converted parameters and user 
    parameters.
    '''

    # .ecc file names
    ocv3_tech_file   = "ocv.ecc"
    ocv4_tech_file   = "ocv4.ecc"
    
    # pick the correct ecc file based on the instrument family
    tech_file_OCV = ocv3_tech_file if is_VMP3 else ocv4_tech_file

    # Convert user parameters to ecc_parms parameter object
    ecc_parms_OCV = convert_OCV_params_ecc(parameters)

    # Store ecc file and parameters in namedtuple
    OCV_tech = namedtuple('OCV_tech', 'ecc_file ecc_params user_params')
    ocv_tech = OCV_tech(tech_file_OCV, ecc_parms_OCV, parameters)
    
    return ocv_tech


#=== Chrono-Potentiometry with Potential Limitations ==========================#

@dataclass
class CPLIM_params :
    current        : float
    duration       : float
    vs_init        : bool 
    nb_steps       : int 
    record_dt      : float
    record_dE      : float
    repeat         : int 
    i_range        : int
    e_range        : int
    exit_cond      : int 
    xctr           : int
    limit_variable : int
    limit_values   : float
    bandwidth      : int

#------------------------------------------------------------------------------#

def convert_CPLIM_params_ecc(parameters):
    '''
    Create parameters object from user values
    '''

    # Create dictionary with BioLogic parameters name
    CPLIM_parm_names = {
        'current_step':  ECC_parm("Current_step", float),
        'step_duration': ECC_parm("Duration_step", float),
        'vs_init':       ECC_parm("vs_initial", bool),
        'nb_steps':      ECC_parm("Step_number", int),
        'record_dt':     ECC_parm("Record_every_dT", float),
        'record_dE':     ECC_parm("Record_every_dE", float),
        'repeat':        ECC_parm("N_Cycles", int),
        'i_range':       ECC_parm("I_Range", int),
        'e_range':       ECC_parm("E_Range", int),
        'exit_cond':     ECC_parm("Exit_Cond",int),
        'xctr':          ECC_parm("xctr",int),
        'test1_config':  ECC_parm("Test1_Config", int),
        'test1_value':   ECC_parm("Test1_Value", float),
        'bandwidth':     ECC_parm('Bandwidth', int),
    }
    
    # Convert user values to BioLogic parameters
    idx = 0 # This way only one setp is allowed
    p_current_steps  = list()
    p_current_steps.append( make_ecc_parm(CPLIM_parm_names['current_step'], parameters.current, idx ) )
    p_current_steps.append( make_ecc_parm(CPLIM_parm_names['step_duration'], parameters.duration, idx ) )
    p_current_steps.append( make_ecc_parm(CPLIM_parm_names['vs_init'], parameters.vs_init, idx ) )
    p_current_steps.append( make_ecc_parm(CPLIM_parm_names['exit_cond'], parameters.exit_cond, idx) )
    p_current_steps.append( make_ecc_parm(CPLIM_parm_names['test1_config'], parameters.limit_variable, idx ) )
    p_current_steps.append( make_ecc_parm(CPLIM_parm_names['test1_value'], parameters.limit_values, idx ) )
    p_nb_steps       = make_ecc_parm(CPLIM_parm_names['nb_steps'], parameters.nb_steps )
    p_record_dt      = make_ecc_parm(CPLIM_parm_names['record_dt'], parameters.record_dt )
    p_record_dE      = make_ecc_parm(CPLIM_parm_names['record_dE'], parameters.record_dE )
    p_xctr           = make_ecc_parm(CPLIM_parm_names['xctr'], parameters.xctr )
    p_repeat         = make_ecc_parm(CPLIM_parm_names['repeat'], parameters.repeat )
    p_IRange         = make_ecc_parm(CPLIM_parm_names['i_range'], KBIO.I_RANGE[parameters.i_range].value )
    p_ERange         = make_ecc_parm(CPLIM_parm_names['e_range'], KBIO.E_RANGE[parameters.e_range].value)
    p_band           = make_ecc_parm(CPLIM_parm_names['bandwidth'], parameters.bandwidth )
    
    # Create parameters object
    ecc_parms_CPLIM  = make_ecc_parms(*p_current_steps, 
                                      p_nb_steps, 
                                      p_record_dt, 
                                      p_record_dE, 
                                      p_IRange,
                                      p_ERange, 
                                      p_repeat,
                                      p_xctr,
                                      p_band)
    
    return ecc_parms_CPLIM

#------------------------------------------------------------------------------#

def make_CPLIM_tech(is_VMP3, parameters):
    '''
    Create a named tuple with technique file name converted parameters and user 
    parameters.
    '''

    # Name of the dll for the CPLIM technique (for both types of instruments VMP3/VSP300)
    cplim3_tech_file = "cplimit.ecc"
    cplim4_tech_file = "cplimit4.ecc"
    
    # Pick the correct ecc file based on the instrument family
    tech_file_CPLIM = cplim3_tech_file if is_VMP3 else cplim4_tech_file
    
    # Convert user parameters to ecc_parms parameter object
    ecc_parms_CPLIM = convert_CPLIM_params_ecc(parameters)
    
    # Store ecc file and parameters in namedtuple
    CPLIM_tech = namedtuple('CPLIM_tech', 'ecc_file ecc_params user_params')
    cplim_tech = CPLIM_tech(tech_file_CPLIM, ecc_parms_CPLIM, parameters)
    
    return cplim_tech

#=== Chrono-Amperometry =======================================================#

@dataclass
class CA_params :
    voltage   : float
    duration  : float
    vs_init   : bool 
    nb_steps  : int 
    record_dt : float
    record_dI : float
    repeat    : int 
    i_range   : int
    e_range   : int
    exit_cond : int 
    xctr      : int
    bandwidth : int

#------------------------------------------------------------------------------#

def convert_CA_params_ecc(parameters):
    '''
    Create parameters object from user values
    '''
    # Create dictionary with BioLogic parameters name
    CA_parm_names = {
        'voltage_step':  ECC_parm("Voltage_step", float),
        'step_duration': ECC_parm("Duration_step", float),
        'vs_init':       ECC_parm("vs_initial", bool),
        'nb_steps':      ECC_parm("Step_number", int),
        'record_dt':     ECC_parm("Record_every_dT", float),
        'record_dI':     ECC_parm("Record_every_dI", float),
        'repeat':        ECC_parm("N_Cycles", int),
        'i_range':       ECC_parm("I_Range", int),
        'e_range':       ECC_parm("E_Range", int),
        'exit_cond':     ECC_parm("Exit_Cond",int),
        'xctr':          ECC_parm("xctr",int),
        'bandwidth':     ECC_parm('Bandwidth', int),
    }

    # Convert user values to BioLogic parameters
    idx = 0 # This way only one setp is allowed 
    p_voltage_steps  = list()
    p_voltage_steps.append( make_ecc_parm(CA_parm_names['voltage_step'], parameters.voltage, idx ) )
    p_voltage_steps.append( make_ecc_parm(CA_parm_names['step_duration'], parameters.duration, idx ) )
    p_voltage_steps.append( make_ecc_parm(CA_parm_names['vs_init'], parameters.vs_init, idx ) )
    p_nb_steps       = make_ecc_parm(CA_parm_names['nb_steps'], parameters.nb_steps )
    p_record_dt      = make_ecc_parm(CA_parm_names['record_dt'], parameters.record_dt )
    p_record_dI      = make_ecc_parm(CA_parm_names['record_dI'], parameters.record_dI )
    p_xctr           = make_ecc_parm(CA_parm_names['xctr'], parameters.xctr )
    p_repeat         = make_ecc_parm(CA_parm_names['repeat'], parameters.repeat )
    p_IRange         = make_ecc_parm(CA_parm_names['i_range'], KBIO.I_RANGE[parameters.i_range].value )
    p_ERange         = make_ecc_parm(CA_parm_names['e_range'], KBIO.E_RANGE[parameters.e_range].value)
    p_band           = make_ecc_parm(CA_parm_names['bandwidth'], parameters.bandwidth )
    
    # Create parameters object
    ecc_parms_CA = make_ecc_parms(*p_voltage_steps, # all array type paramaters goes together
                                  p_nb_steps, 
                                  p_record_dt, 
                                  p_record_dI,
                                  p_IRange,
                                  p_ERange, 
                                  p_repeat,
                                  p_xctr,
                                  p_band)
    
    return ecc_parms_CA

#------------------------------------------------------------------------------#

def make_CA_tech(is_VMP3, parameters):
    '''
    Create a named tuple with technique file name converted parameters and user 
    parameters.
    '''

    # Name of the dll for the CA technique (for both types of instruments VMP3/VSP300)
    cplim3_tech_file = "ca.ecc"
    cplim4_tech_file = "ca4.ecc"

    # pick the correct ecc file based on the instrument family
    tech_file_CA = cplim3_tech_file if is_VMP3 else cplim4_tech_file
    
    # Convert user parameters to ecc_parms parameter object
    ecc_parms_CA = convert_CA_params_ecc(parameters)
    
    # Store ecc file and parameters in namedtuple
    CA_tech = namedtuple('CA_tech', 'ecc_file ecc_params user_params')
    ca_tech = CA_tech(tech_file_CA, ecc_parms_CA, parameters)
    
    return ca_tech

#=== Loop =====================================================================#

@dataclass
class LOOP_params :
    repeat_N  : int
    loop_start : int

#------------------------------------------------------------------------------#

def convert_LOOP_params_ecc(parameters):
    '''
    Create parameters object from user values
    '''
    # Create dictionary with BioLogic parameters name
    loop_parms = {
        'reapeat' :    ECC_parm("loop_N_times", int),
        'loop_start' : ECC_parm('protocol_number', int),
    }

    # Convert user values to BioLogic parameters
    p_repeat_N     = make_ecc_parm(loop_parms['reapeat'], parameters.repeat_N)
    p_loop_start   = make_ecc_parm(loop_parms['loop_start'], parameters.loop_start)
    
    # Create parameters object
    ecc_parms_loop = make_ecc_parms(p_repeat_N, 
                                    p_loop_start)
    
    return ecc_parms_loop

#------------------------------------------------------------------------------#

def make_LOOP_tech(is_VMP3, parameters):
    '''
    Create a named tuple with technique file name converted parameters and user 
    parameters.
    '''

    # Name of the dll for the loop technique (for both types of instruments VMP3/VSP300)
    loop3_tech_file   = "loop.ecc"
    loop4_tech_file   = "loop4.ecc"

    # Pick the correct ecc file based on the instrument family
    tech_file_loop = loop3_tech_file if is_VMP3 else loop4_tech_file
    
    # Convert user parameters to ecc_parms parameter object
    ecc_parms_loop = convert_LOOP_params_ecc(parameters)
    
    # Store ecc file and parameters in namedtuple
    LOOP_tech = namedtuple('LOOP_tech', 'ecc_file ecc_params user_params')
    loop_tech = LOOP_tech(tech_file_loop, ecc_parms_loop, parameters)
    
    return loop_tech